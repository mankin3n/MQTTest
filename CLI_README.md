# SmartHome IoT Test Framework - Enhanced CLI

A modern, user-friendly command-line interface for running Robot Framework tests with rich UI and interactive features.

## Features

### 🎨 Modern UI
- Beautiful terminal graphics with Rich library
- Interactive menus with questionary
- Progress bars and spinners for long operations
- Color-coded output for better readability
- Tree views for test structure
- Formatted tables for reports and status

### 🚀 Quick Start
- One-command test execution
- Interactive wizards for common tasks
- Automatic prerequisite checking
- Integrated report viewing

### 📊 Enhanced Reporting
- Browse recent test reports
- Open HTML reports directly from CLI
- Visual test result summaries
- Real-time progress tracking

## Installation

1. Install enhanced dependencies:
```bash
pip install -r requirements.txt
```

2. Make the CLI executable (Linux/Mac):
```bash
chmod +x cli_enhanced.py
```

## Usage

### Interactive Mode (Recommended)

Simply run the CLI without arguments to enter interactive mode:

```bash
python cli_enhanced.py
```

This will display a beautiful interactive menu with options:
- 🚀 Quick Start - Run smoke tests
- 🧪 Run Tests - Select test suite
- 🔧 Setup - Initialize environment
- 📊 View Reports - Recent test results
- 🐳 Services - Manage Docker containers
- 📋 List Tests - Browse available tests
- ℹ️ Info - Project information
- 🧹 Clean - Remove reports and cache

### Command Line Mode

You can also use specific commands directly:

#### Setup Environment
```bash
python cli_enhanced.py setup
python cli_enhanced.py setup --skip-deps  # Skip dependency installation
```

#### Run Tests
```bash
# Run smoke tests (default)
python cli_enhanced.py run

# Run specific suite
python cli_enhanced.py run --suite api
python cli_enhanced.py run --suite mqtt
python cli_enhanced.py run --suite security
python cli_enhanced.py run --suite integration
python cli_enhanced.py run --suite all

# With options
python cli_enhanced.py run --suite api --env ci --verbose
python cli_enhanced.py run --suite mqtt --parallel
python cli_enhanced.py run --suite security --dry-run
```

#### Manage Services
```bash
# Start Docker services
python cli_enhanced.py services

# Stop services
python cli_enhanced.py stop

# Check status
python cli_enhanced.py status
```

#### View Information
```bash
# Project information
python cli_enhanced.py info

# List all tests
python cli_enhanced.py tests

# View recent reports
python cli_enhanced.py reports
```

#### Cleanup
```bash
python cli_enhanced.py clean
```

## Features in Detail

### 🚀 Quick Start
Perfect for running a quick smoke test to verify everything works:
- Checks prerequisites automatically
- Runs smoke tests with sensible defaults
- Opens test report in browser
- Shows clear pass/fail results

### 🧪 Interactive Test Runner
Guide you through test execution with prompts:
1. Select test suite (api, mqtt, security, integration, smoke, all)
2. Choose environment (dev, ci)
3. Pick options (verbose, parallel, dry-run)
4. Watch progress with live updates
5. Automatically opens HTML report

### 🔧 Setup Wizard
Initialize your test environment step-by-step:
- Install Python dependencies
- Generate test certificates
- Create necessary directories
- Clear next-step instructions

### 📊 Report Viewer
Browse and open recent test reports:
- Lists last 10 test runs
- Shows suite name and timestamp
- One-click report opening
- Organized in a beautiful table

### 🐳 Service Management
Interactive Docker container management:
- Start services with one command
- Stop all services
- Restart services
- View current status
- See service URLs in a table

### 📋 Test Browser
Explore available tests in tree structure:
- Organized by test suite
- Shows test files and test cases
- Displays first 5 tests per file
- Easy-to-navigate hierarchy

### ℹ️ Project Info
View comprehensive project details:
- Project metadata
- Python version
- Test statistics
- Directory paths
- Available services

### 🧹 Cleanup
Remove generated files safely:
- Confirmation prompt
- Removes all test reports
- Cleans Python cache
- Shows progress for each step

## UI Elements

### Banner
Beautiful ASCII art banner displayed on startup

### Progress Indicators
- Spinners for indeterminate operations
- Progress bars for tracked operations
- Live status updates
- Color-coded completion states

### Tables
- Formatted tables for data display
- Multiple box styles (rounded, double, simple)
- Color-coded columns
- Automatic column width adjustment

### Panels
- Highlighted information boxes
- Command previews
- Result summaries
- Next-step guidance

### Tree Views
- Hierarchical test structure
- Expandable/collapsible nodes
- Icon-based visualization
- Color-coded items

## Tips

1. **First Time Setup**: Run `python cli_enhanced.py setup` before running tests

2. **Quick Testing**: Use interactive mode for the best experience - just run `python cli_enhanced.py`

3. **CI/CD Integration**: Use command-line mode in scripts:
   ```bash
   python cli_enhanced.py run --suite all --env ci
   ```

4. **Parallel Execution**: Speed up test runs with `--parallel` flag:
   ```bash
   python cli_enhanced.py run --suite integration --parallel
   ```

5. **Report Access**: After tests complete, the CLI automatically asks if you want to open the HTML report

6. **Docker Services**: Start services before running tests:
   ```bash
   python cli_enhanced.py services
   python cli_enhanced.py run --suite smoke
   ```

## Comparison with Original CLI

| Feature | Original CLI | Enhanced CLI |
|---------|-------------|--------------|
| UI Style | Basic colors | Rich terminal UI |
| Menus | None | Interactive menus |
| Progress | Text only | Progress bars & spinners |
| Tables | Simple | Rich formatted tables |
| Tree Views | No | Yes |
| Report Opening | Manual | One-click from CLI |
| Wizards | No | Yes (setup, test runner) |
| Service Management | Basic | Interactive menu |
| Prerequisites Check | Basic | Visual with status |

## Requirements

- Python 3.8+
- Rich >= 13.7.0
- Questionary >= 2.0.1
- Click >= 8.1.7
- All standard project dependencies

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Docker services won't start
Check Docker is running:
```bash
docker --version
docker compose version
```

### Tests fail immediately
Run setup first:
```bash
python cli_enhanced.py setup
```

### Reports not opening
Check your default browser settings or manually open:
```bash
open reports/<report_dir>/report.html  # Mac
xdg-open reports/<report_dir>/report.html  # Linux
```

## Screenshots

### Interactive Menu
```
╔═══════════════════════════════════════════════════════════════╗
║   ███████╗███╗   ███╗ █████╗ ██████╗ ████████╗██╗  ██╗      ║
║   SmartHome IoT Test Framework - Enhanced CLI                 ║
╚═══════════════════════════════════════════════════════════════╝

? What would you like to do?
  ❯ 🚀 Quick Start - Run smoke tests
    🧪 Run Tests - Select test suite
    🔧 Setup - Initialize environment
    📊 View Reports - Recent test results
    ...
```

### Test Execution
```
╔══════════════════════════════════════════╗
║  🚀 Quick Start - Running Smoke Tests    ║
╚══════════════════════════════════════════╝

✅ Certificates found
✅ Robot Framework installed
✅ Docker services running

⠋ Running smoke tests...  ━━━━━━━━━━━━━━━━━━  50%
```

### Test Results
```
╔═══════════════════════════════════════╗
║  ✅ All tests passed!                 ║
╚═══════════════════════════════════════╝

📊 Test Reports:
┌─────────┬───────────────────────────────────┐
│ 📄 Log  │ reports/smoke_20241218/log.html  │
│ 📊 Report│ reports/smoke_20241218/report.html│
│ 📋 Output│ reports/smoke_20241218/output.xml│
└─────────┴───────────────────────────────────┘

? Open HTML report in browser? (Y/n)
```