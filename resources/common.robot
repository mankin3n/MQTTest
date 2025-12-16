*** Settings ***
Documentation     Common keywords and setup/teardown procedures
Library           ../libraries/api/APILibrary.py
Library           ../libraries/mqtt/MQTTLibrary.py
Library           ../libraries/utils/TestDataFactory.py
Library           Collections
Library           String
Library           BuiltIn
Variables         ../config/environments/${ENV}.yaml


*** Variables ***
${ENV}            dev


*** Keywords ***
Initialize Test Environment
    [Documentation]    Initialize API and MQTT connections for tests
    [Arguments]    ${use_mqtt}=${True}

    Log    Initializing test environment: ${environment}

    # Initialize API client
    Initialize API Client
    ...    ${api.base_url}
    ...    timeout=${api.timeout}
    ...    retry_attempts=${api.retry_attempts}

    # Initialize MQTT client if needed
    IF    ${use_mqtt}
        Connect To MQTT Broker
        ...    ${mqtt.broker_host}
        ...    ${mqtt.broker_port}
        ...    ca_cert=${mqtt.ca_cert}
        ...    client_cert=${mqtt.client_cert}
        ...    client_key=${mqtt.client_key}
        ...    keepalive=${mqtt.keepalive}

        Connection Should Be Active
    END

Cleanup Test Environment
    [Documentation]    Clean up connections and resources
    [Arguments]    ${use_mqtt}=${True}

    Log    Cleaning up test environment

    IF    ${use_mqtt}
        Run Keyword And Ignore Error    Disconnect From MQTT Broker
    END

Authenticate As Admin
    [Documentation]    Generate and set admin JWT token
    ${token}=    Generate JWT Token
    ...    user_id=admin001
    ...    username=${auth.admin_username}
    ...    role=admin
    ...    secret_key=${auth.jwt_secret}
    ...    expiry_seconds=${auth.token_expiry}

    Set Authorization Token    ${token}
    Log    Authenticated as admin
    RETURN    ${token}

Authenticate As User
    [Documentation]    Generate and set regular user JWT token
    ${token}=    Generate JWT Token
    ...    user_id=user001
    ...    username=${auth.test_username}
    ...    role=user
    ...    secret_key=${auth.jwt_secret}
    ...    expiry_seconds=${auth.token_expiry}

    Set Authorization Token    ${token}
    Log    Authenticated as user
    RETURN    ${token}

Wait For MQTT Message With Retry
    [Documentation]    Wait for MQTT message with multiple retry attempts
    [Arguments]    ${topic}    ${timeout}=10    ${retries}=3

    FOR    ${i}    IN RANGE    ${retries}
        ${status}    ${message}=    Run Keyword And Ignore Error
        ...    Wait For Message    ${topic}    timeout=${timeout}    clear_queue=${False}

        IF    '${status}' == 'PASS'
            RETURN    ${message}
        END

        Log    Retry ${i+1}/${retries}: No message received on ${topic}
        Sleep    1s
    END

    Fail    No message received on topic ${topic} after ${retries} retries

Verify Performance Metrics
    [Documentation]    Verify API and MQTT performance metrics
    [Arguments]    ${max_response_time}=${performance.max_response_time_ms}

    ${api_metrics}=    Get API Metrics
    Log    API Metrics: ${api_metrics}

    ${avg_response_time}=    Get From Dictionary    ${api_metrics}    avg_response_time_ms
    Should Be True    ${avg_response_time} < ${max_response_time}
    ...    Average response time ${avg_response_time}ms exceeds max ${max_response_time}ms
