*** Settings ***
Documentation     Device management resource file with reusable keywords
Library           ../libraries/api/APILibrary.py
Library           ../libraries/mqtt/MQTTLibrary.py
Library           ../libraries/utils/TestDataFactory.py
Library           Collections


*** Keywords ***
Register New Device
    [Documentation]    Register a new device via API
    [Arguments]    ${device_type}=light    ${device_id}=${None}

    # Generate device data
    ${device_data}=    Generate Device Data
    ...    device_type=${device_type}
    ...    device_id=${device_id}

    # Register device via API
    ${response}=    POST Request
    ...    /api/v1/devices
    ...    data=${device_data}
    ...    expected_status=201

    Response Should Contain Field    ${response}    device_id

    ${registered_device_id}=    Extract Response Field    ${response}    device_id
    Log    Device registered: ${registered_device_id}

    RETURN    ${registered_device_id}    ${device_data}

Get Device Status
    [Documentation]    Get device status via API
    [Arguments]    ${device_id}

    ${response}=    GET Request
    ...    /api/v1/devices/${device_id}/status
    ...    expected_status=200

    Response Should Contain Field    ${response}    status

    ${status}=    Extract Response Field    ${response}    status
    Log    Device ${device_id} status: ${status}

    RETURN    ${status}

Update Device Configuration
    [Documentation]    Update device configuration via API
    [Arguments]    ${device_id}    ${config_data}

    ${response}=    PUT Request
    ...    /api/v1/devices/${device_id}
    ...    data=${config_data}
    ...    expected_status=200

    Response Should Contain Field    ${response}    updated
    Log    Device ${device_id} updated

    RETURN    ${response}

Delete Device
    [Documentation]    Delete device via API
    [Arguments]    ${device_id}

    ${response}=    DELETE Request
    ...    /api/v1/devices/${device_id}
    ...    expected_status=204

    Log    Device ${device_id} deleted

Publish Device Telemetry
    [Documentation]    Publish device telemetry via MQTT
    [Arguments]    ${device_id}    ${device_type}

    # Generate telemetry data
    ${telemetry}=    Generate Telemetry Data
    ...    device_type=${device_type}
    ...    device_id=${device_id}

    ${topic}=    Set Variable    home/${device_id}/telemetry
    ${payload}=    Convert To JSON String    ${telemetry}

    # Publish to MQTT
    Publish Message    ${topic}    ${payload}    qos=1

    Log    Published telemetry for device ${device_id}
    RETURN    ${telemetry}

Send Device Command
    [Documentation]    Send command to device via MQTT
    [Arguments]    ${device_id}    ${command}

    ${topic}=    Set Variable    home/${device_id}/command
    ${payload}=    Convert To JSON String    ${command}

    Publish Message    ${topic}    ${payload}    qos=1

    Log    Sent command to device ${device_id}: ${command}

Subscribe To Device Telemetry
    [Documentation]    Subscribe to device telemetry topic
    [Arguments]    ${device_id}

    ${topic}=    Set Variable    home/${device_id}/telemetry
    Subscribe To Topic    ${topic}    qos=1

    Log    Subscribed to telemetry for device ${device_id}
    RETURN    ${topic}

Subscribe To Device Status
    [Documentation]    Subscribe to device status topic
    [Arguments]    ${device_id}

    ${topic}=    Set Variable    home/${device_id}/status
    Subscribe To Topic    ${topic}    qos=1

    Log    Subscribed to status for device ${device_id}
    RETURN    ${topic}

Verify Device Telemetry Message
    [Documentation]    Verify received telemetry message format
    [Arguments]    ${message}    ${device_id}

    # Verify message structure
    Dictionary Should Contain Key    ${message}    payload
    Dictionary Should Contain Key    ${message}    topic

    # Parse and verify JSON payload
    ${payload}=    Get From Dictionary    ${message}    payload
    ${data}=    Parse JSON String    ${payload}

    # Verify required telemetry fields
    Dictionary Should Contain Key    ${data}    device_id
    Dictionary Should Contain Key    ${data}    timestamp

    # Verify device ID matches
    ${msg_device_id}=    Get From Dictionary    ${data}    device_id
    Should Be Equal    ${msg_device_id}    ${device_id}

    Log    Telemetry message verified for device ${device_id}
    RETURN    ${data}

Provision Device With Certificate
    [Documentation]    Provision device with certificate via API
    [Arguments]    ${device_id}    ${csr_data}

    ${response}=    POST Request
    ...    /api/v1/certificates/provision
    ...    data={"device_id": "${device_id}", "csr": "${csr_data}"}
    ...    expected_status=201

    Response Should Contain Field    ${response}    certificate

    ${certificate}=    Extract Response Field    ${response}    certificate
    Log    Certificate provisioned for device ${device_id}

    RETURN    ${certificate}
