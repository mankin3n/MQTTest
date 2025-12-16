# Quick Start Guide

Get up and running with the SmartHome IoT Test Framework in 5 minutes.

## Prerequisites

- Python 3.11+
- Docker Desktop
- 5 GB free disk space

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone repository
git clone https://github.com/mankin3n/MQTTest.git
cd MQTTest

# Run automated setup
make setup

# Run tests
make smoke
```

### Option 2: Manual Setup

```bash
# Clone repository
git clone https://github.com/mankin3n/MQTTest.git
cd MQTTest

# Install dependencies
pip install -r requirements.txt

# Generate certificates
python3 scripts/generate_certs.py

# Start services
docker-compose up -d

# Run tests
python3 cli.py run --suite smoke
```

## First Test Run

After setup, run your first test:

```bash
# Run smoke tests (fastest)
python3 cli.py run --suite smoke

# Expected output:
# ============================================================
#                    Running SMOKE Tests
# ============================================================
# ✓ All tests passed!
# Reports: reports/smoke_20240101_120000/
```

## What's Running?

After `make services` or `docker-compose up -d`:

1. **MQTT Broker** (Mosquitto)
   - Port: 8883 (MQTT with TLS)
   - Port: 9001 (WebSockets)

2. **Mock API** (Flask)
   - Port: 8000 (HTTP)
   - Health: http://localhost:8000/health

## Running Different Test Suites

```bash
# API tests only
make api

# MQTT tests only
make mqtt

# Security tests
make security

# Integration tests
make integration

# All tests
make test
```

## Viewing Test Reports

After test execution:

```bash
# Reports are saved to reports/ directory
open reports/smoke_*/report.html  # macOS
xdg-open reports/smoke_*/report.html  # Linux
start reports/smoke_*/report.html  # Windows
```

## Common Commands

```bash
# Check service status
make status

# View service logs
docker-compose logs mosquitto
docker-compose logs mock-api

# Stop services
make stop

# Clean up reports
make clean

# List available tests
python3 cli.py list-tests
```

## Troubleshooting

### Services won't start

```bash
# Check Docker is running
docker ps

# Restart services
docker-compose down
docker-compose up -d
```

### Certificate errors

```bash
# Regenerate certificates
python3 scripts/generate_certs.py
```

### Tests fail to connect

```bash
# Wait for services to be ready
sleep 10

# Check service health
curl http://localhost:8000/health
```

## Next Steps

1. **Explore the tests**: Check `tests/` directory
2. **Read the docs**: See [README.md](README.md)
3. **Run in parallel**: `python3 cli.py run --suite all --parallel`
4. **Create custom tests**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## Getting Help

- Check [README.md](README.md) for detailed documentation
- See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Create an issue on GitHub

---

Happy Testing! 🚀
