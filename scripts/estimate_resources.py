#!/usr/bin/env python3
"""
Campaign Resource Estimation Tool

Estimates required resources (RAM, CPU, storage, API calls, costs) for email warming campaigns.
Helps plan infrastructure needs before starting large campaigns.
"""

import sys
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class ResourceEstimate:
    """Resource estimation results."""

    # Campaign parameters
    num_senders: int
    num_receivers: int
    duration_weeks: int

    # Email volume
    total_emails: int
    emails_per_day_avg: int
    emails_per_week_avg: int
    peak_emails_per_day: int

    # Resource requirements
    ram_mb: int
    ram_mb_recommended: int
    cpu_cores: float
    cpu_cores_recommended: float
    storage_mb: int
    storage_gb: float

    # Database
    db_connections: int
    db_pool_size: int

    # Workers
    celery_workers: int
    celery_concurrency: int

    # API usage
    api_calls_total: int
    api_calls_per_day: int

    # Cost estimates (OpenRouter free tier)
    estimated_cost_usd: float

    # Recommendations
    recommended_config: str
    warnings: list[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "campaign": {
                "senders": self.num_senders,
                "receivers": self.num_receivers,
                "duration_weeks": self.duration_weeks,
            },
            "email_volume": {
                "total_emails": self.total_emails,
                "per_day_avg": self.emails_per_day_avg,
                "per_week_avg": self.emails_per_week_avg,
                "peak_per_day": self.peak_emails_per_day,
            },
            "resources": {
                "ram_mb_minimum": self.ram_mb,
                "ram_mb_recommended": self.ram_mb_recommended,
                "cpu_cores_minimum": self.cpu_cores,
                "cpu_cores_recommended": self.cpu_cores_recommended,
                "storage_mb": self.storage_mb,
                "storage_gb": round(self.storage_gb, 2),
            },
            "database": {
                "connections": self.db_connections,
                "pool_size": self.db_pool_size,
            },
            "workers": {
                "celery_workers": self.celery_workers,
                "concurrency": self.celery_concurrency,
            },
            "api": {
                "total_calls": self.api_calls_total,
                "per_day": self.api_calls_per_day,
                "estimated_cost_usd": round(self.estimated_cost_usd, 2),
            },
            "recommendation": {
                "config_profile": self.recommended_config,
                "warnings": self.warnings,
            }
        }


class ResourceEstimator:
    """Estimate resources needed for email warming campaigns."""

    # Constants for estimation
    BASE_RAM_MB = 256  # Base RAM for system
    RAM_PER_SENDER_MB = 50  # RAM per sender account
    RAM_PER_RECEIVER_MB = 30  # RAM per receiver account
    RAM_PER_WORKER_MB = 200  # RAM per Celery worker

    BASE_CPU_CORES = 0.5  # Base CPU for system
    CPU_PER_100_EMAILS = 0.1  # Additional CPU per 100 emails/day

    STORAGE_PER_EMAIL_KB = 5  # Storage per email (metadata + body)
    STORAGE_PER_ACCOUNT_KB = 10  # Storage per account

    DB_CONNECTIONS_PER_WORKER = 5  # DB connections per worker
    DB_POOL_OVERHEAD = 10  # Additional pool connections

    # Email volume estimation (progressive warming)
    # Week 1: 5/day, Week 2: 10/day, Week 3: 20/day, Week 4: 40/day, Week 5: 60/day, Week 6+: 80/day
    VOLUME_PROGRESSION = [5, 10, 20, 40, 60, 80]  # emails per sender per day

    # API cost estimation (conservative, using free tier as baseline)
    API_CALLS_PER_EMAIL = 2  # 1 for initial + 1 for reply
    API_COST_PER_1K_CALLS = 0.0  # Free tier (OpenRouter/Groq)
    # If using paid models, adjust accordingly

    def estimate(
        self,
        num_senders: int,
        num_receivers: int,
        duration_weeks: int = 6,
    ) -> ResourceEstimate:
        """Estimate resources for campaign.

        Args:
            num_senders: Number of sender accounts
            num_receivers: Number of receiver accounts
            duration_weeks: Campaign duration in weeks

        Returns:
            ResourceEstimate with all calculations
        """

        # Calculate email volume
        total_emails = 0
        for week in range(duration_weeks):
            # Get emails per day for this week (use last value if beyond progression)
            week_idx = min(week, len(self.VOLUME_PROGRESSION) - 1)
            emails_per_day = self.VOLUME_PROGRESSION[week_idx] * num_senders
            total_emails += emails_per_day * 7  # 7 days per week

        emails_per_day_avg = total_emails // (duration_weeks * 7)
        emails_per_week_avg = total_emails // duration_weeks

        # Peak is last week (highest volume)
        peak_emails_per_day = self.VOLUME_PROGRESSION[-1] * num_senders

        # Calculate RAM requirements
        ram_accounts = (num_senders * self.RAM_PER_SENDER_MB +
                       num_receivers * self.RAM_PER_RECEIVER_MB)

        # Workers needed (1 worker per 50 emails/day, minimum 2)
        celery_workers = max(2, (peak_emails_per_day // 50) + 1)
        celery_concurrency = max(2, peak_emails_per_day // 20)

        ram_workers = celery_workers * self.RAM_PER_WORKER_MB
        ram_api = 512  # API server
        ram_dashboard = 512  # Dashboard
        ram_postgres = 512  # PostgreSQL
        ram_redis = 256  # Redis

        ram_mb = (self.BASE_RAM_MB + ram_accounts + ram_workers +
                 ram_api + ram_dashboard + ram_postgres + ram_redis)
        ram_mb_recommended = int(ram_mb * 1.5)  # 50% overhead

        # Calculate CPU requirements
        cpu_base = self.BASE_CPU_CORES
        cpu_for_emails = (peak_emails_per_day / 100) * self.CPU_PER_100_EMAILS
        cpu_cores = cpu_base + cpu_for_emails
        cpu_cores_recommended = cpu_cores * 1.5  # 50% overhead

        # Calculate storage requirements
        storage_emails_kb = total_emails * self.STORAGE_PER_EMAIL_KB
        storage_accounts_kb = (num_senders + num_receivers) * self.STORAGE_PER_ACCOUNT_KB
        storage_metrics_kb = duration_weeks * 7 * 100  # Daily metrics
        storage_overhead_kb = 102400  # 100MB for system, logs, etc.

        storage_mb = (storage_emails_kb + storage_accounts_kb +
                     storage_metrics_kb + storage_overhead_kb) // 1024
        storage_gb = storage_mb / 1024

        # Database connections
        db_connections = celery_workers * self.DB_CONNECTIONS_PER_WORKER
        db_pool_size = db_connections + self.DB_POOL_OVERHEAD

        # API usage
        api_calls_total = total_emails * self.API_CALLS_PER_EMAIL
        api_calls_per_day = emails_per_day_avg * self.API_CALLS_PER_EMAIL

        # Cost estimation
        estimated_cost_usd = (api_calls_total / 1000) * self.API_COST_PER_1K_CALLS

        # Determine configuration profile
        if num_senders <= 10:
            config_profile = "small"
        elif num_senders <= 50:
            config_profile = "medium"
        elif num_senders <= 200:
            config_profile = "large"
        else:
            config_profile = "enterprise"

        # Generate warnings
        warnings = []

        if ram_mb_recommended > 8192:
            warnings.append(f"⚠️  High RAM usage ({ram_mb_recommended}MB). Consider splitting campaign.")

        if cpu_cores_recommended > 4:
            warnings.append(f"⚠️  High CPU usage ({cpu_cores_recommended:.1f} cores). Consider multiple machines.")

        if storage_gb > 10:
            warnings.append(f"⚠️  Large storage needed ({storage_gb:.1f}GB). Ensure sufficient disk space.")

        if api_calls_per_day > 10000:
            warnings.append(f"⚠️  High API usage ({api_calls_per_day} calls/day). Monitor rate limits.")

        if num_receivers < num_senders:
            warnings.append(f"⚠️  More senders than receivers. Recommended: receivers >= senders.")

        if num_senders > 100 and duration_weeks < 8:
            warnings.append(f"⚠️  Large campaign with short duration. Consider extending to 8-12 weeks.")

        return ResourceEstimate(
            num_senders=num_senders,
            num_receivers=num_receivers,
            duration_weeks=duration_weeks,
            total_emails=total_emails,
            emails_per_day_avg=emails_per_day_avg,
            emails_per_week_avg=emails_per_week_avg,
            peak_emails_per_day=peak_emails_per_day,
            ram_mb=ram_mb,
            ram_mb_recommended=ram_mb_recommended,
            cpu_cores=cpu_cores,
            cpu_cores_recommended=cpu_cores_recommended,
            storage_mb=storage_mb,
            storage_gb=storage_gb,
            db_connections=db_connections,
            db_pool_size=db_pool_size,
            celery_workers=celery_workers,
            celery_concurrency=celery_concurrency,
            api_calls_total=api_calls_total,
            api_calls_per_day=api_calls_per_day,
            estimated_cost_usd=estimated_cost_usd,
            recommended_config=config_profile,
            warnings=warnings,
        )

    def print_estimate(self, estimate: ResourceEstimate):
        """Print formatted estimate to console."""

        print("\n" + "=" * 80)
        print("🔥 WARMIT - CAMPAIGN RESOURCE ESTIMATION")
        print("=" * 80)

        print("\n📊 CAMPAIGN PARAMETERS")
        print(f"  Sender Accounts:    {estimate.num_senders}")
        print(f"  Receiver Accounts:  {estimate.num_receivers}")
        print(f"  Duration:           {estimate.duration_weeks} weeks")

        print("\n📧 EMAIL VOLUME")
        print(f"  Total Emails:       {estimate.total_emails:,}")
        print(f"  Avg per Day:        {estimate.emails_per_day_avg:,}")
        print(f"  Avg per Week:       {estimate.emails_per_week_avg:,}")
        print(f"  Peak per Day:       {estimate.peak_emails_per_day:,} (week {estimate.duration_weeks})")

        print("\n💾 RESOURCE REQUIREMENTS")
        print(f"  RAM (Minimum):      {estimate.ram_mb:,} MB ({estimate.ram_mb / 1024:.1f} GB)")
        print(f"  RAM (Recommended):  {estimate.ram_mb_recommended:,} MB ({estimate.ram_mb_recommended / 1024:.1f} GB)")
        print(f"  CPU (Minimum):      {estimate.cpu_cores:.1f} cores")
        print(f"  CPU (Recommended):  {estimate.cpu_cores_recommended:.1f} cores")
        print(f"  Storage:            {estimate.storage_mb:,} MB ({estimate.storage_gb:.2f} GB)")

        print("\n🗄️  DATABASE")
        print(f"  Connections Needed: {estimate.db_connections}")
        print(f"  Pool Size:          {estimate.db_pool_size}")

        print("\n⚙️  WORKERS")
        print(f"  Celery Workers:     {estimate.celery_workers}")
        print(f"  Concurrency:        {estimate.celery_concurrency}")

        print("\n🔌 API USAGE")
        print(f"  Total API Calls:    {estimate.api_calls_total:,}")
        print(f"  Calls per Day:      {estimate.api_calls_per_day:,}")
        print(f"  Estimated Cost:     ${estimate.estimated_cost_usd:.2f} (using free tier)")

        print("\n📋 RECOMMENDATION")
        print(f"  Configuration:      {estimate.recommended_config.upper()}")

        if estimate.warnings:
            print("\n⚠️  WARNINGS")
            for warning in estimate.warnings:
                print(f"  {warning}")
        else:
            print("\n✅ No warnings - configuration looks good!")

        print("\n" + "=" * 80)
        print("💡 TIP: Use this estimate to configure docker-compose resource limits")
        print("=" * 80 + "\n")


def main():
    """CLI interface for resource estimation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Estimate resources for WarmIt email warming campaigns"
    )
    parser.add_argument(
        "--senders",
        type=int,
        required=True,
        help="Number of sender accounts to warm up"
    )
    parser.add_argument(
        "--receivers",
        type=int,
        required=True,
        help="Number of receiver accounts"
    )
    parser.add_argument(
        "--weeks",
        type=int,
        default=6,
        help="Campaign duration in weeks (default: 6)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    # Validate inputs
    if args.senders < 1:
        print("❌ Error: Number of senders must be at least 1")
        sys.exit(1)

    if args.receivers < 1:
        print("❌ Error: Number of receivers must be at least 1")
        sys.exit(1)

    if args.weeks < 1:
        print("❌ Error: Duration must be at least 1 week")
        sys.exit(1)

    # Calculate estimate
    estimator = ResourceEstimator()
    estimate = estimator.estimate(
        num_senders=args.senders,
        num_receivers=args.receivers,
        duration_weeks=args.weeks,
    )

    # Output
    if args.json:
        print(json.dumps(estimate.to_dict(), indent=2))
    else:
        estimator.print_estimate(estimate)


if __name__ == "__main__":
    main()
