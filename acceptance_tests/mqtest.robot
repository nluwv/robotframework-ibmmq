*** Comments ***
# robotcode: ignore[KeywordNotFound]


*** Settings ***
Library      OperatingSystem
Library      MQLibrary
Variables    variables/mq_settings.yaml

# robot -d results -L TRACE -P ./src .
# libdoc -P ./src MQLibrary docs/mqlibrary.html


*** Test Cases ***
Test Put And Read
    [Tags]    get    # Connect / Custom alias / Put / Get / Disconnect
    VAR    ${alias}    test_alias
    VAR    ${queue}    MQLIBRARY_TEST
    ${message}    Get File    acceptance_tests/messages/example.json
    Connect MQ
    ...    alias=${alias}
    ...    queue_manager=${MQ_MANAGER}
    ...    hostname=${MQ_HOSTNAME}
    ...    port=${MQ_PORT}
    ...    channel=${MQ_CHANNEL}
    ...    username=${MQ_USERNAME}
    ...    password=${MQ_PASSWORD}
    Put MQ Message    alias=${alias}    queue=${queue}    message=${message}
    ${get_messages_list}    Get MQ Messages    alias=${alias}    queue=${queue}    convert=${False}
    ${message_amount}    Get Length    ${get_messages_list}
    Should Be Equal As Integers    ${message_amount}    1
    [Teardown]    Clear And Disconnect    queue=${queue}    alias=${alias}

Test Browse Multiple Messages
    [Tags]    browse    # Connect / Default alias / Put / Listen for / Put / Clear / Disconnect all
    VAR    ${queue}    MQLIBRARY_TEST
    ${message}    Get File    acceptance_tests/messages/example.json
    Connect MQ
    ...    queue_manager=${MQ_MANAGER}
    ...    hostname=${MQ_HOSTNAME}
    ...    port=${MQ_PORT}
    ...    channel=${MQ_CHANNEL}
    ...    username=${MQ_USERNAME}
    ...    password=${MQ_PASSWORD}
    Put MQ Message    queue=${queue}    message=${message}
    Put MQ Message    queue=${queue}    message=${message}
    ${get_messages_list}    Browse MQ Messages    queue=${queue}    max_messages=3    convert=${False}
    ${message_amount}    Get Length    ${get_messages_list}
    Should Be Equal As Integers    ${message_amount}    2
    ${get_messages_list}    Get MQ Messages    queue=${queue}    message_amount=2    timeout=2s    convert=${False}
    ${message_amount}    Get Length    ${get_messages_list}
    Should Be Equal As Integers    ${message_amount}    2
    [Teardown]    Clear And Disconnect    queue=${queue}

Test Clearing Queue
    [Tags]    clear
    VAR    ${queue}    MQLIBRARY_TEST
    ${message}    Get File    acceptance_tests/messages/example.json
    Connect MQ
    ...    queue_manager=${MQ_MANAGER}
    ...    hostname=${MQ_HOSTNAME}
    ...    port=${MQ_PORT}
    ...    channel=${MQ_CHANNEL}
    ...    username=${MQ_USERNAME}
    ...    password=${MQ_PASSWORD}
    Put MQ Message    queue=${queue}    message=${message}
    Clear MQ Queue    queue=${queue}
    Run Keyword And Expect Error    Expected 1 message(s), but received 0.   Get MQ Messages    queue=${queue}    convert=${False}
    [Teardown]    Clear And Disconnect    queue=${queue}


*** Keywords ***
Clear And Disconnect
    [Arguments]    ${queue}    ${alias}=${EMPTY}
    IF    $alias    Clear MQ Queue    alias=${alias}    queue=${queue}     ELSE    Clear MQ Queue    queue=${queue}     
    IF    $alias    Disconnect MQ    alias=${alias}    ELSE    Disconnect All MQ Connections