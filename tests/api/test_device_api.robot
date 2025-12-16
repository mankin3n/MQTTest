*** Settings ***
Documentation     Device Management API Tests
...               Tests for CRUD operations on IoT devices

Resource          ../../resources/common.robot
Resource          ../../resources/device_management.robot

Suite Setup       Suite Setup For Device API Tests
Suite Teardown    Cleanup Test Environment    use_mqtt=${False}

Test Tags         api    smoke    regression


*** Variables ***
${DEVICE_ID}      test-device-001


*** Keywords ***
Suite Setup For Device API Tests
    Initialize Test Environment    use_mqtt=${False}
    Authenticate As Admin


*** Test Cases ***
TC001: Register New Light Device Successfully
    [Documentation]    Verify that a new light device can be registered
    [Tags]    device    light    positive

    Given device data is prepared
    ${device_data}=    Generate Device Data    device_type=light    device_id=${DEVICE_ID}

    When device is registered via API
    ${response}=    POST Request    /api/v1/devices    data=${device_data}    expected_status=201

    Then response should contain device details
    Response Should Contain Field    ${response}    device_id
    Response Field Should Equal    ${response}    device_id    ${DEVICE_ID}
    Response Should Contain Field    ${response}    type
    Response Field Should Equal    ${response}    type    light

TC002: Register New Thermostat Device Successfully
    [Documentation]    Verify that a thermostat device can be registered
    [Tags]    device    thermostat    positive

    ${device_id}=    ${device_data}=    Register New Device    device_type=thermostat

    Should Not Be Empty    ${device_id}
    Dictionary Should Contain Key    ${device_data}    type
    Should Be Equal    ${device_data}[type]    thermostat

TC003: Get Device Status Returns Correct Information
    [Documentation]    Verify device status retrieval
    [Tags]    device    status    positive

    # First register a device
    ${device_id}=    ${device_data}=    Register New Device    device_type=sensor

    # Get device status
    ${status}=    Get Device Status    ${device_id}

    Should Not Be Empty    ${status}

TC004: Update Device Configuration Successfully
    [Documentation]    Verify device configuration can be updated
    [Tags]    device    update    positive

    # Register device
    ${device_id}=    ${device_data}=    Register New Device

    # Update configuration
    ${config}=    Create Dictionary    name=Updated Device Name    enabled=${True}
    ${response}=    Update Device Configuration    ${device_id}    ${config}

    Response Should Contain Field    ${response}    updated

TC005: Delete Device Successfully
    [Documentation]    Verify device can be deleted
    [Tags]    device    delete    positive

    # Register device
    ${device_id}=    ${device_data}=    Register New Device

    # Delete device
    Delete Device    ${device_id}

TC006: Register Device Without Authentication Fails
    [Documentation]    Verify registration fails without auth token
    [Tags]    device    security    negative

    Clear Authorization Token

    ${device_data}=    Generate Device Data
    ${status}    ${response}=    Run Keyword And Ignore Error
    ...    POST Request    /api/v1/devices    data=${device_data}

    Should Be Equal    ${status}    FAIL
    Should Contain    ${response}    401

    # Restore auth for cleanup
    Authenticate As Admin

TC007: Get Non-Existent Device Returns 404
    [Documentation]    Verify getting non-existent device returns 404
    [Tags]    device    negative

    ${status}    ${response}=    Run Keyword And Ignore Error
    ...    GET Request    /api/v1/devices/non-existent-device    expected_status=200

    Should Be Equal    ${status}    FAIL
    Should Contain    ${response}    404

TC008: Register Device With Invalid Data Fails
    [Documentation]    Verify registration fails with invalid data
    [Tags]    device    validation    negative

    ${invalid_data}=    Create Dictionary    invalid_field=value
    ${status}    ${response}=    Run Keyword And Ignore Error
    ...    POST Request    /api/v1/devices    data=${invalid_data}

    Should Be Equal    ${status}    FAIL

TC009: Register Multiple Devices In Batch
    [Documentation]    Verify multiple devices can be registered
    [Tags]    device    batch    positive

    ${devices}=    Generate Multiple Devices    count=5

    FOR    ${device}    IN    @{devices}
        ${response}=    POST Request    /api/v1/devices    data=${device}    expected_status=201
        Response Should Contain Field    ${response}    device_id
    END

TC010: API Response Time Is Within SLA
    [Documentation]    Verify API response time is acceptable
    [Tags]    device    performance

    ${device_data}=    Generate Device Data

    ${response}=    POST Request    /api/v1/devices    data=${device_data}

    Response Time Should Be Less Than    ${response}    ${performance.max_response_time_ms}
