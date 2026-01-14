#!/usr/bin/env python3
"""CLI tool for WarmIt management."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from sqlalchemy import select
from warmit.database import async_session_maker
from warmit.models.account import Account, AccountType, AccountStatus
from warmit.models.campaign import Campaign, CampaignStatus
from warmit.services.domain_checker import DomainChecker


app = typer.Typer(help="WarmIt CLI - Email warming management tool")
console = Console()


@app.command()
def accounts():
    """List all email accounts."""

    async def _list_accounts():
        async with async_session_maker() as session:
            result = await session.execute(select(Account))
            accounts = result.scalars().all()

            if not accounts:
                rprint("[yellow]No accounts found[/yellow]")
                return

            # Create table
            table = Table(title="Email Accounts", show_lines=True)
            table.add_column("ID", style="cyan")
            table.add_column("Email", style="green")
            table.add_column("Type", style="blue")
            table.add_column("Status", style="magenta")
            table.add_column("Domain Age", style="yellow")
            table.add_column("Sent", style="white")
            table.add_column("Received", style="white")
            table.add_column("Bounce Rate", style="red")

            for acc in accounts:
                domain_age = (
                    f"{acc.domain_age_days}d" if acc.domain_age_days else "Unknown"
                )
                bounce_rate = f"{acc.bounce_rate:.1%}"

                table.add_row(
                    str(acc.id),
                    acc.email,
                    acc.type.value,
                    acc.status.value,
                    domain_age,
                    str(acc.total_sent),
                    str(acc.total_received),
                    bounce_rate,
                )

            console.print(table)

    asyncio.run(_list_accounts())


@app.command()
def campaigns():
    """List all warming campaigns."""

    async def _list_campaigns():
        async with async_session_maker() as session:
            result = await session.execute(select(Campaign))
            campaigns = result.scalars().all()

            if not campaigns:
                rprint("[yellow]No campaigns found[/yellow]")
                return

            # Create table
            table = Table(title="Warming Campaigns", show_lines=True)
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Status", style="magenta")
            table.add_column("Week", style="blue")
            table.add_column("Progress", style="yellow")
            table.add_column("Today", style="white")
            table.add_column("Total Sent", style="white")
            table.add_column("Open Rate", style="green")

            for camp in campaigns:
                progress = f"{camp.progress_percentage:.0f}%"
                today = f"{camp.emails_sent_today}/{camp.target_emails_today}"
                open_rate = f"{camp.open_rate:.1%}"

                table.add_row(
                    str(camp.id),
                    camp.name,
                    camp.status.value,
                    f"{camp.current_week}/{camp.duration_weeks}",
                    progress,
                    today,
                    str(camp.total_emails_sent),
                    open_rate,
                )

            console.print(table)

    asyncio.run(_list_campaigns())


@app.command()
def check_domain(email: str):
    """Check domain age and get warming recommendations."""

    async def _check():
        rprint(f"[cyan]Checking domain for:[/cyan] {email}")
        rprint("")

        domain_info = await DomainChecker.check_domain(email)

        rprint(f"[green]Domain:[/green] {domain_info.domain}")
        rprint(
            f"[green]Age:[/green] {domain_info.age_days} days"
            if domain_info.age_days
            else "[yellow]Age: Unknown[/yellow]"
        )
        rprint(
            f"[green]Creation Date:[/green] {domain_info.creation_date}"
            if domain_info.creation_date
            else "[yellow]Creation Date: Unknown[/yellow]"
        )
        rprint(f"[green]Registrar:[/green] {domain_info.registrar or 'Unknown'}")
        rprint("")
        rprint("[cyan]Recommendations:[/cyan]")
        rprint(f"  - Warmup Duration: {domain_info.warmup_weeks_recommended} weeks")
        rprint(f"  - Initial Daily Limit: {domain_info.initial_daily_limit} emails/day")
        rprint(
            f"  - Is New Domain: {'Yes' if domain_info.is_new_domain else 'No'}"
        )

        # Show schedule
        schedule = DomainChecker.calculate_warmup_schedule(domain_info)
        rprint("")
        rprint("[cyan]Recommended Schedule:[/cyan]")
        for week, limit in schedule.items():
            rprint(f"  Week {week}: {limit} emails/day")

    asyncio.run(_check())


@app.command()
def stats():
    """Show system statistics."""

    async def _stats():
        async with async_session_maker() as session:
            # Count accounts
            result = await session.execute(
                select(Account).where(Account.type == AccountType.SENDER)
            )
            senders = len(result.scalars().all())

            result = await session.execute(
                select(Account).where(Account.type == AccountType.RECEIVER)
            )
            receivers = len(result.scalars().all())

            result = await session.execute(
                select(Account).where(Account.status == AccountStatus.ACTIVE)
            )
            active = len(result.scalars().all())

            # Count campaigns
            result = await session.execute(select(Campaign))
            total_campaigns = len(result.scalars().all())

            result = await session.execute(
                select(Campaign).where(Campaign.status == CampaignStatus.ACTIVE)
            )
            active_campaigns = len(result.scalars().all())

            # Calculate totals
            result = await session.execute(select(Account))
            accounts = result.scalars().all()

            total_sent = sum(acc.total_sent for acc in accounts)
            total_received = sum(acc.total_received for acc in accounts)
            total_bounced = sum(acc.total_bounced for acc in accounts)

            avg_open_rate = (
                sum(acc.open_rate for acc in accounts) / len(accounts)
                if accounts
                else 0
            )
            avg_bounce_rate = (
                sum(acc.bounce_rate for acc in accounts) / len(accounts)
                if accounts
                else 0
            )

            # Display
            rprint("[cyan bold]WarmIt System Statistics[/cyan bold]")
            rprint("")
            rprint("[green]Accounts:[/green]")
            rprint(f"  - Total: {senders + receivers}")
            rprint(f"  - Senders: {senders}")
            rprint(f"  - Receivers: {receivers}")
            rprint(f"  - Active: {active}")
            rprint("")
            rprint("[green]Campaigns:[/green]")
            rprint(f"  - Total: {total_campaigns}")
            rprint(f"  - Active: {active_campaigns}")
            rprint("")
            rprint("[green]Emails:[/green]")
            rprint(f"  - Total Sent: {total_sent:,}")
            rprint(f"  - Total Received: {total_received:,}")
            rprint(f"  - Total Bounced: {total_bounced:,}")
            rprint("")
            rprint("[green]Rates:[/green]")
            rprint(f"  - Avg Open Rate: {avg_open_rate:.1%}")
            rprint(f"  - Avg Bounce Rate: {avg_bounce_rate:.1%}")

    asyncio.run(_stats())


@app.command()
def init_db():
    """Initialize the database."""

    async def _init():
        from warmit.database import init_db

        await init_db()
        rprint("[green]✅ Database initialized successfully[/green]")

    asyncio.run(_init())


if __name__ == "__main__":
    app()
