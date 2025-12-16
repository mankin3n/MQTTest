# Architecture Documentation

## System Overview

The SmartHome IoT Test Automation Framework is designed to test IoT platforms with MQTT messaging and REST APIs, using certificate-based security.

## Components

### 1. Test Framework Layer

```
┌─────────────────────────────────────────────────────┐
│            Robot Framework Test Layer               │
│  ┌────────────┬────────────┬──────────────────────┐ │
│  │ API Tests  │ MQTT Tests │ Integration Tests    │ │
│  └────────────┴────────────┴──────────────────────┘ │
└─────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│          Resource Files (Keywords)                   │
│  ┌────────────┬──────────────┬──────────────────┐  │
│  │  Common    │  Device Mgmt │ Automation Rules │  │
│  └────────────┴──────────────┴──────────────────┘  │
└─────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│           Custom Python Libraries                    │
│  ┌────────────┬──────────────┬──────────────────┐  │
│  │ API Library│ MQTT Library │ Test Data Factory │  │
│  └────────────┴──────────────┴──────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 2. Infrastructure Layer

```
┌──────────────────┐      ┌──────────────────┐
│   MQTT Broker    │      │   Mock REST API  │
│  (Mosquitto)     │      │     (Flask)      │
│                  │      │                  │
│  Port: 8883 TLS  │      │  Port: 8000 HTTP │
│  Port: 9001 WSS  │      │                  │
└──────────────────┘      └──────────────────┘
         │                         │
         └─────────┬───────────────┘
                   │
         ┌─────────▼──────────┐
         │  Docker Network    │
         │  smarthome-network │
         └────────────────────┘
```

### 3. Certificate Infrastructure

```
┌─────────────────────────────────────────┐
│        Certificate Authority (CA)       │
│              Root CA                    │
│          (Self-signed)                  │
└────────────┬────────────────────────────┘
             │
    ┌────────┼────────┬─────────────┐
    │        │        │             │
    ▼        ▼        ▼             ▼
┌────────┐ ┌───────┐ ┌──────┐  ┌─────────┐
│ Broker │ │Device │ │Device│  │ Client  │
│  Cert  │ │ Cert1 │ │ Cert2│  │  Cert   │
└────────┘ └───────┘ └──────┘  └─────────┘
```

## Data Flow

### Device Registration Flow

```
1. Test Suite
      │
      ├─ Generate JWT Token (Admin)
      │
      ├─ Generate Device Data
      │
      └─ POST /api/v1/devices
            │
            └─ Mock API Server
                  │
                  └─ Store in memory
                        │
                        └─ Return 201 Created
```

### MQTT Telemetry Flow

```
1. Device/Test Client
      │
      ├─ Connect with mTLS
      │    │
      │    └─ Present client certificate
      │          │
      │          └─ Mosquitto validates cert
      │
      ├─ Subscribe to topics
      │
      └─ Publish telemetry
            │
            └─ Mosquitto routes message
                  │
                  └─ Deliver to subscribers
                        │
                        └─ Test validates message
```

### Certificate Provisioning Flow

```
1. Generate CSR (Certificate Signing Request)
      │
2. POST /api/v1/certificates/provision
      │
3. CA signs CSR
      │
4. Return signed certificate
      │
5. Device uses cert for MQTT connection
```

## Security Architecture

### Authentication Layers

1. **API Authentication**
   - JWT tokens with role-based access (admin/user)
   - Token expiry validation
   - Secret key signing (HS256)

2. **MQTT Authentication**
   - Client certificates (mTLS)
   - CA certificate validation
   - TLS 1.2+ required

### Authorization

```
Admin Role:
  ✓ Create devices
  ✓ Delete devices
  ✓ Provision certificates
  ✓ Manage automation rules

User Role:
  ✓ View devices
  ✓ Update own devices
  ✗ Delete devices
  ✗ Provision certificates
```

## Test Execution Flow

### Local Execution

```
1. CLI Command: python3 cli.py run --suite smoke
      │
2. Check prerequisites
      │
3. Build Robot command
      │
4. Execute tests
      │
      ├─ Initialize connections (API + MQTT)
      │
      ├─ Run test cases
      │    │
      │    ├─ Setup: Authenticate, subscribe to topics
      │    │
      │    ├─ Execute: API calls, MQTT pub/sub
      │    │
      │    └─ Teardown: Disconnect, cleanup
      │
5. Generate reports
      │
6. Return exit code
```

### CI/CD Execution

```
1. GitHub Actions Trigger
      │
2. Setup Python environment
      │
3. Generate certificates
      │
4. Start Docker services
      │
5. Parallel test execution
      │
      ├─ API Tests
      ├─ MQTT Tests
      ├─ Security Tests
      └─ Integration Tests
      │
6. Merge results
      │
7. Publish reports
      │
8. Upload artifacts
```

## Message Flow Patterns

### Request-Response Pattern

```
Test Client                    MQTT Broker                    Device
    │                              │                            │
    ├─ Publish command ───────────>│                            │
    │   home/device001/command     │                            │
    │                              ├─ Forward ──────────────────>│
    │                              │                            │
    │                              │<─ Publish status ──────────┤
    │                              │   home/device001/status    │
    │<─ Receive status ────────────┤                            │
```

### Automation Rule Pattern

```
Sensor                  MQTT Broker              Rule Engine         Actuator
  │                         │                         │                 │
  ├─ Publish telemetry ────>│                         │                 │
  │   (temp > 25°C)         ├─ Forward ───────────────>│                 │
  │                         │                         ├─ Evaluate rule  │
  │                         │                         │                 │
  │                         │                         ├─ Trigger action │
  │                         │<─ Publish command ──────┤                 │
  │                         ├─ Forward ───────────────────────────────>│
```

## Scalability Considerations

### Parallel Test Execution

- Tests run independently
- Shared MQTT broker handles concurrent connections
- Each test uses unique device IDs to avoid conflicts
- Pabot enables parallel Robot Framework execution

### Performance Testing

```
┌─────────────────────────────────────┐
│  Test Runner (Pabot)                │
│                                     │
│  ┌──────┐ ┌──────┐ ┌──────┐       │
│  │ P1   │ │ P2   │ │ P3   │       │
│  │50msg │ │50msg │ │50msg │       │
│  └──┬───┘ └──┬───┘ └──┬───┘       │
└─────┼────────┼────────┼────────────┘
      │        │        │
      ▼        ▼        ▼
┌─────────────────────────────────────┐
│    MQTT Broker                      │
│    Handles 150 concurrent messages  │
└─────────────────────────────────────┘
```

## Configuration Management

### Environment-Specific Settings

```
config/
├── environments/
    ├── dev.yaml      # Local development
    │   ├── localhost endpoints
    │   ├── Relaxed timeouts
    │   └── Debug logging
    │
    └── ci.yaml       # CI/CD pipeline
        ├── Docker service names
        ├── Stricter timeouts
        └── INFO logging
```

### Dynamic Configuration Loading

```python
ENV = os.getenv('TEST_ENV', 'dev')
config = Config(environment=ENV)

# Access nested values
broker_host = config.get('mqtt.broker_host')
api_url = config.get('api.base_url')
```

## Error Handling

### Retry Logic

```
API Request
    │
    ├─ Attempt 1 ──> Fail (503)
    │
    ├─ Backoff 0.3s
    │
    ├─ Attempt 2 ──> Fail (503)
    │
    ├─ Backoff 0.6s
    │
    └─ Attempt 3 ──> Success (200)
```

### MQTT Reconnection

```
Connection Lost
    │
    ├─ Automatic reconnect (paho-mqtt)
    │
    ├─ Resubscribe to topics
    │
    └─ Resume message handling
```

## Monitoring and Metrics

### Tracked Metrics

1. **API Metrics**
   - Requests sent
   - Requests failed
   - Average response time
   - Total response time

2. **MQTT Metrics**
   - Messages published
   - Messages received
   - Connection time
   - Last message timestamp

3. **Performance Metrics**
   - Max response time threshold
   - Max MQTT latency threshold
   - Message delivery rate

## Extension Points

### Adding New Test Libraries

```python
# libraries/custom/MyLibrary.py
from robot.api.deco import keyword

class MyLibrary:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    @keyword("My Custom Keyword")
    def my_keyword(self, arg):
        # Implementation
        pass
```

### Adding New Resource Files

```robot
*** Settings ***
Library    ../libraries/custom/MyLibrary.py

*** Keywords ***
High Level Keyword
    [Arguments]    ${param}
    My Custom Keyword    ${param}
```

## Technology Stack

- **Test Framework**: Robot Framework 7.0
- **MQTT Client**: Paho MQTT 2.1.0
- **HTTP Client**: Requests 2.31.0
- **Certificate Management**: cryptography 42.0.0
- **Mock API**: Flask 3.0.0
- **MQTT Broker**: Eclipse Mosquitto 2.0
- **CI/CD**: GitHub Actions
- **Containerization**: Docker & Docker Compose
