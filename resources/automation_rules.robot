*** Settings ***
Documentation     Automation rules resource file
Library           ../libraries/api/APILibrary.py
Library           ../libraries/mqtt/MQTTLibrary.py
Library           ../libraries/utils/TestDataFactory.py
Library           Collections


*** Keywords ***
Create Automation Rule
    [Documentation]    Create a new automation rule
    [Arguments]    ${trigger_device_id}    ${action_device_id}

    # Generate rule data
    ${rule_data}=    Generate Automation Rule
    ...    trigger_device_id=${trigger_device_id}
    ...    action_device_id=${action_device_id}

    # Create rule via API
    ${response}=    POST Request
    ...    /api/v1/automation-rules
    ...    data=${rule_data}
    ...    expected_status=201

    Response Should Contain Field    ${response}    rule_id

    ${rule_id}=    Extract Response Field    ${response}    rule_id
    Log    Automation rule created: ${rule_id}

    RETURN    ${rule_id}    ${rule_data}

Get Automation Rule
    [Documentation]    Get automation rule details
    [Arguments]    ${rule_id}

    ${response}=    GET Request
    ...    /api/v1/automation-rules/${rule_id}
    ...    expected_status=200

    Response Should Contain Field    ${response}    rule_id

    RETURN    ${response}

Update Automation Rule
    [Documentation]    Update automation rule
    [Arguments]    ${rule_id}    ${rule_data}

    ${response}=    PUT Request
    ...    /api/v1/automation-rules/${rule_id}
    ...    data=${rule_data}
    ...    expected_status=200

    Log    Automation rule ${rule_id} updated

    RETURN    ${response}

Delete Automation Rule
    [Documentation]    Delete automation rule
    [Arguments]    ${rule_id}

    ${response}=    DELETE Request
    ...    /api/v1/automation-rules/${rule_id}
    ...    expected_status=204

    Log    Automation rule ${rule_id} deleted

Enable Automation Rule
    [Documentation]    Enable an automation rule
    [Arguments]    ${rule_id}

    ${response}=    PATCH Request
    ...    /api/v1/automation-rules/${rule_id}
    ...    data={"enabled": true}
    ...    expected_status=200

    Log    Automation rule ${rule_id} enabled

    RETURN    ${response}

Disable Automation Rule
    [Documentation]    Disable an automation rule
    [Arguments]    ${rule_id}

    ${response}=    PATCH Request
    ...    /api/v1/automation-rules/${rule_id}
    ...    data={"enabled": false}
    ...    expected_status=200

    Log    Automation rule ${rule_id} disabled

    RETURN    ${response}

Subscribe To Automation Events
    [Documentation]    Subscribe to automation events topic

    ${topic}=    Set Variable    home/events/automation
    Subscribe To Topic    ${topic}    qos=1

    Log    Subscribed to automation events
    RETURN    ${topic}

Verify Automation Event
    [Documentation]    Verify automation event message
    [Arguments]    ${message}    ${rule_id}

    # Verify message structure
    Dictionary Should Contain Key    ${message}    payload

    # Parse and verify JSON payload
    ${payload}=    Get From Dictionary    ${message}    payload
    ${data}=    Parse JSON String    ${payload}

    # Verify event fields
    Dictionary Should Contain Key    ${data}    rule_id
    Dictionary Should Contain Key    ${data}    timestamp
    Dictionary Should Contain Key    ${data}    trigger_device_id

    # Verify rule ID matches
    ${msg_rule_id}=    Get From Dictionary    ${data}    rule_id
    Should Be Equal    ${msg_rule_id}    ${rule_id}

    Log    Automation event verified for rule ${rule_id}
    RETURN    ${data}

Trigger Automation Rule
    [Documentation]    Simulate triggering an automation rule by publishing telemetry
    [Arguments]    ${trigger_device_id}    ${device_type}    ${condition_field}    ${condition_value}

    # Generate telemetry data that meets the condition
    ${telemetry}=    Generate Telemetry Data
    ...    device_type=${device_type}
    ...    device_id=${trigger_device_id}

    # Override condition field with trigger value
    Set To Dictionary    ${telemetry}    ${condition_field}    ${condition_value}

    # Publish telemetry
    ${topic}=    Set Variable    home/${trigger_device_id}/telemetry
    ${payload}=    Convert To JSON String    ${telemetry}

    Publish Message    ${topic}    ${payload}    qos=1

    Log    Triggered automation rule with ${condition_field}=${condition_value}
    RETURN    ${telemetry}
