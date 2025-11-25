#!/usr/bin/env python3
"""
Admin Panel Finder Pro - Enhanced Edition
Developed by PUJO
Enhanced with advanced features
"""

import argparse
import requests
import concurrent.futures
import random
import json
import csv
import os
import time
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.live import Live
from rich.layout import Layout

console = Console()

BANNER = """
[cyan]
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    █████╗ ██████╗ ███╗   ███╗██╗███╗   ██╗    ██████╗ █████╗ ║
║   ██╔══██╗██╔══██╗████╗ ████║██║████╗  ██║    ██╔══██╗██╔══██╗║
║   ███████║██║  ██║██╔████╔██║██║██╔██╗ ██║    ██████╔╝███████║║
║   ██╔══██║██║  ██║██║╚██╔╝██║██║██║╚██╗██║    ██╔═══╝ ██╔══██║║
║   ██║  ██║██████╔╝██║ ╚═╝ ██║██║██║ ╚████║    ██║     ██║  ██║║
║   ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝    ╚═╝     ╚═╝  ╚═╝║
║                                                              ║
║            ADMIN PANEL FINDER PRO - ENHANCED                 ║
║                  Developed by PUJO                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
[/cyan]
"""

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
]

# Enhanced wordlist with common admin paths
DEFAULT_WORDLIST = [
    "admin", "administrator", "admin.php", "admin.html", "login", "login.php",
    "admin-login", "wp-admin", "wp-login.php", "administrator/", "admin1",
    "admin2", "admin/login.php", "admin/admin.php", "admin_area", "admin_login",
    "panel", "cpanel", "control", "controlpanel", "adminpanel", "adm",
    "admin/controlpanel.php", "admin/cp.php", "moderator", "webadmin",
    "adminarea", "bb-admin", "admin/admin-login.php", "admin-login.php",
    "admin/account.php", "admin/index.php", "admin/login.html", "admin/admin.html",
    "admin/account.html", "admin/home.php", "admin_area/admin.php", "admin_area/login.php",
    "admin_area/index.php", "bb-admin/index.php", "bb-admin/login.php", "admin/controlpanel.html",
    "admin/", "admin/admin-login.html", "admin-login.html", "admin/cp.html",
    "cp.php", "cp.html", "administrator/index.html", "administrator/login.html",
    "administrator/account.html", "administrator.html", "login.html", "modelsearch/login.html",
    "moderator.html", "moderator/login.html", "moderator/admin.html", "account.html",
    "controlpanel.html", "admincontrol.html", "admin_login.html", "panel-administracion/login.html",
    "dashboard", "admin/dashboard", "admin/settings", "admin/config", "backend",
    "cms", "manager", "management", "secure", "auth", "authentication"
]

class ScanStats:
    """Track scanning statistics in real-time"""
    def __init__(self):
        self.total = 0
        self.scanned = 0
        self.found = 0
        self.status_codes = defaultdict(int)
        self.start_time = time.time()
        self.errors = 0
        
    def get_elapsed(self):
        return time.time() - self.start_time
    
    def get_rate(self):
        elapsed = self.get_elapsed()
        return self.scanned / elapsed if elapsed > 0 else 0
    
    def get_eta(self):
        rate = self.get_rate()
        remaining = self.total - self.scanned
        return remaining / rate if rate > 0 else 0

def print_banner():
    """Display enhanced banner"""
    console.print(BANNER)
    console.print(Panel(
        "[yellow]Enhanced Features:[/yellow]\n"
        "✓ Smart response detection\n"
        "✓ Real-time statistics\n"
        "✓ Advanced filtering\n"
        "✓ Auto-retry on failures\n"
        "✓ Detailed HTML analysis\n"
        "✓ Export in multiple formats\n"
        "✓ Rate limiting & stealth mode",
        title="[green]New Features[/green]",
        border_style="cyan",
        box=box.ROUNDED
    ))

def get_user_input():
    """Enhanced user input with validation and defaults"""
    console.print("\n[cyan]🎯 Configuration Setup:[/cyan]")
    
    target = console.input("[yellow]🔗 Target URL: [/yellow]").strip()
    if not target:
        console.print("[red]❌ Target URL required![/red]")
        return None
    
    if not target.startswith(('http://', 'https://')):
        target = "https://" + target
        console.print(f"[yellow]⚠️  Added https:// → {target}[/yellow]")
    
    # Ask if user wants to use default wordlist or custom
    use_default = console.input("[yellow]📁 Use built-in wordlist? [cyan](y/n, default: y)[/cyan]: [/yellow]").strip().lower()
    
    if use_default in ['n', 'no']:
        wordlist_file = console.input("[yellow]📁 Enter wordlist path: [/yellow]").strip()
        if not wordlist_file:
            wordlist_file = "admin_wordlist.txt"
    else:
        wordlist_file = None  # Use default
    
    output_file = console.input("[yellow]💾 Output filename [cyan](Enter to skip)[/cyan]: [/yellow]").strip()
    
    output_format = "txt"
    if output_file:
        format_choice = console.input("[yellow]📄 Format [cyan](txt/json/csv/html, default: txt)[/cyan]: [/yellow]").strip().lower()
        if format_choice in ["txt", "json", "csv", "html"]:
            output_format = format_choice
    
    threads_input = console.input("[yellow]⚡ Threads [cyan](default: 20, max: 100)[/cyan]: [/yellow]").strip()
    try:
        threads = min(int(threads_input) if threads_input else 20, 100)
    except ValueError:
        threads = 20
    
    timeout_input = console.input("[yellow]⏱️  Timeout [cyan](default: 10)[/cyan]: [/yellow]").strip()
    try:
        timeout = int(timeout_input) if timeout_input else 10
    except ValueError:
        timeout = 10
    
    proxy = console.input("[yellow]🔌 Proxy [cyan](Enter to skip)[/cyan]: [/yellow]").strip()
    
    # Advanced options
    console.print("\n[cyan]⚙️  Advanced Options:[/cyan]")
    stealth = console.input("[yellow]🥷 Enable stealth mode? [cyan](y/n, default: n)[/cyan]: [/yellow]").strip().lower() in ['y', 'yes']
    
    follow_redirects = console.input("[yellow]🔄 Follow redirects? [cyan](y/n, default: n)[/cyan]: [/yellow]").strip().lower() in ['y', 'yes']
    
    return {
        'target': target,
        'wordlist': wordlist_file,
        'output': output_file if output_file else None,
        'format': output_format,
        'threads': threads,
        'timeout': timeout,
        'proxy': proxy if proxy else None,
        'stealth': stealth,
        'follow_redirects': follow_redirects
    }

def load_wordlist(wordlist_file=None):
    """Load wordlist from file or use default"""
    if wordlist_file is None:
        console.print(f"[green]✓ Using built-in wordlist ({len(DEFAULT_WORDLIST)} paths)[/green]")
        return DEFAULT_WORDLIST
    
    if not os.path.exists(wordlist_file):
        console.print(f"[red]❌ Wordlist not found: {wordlist_file}[/red]")
        console.print(f"[yellow]⚠️  Falling back to built-in wordlist[/yellow]")
        return DEFAULT_WORDLIST
    
    try:
        with open(wordlist_file, "r", encoding='utf-8', errors='ignore') as f:
            wordlist = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        console.print(f"[green]✓ Loaded {len(wordlist)} paths from {wordlist_file}[/green]")
        return wordlist
    except Exception as e:
        console.print(f"[red]❌ Error loading wordlist: {str(e)}[/red]")
        console.print(f"[yellow]⚠️  Falling back to built-in wordlist[/yellow]")
        return DEFAULT_WORDLIST

def analyze_response(response):
    """Enhanced response analysis"""
    indicators = {
        'is_admin': False,
        'confidence': 0,
        'indicators': []
    }
    
    # Check for common admin indicators in content
    admin_keywords = [
        'admin', 'login', 'password', 'username', 'dashboard',
        'control panel', 'administrator', 'authentication',
        'sign in', 'log in', 'backend', 'cms', 'management'
    ]
    
    content_lower = response.text.lower()
    title_match = re.search(r'<title>(.*?)</title>', content_lower)
    
    if title_match:
        title = title_match.group(1)
        indicators['title'] = title
        for keyword in admin_keywords:
            if keyword in title:
                indicators['confidence'] += 15
                indicators['indicators'].append(f"Title contains '{keyword}'")
    
    # Check for login forms
    if '<form' in content_lower and ('password' in content_lower or 'login' in content_lower):
        indicators['confidence'] += 25
        indicators['indicators'].append("Login form detected")
        indicators['is_admin'] = True
    
    # Check for admin-related input fields
    if re.search(r'type=["\']password["\']', content_lower):
        indicators['confidence'] += 20
        indicators['indicators'].append("Password field found")
    
    # Check body content for keywords
    keyword_count = sum(1 for keyword in admin_keywords if keyword in content_lower)
    if keyword_count >= 3:
        indicators['confidence'] += keyword_count * 5
        indicators['indicators'].append(f"{keyword_count} admin keywords found")
    
    indicators['is_admin'] = indicators['confidence'] >= 30
    
    return indicators

def check_url(base_url, path, timeout, proxy, stealth, follow_redirects, stats, progress=None, task=None):
    """Enhanced URL checking with retry logic and analysis"""
    url = urljoin(base_url, path)
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1"
    }
    
    if stealth:
        time.sleep(random.uniform(0.1, 0.5))  # Random delay for stealth
    
    max_retries = 2
    for attempt in range(max_retries):
        try:
            resp = requests.get(
                url,
                headers=headers,
                timeout=timeout,
                proxies=proxy,
                allow_redirects=follow_redirects,
                verify=False
            )
            
            stats.scanned += 1
            stats.status_codes[resp.status_code] += 1
            
            if progress and task:
                progress.update(task, advance=1)
            
            result = {
                'url': url,
                'status': resp.status_code,
                'size': len(resp.content),
                'server': resp.headers.get('Server', 'Unknown'),
                'content_type': resp.headers.get('Content-Type', 'Unknown'),
                'redirect': resp.headers.get('Location', None) if resp.is_redirect else None,
                'response_time': resp.elapsed.total_seconds()
            }
            
            # Analyze response content for admin indicators
            if resp.status_code == 200:
                analysis = analyze_response(resp)
                result['analysis'] = analysis
            
            return result
        
        except requests.RequestException as e:
            stats.errors += 1
            if attempt == max_retries - 1:
                stats.scanned += 1
                if progress and task:
                    progress.update(task, advance=1)
                return {
                    'url': url,
                    'status': 'ERROR',
                    'size': 0,
                    'server': 'Unknown',
                    'error': str(e)
                }
            time.sleep(1)  # Wait before retry

def scan_admin_panels(base_url, wordlist, threads, timeout, proxy, stealth, follow_redirects):
    """Enhanced scanning with real-time statistics"""
    results = []
    stats = ScanStats()
    stats.total = len(wordlist)
    
    console.print(f"\n[cyan]🎯 Target: {base_url}[/cyan]")
    console.print(f"[blue]📊 Total paths: {stats.total} | Threads: {threads} | Timeout: {timeout}s[/blue]")
    if stealth:
        console.print("[yellow]🥷 Stealth mode: ACTIVE[/yellow]")
    console.print()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("•"),
        TextColumn("{task.fields[found]}"),
        TextColumn("•"),
        TextColumn("{task.fields[rate]}"),
        console=console,
        transient=False,
    ) as progress:
        
        task = progress.add_task(
            "Scanning",
            total=stats.total,
            found="[green]Found: 0[/green]",
            rate="[cyan]0 req/s[/cyan]"
        )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_url = {
                executor.submit(
                    check_url, base_url, path, timeout, proxy,
                    stealth, follow_redirects, stats, progress, task
                ): path
                for path in wordlist
            }
            
            for future in concurrent.futures.as_completed(future_to_url):
                result = future.result()
                
                # Filter interesting results
                if result['status'] in [200, 301, 302, 401, 403, 307, 308]:
                    stats.found += 1
                    
                    # Additional filtering for 200 responses
                    if result['status'] == 200:
                        if 'analysis' in result and result['analysis']['is_admin']:
                            confidence = result['analysis']['confidence']
                            console.print(
                                f"[green]🎯 HIGH CONFIDENCE ({confidence}%): {result['url']}[/green] "
                                f"[yellow](Status: {result['status']})[/yellow]"
                            )
                            result['priority'] = 'high'
                            results.append(result)
                        elif result['size'] > 500:  # Minimum size filter
                            console.print(
                                f"[cyan]📍 FOUND: {result['url']}[/cyan] "
                                f"[yellow](Status: {result['status']})[/yellow]"
                            )
                            result['priority'] = 'medium'
                            results.append(result)
                    else:
                        status_color = get_status_color(result['status'])
                        console.print(
                            f"[{status_color}]📍 {result['url']}[/{status_color}] "
                            f"[yellow](Status: {result['status']})[/yellow]"
                        )
                        result['priority'] = 'low'
                        results.append(result)
                    
                    progress.update(
                        task,
                        found=f"[green]Found: {stats.found}[/green]",
                        rate=f"[cyan]{stats.get_rate():.1f} req/s[/cyan]"
                    )
    
    return results, stats

def get_status_color(status_code):
    """Enhanced status color coding"""
    colors = {
        200: "green",
        301: "yellow",
        302: "yellow",
        307: "yellow",
        308: "yellow",
        401: "red",
        403: "magenta"
    }
    return colors.get(status_code, "white")

def save_results(results, output_file, output_format, stats):
    """Enhanced save with multiple formats including HTML"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if output_format == "txt":
            with open(output_file, "w", encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("Admin Panel Finder Pro - Enhanced Edition\n")
                f.write("Developed by PUJO\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"Scan Date: {timestamp}\n")
                f.write(f"Total Scanned: {stats.scanned}\n")
                f.write(f"Total Found: {stats.found}\n")
                f.write(f"Scan Duration: {stats.get_elapsed():.2f}s\n")
                f.write(f"Average Rate: {stats.get_rate():.2f} req/s\n")
                f.write("\n" + "=" * 70 + "\n\n")
                
                for idx, r in enumerate(results, 1):
                    f.write(f"[{idx}] {r.get('priority', 'medium').upper()} PRIORITY\n")
                    f.write(f"URL: {r['url']}\n")
                    f.write(f"Status: {r['status']}\n")
                    f.write(f"Size: {r['size']} bytes\n")
                    f.write(f"Server: {r['server']}\n")
                    f.write(f"Content-Type: {r.get('content_type', 'N/A')}\n")
                    f.write(f"Response Time: {r.get('response_time', 0):.3f}s\n")
                    
                    if 'analysis' in r:
                        f.write(f"Confidence: {r['analysis']['confidence']}%\n")
                        if r['analysis']['indicators']:
                            f.write(f"Indicators: {', '.join(r['analysis']['indicators'])}\n")
                    
                    if r.get('redirect'):
                        f.write(f"Redirects to: {r['redirect']}\n")
                    
                    f.write("-" * 70 + "\n\n")
        
        elif output_format == "json":
            with open(output_file, "w", encoding='utf-8') as f:
                json.dump({
                    "tool": "Admin Panel Finder Pro - Enhanced",
                    "developer": "PUJO",
                    "scan_info": {
                        "timestamp": timestamp,
                        "total_scanned": stats.scanned,
                        "total_found": stats.found,
                        "duration": stats.get_elapsed(),
                        "rate": stats.get_rate(),
                        "errors": stats.errors,
                        "status_distribution": dict(stats.status_codes)
                    },
                    "results": results
                }, f, indent=2)
        
        elif output_format == "csv":
            with open(output_file, "w", newline="", encoding='utf-8') as f:
                fieldnames = ["priority", "url", "status", "size", "server", "content_type", "response_time", "confidence"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for r in results:
                    writer.writerow({
                        "priority": r.get('priority', 'N/A'),
                        "url": r['url'],
                        "status": r['status'],
                        "size": r['size'],
                        "server": r['server'],
                        "content_type": r.get('content_type', 'N/A'),
                        "response_time": r.get('response_time', 0),
                        "confidence": r.get('analysis', {}).get('confidence', 0)
                    })
        
        elif output_format == "html":
            with open(output_file, "w", encoding='utf-8') as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel Finder Pro - Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }}
        h1 {{ color: #00ff88; }}
        .stats {{ background: #2a2a2a; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; background: #2a2a2a; }}
        th {{ background: #00ff88; color: #000; padding: 10px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #3a3a3a; }}
        .high {{ color: #ff4444; font-weight: bold; }}
        .medium {{ color: #ffaa00; }}
        .low {{ color: #00aaff; }}
        .status-200 {{ color: #00ff88; }}
        .status-30x {{ color: #ffaa00; }}
        .status-40x {{ color: #ff4444; }}
    </style>
</head>
<body>
    <h1>🎯 Admin Panel Finder Pro - Enhanced Edition</h1>
    <p>Developed by PUJO | Scan Date: {timestamp}</p>
    
    <div class="stats">
        <h2>📊 Scan Statistics</h2>
        <p><strong>Total Scanned:</strong> {stats.scanned}</p>
        <p><strong>Total Found:</strong> {stats.found}</p>
        <p><strong>Duration:</strong> {stats.get_elapsed():.2f}s</p>
        <p><strong>Average Rate:</strong> {stats.get_rate():.2f} req/s</p>
        <p><strong>Errors:</strong> {stats.errors}</p>
    </div>
    
    <h2>🎯 Results ({len(results)} found)</h2>
    <table>
        <tr>
            <th>Priority</th>
            <th>URL</th>
            <th>Status</th>
            <th>Size</th>
            <th>Server</th>
            <th>Confidence</th>
        </tr>
""")
                for r in results:
                    priority_class = r.get('priority', 'medium')
                    status_class = f"status-{str(r['status'])[0]}0x" if r['status'] != 200 else "status-200"
                    confidence = r.get('analysis', {}).get('confidence', 0)
                    
                    f.write(f"""        <tr>
            <td class="{priority_class}">{priority_class.upper()}</td>
            <td><a href="{r['url']}" target="_blank">{r['url']}</a></td>
            <td class="{status_class}">{r['status']}</td>
            <td>{r['size']} bytes</td>
            <td>{r['server']}</td>
            <td>{confidence}%</td>
        </tr>
""")
                
                f.write("""    </table>
</body>
</html>""")
        
        return True
    except Exception as e:
        console.print(f"[red]❌ Error saving: {str(e)}[/red]")
        return False

def display_results_table(results, stats):
    """Enhanced results display with priority sorting"""
    if not results:
        console.print(Panel(
            "[red]❌ No admin panels found[/red]",
            title="Scan Results",
            style="red",
            box=box.ROUNDED
        ))
        return
    
    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    results.sort(key=lambda x: priority_order.get(x.get('priority', 'medium'), 3))
    
    table = Table(
        title=f"[green]]✓ Found {len(results)} Potential Admin Panels[/green]",
        show_header=True,
        header_style="magenta bold",
        box=box.DOUBLE_EDGE,
        title_style="green bold"
    )
    
    table.add_column("#", style="cyan", width=4)
    table.add_column("Priority", style="yellow", width=8)
    table.add_column("URL", style="white", min_width=35)
    table.add_column("Status", style="green", width=8)
    table.add_column("Size", style="yellow", width=10)
    table.add_column("Confidence", style="magenta", width=11)
    
    for idx, r in enumerate(results, 1):
        priority = r.get('priority', 'medium').upper()
        priority_style = {"HIGH": "red bold", "MEDIUM": "yellow", "LOW": "blue"}.get(priority, "white")
        
        status_color = get_status_color(r['status'])
        confidence = r.get('analysis', {}).get('confidence', 0)
        
        table.add_row(
            str(idx),
            f"[{priority_style}]{priority}[/{priority_style}]",
            r['url'],
            f"[{status_color}]{r['status']}[/{status_color}]",
            f"{r['size']} B",
            f"{confidence}%" if confidence > 0 else "N/A"
        )
    
    console.print("\n")
    console.print(table)
    
    # Statistics panel
    stats_text = (
        f"[green]✓ Scan Complete![/green]\n\n"
        f"[cyan]Scanned:[/cyan] {stats.scanned} paths\n"
        f"[green]Found:[/green] {stats.found} panels\n"
        f"[yellow]Duration:[/yellow] {stats.get_elapsed():.2f}s\n"
        f"[blue]Rate:[/blue] {stats.get_rate():.2f} req/s\n"
        f"[red]Errors:[/red] {stats.errors}"
    )
    
    console.print(Panel(
        stats_text,
        title="[yellow]📈 Statistics[/yellow]",
        border_style="green",
        box=box.ROUNDED
    ))

def main():
    """Enhanced main function"""
    print_banner()
    
    params = get_user_input()
    if not params:
        return
    
    base_url = params['target'] if params['target'].endswith("/") else params['target'] + "/"
    
    proxy = None
    if params['proxy']:
        proxy = {"http": params['proxy'], "https": params['proxy']}
        console.print(f"[yellow]🔌 Proxy: {params['proxy']}[/yellow]")
    
    wordlist = load_wordlist(params['wordlist'])
    if not wordlist:
        console.print("[red]❌ No wordlist available[/red]")
        return
    
    # Configuration summary
    console.print(Panel(
        f"[cyan]Target:[/cyan] {base_url}\n"
        f"[cyan]Paths:[/cyan] {len(wordlist)}\n"
        f"[cyan]Threads:[/cyan] {params['threads']}\n"
        f"[cyan]Timeout:[/cyan] {params['timeout']}s\n"
        f"[cyan]Stealth:[/cyan] {'Yes' if params['stealth'] else 'No'}\n"
        f"[cyan]Redirects:[/cyan] {'Yes' if params['follow_redirects'] else 'No'}",
        title="[green]⚙️  Configuration[/green]",
        border_style="cyan",
        box=box.ROUNDED
    ))
    
    # Start scan
    start_time = time.time()
    results, stats = scan_admin_panels(
        base_url,
        wordlist,
        params['threads'],
        params['timeout'],
        proxy,
        params['stealth'],
        params['follow_redirects']
    )
    
    # Display results
    console.print()
    display_results_table(results, stats)
    
    # Save results if requested
    if params['output']:
        output_filename = params['output']
        if not output_filename.endswith(f".{params['format']}"):
            output_filename += f".{params['format']}"
        
        if save_results(results, output_filename, params['format'], stats):
            console.print(f"\n[green]💾 Results saved: {output_filename}[/green]")
    
    # High priority findings summary
    high_priority = [r for r in results if r.get('priority') == 'high']
    if high_priority:
        console.print("\n")
        console.print(Panel(
            f"[red]⚠️  {len(high_priority)} HIGH PRIORITY findings detected![/red]\n"
            f"These URLs show strong indicators of admin panels.\n"
            f"Review them immediately!",
            title="[red]🚨 Alert[/red]",
            border_style="red bold",
            box=box.DOUBLE_EDGE
        ))
    
    # Final summary
    console.print(f"\n[yellow]✨ Scan completed by Admin Panel Finder Pro ✨[/yellow]")
    console.print(f"[cyan]Developed by PUJO - Enhanced Edition[/cyan]\n")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings('ignore')
    
    try:
        requests.packages.urllib3.disable_warnings()
    except:
        pass
    
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Scan interrupted by user[/yellow]")
        console.print("[cyan]Exiting gracefully...[/cyan]")
    except Exception as e:
        console.print(f"\n[red]❌ Fatal error: {str(e)}[/red]")
        console.print("[yellow]Please report this issue to the developer[/yellow]")