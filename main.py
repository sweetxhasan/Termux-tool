#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TG Post Reaction Tool v2.0
Advanced Telegram Post Reaction Bot for Termux
Author: Your Name
Description: Send love reactions to Telegram public posts using multiple bots
"""

import os
import sys
import json
import time
import re
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# Third-party imports
try:
    from telegram import Bot, ReactionTypeEmoji
    from telegram.error import TelegramError, TimedOut, NetworkError
    from colorama import init, Fore, Back, Style
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich import box
except ImportError as e:
    print(f"Error: Missing required module: {e}")
    print("Please run: pip install python-telegram-bot colorama rich")
    sys.exit(1)

# Initialize colorama for cross-platform colors
init(autoreset=True)

# Initialize rich console
console = Console()

# Configuration
CONFIG_FILE = "config.json"
LOG_FILE = "reaction_log.txt"

class TGPostReactionTool:
    """Main tool class for Telegram post reactions"""
    
    def __init__(self):
        self.config = self.load_config()
        self.bots = []
        self.results = []
        self.stats = {"success": 0, "failed": 0, "total": 0}
        self.setup_bots()
        
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            else:
                console.print(f"[bold red]❌ Config file {CONFIG_FILE} not found![/]")
                console.print("[yellow]Creating default config...[/]")
                default_config = {
                    "bots": [],
                    "settings": {
                        "reaction": "❤️",
                        "delay_between_bots": 1.5,
                        "max_retries": 3
                    }
                }
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception as e:
            console.print(f"[bold red]Error loading config: {e}[/]")
            return {"bots": [], "settings": {"reaction": "❤️", "delay_between_bots": 1.5, "max_retries": 3}}
    
    def setup_bots(self):
        """Initialize bot instances from tokens"""
        tokens = self.config.get("bots", [])
        for i, token in enumerate(tokens):
            try:
                bot = Bot(token=token.strip())
                # Test bot connection
                asyncio.run(bot.get_me())
                self.bots.append({
                    "id": i + 1,
                    "token": token[-12:],  # Show only last 12 chars for security
                    "bot": bot,
                    "status": "✅ Active"
                })
            except Exception as e:
                self.bots.append({
                    "id": i + 1,
                    "token": token[-12:],
                    "bot": None,
                    "status": f"❌ Failed: {str(e)[:30]}"
                })
    
    def display_banner(self):
        """Show beautiful ASCII banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║    ████████╗ ██████╗     ██████╗  ██████╗ ███████╗████████╗    ║
║    ╚══██╔══╝██╔════╝     ██╔══██╗██╔═══██╗██╔════╝╚══██╔══╝    ║
║       ██║   ██║  ███╗    ██████╔╝██║   ██║███████╗   ██║       ║
║       ██║   ██║   ██║    ██╔═══╝ ██║   ██║╚════██║   ██║       ║
║       ██║   ╚██████╔╝    ██║     ╚██████╔╝███████║   ██║       ║
║       ╚═╝    ╚═════╝     ╚═╝      ╚═════╝ ╚══════╝   ╚═╝       ║
║                                                                  ║
║             🔥 POST REACTION TOOL v2.0 🔥                       ║
║           [ Termux Edition - Advanced Version ]                 ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """
        console.print(f"[bold cyan]{banner}[/]")
        console.print("[dim]══════════════════════════════════════════════════════════════════════[/]")
    
    def show_bot_status(self):
        """Display status of all configured bots"""
        table = Table(title="🤖 Bot Status Overview", box=box.ROUNDED)
        table.add_column("Bot #", style="cyan", justify="center")
        table.add_column("Token (Last 12)", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Performance", style="blue")
        
        for bot in self.bots:
            status_color = "green" if "✅" in bot["status"] else "red"
            perf = "⚡ Fast" if "✅" in bot["status"] else "💀 Dead"
            table.add_row(
                f"#{bot['id']}",
                f"...{bot['token']}",
                f"[{status_color}]{bot['status']}[/]",
                f"[{status_color}]{perf}[/]"
            )
        
        console.print(table)
        
        # Show summary
        active = sum(1 for b in self.bots if "✅" in b["status"])
        total = len(self.bots)
        console.print(f"\n[bold]📊 Summary: [green]{active}[/] Active | [red]{total-active}[/] Failed | [blue]{total}[/] Total[/]")
    
    def parse_telegram_link(self, link: str) -> Tuple[Optional[str], Optional[int]]:
        """Extract chat username/ID and message ID from Telegram link"""
        # Patterns for different Telegram link formats
        patterns = [
            r'https?://t\.me/([a-zA-Z0-9_]+)/(\d+)',  # https://t.me/username/123
            r'https?://telegram\.me/([a-zA-Z0-9_]+)/(\d+)',  # https://telegram.me/username/123
            r'https?://t\.me/c/(\d+)/(\d+)',  # Private/supergroup: https://t.me/c/123456789/123
            r'@?([a-zA-Z0-9_]+)/(\d+)',  # username/123 format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, link)
            if match:
                chat = match.group(1)
                msg_id = int(match.group(2))
                
                # Handle private channel format
                if chat.isdigit() and len(chat) > 9:
                    chat = f"-100{chat}"  # Convert to supergroup chat ID format
                elif not chat.startswith('@') and not chat.startswith('-100'):
                    chat = f"@{chat}"  # Add @ for public channels
                
                return chat, msg_id
        
        console.print("[bold red]❌ Invalid Telegram link format![/]")
        console.print("[yellow]✅ Example: https://t.me/username/123[/]")
        return None, None
    
    async def send_reaction(self, bot_info: Dict, chat_id: str, message_id: int) -> bool:
        """Send reaction using a specific bot"""
        bot = bot_info["bot"]
        if not bot:
            return False
        
        reaction = self.config["settings"].get("reaction", "❤️")
        max_retries = self.config["settings"].get("max_retries", 3)
        
        for attempt in range(max_retries):
            try:
                # Send the reaction
                await bot.set_message_reaction(
                    chat_id=chat_id,
                    message_id=message_id,
                    reaction=[ReactionTypeEmoji(emoji=reaction)]
                )
                return True
            except TimedOut:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                    continue
                console.print(f"[yellow]⚠️ Bot #{bot_info['id']} timeout after {max_retries} attempts[/]")
            except NetworkError as e:
                console.print(f"[yellow]⚠️ Bot #{bot_info['id']} network error: {str(e)[:50]}[/]")
                break
            except TelegramError as e:
                console.print(f"[red]❌ Bot #{bot_info['id']} failed: {str(e)[:50]}[/]")
                break
            except Exception as e:
                console.print(f"[red]❌ Bot #{bot_info['id']} unexpected error: {str(e)[:50]}[/]")
                break
        
        return False
    
    async def process_post(self, link: str):
        """Process a single post with all bots"""
        console.print(f"\n[bold cyan]🔗 Processing link: {link}[/]")
        
        # Parse the link
        chat_id, message_id = self.parse_telegram_link(link)
        if not chat_id or not message_id:
            self.log_to_file(f"Failed to parse link: {link}")
            return
        
        console.print(f"[green]✓ Chat ID: {chat_id}[/]")
        console.print(f"[green]✓ Message ID: {message_id}[/]")
        console.print(f"[green]✓ Reaction: {self.config['settings']['reaction']}[/]\n")
        
        # Filter active bots
        active_bots = [b for b in self.bots if "✅" in b["status"]]
        
        if not active_bots:
            console.print("[bold red]❌ No active bots available![/]")
            return
        
        console.print(f"[bold]🤖 Using {len(active_bots)} active bots...[/]\n")
        
        # Progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Sending reactions...", total=len(active_bots))
            
            # Send reactions with each bot
            for i, bot_info in enumerate(active_bots):
                success = await self.send_reaction(bot_info, chat_id, message_id)
                
                # Update stats
                self.stats["total"] += 1
                if success:
                    self.stats["success"] += 1
                    result = f"✅ Bot #{bot_info['id']} sent {self.config['settings']['reaction']}"
                    console.print(f"  {result}")
                else:
                    self.stats["failed"] += 1
                    result = f"❌ Bot #{bot_info['id']} failed"
                    console.print(f"  {result}")
                
                self.results.append({
                    "bot_id": bot_info['id'],
                    "success": success,
                    "timestamp": datetime.now().isoformat(),
                    "link": link
                })
                
                # Log to file
                self.log_to_file(f"Bot #{bot_info['id']}: {'SUCCESS' if success else 'FAILED'} - {link}")
                
                progress.update(task, advance=1)
                
                # Delay between bots (except last)
                if i < len(active_bots) - 1:
                    delay = self.config["settings"].get("delay_between_bots", 1.5)
                    await asyncio.sleep(delay)
        
        # Show result summary
        self.show_result_summary()
    
    def show_result_summary(self):
        """Display summary of operation"""
        console.print("\n" + "═" * 60)
        
        # Create stats panel
        stats_text = Text()
        stats_text.append("📊 Operation Summary\n", style="bold cyan")
        stats_text.append(f"✅ Successful: {self.stats['success']}\n", style="green")
        stats_text.append(f"❌ Failed: {self.stats['failed']}\n", style="red")
        stats_text.append(f"📈 Total attempts: {self.stats['total']}\n", style="blue")
        stats_text.append(f"🎯 Success rate: ", style="white")
        
        if self.stats['total'] > 0:
            rate = (self.stats['success'] / self.stats['total']) * 100
            if rate >= 80:
                stats_text.append(f"{rate:.1f}% ⭐", style="bold green")
            elif rate >= 50:
                stats_text.append(f"{rate:.1f}% ⚡", style="bold yellow")
            else:
                stats_text.append(f"{rate:.1f}% ⚠️", style="bold red")
        
        panel = Panel(stats_text, title="[bold]Results[/]", border_style="green")
        console.print(panel)
        console.print("═" * 60)
    
    def log_to_file(self, message: str):
        """Log message to file with timestamp"""
        try:
            with open(LOG_FILE, 'a') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass
    
    def show_menu(self):
        """Display main menu"""
        menu = Panel(
            "[bold cyan]1.[/] 🔗 Send Reaction to Post\n"
            "[bold cyan]2.[/] 🤖 View Bot Status\n"
            "[bold cyan]3.[/] ⚙️ Settings\n"
            "[bold cyan]4.[/] 📊 View Logs\n"
            "[bold cyan]5.[/] 🔄 Reload Config\n"
            "[bold cyan]6.[/] 🧹 Clear Logs\n"
            "[bold cyan]7.[/] 🚪 Exit",
            title="[bold yellow]📋 Main Menu[/]",
            border_style="cyan"
        )
        console.print(menu)
    
    def settings_menu(self):
        """Display settings menu"""
        while True:
            console.clear()
            console.print("[bold cyan]⚙️ Settings[/]\n")
            console.print(f"[white]Current Reaction: [green]{self.config['settings']['reaction']}[/][/]")
            console.print(f"[white]Delay Between Bots: [green]{self.config['settings']['delay_between_bots']}s[/][/]")
            console.print(f"[white]Max Retries: [green]{self.config['settings']['max_retries']}[/][/]\n")
            
            console.print("[bold cyan]1.[/] Change Reaction")
            console.print("[bold cyan]2.[/] Change Delay")
            console.print("[bold cyan]3.[/] Change Max Retries")
            console.print("[bold cyan]4.[/] Add New Bot Token")
            console.print("[bold cyan]5.[/] Back to Main Menu")
            
            choice = console.input("\n[bold yellow]Enter choice (1-5): [/]")
            
            if choice == "1":
                new_reaction = console.input("[cyan]Enter new reaction emoji (e.g., ❤️, 👍, 😂): [/]")
                if new_reaction:
                    self.config['settings']['reaction'] = new_reaction
                    self.save_config()
                    console.print("[green]✅ Reaction updated![/]")
            elif choice == "2":
                try:
                    new_delay = float(console.input("[cyan]Enter delay in seconds (e.g., 1.5): [/]"))
                    self.config['settings']['delay_between_bots'] = new_delay
                    self.save_config()
                    console.print("[green]✅ Delay updated![/]")
                except:
                    console.print("[red]❌ Invalid number![/]")
            elif choice == "3":
                try:
                    new_retries = int(console.input("[cyan]Enter max retries (1-5): [/]"))
                    if 1 <= new_retries <= 5:
                        self.config['settings']['max_retries'] = new_retries
                        self.save_config()
                        console.print("[green]✅ Max retries updated![/]")
                    else:
                        console.print("[red]❌ Please enter between 1-5![/]")
                except:
                    console.print("[red]❌ Invalid number![/]")
            elif choice == "4":
                new_token = console.input("[cyan]Enter new bot token: [/]")
                if new_token and len(new_token) > 20:
                    self.config['bots'].append(new_token)
                    self.save_config()
                    console.print("[green]✅ Bot token added! Reloading bots...[/]")
                    self.bots = []
                    self.setup_bots()
                    time.sleep(2)
            elif choice == "5":
                break
            
            time.sleep(1.5)
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            console.print(f"[red]❌ Failed to save config: {e}[/]")
    
    def view_logs(self):
        """Display recent logs"""
        console.clear()
        console.print("[bold cyan]📊 Recent Logs[/]\n")
        
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r') as f:
                    lines = f.readlines()[-20:]  # Last 20 lines
                    for line in lines:
                        if "SUCCESS" in line:
                            console.print(f"[green]{line.strip()}[/]")
                        elif "FAILED" in line:
                            console.print(f"[red]{line.strip()}[/]")
                        else:
                            console.print(f"[white]{line.strip()}[/]")
            else:
                console.print("[yellow]No logs found yet.[/]")
        except Exception as e:
            console.print(f"[red]Error reading logs: {e}[/]")
        
        console.input("\n[bold yellow]Press Enter to continue...[/]")
    
    def clear_logs(self):
        """Clear all logs"""
        try:
            if os.path.exists(LOG_FILE):
                open(LOG_FILE, 'w').close()
                console.print("[green]✅ Logs cleared![/]")
            else:
                console.print("[yellow]No logs to clear.[/]")
        except Exception as e:
            console.print(f"[red]❌ Error clearing logs: {e}[/]")
        time.sleep(1.5)
    
    async def run(self):
        """Main execution loop"""
        while True:
            console.clear()
            self.display_banner()
            self.show_bot_status()
            self.show_menu()
            
            choice = console.input("\n[bold yellow]👉 Enter your choice: [/]")
            
            if choice == "1":
                link = console.input("[cyan]📎 Enter Telegram post link: [/]")
                if link:
                    await self.process_post(link)
                    console.input("\n[bold yellow]Press Enter to continue...[/]")
            elif choice == "2":
                console.clear()
                self.display_banner()
                self.show_bot_status()
                console.input("\n[bold yellow]Press Enter to continue...[/]")
            elif choice == "3":
                self.settings_menu()
            elif choice == "4":
                self.view_logs()
            elif choice == "5":
                console.print("[yellow]🔄 Reloading configuration...[/]")
                self.config = self.load_config()
                self.bots = []
                self.setup_bots()
                console.print("[green]✅ Config reloaded![/]")
                time.sleep(1.5)
            elif choice == "6":
                self.clear_logs()
            elif choice == "7":
                console.print("[bold green]👋 Thanks for using TG Post Reaction Tool![/]")
                console.print("[cyan]📝 Check logs at: " + LOG_FILE + "[/]")
                sys.exit(0)
            else:
                console.print("[red]❌ Invalid choice![/]")
                time.sleep(1)

def main():
    """Entry point"""
    try:
        # Check Python version
        if sys.version_info < (3, 7):
            console.print("[red]❌ Python 3.7+ required![/]")
            sys.exit(1)
        
        # Create tool instance and run
        tool = TGPostReactionTool()
        asyncio.run(tool.run())
        
    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]⚠️ Tool interrupted by user[/]")
        console.print("[cyan]👋 Goodbye![/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]❌ Fatal error: {e}[/]")
        sys.exit(1)

if __name__ == "__main__":
    main()
