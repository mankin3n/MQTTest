*** Settings ***
Documentation     MQTT Publish/Subscribe Tests
...               Tests for MQTT messaging with different QoS levels

Resource          ../../resources/common.robot
Resource          ../../resources/device_management.robot

Suite Setup       Suite Setup For MQTT Tests
Suite Teardown    Cleanup Test Environment    use_mqtt=${True}

Test Tags         mqtt    messaging    regression


*** Variables ***
${TEST_DEVICE_ID}     mqtt-test-device-001
${TEST_TOPIC}         home/${TEST_DEVICE_ID}/telemetry


*** Keywords ***
Suite Setup For MQTT Tests
    Initialize Test Environment    use_mqtt=${True}


*** Test Cases ***
TC011: Publish And Receive Message With QoS 0
    [Documentation]    Verify MQTT pub/sub works with QoS 0
    [Tags]    mqtt    qos0    positive

    Given MQTT topic is subscribed
    Subscribe To Topic    ${TEST_TOPIC}    qos=0
    Clear Message Queue    ${TEST_TOPIC}

    When message is published with QoS 0
    ${payload}=    Create Dictionary    device_id=${TEST_DEVICE_ID}    status=online
    ${json_payload}=    Convert To JSON String    ${payload}
    Publish Message    ${TEST_TOPIC}    ${json_payload}    qos=0

    Then message should be received
    ${message}=    Wait For Message    ${TEST_TOPIC}    timeout=5

    And message should contain correct data
    Dictionary Should Contain Key    ${message}    payload
    ${received_data}=    Parse JSON String    ${message}[payload]
    Should Be Equal    ${received_data}[device_id]    ${TEST_DEVICE_ID}

TC012: Publish And Receive Message With QoS 1
    [Documentation]    Verify MQTT pub/sub works with QoS 1
    [Tags]    mqtt    qos1    positive

    Subscribe To Topic    ${TEST_TOPIC}    qos=1
    Clear Message Queue    ${TEST_TOPIC}

    ${payload}=    Create Dictionary    device_id=${TEST_DEVICE_ID}    temperature=22.5
    ${json_payload}=    Convert To JSON String    ${payload}
    Publish Message    ${TEST_TOPIC}    ${json_payload}    qos=1

    ${message}=    Wait For Message    ${TEST_TOPIC}    timeout=5
    Should Be Equal As Integers    ${message}[qos]    1

TC013: Publish And Receive Message With QoS 2
    [Documentation]    Verify MQTT pub/sub works with QoS 2
    [Tags]    mqtt    qos2    positive

    Subscribe To Topic    ${TEST_TOPIC}    qos=2
    Clear Message Queue    ${TEST_TOPIC}

    ${payload}=    Create Dictionary    device_id=${TEST_DEVICE_ID}    humidity=65
    ${json_payload}=    Convert To JSON String    ${payload}
    Publish Message    ${TEST_TOPIC}    ${json_payload}    qos=2

    ${message}=    Wait For Message    ${TEST_TOPIC}    timeout=5
    Should Be Equal As Integers    ${message}[qos]    2

TC014: Subscribe To Wildcard Topic
    [Documentation]    Verify subscription to wildcard topics
    [Tags]    mqtt    wildcard    positive

    ${wildcard_topic}=    Set Variable    home/+/telemetry
    Subscribe To Topic    ${wildcard_topic}    qos=1
    Clear Message Queue    ${wildcard_topic}

    # Publish to specific device topic
    ${device_topic}=    Set Variable    home/device123/telemetry
    ${payload}=    Create Dictionary    device_id=device123    value=100
    ${json_payload}=    Convert To JSON String    ${payload}
    Publish Message    ${device_topic}    ${json_payload}    qos=1

    # Should receive on wildcard subscription
    ${message}=    Wait For Message    ${wildcard_topic}    timeout=5
    Should Contain    ${message}[topic]    device123

TC015: Publish Retained Message
    [Documentation]    Verify retained messages work correctly
    [Tags]    mqtt    retained    positive

    ${retained_topic}=    Set Variable    home/${TEST_DEVICE_ID}/status

    # Publish retained message
    ${payload}=    Create Dictionary    status=online    last_seen=2024-01-01T00:00:00Z
    ${json_payload}=    Convert To JSON String    ${payload}
    Publish Message    ${retained_topic}    ${json_payload}    qos=1    retain=${True}

    # Subscribe after publish (should receive retained message)
    Subscribe To Topic    ${retained_topic}    qos=1
    ${message}=    Wait For Message    ${retained_topic}    timeout=5

    Should Be True    ${message}[retained]

TC016: Publish Device Telemetry
    [Documentation]    Verify device telemetry publishing
    [Tags]    mqtt    telemetry    positive

    Subscribe To Device Telemetry    ${TEST_DEVICE_ID}
    Clear Message Queue    home/${TEST_DEVICE_ID}/telemetry

    ${telemetry}=    Publish Device Telemetry    ${TEST_DEVICE_ID}    light

    ${message}=    Wait For Message    home/${TEST_DEVICE_ID}/telemetry    timeout=5
    ${data}=    Verify Device Telemetry Message    ${message}    ${TEST_DEVICE_ID}

    Dictionary Should Contain Key    ${data}    timestamp
    Dictionary Should Contain Key    ${data}    device_id

TC017: Send Device Command Via MQTT
    [Documentation]    Verify device commands can be sent
    [Tags]    mqtt    command    positive

    ${command_topic}=    Set Variable    home/${TEST_DEVICE_ID}/command
    Subscribe To Topic    ${command_topic}    qos=1
    Clear Message Queue    ${command_topic}

    ${command}=    Create Dictionary    action=turn_on    brightness=75
    Send Device Command    ${TEST_DEVICE_ID}    ${command}

    ${message}=    Wait For Message    ${command_topic}    timeout=5
    ${received_cmd}=    Parse JSON String    ${message}[payload]
    Should Be Equal    ${received_cmd}[action]    turn_on

TC018: Multiple Subscriptions On Same Connection
    [Documentation]    Verify multiple topic subscriptions work
    [Tags]    mqtt    subscriptions    positive

    ${topic1}=    Set Variable    home/device1/telemetry
    ${topic2}=    Set Variable    home/device2/telemetry
    ${topic3}=    Set Variable    home/device3/status

    Subscribe To Topic    ${topic1}    qos=1
    Subscribe To Topic    ${topic2}    qos=1
    Subscribe To Topic    ${topic3}    qos=1

    # Publish to each topic
    Publish Message    ${topic1}    {"msg": "test1"}    qos=1
    Publish Message    ${topic2}    {"msg": "test2"}    qos=1
    Publish Message    ${topic3}    {"msg": "test3"}    qos=1

    # Verify all messages received
    ${msg1}=    Wait For Message    ${topic1}    timeout=5
    ${msg2}=    Wait For Message    ${topic2}    timeout=5
    ${msg3}=    Wait For Message    ${topic3}    timeout=5

    Should Contain    ${msg1}[payload]    test1
    Should Contain    ${msg2}[payload]    test2
    Should Contain    ${msg3}[payload]    test3

TC019: Unsubscribe From Topic
    [Documentation]    Verify unsubscribe functionality
    [Tags]    mqtt    unsubscribe    positive

    ${topic}=    Set Variable    home/test/unsubscribe
    Subscribe To Topic    ${topic}    qos=1
    Clear Message Queue    ${topic}

    # Verify subscription works
    Publish Message    ${topic}    {"test": "before"}    qos=1
    ${msg}=    Wait For Message    ${topic}    timeout=5
    Should Contain    ${msg}[payload]    before

    # Unsubscribe
    Unsubscribe From Topic    ${topic}

    # Publish again (should not receive)
    Publish Message    ${topic}    {"test": "after"}    qos=1
    Sleep    2s

    ${messages}=    Get All Messages    ${topic}
    Length Should Be    ${messages}    0

TC020: Verify MQTT Connection Metrics
    [Documentation]    Verify MQTT metrics are tracked
    [Tags]    mqtt    metrics    monitoring

    ${metrics}=    Get MQTT Metrics

    Dictionary Should Contain Key    ${metrics}    messages_published
    Dictionary Should Contain Key    ${metrics}    messages_received
    Dictionary Should Contain Key    ${metrics}    connection_time

    Should Be True    ${metrics}[messages_published] > 0
