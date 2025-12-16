"""
Custom Robot Framework library for REST API operations with retry logic and JWT authentication.
Supports device management, user authentication, and automation rules testing.
"""
import json
import time
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from robot.api import logger
from robot.api.deco import keyword


class APILibrary:
    """
    Robot Framework library for REST API testing with automatic retry and JWT support.

    Provides keywords for HTTP operations, authentication, and response validation.
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'

    def __init__(self):
        self.base_url: Optional[str] = None
        self.session: Optional[requests.Session] = None
        self.auth_token: Optional[str] = None
        self.last_response: Optional[requests.Response] = None
        self.metrics = {
            'requests_sent': 0,
            'requests_failed': 0,
            'total_response_time': 0,
            'last_request_time': None
        }

    def _create_session_with_retry(
        self,
        retry_attempts: int = 3,
        backoff_factor: float = 0.3,
        status_forcelist: tuple = (500, 502, 503, 504)
    ) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()

        retry_strategy = Retry(
            total=retry_attempts,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    @keyword("Initialize API Client")
    def initialize_api_client(
        self,
        base_url: str,
        timeout: int = 30,
        retry_attempts: int = 3,
        verify_ssl: bool = True
    ):
        """
        Initialize the API client with base URL and configuration.

        Args:
            base_url: Base URL of the API
            timeout: Default timeout for requests in seconds
            retry_attempts: Number of retry attempts for failed requests
            verify_ssl: Whether to verify SSL certificates

        Example:
            | Initialize API Client | http://localhost:8000 | timeout=30 |
        """
        self.base_url = base_url.rstrip('/')
        self.session = self._create_session_with_retry(retry_attempts=retry_attempts)
        self.session.verify = verify_ssl

        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'RobotFramework-APILibrary/1.0'
        })

        logger.info(f"API client initialized with base URL: {self.base_url}")

    @keyword("Set Authorization Token")
    def set_authorization_token(self, token: str):
        """
        Set JWT authorization token for API requests.

        Args:
            token: JWT token string

        Example:
            | Set Authorization Token | ${token} |
        """
        self.auth_token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
        logger.info("Authorization token set")

    @keyword("Clear Authorization Token")
    def clear_authorization_token(self):
        """
        Remove authorization token from session headers.

        Example:
            | Clear Authorization Token |
        """
        self.auth_token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
        logger.info("Authorization token cleared")

    @keyword("Generate JWT Token")
    def generate_jwt_token(
        self,
        user_id: str,
        username: str,
        role: str = "user",
        secret_key: str = "dev-secret-key",
        expiry_seconds: int = 3600
    ) -> str:
        """
        Generate a JWT token for testing.

        Args:
            user_id: User ID
            username: Username
            role: User role (admin, user, etc.)
            secret_key: Secret key for signing
            expiry_seconds: Token expiry time in seconds

        Returns:
            JWT token string

        Example:
            | ${token}= | Generate JWT Token | user123 | testuser | user |
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'exp': datetime.utcnow() + timedelta(seconds=int(expiry_seconds)),
            'iat': datetime.utcnow()
        }

        token = jwt.encode(payload, secret_key, algorithm='HS256')
        logger.info(f"Generated JWT token for user: {username} (role: {role})")

        return token

    @keyword("POST Request")
    def post_request(
        self,
        endpoint: str,
        data: Any = None,
        timeout: int = 30,
        expected_status: int = None
    ) -> Dict[str, Any]:
        """
        Send POST request to API endpoint.

        Args:
            endpoint: API endpoint path
            data: Request body (dict or JSON string)
            timeout: Request timeout in seconds
            expected_status: Expected HTTP status code (optional)

        Returns:
            Response data dictionary

        Example:
            | ${response}= | POST Request | /api/v1/devices |
            | ...  | {"name": "Light 1", "type": "light"} |
        """
        return self._send_request('POST', endpoint, data=data, timeout=timeout, expected_status=expected_status)

    @keyword("GET Request")
    def get_request(
        self,
        endpoint: str,
        params: Dict[str, Any] = None,
        timeout: int = 30,
        expected_status: int = None
    ) -> Dict[str, Any]:
        """
        Send GET request to API endpoint.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            timeout: Request timeout in seconds
            expected_status: Expected HTTP status code (optional)

        Returns:
            Response data dictionary

        Example:
            | ${response}= | GET Request | /api/v1/devices/device001 |
        """
        return self._send_request('GET', endpoint, params=params, timeout=timeout, expected_status=expected_status)

    @keyword("PUT Request")
    def put_request(
        self,
        endpoint: str,
        data: Any = None,
        timeout: int = 30,
        expected_status: int = None
    ) -> Dict[str, Any]:
        """
        Send PUT request to API endpoint.

        Args:
            endpoint: API endpoint path
            data: Request body (dict or JSON string)
            timeout: Request timeout in seconds
            expected_status: Expected HTTP status code (optional)

        Returns:
            Response data dictionary

        Example:
            | ${response}= | PUT Request | /api/v1/devices/device001 |
            | ...  | {"status": "active"} |
        """
        return self._send_request('PUT', endpoint, data=data, timeout=timeout, expected_status=expected_status)

    @keyword("DELETE Request")
    def delete_request(
        self,
        endpoint: str,
        timeout: int = 30,
        expected_status: int = None
    ) -> Dict[str, Any]:
        """
        Send DELETE request to API endpoint.

        Args:
            endpoint: API endpoint path
            timeout: Request timeout in seconds
            expected_status: Expected HTTP status code (optional)

        Returns:
            Response data dictionary

        Example:
            | ${response}= | DELETE Request | /api/v1/devices/device001 |
        """
        return self._send_request('DELETE', endpoint, timeout=timeout, expected_status=expected_status)

    @keyword("PATCH Request")
    def patch_request(
        self,
        endpoint: str,
        data: Any = None,
        timeout: int = 30,
        expected_status: int = None
    ) -> Dict[str, Any]:
        """
        Send PATCH request to API endpoint.

        Args:
            endpoint: API endpoint path
            data: Request body (dict or JSON string)
            timeout: Request timeout in seconds
            expected_status: Expected HTTP status code (optional)

        Returns:
            Response data dictionary

        Example:
            | ${response}= | PATCH Request | /api/v1/devices/device001 |
            | ...  | {"enabled": true} |
        """
        return self._send_request('PATCH', endpoint, data=data, timeout=timeout, expected_status=expected_status)

    def _send_request(
        self,
        method: str,
        endpoint: str,
        data: Any = None,
        params: Dict[str, Any] = None,
        timeout: int = 30,
        expected_status: int = None
    ) -> Dict[str, Any]:
        """Internal method to send HTTP requests."""
        if not self.session:
            raise RuntimeError("API client not initialized. Call 'Initialize API Client' first.")

        url = f"{self.base_url}{endpoint}"

        # Convert data to JSON if it's a dict
        json_data = None
        if data is not None:
            if isinstance(data, str):
                json_data = json.loads(data)
            else:
                json_data = data

        logger.info(f"Sending {method} request to: {url}")
        if json_data:
            logger.debug(f"Request body: {json.dumps(json_data, indent=2)}")
        if params:
            logger.debug(f"Query params: {params}")

        start_time = time.time()

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                timeout=timeout
            )

            elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
            self.last_response = response

            # Update metrics
            self.metrics['requests_sent'] += 1
            self.metrics['total_response_time'] += elapsed_time
            self.metrics['last_request_time'] = datetime.now().isoformat()

            logger.info(
                f"Response: {response.status_code} ({elapsed_time:.0f}ms)"
            )

            # Check expected status if provided
            if expected_status is not None and response.status_code != expected_status:
                self.metrics['requests_failed'] += 1
                raise AssertionError(
                    f"Expected status {expected_status}, got {response.status_code}. "
                    f"Response: {response.text}"
                )

            # Parse response
            try:
                response_data = response.json() if response.text else {}
            except json.JSONDecodeError:
                response_data = {'text': response.text}

            logger.debug(f"Response body: {json.dumps(response_data, indent=2)}")

            return {
                'status_code': response.status_code,
                'data': response_data,
                'headers': dict(response.headers),
                'response_time_ms': elapsed_time
            }

        except requests.exceptions.RequestException as e:
            self.metrics['requests_failed'] += 1
            logger.error(f"Request failed: {str(e)}")
            raise

    @keyword("Response Status Should Be")
    def response_status_should_be(self, expected_status: int):
        """
        Verify that the last response status code matches expected value.

        Args:
            expected_status: Expected HTTP status code

        Example:
            | Response Status Should Be | 200 |
        """
        if not self.last_response:
            raise RuntimeError("No response available. Send a request first.")

        actual_status = self.last_response.status_code
        if actual_status != int(expected_status):
            raise AssertionError(
                f"Expected status {expected_status}, got {actual_status}. "
                f"Response: {self.last_response.text}"
            )

        logger.info(f"Status code verified: {actual_status}")

    @keyword("Response Should Contain Field")
    def response_should_contain_field(self, response: Dict[str, Any], field_path: str):
        """
        Verify that response contains a specific field.

        Args:
            response: Response dictionary from request keyword
            field_path: Dot-notation path to field (e.g., "data.device.id")

        Example:
            | Response Should Contain Field | ${response} | data.device_id |
        """
        data = response.get('data', {})
        fields = field_path.split('.')
        value = data

        for field in fields:
            if isinstance(value, dict) and field in value:
                value = value[field]
            else:
                raise AssertionError(f"Field '{field_path}' not found in response")

        logger.info(f"Field '{field_path}' found in response: {value}")

    @keyword("Response Field Should Equal")
    def response_field_should_equal(
        self,
        response: Dict[str, Any],
        field_path: str,
        expected_value: Any
    ):
        """
        Verify that a response field equals expected value.

        Args:
            response: Response dictionary from request keyword
            field_path: Dot-notation path to field
            expected_value: Expected field value

        Example:
            | Response Field Should Equal | ${response} | data.status | active |
        """
        data = response.get('data', {})
        fields = field_path.split('.')
        value = data

        for field in fields:
            if isinstance(value, dict) and field in value:
                value = value[field]
            else:
                raise AssertionError(f"Field '{field_path}' not found in response")

        if str(value) != str(expected_value):
            raise AssertionError(
                f"Field '{field_path}' mismatch.\nExpected: {expected_value}\nActual: {value}"
            )

        logger.info(f"Field '{field_path}' verified: {value}")

    @keyword("Response Time Should Be Less Than")
    def response_time_should_be_less_than(self, response: Dict[str, Any], max_time_ms: int):
        """
        Verify that response time is less than maximum allowed time.

        Args:
            response: Response dictionary from request keyword
            max_time_ms: Maximum allowed response time in milliseconds

        Example:
            | Response Time Should Be Less Than | ${response} | 2000 |
        """
        actual_time = response.get('response_time_ms', 0)

        if actual_time > int(max_time_ms):
            raise AssertionError(
                f"Response time {actual_time}ms exceeds maximum {max_time_ms}ms"
            )

        logger.info(f"Response time verified: {actual_time}ms < {max_time_ms}ms")

    @keyword("Get API Metrics")
    def get_api_metrics(self) -> Dict[str, Any]:
        """
        Get API request metrics.

        Returns:
            Dictionary containing metrics

        Example:
            | ${metrics}= | Get API Metrics |
            | Log | Total requests: ${metrics['requests_sent']} |
        """
        avg_response_time = 0
        if self.metrics['requests_sent'] > 0:
            avg_response_time = self.metrics['total_response_time'] / self.metrics['requests_sent']

        metrics_copy = self.metrics.copy()
        metrics_copy['avg_response_time_ms'] = avg_response_time

        logger.info(f"API Metrics: {metrics_copy}")
        return metrics_copy

    @keyword("Extract Response Field")
    def extract_response_field(self, response: Dict[str, Any], field_path: str) -> Any:
        """
        Extract a field value from response data.

        Args:
            response: Response dictionary from request keyword
            field_path: Dot-notation path to field

        Returns:
            Field value

        Example:
            | ${device_id}= | Extract Response Field | ${response} | data.device_id |
        """
        data = response.get('data', {})
        fields = field_path.split('.')
        value = data

        for field in fields:
            if isinstance(value, dict) and field in value:
                value = value[field]
            else:
                raise KeyError(f"Field '{field_path}' not found in response")

        logger.info(f"Extracted field '{field_path}': {value}")
        return value
