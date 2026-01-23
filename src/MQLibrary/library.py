import os
import subprocess

import ibmmq
from robot.api import logger
from robot.api.deco import keyword, library
from robot.utils import timestr_to_secs

from .exceptions import MQMIError_handling


def _new_md() -> ibmmq.MD:
    """Return a fresh MQ Message Descriptor (MD)."""
    md = ibmmq.MD()
    md.Version = ibmmq.CMQC.MQMD_VERSION_2
    return md


@library
class MQLibrary:
    """
    MQLibrary - A Robot Framework Library for IBM MQ Integration with multi-alias connection support.

    This library enables easy interaction with IBM MQ message queues from Robot Framework.

    It supports multiple simultaneous connections to different queue managers through aliases.
    If only one connection is used, the alias parameter can be omitted (defaults to "default").

    MQ server and MQ client must use compatible code pages.
    If code pages are not compatible error `2539: MQRC_CHANNEL_CONFIG_ERROR` will occur.
    If the client uses codepage 65001 (the windows equivalent of UTF-8) and the server uses codepage 850
    the channel name will not be found and the connection will fail.
    Forcing the client code page can be done with the `chcp` command.
    For example `chcp 437` to use default ascii code page.

    === Examples === 
    | `Connect MQ`    queue_manager=QM1
    | ...    hostname=localhost
    | ...    port=1414
    | ...    channel=DEV.APP.SVRCONN
    | ...    username=%{USERNAME}
    | ...    password=%{PASSWORD}
    | `Put MQ Message`    queue=QUEUE.TEST    message=Hello
    | ${messages}     `Get MQ Message`    queue=QUEUE.TEST    max_messages=1
    | `Clear MQ Queue`    queue=QUEUE.TEST
    | `Disconnect MQ`
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.connections = {}  # Holds aliases mapped to queue manager connections

        # Check for unsupported code page 65001 (Windows utf-8)
        if os.name == 'nt':
            codepage = int(subprocess.getoutput("chcp").split()[-1])
            if codepage == 65001:
                logger.warn("This shell uses codepage 65001, which is not supported by MQ, you will likely encounter error: 2539: MQRC_CHANNEL_CONFIG_ERROR.\n Use `chcp 437` in your shell to switch to a compatible codepage.")

    @keyword(name="Connect MQ", tags=["Connection"])
    def connect_mq(self, queue_manager: str, hostname: str, port: int, channel: str, username: str | None = None, password: str | None = None, alias: str = "default"):
        """
        Connects to the remote queue manager and stores it under an alias.

        | =Argument=        | =Description=                           |
        | ``queue_manager`` | Name of the queue manager               |
        | ``hostname``      | Hostname of the MQ server               |
        | ``port``          | Port used to connect                    |
        | ``channel``       | Channel name used for communication     |
        | ``username``      | Username for authentication (optional)  |
        | ``password``      | Password for authentication (optional)  |
        | ``alias``         | Connection alias (default = "default")  |

        === Example ===
        | `Connect MQ`    queue_manager=QM1
        | ...    hostname=localhost
        | ...    port=1414
        | ...    channel=DEV.APP.SVRCONN
        | ...    username=&{USERNAME}
        | ...    password=&{PASSWORD}
        """
        if alias in self.connections:
            raise ValueError(f"Alias '{alias}' is already connected.")

        try:
            conn_info = f"{hostname}({port})"
            cd = ibmmq.CD()
            cd.ChannelName = channel
            cd.ConnectionName = conn_info
            cd.ChannelType = ibmmq.CMQXC.MQCHT_CLNTCONN
            cd.TransportType = ibmmq.CMQXC.MQXPT_TCP

            qmgr = ibmmq.QueueManager(None)
            qmgr.connect_tcp_client(
                name=queue_manager,
                cd=cd,
                channel=channel,
                conn_name=conn_info,
                user=username,
                password=password
            )
            self.connections[alias] = qmgr
            logger.info(f"Connected to MQ with alias '{alias}'.")

        except ibmmq.MQMIError as e:
            MQMIError_handling(e, mqmanager=queue_manager, mqhost=hostname, mqport=port, mqchannel=channel)
        except Exception as e:
            logger.error(f"Failed to connect to MQ: {e}")
            raise


    def _get_qmgr(self, alias: str):
        if alias not in self.connections:
            raise ValueError("No valid MQ alias provided or no default connection available.")
        return self.connections[alias]


    @keyword(name="Put MQ Message", tags=["Put"])
    def put_message(self, queue: str, message: str, ccsid: int = 1208, alias: str = "default"):
        """
        Puts a message onto the target queue.

        | =Argument=  | =Description=                         |
        | ``queue``   | Name of the target queue              |
        | ``message`` | Message content to put on the queue   |
        | ``ccsid``   | Character encoding set (default 1208) |
        | ``alias``   | Alias of the MQ connection            |

        === Example ===
        | `Put MQ Message`    queue=QUEUE.TEST    message=Hello World
        """
        qmgr = self._get_qmgr(alias)
        queue_obj = None
        try:
            queue_obj = ibmmq.Queue(qmgr, queue)
            md = _new_md()
            md.CodedCharSetId = ccsid
            message_bytes = message.encode('utf-8')
            queue_obj.put(message_bytes, md)
            logger.info(f"Message put on queue '{queue}' via alias '{alias}'.")
        finally:
            if queue_obj:
                queue_obj.close()


    @keyword(name="Get MQ Messages", tags=["Retrieve"])
    def get_messages(self, queue: str, message_amount: int = 1, convert: bool = True, timeout: str = 0, alias: str = "default") -> list:
        """
        Retrieves messages from a queue and returns it as a list.
        Removes the messages from the queue on retrieval.

        | =Argument=         | =Description=                                       |
        | ``queue``          | Queue to read messages from                         |
        | ``message_amount`` | Number of messages to retrieve, fails if it doesn't |
        | ``convert``        | Convert message (MQGMO_CONVERT) if True             |
        | ``timeout``        | Timeout per message in seconds (default = 0)        |
        | ``alias``          | Alias of the MQ connection (default = "default")    |

        === Example ===
        | ${msgs}    `Get MQ Messages`    queue=QUEUE.TEST    message_amount=5    timeout=2
        """
        qmgr = self._get_qmgr(alias)
        queue_obj = None
        messages = []
        try:
            gmo = ibmmq.GMO()
            gmo.Options = ibmmq.CMQC.MQGMO_WAIT | (ibmmq.CMQC.MQGMO_CONVERT if convert else 0)

            timeout_ms = int(timestr_to_secs(timeout) * 1000)
            gmo.WaitInterval = timeout_ms

            queue_obj = ibmmq.Queue(qmgr, queue)
            for _ in range(message_amount):
                md = _new_md()
                try:
                    message = queue_obj.get(None, md, gmo)
                    try:
                        decoded = message.decode("utf-8")
                    except UnicodeDecodeError:
                        logger.warn("UTF-8 decoding failed, falling back to ISO-8859-1.")
                        decoded = message.decode("iso-8859-1")
                    messages.append(decoded)
                    logger.info(f"Received message from queue '{queue}': {decoded}")
                except ibmmq.MQMIError as e:
                    if e.reason == ibmmq.CMQC.MQRC_NO_MSG_AVAILABLE:
                        logger.info(f"No more messages available on queue '{queue}'.")
                        break
                    logger.error(f"Failed to get message from queue '{queue}': {e}")
                    raise
            if len(messages) == message_amount:
                return messages
            message = f"Expected {message_amount} message(s), but received {len(messages)}."
            logger.error(message)
            raise AssertionError(message)
        finally:
            if queue_obj:
                queue_obj.close()


    @keyword(name="Browse MQ Messages", tags=["Retrieve"])
    def browse_messages(self, queue: str, max_messages: int = 1, timeout: str = '5s', convert: bool = True, alias: str = "default") -> list:
        """
        Browses for messages on ``queue`` and returns them in a list.
        Doesn't delete a message after being browsed.

        | =Argument=        | =Description=                                      |
        | ``queue``         | Queue to listen on                                 |
        | ``max_messages``  | Maximum number of messages it tries to retrieve    |
        | ``timeout``       | Timeout per message in milliseconds (default 5000) |
        | ``convert``       | Convert message encoding if True                   |
        | ``alias``         | MQ connection alias (default = "default")          |

        === Example ===
        | ${msgs}    `Browse MQ Messages`    queue=QUEUE.TEST    max_messages=3
        """
        qmgr = self._get_qmgr(alias)
        messages = []
        queue_obj = None
        try:
            timeout_ms = int(timestr_to_secs(timeout) * 1000)
            queue_obj = ibmmq.Queue(qmgr, queue, ibmmq.CMQC.MQOO_BROWSE)
            logger.info(f"Browsing messages on '{queue}' via alias '{alias}'...")

            for i in range(max_messages):
                gmo = ibmmq.GMO()
                gmo.Options = ibmmq.CMQC.MQGMO_WAIT | (ibmmq.CMQC.MQGMO_CONVERT if convert else 0)
                gmo.WaitInterval = timeout_ms
                gmo.Options |= ibmmq.CMQC.MQGMO_BROWSE_FIRST if i == 0 else ibmmq.CMQC.MQGMO_BROWSE_NEXT

                md = _new_md()
                try:
                    message = queue_obj.get(None, md, gmo)
                    try:
                        decoded = message.decode("utf-8")
                    except UnicodeDecodeError:
                        logger.warn("UTF-8 decoding failed, falling back to ISO-8859-1.")
                        decoded = message.decode("iso-8859-1")
                    messages.append(decoded)
                    logger.info(f"Browsed message {i + 1}: {decoded}")
                except ibmmq.MQMIError as e:
                    if e.reason == ibmmq.CMQC.MQRC_NO_MSG_AVAILABLE:
                        logger.info(f"No more messages available to browse on queue '{queue}'.")
                        break
                    logger.error(f"Error while browsing message: {e}")
                    raise
            return messages
        finally:
            if queue_obj:
                queue_obj.close()


    @keyword(name="Clear MQ Queue", tags=["Cleanup"])
    def clear_queue(self, queue: str, alias: str = "default"):
        """
        Removes all messages from a queue immediately without waiting.

        | =Argument=     | =Description=                                  |
        | ``queue``      | The queue to clear                             |
        | ``alias``      | MQ connection alias (default = "default")      |

        === Example ===
        | `Clear MQ Queue`    queue=QUEUE.TEST
        """
        qmgr = self._get_qmgr(alias)
        queue_obj = None
        try:
            gmo = ibmmq.GMO()
            gmo.Options = ibmmq.CMQC.MQGMO_NO_WAIT
            gmo.WaitInterval = 0
            queue_obj = ibmmq.Queue(qmgr, queue, ibmmq.CMQC.MQOO_INPUT_AS_Q_DEF)

            logger.info(f"Clearing all messages from queue '{queue}' via alias '{alias}'...")

            cleared_count = 0
            while True:
                md = _new_md()
                try:
                    _ = queue_obj.get(None, md, gmo)
                    cleared_count += 1
                except ibmmq.MQMIError as e:
                    if e.reason == ibmmq.CMQC.MQRC_NO_MSG_AVAILABLE:
                        break
                    logger.error(f"Error while clearing queue: {e}")
                    raise

            logger.info(f"Cleared {cleared_count} message(s) from queue '{queue}' via alias '{alias}'.")

            # Final verification that queue is empty
            md = _new_md()
            try:
                queue_obj.get(None, md, gmo)
                raise AssertionError(f"Queue '{queue}' still contains messages after clearing.")
            except ibmmq.MQMIError as e:
                if e.reason == ibmmq.CMQC.MQRC_NO_MSG_AVAILABLE:
                    logger.info(f"Verified queue '{queue}' is empty.")
                else:
                    logger.error(f"Unexpected error while verifying queue: {e}")
                    raise
        finally:
            if queue_obj:
                queue_obj.close()


    @keyword(name="Disconnect MQ", tags=["Connection"])
    def disconnect_mq(self, alias: str = "default"):
        """Disconnects a specific MQ connection using alias."""
        if alias in self.connections:
            try:
                self.connections[alias].disconnect()
                logger.info(f"Disconnected from MQ alias '{alias}'.")
            except Exception as e:
                logger.warn(f"Error while disconnecting alias '{alias}': {e}")
            finally:
                del self.connections[alias]


    @keyword(name="Disconnect All MQ Connections", tags=["Connection"])
    def disconnect_all(self):
        """Disconnects all active MQ connections."""
        for alias in list(self.connections.keys()):
            self.disconnect_mq(alias)
