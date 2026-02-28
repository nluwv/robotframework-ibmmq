import ibmmq
from robot.api import logger

def MQMIError_handling(mqerror, **manager_settings):
    match mqerror.reason:
        case ibmmq.CMQC.MQRC_Q_MGR_NAME_ERROR:  # 2058
            message = f"Queue Manager {manager_settings['mqmanager']} does not exist or is unavailable."
            logger.error(message)
            raise ValueError(mqerror)
        case ibmmq.CMQC.MQRC_HOST_NOT_AVAILABLE:  # 2538
            message = f"Cannot connect to MQ host {manager_settings['mqhost']}:{manager_settings['mqport']}. Host not available or refusing connection."
            logger.error(message)
            raise ValueError(mqerror)
        case ibmmq.CMQC.MQRC_UNKNOWN_CHANNEL_NAME:  # 2540
            message = f"Channel {manager_settings['mqchannel']} is unknown or not configured correctly on the MQ server."
            logger.error(message)
            raise ValueError(mqerror)
        case ibmmq.CMQC.MQRC_SECURITY_ERROR:  # 2063
            message = f"Authentication failed. Check username and password for queue manager {manager_settings['mqmanager']}."
            logger.error(message)
            raise ValueError(mqerror)
        case _:
            logger.error(f"MQ connection failed with reason code {mqerror.reason}: {mqerror}")  # Generiek maken
            raise
