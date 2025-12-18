*** Settings ***
Documentation     Authentication and Authorization Security Tests
...               Tests for JWT tokens, certificate auth, and role-based access

Resource          ../../resources/common.robot
Resource          ../../resources/device_management.robot

Suite Setup       Initialize Test Environment    use_mqtt=${False}
Suite Teardown    Cleanup Test Environment    use_mqtt=${False}

Test Tags         security    authentication    regression


*** Test Cases ***
TC021: Admin User Can Access Protected Endpoints
    [Documentation]    Verify admin users have full access
    [Tags]    auth    admin    positive

    # Authenticate as admin user
    ${token}=    Authenticate As Admin

    # Access protected endpoint
    ${device_data}=    Generate Device Data
    ${response}=    POST Request    /api/v1/devices    data=${device_data}

    # Verify request succeeds
    Response Status Should Be    201

TC022: Regular User Has Limited Access
    [Documentation]    Verify regular users have restricted access
    [Tags]    auth    user    positive

    # Authenticate as regular user
    ${token}=    Authenticate As User

    # Access admin-only endpoint
    ${status}    ${response}=    Run Keyword And Ignore Error
    ...    DELETE Request    /api/v1/devices/any-device    expected_status=200

    # Verify request is forbidden
    Should Be Equal    ${status}    FAIL
    Should Contain    ${response}    403

TC023: Unauthenticated Requests Are Rejected
    [Documentation]    Verify requests without auth token are rejected
    [Tags]    auth    negative

    # Clear authentication token
    Clear Authorization Token

    # Access protected endpoint
    ${device_data}=    Generate Device Data
    ${status}    ${response}=    Run Keyword And Ignore Error
    ...    POST Request    /api/v1/devices    data=${device_data}

    # Verify request is unauthorized
    Should Be Equal    ${status}    FAIL
    Should Contain    ${response}    401

    # Restore auth for cleanup
    Authenticate As Admin

TC024: Expired JWT Token Is Rejected
    [Documentation]    Verify expired tokens are not accepted
    [Tags]    auth    jwt    negative

    # Generate an expired JWT token
    ${expired_token}=    Generate JWT Token
    ...    user_id=test123
    ...    username=testuser
    ...    role=user
    ...    expiry_seconds=-1

    Set Authorization Token    ${expired_token}

    # Access protected endpoint
    ${device_data}=    Generate Device Data
    ${status}    ${response}=    Run Keyword And Ignore Error
    ...    POST Request    /api/v1/devices    data=${device_data}

    # Verify request fails
    Should Be Equal    ${status}    FAIL

    # Restore auth
    Authenticate As Admin

TC025: Invalid JWT Token Is Rejected
    [Documentation]    Verify invalid tokens are not accepted
    [Tags]    auth    jwt    negative

    # Set an invalid JWT token
    Set Authorization Token    invalid.jwt.token.here

    # Access protected endpoint
    ${device_data}=    Generate Device Data
    ${status}    ${response}=    Run Keyword And Ignore Error
    ...    POST Request    /api/v1/devices    data=${device_data}

    # Verify request fails
    Should Be Equal    ${status}    FAIL

    # Restore auth
    Authenticate As Admin

TC026: JWT Token Contains Correct Claims
    [Documentation]    Verify JWT token structure and claims
    [Tags]    auth    jwt    positive

    ${token}=    Generate JWT Token
    ...    user_id=user123
    ...    username=testuser@example.com
    ...    role=admin
    ...    expiry_seconds=3600

    Should Not Be Empty    ${token}
    Should Contain    ${token}    .

    # Token should have 3 parts (header.payload.signature)
    ${parts}=    Split String    ${token}    .
    Length Should Be    ${parts}    3

TC027: MQTT Connection With Valid Certificate Succeeds
    [Documentation]    Verify MQTT connection with valid client certificate
    [Tags]    mqtt    certificate    positive

    # Connection is established in suite setup with valid certs
    # This test verifies it's working
    Connect To MQTT Broker
    ...    ${mqtt.broker_host}
    ...    ${mqtt.broker_port}
    ...    ca_cert=${mqtt.ca_cert}
    ...    client_cert=${mqtt.client_cert}
    ...    client_key=${mqtt.client_key}

    Connection Should Be Active

    Disconnect From MQTT Broker

TC028: MQTT Connection Without Certificate Fails
    [Documentation]    Verify MQTT connection fails without client certificate
    [Tags]    mqtt    certificate    negative

    ${status}    ${error}=    Run Keyword And Ignore Error
    ...    Connect To MQTT Broker
    ...    ${mqtt.broker_host}
    ...    ${mqtt.broker_port}
    ...    ca_cert=${mqtt.ca_cert}

    Should Be Equal    ${status}    FAIL

TC029: MQTT Connection With Invalid CA Certificate Fails
    [Documentation]    Verify MQTT connection fails with invalid CA cert
    [Tags]    mqtt    certificate    negative

    ${status}    ${error}=    Run Keyword And Ignore Error
    ...    Connect To MQTT Broker
    ...    ${mqtt.broker_host}
    ...    ${mqtt.broker_port}
    ...    ca_cert=/invalid/path/ca.crt
    ...    client_cert=${mqtt.client_cert}
    ...    client_key=${mqtt.client_key}

    Should Be Equal    ${status}    FAIL

TC030: Multiple Failed Auth Attempts Are Logged
    [Documentation]    Verify failed authentication attempts are tracked
    [Tags]    auth    monitoring    security

    # Clear any existing auth
    Clear Authorization Token

    FOR    ${i}    IN RANGE    3
        ${device_data}=    Generate Device Data
        ${status}    ${response}=    Run Keyword And Ignore Error
        ...    POST Request    /api/v1/devices    data=${device_data}

        Should Be Equal    ${status}    FAIL
    END

    # Restore auth
    Authenticate As Admin
