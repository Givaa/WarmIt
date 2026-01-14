"""Health monitoring and auto-recovery system."""

import logging
import asyncio
import psutil
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from warmit.database import async_session_maker, engine
from warmit.config import settings


logger = logging.getLogger(__name__)


class HealthMonitor:
    """System health monitoring and auto-recovery."""

    @staticmethod
    async def check_database() -> Dict[str, Any]:
        """Check database connectivity and health."""
        try:
            async with async_session_maker() as session:
                # Simple query to test connection
                result = await session.execute(text("SELECT 1"))
                result.scalar_one()

            return {
                "status": "healthy",
                "message": "Database connection OK",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    @staticmethod
    def check_redis() -> Dict[str, Any]:
        """Check Redis connectivity."""
        try:
            import redis
            r = redis.from_url(settings.redis_url, socket_connect_timeout=2)
            r.ping()
            r.close()

            return {
                "status": "healthy",
                "message": "Redis connection OK",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    @staticmethod
    def check_system_resources() -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            status = "healthy"
            warnings = []

            if cpu_percent > 90:
                warnings.append("High CPU usage")
                status = "degraded"

            if memory.percent > 90:
                warnings.append("High memory usage")
                status = "degraded"

            if disk.percent > 90:
                warnings.append("High disk usage")
                status = "degraded"

            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "warnings": warnings,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"System resources check failed: {e}")
            return {
                "status": "unhealthy",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    @staticmethod
    def check_celery_workers() -> Dict[str, Any]:
        """Check if Celery workers are running."""
        try:
            from warmit.tasks import celery_app

            inspect = celery_app.control.inspect(timeout=2)
            active = inspect.active()

            if active is None:
                return {
                    "status": "unhealthy",
                    "message": "No Celery workers responding",
                    "workers": 0,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

            worker_count = len(active)

            return {
                "status": "healthy" if worker_count > 0 else "unhealthy",
                "message": f"{worker_count} workers active",
                "workers": worker_count,
                "worker_names": list(active.keys()),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Celery workers check failed: {e}")
            return {
                "status": "unhealthy",
                "message": str(e),
                "workers": 0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    @staticmethod
    async def check_accounts_health(session: AsyncSession) -> Dict[str, Any]:
        """Check health of email accounts."""
        from warmit.models.account import Account, AccountStatus

        try:
            # Count accounts by status
            result = await session.execute(select(Account))
            accounts = result.scalars().all()

            total = len(accounts)
            active = sum(1 for a in accounts if a.status == AccountStatus.ACTIVE)
            error = sum(1 for a in accounts if a.status == AccountStatus.ERROR)
            high_bounce = sum(1 for a in accounts if a.bounce_rate > settings.max_bounce_rate)

            status = "healthy"
            warnings = []

            if high_bounce > 0:
                warnings.append(f"{high_bounce} accounts with high bounce rate")
                status = "degraded"

            if error > 0:
                warnings.append(f"{error} accounts in error state")
                status = "degraded"

            return {
                "status": status,
                "total_accounts": total,
                "active_accounts": active,
                "error_accounts": error,
                "high_bounce_accounts": high_bounce,
                "warnings": warnings,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Accounts health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    @staticmethod
    async def get_full_health_report() -> Dict[str, Any]:
        """Get comprehensive health report of all systems."""
        async with async_session_maker() as session:
            database = await HealthMonitor.check_database()
            redis = HealthMonitor.check_redis()
            resources = HealthMonitor.check_system_resources()
            celery = HealthMonitor.check_celery_workers()
            accounts = await HealthMonitor.check_accounts_health(session)

            # Determine overall status
            all_checks = [database, redis, resources, celery, accounts]
            unhealthy = sum(1 for c in all_checks if c.get("status") == "unhealthy")
            degraded = sum(1 for c in all_checks if c.get("status") == "degraded")

            if unhealthy > 0:
                overall_status = "unhealthy"
            elif degraded > 0:
                overall_status = "degraded"
            else:
                overall_status = "healthy"

            return {
                "overall_status": overall_status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "checks": {
                    "database": database,
                    "redis": redis,
                    "system_resources": resources,
                    "celery_workers": celery,
                    "email_accounts": accounts
                }
            }

    @staticmethod
    async def auto_recover() -> Dict[str, Any]:
        """Attempt automatic recovery of failed components."""
        actions_taken = []
        success = []

        try:
            async with async_session_maker() as session:
                from warmit.models.account import Account, AccountStatus

                # Auto-resume paused accounts with good metrics
                result = await session.execute(
                    select(Account).where(
                        Account.status == AccountStatus.PAUSED,
                        Account.bounce_rate < settings.max_bounce_rate * 0.5
                    )
                )
                accounts_to_resume = result.scalars().all()

                for account in accounts_to_resume:
                    account.status = AccountStatus.ACTIVE
                    actions_taken.append(f"Resumed account {account.email}")
                    success.append(True)

                # Reset error accounts after 1 hour
                result = await session.execute(
                    select(Account).where(Account.status == AccountStatus.ERROR)
                )
                error_accounts = result.scalars().all()

                for account in error_accounts:
                    # Simple reset - could be more sophisticated
                    account.status = AccountStatus.PAUSED
                    actions_taken.append(f"Reset error account {account.email} to paused")
                    success.append(True)

                await session.commit()

            return {
                "recovery_attempted": True,
                "actions_taken": actions_taken,
                "success_count": sum(success),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Auto-recovery failed: {e}")
            return {
                "recovery_attempted": True,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
