#!/usr/bin/env python3
"""
SmartHome IoT Test Framework CLI
Command-line interface for running Robot Framework tests with various options.
"""
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import click
from tabulate import tabulate
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init(autoreset=True)

# Project paths
PROJECT_ROOT = Path(__file__).parent
TESTS_DIR = PROJECT_ROOT / 'tests'
REPORTS_DIR = PROJECT_ROOT / 'reports'
CERTS_DIR = PROJECT_ROOT / 'certs'


def print_header(text):
    """Print styled header."""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}{text.center(60)}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")


def print_success(text):
    """Print success message."""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")


def print_error(text):
    """Print error message."""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")


def print_info(text):
    """Print info message."""
    print(f"{Fore.YELLOW}ℹ {text}{Style.RESET_ALL}")


def check_prerequisites():
    """Check if prerequisites are met."""
    issues = []

    # Check if certificates exist
    ca_cert = CERTS_DIR / 'ca' / 'ca.crt'
    if not ca_cert.exists():
        issues.append("Certificates not found. Run 'python cli.py setup' first.")

    # Check if Python dependencies are installed
    try:
        import robot
    except ImportError:
        issues.append("Robot Framework not installed. Run 'pip install -r requirements.txt'")

    return issues


@click.group()
def cli():
    """SmartHome IoT Test Framework CLI - Advanced Robot Framework test automation."""
    pass


@cli.command()
@click.option('--skip-deps', is_flag=True, help='Skip dependency installation')
def setup(skip_deps):
    """Set up the test environment (install deps, generate certs)."""
    print_header("Setting Up Test Environment")

    if not skip_deps:
        print_info("Installing Python dependencies...")
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                check=True,
                cwd=PROJECT_ROOT
            )
            print_success("Dependencies installed")
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to install dependencies: {e}")
            sys.exit(1)

    print_info("Generating certificates...")
    try:
        subprocess.run(
            [sys.executable, 'scripts/generate_certs.py'],
            check=True,
            cwd=PROJECT_ROOT
        )
        print_success("Certificates generated")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to generate certificates: {e}")
        sys.exit(1)

    print_info("Creating directories...")
    REPORTS_DIR.mkdir(exist_ok=True)
    (PROJECT_ROOT / 'logs').mkdir(exist_ok=True)
    print_success("Directories created")

    print_success("\nSetup completed successfully!")
    print_info("\nNext steps:")
    print("  1. Start services: docker-compose up -d")
    print("  2. Run tests: python cli.py run --suite smoke")


@cli.command()
@click.option('--suite', type=click.Choice(['all', 'smoke', 'api', 'mqtt', 'security', 'integration']),
              default='smoke', help='Test suite to run')
@click.option('--env', type=click.Choice(['dev', 'ci']), default='dev', help='Environment configuration')
@click.option('--parallel', is_flag=True, help='Run tests in parallel')
@click.option('--tags', multiple=True, help='Run tests with specific tags')
@click.option('--verbose', is_flag=True, help='Verbose output')
@click.option('--dry-run', is_flag=True, help='Show what would be run without executing')
def run(suite, env, parallel, tags, verbose, dry_run):
    """Run test suites."""
    print_header(f"Running {suite.upper()} Tests")

    # Check prerequisites
    issues = check_prerequisites()
    if issues:
        print_error("Prerequisites check failed:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)

    # Prepare test paths
    test_paths = []
    if suite == 'all':
        test_paths.append(str(TESTS_DIR))
    elif suite == 'smoke':
        test_paths.append(str(TESTS_DIR))
    else:
        test_paths.append(str(TESTS_DIR / suite))

    # Create timestamp for report directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_dir = REPORTS_DIR / f"{suite}_{timestamp}"
    report_dir.mkdir(parents=True, exist_ok=True)

    # Build robot command
    cmd = ['robot']

    # Output directory
    cmd.extend(['--outputdir', str(report_dir)])

    # Log level
    if verbose:
        cmd.extend(['--loglevel', 'DEBUG'])
    else:
        cmd.extend(['--loglevel', 'INFO'])

    # Environment variable
    cmd.extend(['--variable', f'ENV:{env}'])

    # Tags
    if suite == 'smoke':
        cmd.extend(['--include', 'smoke'])
    elif tags:
        for tag in tags:
            cmd.extend(['--include', tag])

    # Test name
    cmd.extend(['--name', f'{suite.title()} Tests'])

    # Timestamp in report
    cmd.extend(['--timestampoutputs'])

    # Add test paths
    cmd.extend(test_paths)

    # Print command
    print_info(f"Command: {' '.join(cmd)}")
    print_info(f"Reports will be saved to: {report_dir}")

    if dry_run:
        print_info("Dry run - not executing tests")
        return

    # Run tests
    try:
        if parallel:
            print_info("Running tests in parallel...")
            cmd[0] = 'pabot'
            cmd.insert(1, '--processes')
            cmd.insert(2, '4')

        result = subprocess.run(cmd, cwd=PROJECT_ROOT)

        if result.returncode == 0:
            print_success("\nAll tests passed!")
        else:
            print_error(f"\nTests failed with exit code: {result.returncode}")

        print_info(f"\nReports: {report_dir}")
        print_info(f"  - log.html")
        print_info(f"  - report.html")
        print_info(f"  - output.xml")

        sys.exit(result.returncode)

    except KeyboardInterrupt:
        print_error("\nTest execution interrupted")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nTest execution failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--env', type=click.Choice(['dev', 'ci']), default='dev')
def services(env):
    """Start Docker services (Mosquitto, Mock API)."""
    print_header("Starting Services")

    print_info("Starting Docker Compose services...")
    try:
        subprocess.run(
            ['docker-compose', 'up', '-d'],
            check=True,
            cwd=PROJECT_ROOT
        )
        print_success("Services started successfully")

        print_info("\nService URLs:")
        print(f"  - MQTT Broker: mqtts://localhost:8883")
        print(f"  - Mock API: http://localhost:8000")
        print(f"  - API Health: http://localhost:8000/health")

    except subprocess.CalledProcessError as e:
        print_error(f"Failed to start services: {e}")
        sys.exit(1)


@cli.command()
def stop():
    """Stop Docker services."""
    print_header("Stopping Services")

    print_info("Stopping Docker Compose services...")
    try:
        subprocess.run(
            ['docker-compose', 'down'],
            check=True,
            cwd=PROJECT_ROOT
        )
        print_success("Services stopped successfully")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to stop services: {e}")
        sys.exit(1)


@cli.command()
def status():
    """Show status of Docker services."""
    print_header("Service Status")

    try:
        result = subprocess.run(
            ['docker-compose', 'ps'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to get service status: {e}")
        sys.exit(1)


@cli.command()
def certs():
    """Manage certificates."""
    print_header("Certificate Management")

    ca_cert = CERTS_DIR / 'ca' / 'ca.crt'
    broker_cert = CERTS_DIR / 'broker' / 'broker.crt'
    client_cert = CERTS_DIR / 'clients' / 'test-client.crt'

    certs_info = [
        ['CA Certificate', ca_cert, ca_cert.exists()],
        ['Broker Certificate', broker_cert, broker_cert.exists()],
        ['Client Certificate', client_cert, client_cert.exists()],
    ]

    # Count device certificates
    device_certs = list((CERTS_DIR / 'devices').glob('*.crt')) if (CERTS_DIR / 'devices').exists() else []
    certs_info.append(['Device Certificates', CERTS_DIR / 'devices', f"{len(device_certs)} found"])

    table = []
    for name, path, status in certs_info:
        status_str = f"{Fore.GREEN}✓" if status in [True, *range(1, 100)] else f"{Fore.RED}✗"
        if isinstance(status, str):
            status_str = status
        table.append([name, str(path), status_str])

    print(tabulate(table, headers=['Certificate', 'Path', 'Status'], tablefmt='grid'))

    if not ca_cert.exists():
        print_info("\nTo generate certificates, run: python cli.py setup")


@cli.command()
@click.option('--suite', type=click.Choice(['all', 'api', 'mqtt', 'security', 'integration']))
def list_tests(suite):
    """List available tests."""
    print_header("Available Tests")

    if suite:
        test_dir = TESTS_DIR / suite if suite != 'all' else TESTS_DIR
    else:
        test_dir = TESTS_DIR

    robot_files = list(test_dir.glob('**/*.robot'))

    print(f"Found {len(robot_files)} test files:\n")

    for robot_file in sorted(robot_files):
        relative_path = robot_file.relative_to(PROJECT_ROOT)
        print(f"  {Fore.CYAN}{relative_path}{Style.RESET_ALL}")

        # Try to extract test case names
        try:
            with open(robot_file, 'r') as f:
                in_test_cases = False
                for line in f:
                    if line.strip().startswith('*** Test Cases ***'):
                        in_test_cases = True
                        continue
                    if in_test_cases:
                        if line.strip().startswith('***'):
                            break
                        if line.strip() and not line.strip().startswith('[') and not line.strip().startswith('#'):
                            if not line.startswith('    '):
                                print(f"    - {line.strip()}")
        except Exception:
            pass

        print()


@cli.command()
def clean():
    """Clean up reports and temporary files."""
    print_header("Cleaning Up")

    # Clean reports
    if REPORTS_DIR.exists():
        import shutil
        print_info(f"Removing reports directory: {REPORTS_DIR}")
        shutil.rmtree(REPORTS_DIR)
        REPORTS_DIR.mkdir()
        print_success("Reports cleaned")

    # Clean Python cache
    for pycache in PROJECT_ROOT.rglob('__pycache__'):
        print_info(f"Removing: {pycache}")
        import shutil
        shutil.rmtree(pycache)

    print_success("Cleanup completed")


@cli.command()
def info():
    """Show project information."""
    print_header("Project Information")

    info_data = [
        ['Project', 'SmartHome IoT Test Framework'],
        ['Framework', 'Robot Framework'],
        ['Python Version', f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"],
        ['Project Root', str(PROJECT_ROOT)],
        ['Tests Directory', str(TESTS_DIR)],
        ['Reports Directory', str(REPORTS_DIR)],
    ]

    print(tabulate(info_data, tablefmt='grid'))

    # Count test files
    test_files = list(TESTS_DIR.glob('**/*.robot'))
    print(f"\n{Fore.CYAN}Test Files:{Style.RESET_ALL} {len(test_files)}")

    # Check services
    print(f"\n{Fore.CYAN}Services:{Style.RESET_ALL}")
    print(f"  - MQTT Broker: mqtts://localhost:8883")
    print(f"  - Mock API: http://localhost:8000")


if __name__ == '__main__':
    cli()
