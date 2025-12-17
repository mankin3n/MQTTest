*** Settings ***
Documentation     Example of an intentional test failure for demonstration
Library           Collections


*** Test Cases ***
Example: Intentional Failure - Testing Negative Scenario
    [Documentation]    This test intentionally fails to verify error handling
    [Tags]    example    negative    intentional-failure

    # This test is designed to fail to verify that our test framework
    # correctly identifies and reports failures

    ${expected_value}=    Set Variable    Success
    ${actual_value}=    Set Variable    Failure

    # This assertion will fail intentionally
    Should Be Equal    ${actual_value}    ${expected_value}
    ...    msg=This is an intentional failure for testing purposes


Example: Testing That Error Is Raised
    [Documentation]    Verify that an error is correctly raised and caught
    [Tags]    example    error-handling

    # Test that verifies error handling works correctly
    # This should PASS because we're expecting it to fail

    ${status}    ${error}=    Run Keyword And Ignore Error
    ...    Fail    This is an expected error for testing

    Should Be Equal    ${status}    FAIL
    Should Contain    ${error}    expected error


Example: Invalid Configuration Detection
    [Documentation]    Test that invalid configuration is properly detected
    [Tags]    example    validation    intentional-failure

    ${invalid_config}=    Create Dictionary    timeout=-1    retries=invalid

    # This would fail because negative timeout is invalid
    Should Be True    ${invalid_config}[timeout] > 0
    ...    msg=Timeout must be positive - this failure is intentional to test validation
