*** Settings ***
Documentation     End-to-End Integration Tests
...               Tests complete workflows from device registration to telemetry

Resource          ../../resources/common.robot
Resource          ../../resources/device_management.robot
Resource          ../../resources/automation_rules.robot

Suite Setup       Suite Setup For Integration Tests
Suite Teardown    Cleanup Test Environment    use_mqtt=${True}

Test Tags         integration    e2e


*** Keywords ***
Suite Setup For Integration Tests
    Initialize Test Environment    use_mqtt=${True}
    Authenticate As Admin


*** Test Cases ***
TC031: Complete Device Lifecycle
    [Documentation]    Test full device lifecycle from registration to deletion
    [Tags]    device    lifecycle    smoke

    ${device_id}    ${device_data}=    Register New Device    device_type=light

    Subscribe To Device Telemetry    ${device_id}
    ${telemetry}=    Publish Device Telemetry    ${device_id}    light

    ${message}=    Wait For Message    home/${device_id}/telemetry    timeout=10
    Verify Device Telemetry Message    ${message}    ${device_id}

    ${status}=    Get Device Status    ${device_id}
    Should Not Be Empty    ${status}

    Delete Device    ${device_id}

TC032: Device Command And Response Flow
    [Documentation]    Test sending command and receiving response
    [Tags]    device    command    positive

    # Register device
    ${device_id}    ${device_data}=    Register New Device    device_type=light

    # Subscribe to command and status topics
    Subscribe To Topic    home/${device_id}/command    qos=1
    Subscribe To Device Status    ${device_id}

    # Send command
    ${command}=    Create Dictionary    action=turn_on    brightness=80
    Send Device Command    ${device_id}    ${command}

    # Verify command received
    ${cmd_msg}=    Wait For Message    home/${device_id}/command    timeout=10
    ${received_cmd}=    Parse JSON String    ${cmd_msg}[payload]
    Should Be Equal    ${received_cmd}[action]    turn_on

    # Simulate device status update
    ${status_update}=    Create Dictionary    device_id=${device_id}    status=on    brightness=80
    ${json_status}=    Convert To JSON String    ${status_update}
    Publish Message    home/${device_id}/status    ${json_status}    qos=1

    # Verify status update
    ${status_msg}=    Wait For Message    home/${device_id}/status    timeout=10
    Should Contain    ${status_msg}[payload]    "status":"on"

TC033: Automation Rule End-to-End
    [Documentation]    Test complete automation rule workflow
    [Tags]    automation    e2e    positive

    # Register trigger and action devices
    ${trigger_device}    ${trigger_data}=    Register New Device    device_type=sensor
    ${action_device}    ${action_data}=    Register New Device    device_type=light

    # Create automation rule
    ${rule_id}    ${rule_data}=    Create Automation Rule    ${trigger_device}    ${action_device}

    # Subscribe to automation events
    ${events_topic}=    Subscribe To Automation Events

    # Trigger the rule by publishing sensor data
    ${telemetry}=    Trigger Automation Rule
    ...    ${trigger_device}
    ...    sensor
    ...    temperature
    ...    30

    # Wait for automation event
    ${event_msg}=    Wait For Message    ${events_topic}    timeout=10
    ${event_data}=    Verify Automation Event    ${event_msg}    ${rule_id}

    # Clean up
    Delete Automation Rule    ${rule_id}

TC034: Multi-Device Telemetry Collection
    [Documentation]    Test collecting telemetry from multiple devices
    [Tags]    telemetry    multiple-devices    performance

    # Register multiple devices
    ${device_count}=    Set Variable    5
    ${devices}=    Generate Multiple Devices    count=${device_count}

    @{device_ids}=    Create List

    FOR    ${device}    IN    @{devices}
        ${response}=    POST Request    /api/v1/devices    data=${device}    expected_status=201
        ${device_id}=    Extract Response Field    ${response}    device_id
        Append To List    ${device_ids}    ${device_id}
    END

    # Subscribe to all device telemetry with wildcard
    Subscribe To Topic    home/+/telemetry    qos=1

    # Publish telemetry from all devices
    FOR    ${device_id}    IN    @{device_ids}
        ${telemetry}=    Publish Device Telemetry    ${device_id}    light
        Sleep    100ms
    END

    # Verify all messages received
    Sleep    2s
    ${messages}=    Get All Messages    home/+/telemetry
    ${msg_count}=    Get Length    ${messages}
    Should Be True    ${msg_count} >= ${device_count}

TC035: Device Registration With Certificate Provisioning
    [Documentation]    Test device registration with certificate
    [Tags]    security    certificate    integration

    ${device_id}=    Set Variable    cert-device-001

    # Generate CSR (simplified for testing)
    ${csr_data}=    Set Variable    -----BEGIN CERTIFICATE REQUEST-----test-----END CERTIFICATE REQUEST-----

    # Provision certificate
    ${certificate}=    Provision Device With Certificate    ${device_id}    ${csr_data}

    Should Not Be Empty    ${certificate}

TC036: High-Volume Message Throughput
    [Documentation]    Test system performance with high message volume
    [Tags]    performance    stress    mqtt

    ${device_id}=    Set Variable    perf-test-device
    ${message_count}=    Set Variable    50

    # Subscribe to telemetry
    Subscribe To Topic    home/${device_id}/telemetry    qos=1
    Clear Message Queue    home/${device_id}/telemetry

    # Publish multiple messages rapidly
    FOR    ${i}    IN RANGE    ${message_count}
        ${telemetry}=    Create Dictionary
        ...    device_id=${device_id}
        ...    sequence=${i}
        ...    timestamp=${i}
        ${json_data}=    Convert To JSON String    ${telemetry}
        Publish Message    home/${device_id}/telemetry    ${json_data}    qos=1
    END

    # Wait and verify messages received
    Sleep    5s
    ${messages}=    Get All Messages    home/${device_id}/telemetry
    ${received_count}=    Get Length    ${messages}

    Should Be True    ${received_count} >= ${message_count} * 0.95
    Log    Received ${received_count}/${message_count} messages

TC037: API And MQTT Performance Verification
    [Documentation]    Verify overall system performance metrics
    [Tags]    performance    metrics

    # Perform multiple API operations
    FOR    ${i}    IN RANGE    10
        ${device_data}=    Generate Device Data
        POST Request    /api/v1/devices    data=${device_data}    expected_status=201
    END

    # Check API performance
    ${api_metrics}=    Get API Metrics
    Log    API Metrics: ${api_metrics}

    ${avg_time}=    Get From Dictionary    ${api_metrics}    avg_response_time_ms
    Should Be True    ${avg_time} < ${performance.max_response_time_ms}

    # Check MQTT metrics
    ${mqtt_metrics}=    Get MQTT Metrics
    Log    MQTT Metrics: ${mqtt_metrics}

TC038: Multiple Automation Rules Execution
    [Documentation]    Test multiple automation rules working together
    [Tags]    automation    multiple-rules

    # Create multiple trigger/action device pairs
    ${rule_count}=    Set Variable    3

    FOR    ${i}    IN RANGE    ${rule_count}
        ${trigger}    ${t_data}=    Register New Device    device_type=sensor
        ${action}    ${a_data}=    Register New Device    device_type=light
        ${rule_id}    ${rule}=    Create Automation Rule    ${trigger}    ${action}
        Log    Created rule ${rule_id}
    END

TC039: Device Status Monitoring Over Time
    [Documentation]    Monitor device status updates over time
    [Tags]    monitoring    telemetry

    ${device_id}    ${device_data}=    Register New Device    device_type=thermostat

    Subscribe To Device Telemetry    ${device_id}

    # Simulate periodic status updates
    FOR    ${i}    IN RANGE    5
        ${telemetry}=    Publish Device Telemetry    ${device_id}    thermostat
        ${message}=    Wait For Message    home/${device_id}/telemetry    timeout=5
        Verify Device Telemetry Message    ${message}    ${device_id}
        Sleep    1s
    END

TC040: System Health Check
    [Documentation]    Verify overall system health and connectivity
    [Tags]    health    smoke    monitoring

    # Verify API is responsive
    ${device_data}=    Generate Device Data
    ${response}=    POST Request    /api/v1/devices    data=${device_data}    expected_status=201

    # Verify MQTT connection is active
    Connection Should Be Active

    # Verify can publish and receive messages
    ${test_topic}=    Set Variable    home/healthcheck/test
    Subscribe To Topic    ${test_topic}    qos=1
    Sleep    100ms    # Allow subscription to be fully established
    Publish Message    ${test_topic}    {"health": "ok"}    qos=1
    ${message}=    Wait For Message    ${test_topic}    timeout=5

    Should Contain    ${message}[payload]    health

    # Verify performance is acceptable
    Verify Performance Metrics
