# Contributing Guide

Thank you for considering contributing to the SmartHome IoT Test Automation Framework!

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Git
- Basic knowledge of Robot Framework
- Understanding of MQTT and REST APIs

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/smarthome-iot-tests.git
   cd smarthome-iot-tests
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate certificates**
   ```bash
   python3 scripts/generate_certs.py
   ```

5. **Start services**
   ```bash
   docker-compose up -d
   ```

6. **Run tests to verify setup**
   ```bash
   python3 cli.py run --suite smoke
   ```

## Development Workflow

### Branch Naming Convention

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `test/description` - New tests
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

Example: `feature/add-camera-device-support`

### Commit Message Format

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `test`: Adding or updating tests
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

Example:
```
feat(mqtt): add support for MQTT v5 protocol

Implemented MQTT v5 protocol support in MQTTLibrary with
backward compatibility for v3.1.1

Closes #123
```

## Code Style

### Python Code

- Follow PEP 8 style guide
- Use Black formatter (line length: 120)
- Use meaningful variable names
- Add docstrings to all functions/classes

```python
def my_function(param1: str, param2: int) -> dict:
    """
    Brief description of function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Example:
        >>> my_function("test", 42)
        {'result': 'success'}
    """
    # Implementation
    pass
```

### Robot Framework Tests

- Use clear, descriptive test names
- Follow Given-When-Then structure
- Add meaningful tags
- Include documentation strings

```robot
*** Test Cases ***
TC001: Device Registration With Valid Data Succeeds
    [Documentation]    Verify that a device can be registered with valid data
    [Tags]    device    registration    positive    smoke

    Given admin user is authenticated
    And device data is prepared
    When device registration request is sent
    Then response status should be 201
    And device should be created in system
```

## Adding New Features

### 1. Adding a New Test Case

1. **Identify the test category** (API, MQTT, Security, Integration)

2. **Create the test case**
   ```robot
   *** Test Cases ***
   TC0XX: Your Test Case Name
       [Documentation]    What this test validates
       [Tags]    category    subcategory    priority

       # Test steps with Given-When-Then structure
       Given precondition
       When action is performed
       Then result should be verified
   ```

3. **Run the test**
   ```bash
   python3 cli.py run --tags your-tag
   ```

4. **Update test count** in README.md

### 2. Adding a New Custom Library

1. **Create library file**
   ```
   libraries/
   └── myfeature/
       ├── __init__.py
       └── MyFeatureLibrary.py
   ```

2. **Implement the library**
   ```python
   from robot.api import logger
   from robot.api.deco import keyword

   class MyFeatureLibrary:
       ROBOT_LIBRARY_SCOPE = 'GLOBAL'
       ROBOT_LIBRARY_VERSION = '1.0.0'

       @keyword("My Custom Keyword")
       def my_custom_keyword(self, param: str) -> str:
           """Keyword documentation."""
           logger.info(f"Processing: {param}")
           return result
   ```

3. **Add tests for the library**
   ```python
   # tests/unit/test_myfeature_library.py
   import pytest
   from libraries.myfeature.MyFeatureLibrary import MyFeatureLibrary

   def test_my_custom_keyword():
       lib = MyFeatureLibrary()
       result = lib.my_custom_keyword("test")
       assert result == expected_value
   ```

### 3. Adding a New Resource File

1. **Create resource file** in `resources/`
   ```robot
   *** Settings ***
   Documentation     Description of this resource file
   Library           ../libraries/myfeature/MyFeatureLibrary.py

   *** Keywords ***
   High Level Keyword
       [Documentation]    What this keyword does
       [Arguments]    ${param1}    ${param2}

       My Custom Keyword    ${param1}
       # More steps
   ```

2. **Use in tests**
   ```robot
   *** Settings ***
   Resource    ../../resources/myfeature.robot
   ```

## Testing Guidelines

### Test Categories

1. **Smoke Tests** (`smoke` tag)
   - Critical functionality
   - Fast execution (< 5 min total)
   - Run before every commit

2. **Regression Tests** (`regression` tag)
   - Comprehensive coverage
   - All features
   - Run before merge

3. **Integration Tests** (`integration` tag)
   - End-to-end scenarios
   - Multiple components
   - Real workflows

4. **Performance Tests** (`performance` tag)
   - Response time validation
   - Load testing
   - Throughput verification

### Test Design Principles

1. **Independence**: Tests should not depend on each other
2. **Repeatability**: Tests should produce same results every run
3. **Isolation**: Clean up resources after each test
4. **Clarity**: Test intent should be obvious from name
5. **Maintainability**: Use keywords for reusable logic

### Example: Good vs Bad Test Design

❌ **Bad**:
```robot
Test 1
    Register Device    device001
    # Device001 now exists

Test 2
    # Assumes device001 exists from Test 1
    Get Device    device001
```

✅ **Good**:
```robot
Test 1
    [Setup]    Initialize Test Environment
    ${device_id}=    Register Device    device001
    [Teardown]    Delete Device    ${device_id}

Test 2
    [Setup]    Initialize Test Environment
    ${device_id}=    Register Device    device001
    Get Device    ${device_id}
    [Teardown]    Delete Device    ${device_id}
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run tests locally**
   ```bash
   python3 cli.py run --suite smoke
   python3 cli.py run --suite all  # Full test suite
   ```

4. **Format code**
   ```bash
   black libraries/ config/
   flake8 libraries/ config/ --max-line-length=120
   ```

5. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/my-new-feature
   ```

7. **Create Pull Request**
   - Provide clear description
   - Reference related issues
   - Add screenshots if applicable

### PR Checklist

- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] Commits follow convention
- [ ] No merge conflicts
- [ ] Related issues referenced

## Code Review Process

### For Reviewers

- Check code quality and style
- Verify tests cover new functionality
- Ensure documentation is updated
- Test locally if possible
- Provide constructive feedback

### For Contributors

- Respond to feedback promptly
- Make requested changes
- Update PR description if scope changes
- Be open to suggestions

## Documentation

### When to Update Documentation

- Adding new features
- Changing CLI commands
- Modifying configuration
- Adding new dependencies
- Updating architecture

### Documentation Files

- `README.md` - Main documentation
- `ARCHITECTURE.md` - System design
- `CONTRIBUTING.md` - This file
- Docstrings - In-code documentation

## Testing Your Changes

### Local Testing

```bash
# Run affected test suite
python3 cli.py run --suite api

# Run with verbose output
python3 cli.py run --suite api --verbose

# Run specific tags
python3 cli.py run --tags positive

# Dry run to check syntax
python3 cli.py run --suite api --dry-run
```

### CI/CD Testing

- Push to your branch triggers CI
- All test suites run in parallel
- Check GitHub Actions for results

## Common Issues and Solutions

### Import Errors

```bash
# Ensure you're in the project root
cd /path/to/smarthome-iot-tests

# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Certificate Issues

```bash
# Regenerate certificates
python3 scripts/generate_certs.py

# Verify certificates
./scripts/cert_manager.sh list
```

### Service Connection Issues

```bash
# Restart services
docker-compose down
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs mosquitto
docker-compose logs mock-api
```

## Getting Help

- **Issues**: Create a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Email**: your.email@example.com

## Recognition

Contributors will be acknowledged in:
- README.md
- Release notes
- Project documentation

Thank you for contributing! 🎉
