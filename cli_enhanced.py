#!/usr/bin/env python3
"""
SmartHome IoT Test Framework CLI - Enhanced Edition
Modern command-line interface with rich UI and interactive features.
"""
import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
import click
import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.tree import Tree
from rich.syntax import Syntax
from rich import box
from rich.prompt import Confirm

# Initialize rich console
console = Console()

# Project paths
PROJECT_ROOT = Path(__file__).parent
TESTS_DIR = PROJECT_ROOT / 'tests'
REPORTS_DIR = PROJECT_ROOT / 'reports'
CERTS_DIR = PROJECT_ROOT / 'certs'


def create_banner():
    """Create an attractive CLI banner."""
    banner_text = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ███████╗███╗   ███╗ █████╗ ██████╗ ████████╗██╗  ██╗      ║
║   ██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝██║  ██║      ║
║   ███████╗██╔████╔██║███████║██████╔╝   ██║   ███████║      ║
║   ╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║   ██╔══██║      ║
║   ███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║   ██║  ██║      ║
║   ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝      ║
║                                                               ║
║              IoT Test Framework - Enhanced CLI                ║
║                  Robot Framework Automation                   ║
╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(banner_text, style="bold cyan")


def check_prerequisites():
    """Check if prerequisites are met with rich output."""
    issues = []

    with console.status("[bold green]Checking prerequisites...", spinner="dots"):
        time.sleep(0.5)

        # Check if certificates exist
        ca_cert = CERTS_DIR / 'ca' / 'ca.crt'
        if not ca_cert.exists():
            issues.append("❌ Certificates not found")
        else:
            console.print("✅ Certificates found", style="green")

        # Check if Python dependencies are installed
        try:
            import robot
            console.print("✅ Robot Framework installed", style="green")
        except ImportError:
            issues.append("❌ Robot Framework not installed")

        # Check if Docker services are running
        try:
            result = subprocess.run(
                ['docker', 'compose', 'ps', '-q'],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                console.print("✅ Docker services running", style="green")
            else:
                console.print("⚠️  Docker services not running", style="yellow")
        except:
            console.print("⚠️  Docker not available", style="yellow")

    return issues


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """SmartHome IoT Test Framework - Enhanced CLI with modern UI."""
    if ctx.invoked_subcommand is None:
        create_banner()
        show_main_menu()


def show_main_menu():
    """Display interactive main menu."""
    choices = [
        '🚀 Quick Start - Run smoke tests',
        '🧪 Run Tests - Select test suite',
        '🔧 Setup - Initialize environment',
        '📊 View Reports - Recent test results',
        '🐳 Services - Manage Docker containers',
        '📋 List Tests - Browse available tests',
        'ℹ️  Info - Project information',
        '🧹 Clean - Remove reports and cache',
        '❌ Exit'
    ]

    while True:
        console.print()
        action = questionary.select(
            "What would you like to do?",
            choices=choices,
            style=questionary.Style([
                ('qmark', 'fg:cyan bold'),
                ('question', 'bold'),
                ('answer', 'fg:green bold'),
                ('pointer', 'fg:cyan bold'),
                ('highlighted', 'fg:cyan bold'),
                ('selected', 'fg:green'),
            ])
        ).ask()

        if not action or 'Exit' in action:
            console.print("\n👋 Goodbye!", style="bold cyan")
            break

        console.print()

        if 'Quick Start' in action:
            run_quick_start()
        elif 'Run Tests' in action:
            interactive_run_tests()
        elif 'Setup' in action:
            setup_environment(skip_deps=False)
        elif 'View Reports' in action:
            view_reports()
        elif 'Services' in action:
            manage_services()
        elif 'List Tests' in action:
            list_all_tests()
        elif 'Info' in action:
            show_project_info()
        elif 'Clean' in action:
            clean_project()


def run_quick_start():
    """Quick start - run smoke tests."""
    console.print(Panel.fit(
        "🚀 Quick Start - Running Smoke Tests",
        style="bold green",
        box=box.DOUBLE
    ))

    # Check prerequisites
    issues = check_prerequisites()
    if issues:
        console.print("\n[bold red]⚠️  Prerequisites check failed:[/]")
        for issue in issues:
            console.print(f"  {issue}")

        if Confirm.ask("\nContinue anyway?", default=False):
            pass
        else:
            return

    # Run smoke tests
    run_tests_with_progress('smoke', 'dev', tags=['smoke'])


def interactive_run_tests():
    """Interactive test runner with questionary."""
    suite = questionary.select(
        "Select test suite:",
        choices=['smoke', 'api', 'mqtt', 'security', 'integration', 'all']
    ).ask()

    if not suite:
        return

    env = questionary.select(
        "Select environment:",
        choices=['dev', 'ci'],
        default='dev'
    ).ask()

    if not env:
        return

    options = questionary.checkbox(
        "Select options:",
        choices=[
            questionary.Choice('Verbose output', value='verbose'),
            questionary.Choice('Parallel execution', value='parallel'),
            questionary.Choice('Dry run', value='dry_run'),
        ]
    ).ask()

    if options is None:
        return

    run_tests_with_progress(
        suite,
        env,
        verbose='verbose' in options,
        parallel='parallel' in options,
        dry_run='dry_run' in options
    )


def run_tests_with_progress(suite, env, tags=None, verbose=False, parallel=False, dry_run=False):
    """Run tests with rich progress indicators."""
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
    cmd.extend(['--outputdir', str(report_dir)])
    cmd.extend(['--loglevel', 'DEBUG' if verbose else 'INFO'])
    cmd.extend(['--variable', f'ENV:{env}'])

    if suite == 'smoke' or tags:
        tag_list = tags or ['smoke']
        for tag in tag_list:
            cmd.extend(['--include', tag])

    cmd.extend(['--name', f'{suite.title()} Tests'])
    cmd.extend(['--timestampoutputs'])
    cmd.extend(test_paths)

    # Show command info
    console.print(Panel(
        f"[bold cyan]Command:[/] {' '.join(cmd)}\n"
        f"[bold cyan]Reports:[/] {report_dir}",
        title="Test Execution Info",
        border_style="cyan"
    ))

    if dry_run:
        console.print("\n[yellow]🔍 Dry run - not executing tests[/]")
        return

    # Run with progress
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Running {suite} tests...", total=None)

        try:
            if parallel:
                cmd[0] = 'pabot'
                cmd.insert(1, '--processes')
                cmd.insert(2, '4')

            result = subprocess.run(
                cmd,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True
            )

            progress.update(task, completed=100, description=f"[green]Tests completed")

            # Show results
            console.print()
            if result.returncode == 0:
                console.print(Panel(
                    "[bold green]✅ All tests passed![/]",
                    style="green",
                    box=box.DOUBLE
                ))
            else:
                console.print(Panel(
                    f"[bold red]❌ Tests failed with exit code: {result.returncode}[/]",
                    style="red",
                    box=box.DOUBLE
                ))

            # Show report files
            console.print("\n[bold cyan]📊 Test Reports:[/]")
            reports_table = Table(show_header=False, box=box.SIMPLE)
            reports_table.add_row("📄 Log", f"{report_dir}/log.html")
            reports_table.add_row("📊 Report", f"{report_dir}/report.html")
            reports_table.add_row("📋 Output", f"{report_dir}/output.xml")
            console.print(reports_table)

            # Ask to open report
            if Confirm.ask("\nOpen HTML report in browser?", default=True):
                import webbrowser
                webbrowser.open(f"file://{report_dir}/report.html")

        except KeyboardInterrupt:
            progress.update(task, description="[red]Test execution interrupted")
            console.print("\n[red]❌ Test execution interrupted[/]")
        except Exception as e:
            progress.update(task, description="[red]Test execution failed")
            console.print(f"\n[red]❌ Test execution failed: {e}[/]")


def setup_environment(skip_deps):
    """Set up the test environment with progress indicators."""
    console.print(Panel.fit(
        "🔧 Setting Up Test Environment",
        style="bold cyan",
        box=box.DOUBLE
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        if not skip_deps:
            task1 = progress.add_task("[cyan]Installing Python dependencies...", total=None)
            try:
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                    check=True,
                    cwd=PROJECT_ROOT,
                    capture_output=True
                )
                progress.update(task1, description="[green]✅ Dependencies installed", completed=100)
            except subprocess.CalledProcessError as e:
                progress.update(task1, description="[red]❌ Failed to install dependencies", completed=100)
                console.print(f"\n[red]Error: {e}[/]")
                return

        task2 = progress.add_task("[cyan]Generating certificates...", total=None)
        try:
            subprocess.run(
                [sys.executable, 'scripts/generate_certs.py'],
                check=True,
                cwd=PROJECT_ROOT,
                capture_output=True
            )
            progress.update(task2, description="[green]✅ Certificates generated", completed=100)
        except subprocess.CalledProcessError as e:
            progress.update(task2, description="[red]❌ Failed to generate certificates", completed=100)
            console.print(f"\n[red]Error: {e}[/]")
            return

        task3 = progress.add_task("[cyan]Creating directories...", total=None)
        REPORTS_DIR.mkdir(exist_ok=True)
        (PROJECT_ROOT / 'logs').mkdir(exist_ok=True)
        progress.update(task3, description="[green]✅ Directories created", completed=100)

    console.print("\n[bold green]✅ Setup completed successfully![/]")

    console.print(Panel(
        "[bold cyan]Next steps:[/]\n"
        "1. Start services: [green]python cli_enhanced.py[/] → Services\n"
        "2. Run tests: [green]python cli_enhanced.py[/] → Run Tests",
        title="What's Next?",
        border_style="cyan"
    ))


def manage_services():
    """Manage Docker services with interactive menu."""
    action = questionary.select(
        "Service management:",
        choices=[
            '▶️  Start services',
            '⏹️  Stop services',
            '🔄 Restart services',
            '📊 Show status',
            '◀️  Back'
        ]
    ).ask()

    if not action or 'Back' in action:
        return

    if 'Start' in action:
        start_services()
    elif 'Stop' in action:
        stop_services()
    elif 'Restart' in action:
        stop_services()
        time.sleep(1)
        start_services()
    elif 'status' in action:
        show_service_status()


def start_services():
    """Start Docker services."""
    with console.status("[bold green]Starting Docker services...", spinner="dots"):
        try:
            subprocess.run(
                ['docker', 'compose', 'up', '-d'],
                check=True,
                cwd=PROJECT_ROOT,
                capture_output=True
            )
            time.sleep(2)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ Failed to start services: {e}[/]")
            return

    console.print("[green]✅ Services started successfully[/]\n")

    # Show service URLs in a nice table
    table = Table(title="Service URLs", box=box.ROUNDED)
    table.add_column("Service", style="cyan", no_wrap=True)
    table.add_column("URL", style="green")
    table.add_row("MQTT Broker (TLS)", "mqtts://localhost:8883")
    table.add_row("MQTT Broker (WebSocket)", "ws://localhost:9001")
    table.add_row("Mock API", "http://localhost:8000")
    table.add_row("API Health Check", "http://localhost:8000/health")

    console.print(table)


def stop_services():
    """Stop Docker services."""
    with console.status("[bold yellow]Stopping Docker services...", spinner="dots"):
        try:
            subprocess.run(
                ['docker', 'compose', 'down'],
                check=True,
                cwd=PROJECT_ROOT,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ Failed to stop services: {e}[/]")
            return

    console.print("[green]✅ Services stopped successfully[/]")


def show_service_status():
    """Show status of Docker services."""
    try:
        result = subprocess.run(
            ['docker', 'compose', 'ps'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )

        console.print(Panel(
            result.stdout,
            title="Service Status",
            border_style="cyan",
            box=box.ROUNDED
        ))
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to get service status: {e}[/]")


def view_reports():
    """View recent test reports."""
    if not REPORTS_DIR.exists() or not any(REPORTS_DIR.iterdir()):
        console.print("[yellow]No test reports found. Run some tests first![/]")
        return

    # List all report directories
    report_dirs = sorted(
        [d for d in REPORTS_DIR.iterdir() if d.is_dir()],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )[:10]  # Show last 10

    table = Table(title="Recent Test Reports", box=box.ROUNDED)
    table.add_column("#", style="cyan", width=4)
    table.add_column("Suite", style="green")
    table.add_column("Timestamp", style="yellow")
    table.add_column("Report", style="blue")

    for idx, report_dir in enumerate(report_dirs, 1):
        suite_name = report_dir.name.rsplit('_', 2)[0]
        timestamp_str = report_dir.name.rsplit('_', 2)[1] + '_' + report_dir.name.rsplit('_', 2)[2]

        table.add_row(
            str(idx),
            suite_name,
            timestamp_str,
            str(report_dir / 'report.html')
        )

    console.print(table)

    if report_dirs and Confirm.ask("\nOpen most recent report?", default=True):
        import webbrowser
        webbrowser.open(f"file://{report_dirs[0]}/report.html")


def list_all_tests():
    """List all available tests in a tree structure."""
    tree = Tree("📁 [bold cyan]Test Suites[/]", guide_style="bright_blue")

    for test_dir in sorted(TESTS_DIR.iterdir()):
        if test_dir.is_dir() and not test_dir.name.startswith('__'):
            dir_branch = tree.add(f"📂 [green]{test_dir.name}[/]")

            robot_files = list(test_dir.glob('*.robot'))
            for robot_file in sorted(robot_files):
                file_branch = dir_branch.add(f"🤖 [cyan]{robot_file.name}[/]")

                # Try to extract test case names
                try:
                    with open(robot_file, 'r') as f:
                        in_test_cases = False
                        test_count = 0
                        for line in f:
                            if line.strip().startswith('*** Test Cases ***'):
                                in_test_cases = True
                                continue
                            if in_test_cases:
                                if line.strip().startswith('***'):
                                    break
                                if line.strip() and not line.strip().startswith('[') and not line.strip().startswith('#'):
                                    if not line.startswith('    '):
                                        test_count += 1
                                        if test_count <= 5:  # Show first 5 tests
                                            file_branch.add(f"✓ [dim]{line.strip()}[/]")

                        if test_count > 5:
                            file_branch.add(f"[dim]... and {test_count - 5} more tests[/]")
                except Exception:
                    pass

    console.print(tree)


def show_project_info():
    """Show project information in a nice panel."""
    # Count test files
    test_files = list(TESTS_DIR.glob('**/*.robot'))

    # Count test cases
    total_tests = 0
    for robot_file in test_files:
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
                                total_tests += 1
        except Exception:
            pass

    # Create info table
    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    table.add_column("Key", style="cyan bold")
    table.add_column("Value", style="green")

    table.add_row("📦 Project", "SmartHome IoT Test Framework")
    table.add_row("🤖 Framework", "Robot Framework")
    table.add_row("🐍 Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    table.add_row("📁 Project Root", str(PROJECT_ROOT))
    table.add_row("📋 Test Files", str(len(test_files)))
    table.add_row("✓ Test Cases", str(total_tests))
    table.add_row("📊 Reports Dir", str(REPORTS_DIR))

    console.print(Panel(
        table,
        title="[bold cyan]Project Information[/]",
        border_style="cyan",
        box=box.DOUBLE
    ))

    # Show services
    console.print()
    services_table = Table(title="Available Services", box=box.ROUNDED)
    services_table.add_column("Service", style="cyan")
    services_table.add_column("URL", style="green")
    services_table.add_row("MQTT Broker", "mqtts://localhost:8883")
    services_table.add_row("Mock API", "http://localhost:8000")
    console.print(services_table)


def clean_project():
    """Clean up reports and temporary files."""
    if not Confirm.ask("\n⚠️  This will remove all reports and cache. Continue?", default=False):
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Clean reports
        if REPORTS_DIR.exists():
            import shutil
            task1 = progress.add_task("[cyan]Removing reports...", total=None)
            shutil.rmtree(REPORTS_DIR)
            REPORTS_DIR.mkdir()
            progress.update(task1, description="[green]✅ Reports cleaned", completed=100)

        # Clean Python cache
        task2 = progress.add_task("[cyan]Removing Python cache...", total=None)
        cache_count = 0
        for pycache in PROJECT_ROOT.rglob('__pycache__'):
            import shutil
            shutil.rmtree(pycache)
            cache_count += 1
        progress.update(task2, description=f"[green]✅ Removed {cache_count} cache directories", completed=100)

    console.print("\n[green]✅ Cleanup completed successfully![/]")


# CLI Commands (for direct command-line usage)
@cli.command()
@click.option('--skip-deps', is_flag=True, help='Skip dependency installation')
def setup(skip_deps):
    """Set up the test environment."""
    create_banner()
    setup_environment(skip_deps)


@cli.command()
@click.option('--suite', type=click.Choice(['all', 'smoke', 'api', 'mqtt', 'security', 'integration']),
              default='smoke', help='Test suite to run')
@click.option('--env', type=click.Choice(['dev', 'ci']), default='dev', help='Environment')
@click.option('--parallel', is_flag=True, help='Run tests in parallel')
@click.option('--verbose', is_flag=True, help='Verbose output')
@click.option('--dry-run', is_flag=True, help='Dry run')
def run(suite, env, parallel, verbose, dry_run):
    """Run test suites."""
    create_banner()
    run_tests_with_progress(suite, env, verbose=verbose, parallel=parallel, dry_run=dry_run)


@cli.command()
def services():
    """Start Docker services."""
    create_banner()
    start_services()


@cli.command()
def stop():
    """Stop Docker services."""
    create_banner()
    stop_services()


@cli.command()
def status():
    """Show service status."""
    create_banner()
    show_service_status()


@cli.command()
def info():
    """Show project information."""
    create_banner()
    show_project_info()


@cli.command()
def clean():
    """Clean up reports and cache."""
    create_banner()
    clean_project()


@cli.command()
def reports():
    """View recent test reports."""
    create_banner()
    view_reports()


@cli.command()
def tests():
    """List available tests."""
    create_banner()
    list_all_tests()


if __name__ == '__main__':
    cli()
