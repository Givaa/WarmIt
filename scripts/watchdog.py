#!/usr/bin/env python3
"""Watchdog service for monitoring and auto-recovery."""

import asyncio
import logging
import os
import sys
import time
from datetime import datetime
import requests

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from warmit.services.health_monitor import HealthMonitor
from warmit.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('watchdog')

# Configuration
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 300))  # 5 minutes default
API_URL = os.getenv('API_URL', 'http://localhost:8000')
MAX_CONSECUTIVE_FAILURES = 3
RECOVERY_COOLDOWN = 3600  # 1 hour between recovery attempts


class Watchdog:
    """Monitoring and auto-recovery watchdog."""

    def __init__(self):
        self.consecutive_failures = {
            'api': 0,
            'database': 0,
            'redis': 0,
            'celery': 0
        }
        self.last_recovery_time = 0
        self.start_time = time.time()

    async def check_api_health(self) -> bool:
        """Check if API is responding."""
        try:
            response = requests.get(f"{API_URL}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"API health check failed: {e}")
            return False

    async def get_detailed_health(self) -> dict:
        """Get detailed health report from API."""
        try:
            response = requests.get(f"{API_URL}/health/detailed", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get detailed health: {e}")
            return None

    async def trigger_api_recovery(self) -> bool:
        """Trigger recovery via API."""
        try:
            response = requests.post(f"{API_URL}/health/recover", timeout=30)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Recovery triggered via API: {result}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to trigger API recovery: {e}")
            return False

    async def perform_local_recovery(self):
        """Perform local recovery actions."""
        try:
            result = await HealthMonitor.auto_recover()
            logger.info(f"Local recovery completed: {result}")
            return True
        except Exception as e:
            logger.error(f"Local recovery failed: {e}")
            return False

    async def check_and_recover(self):
        """Main check and recovery logic."""
        logger.info("Running health checks...")

        # Check API availability
        api_healthy = await self.check_api_health()

        if not api_healthy:
            self.consecutive_failures['api'] += 1
            logger.warning(f"API unhealthy (consecutive failures: {self.consecutive_failures['api']})")

            if self.consecutive_failures['api'] >= MAX_CONSECUTIVE_FAILURES:
                logger.error("API has failed multiple times! Manual intervention may be required.")
                # Could send alert here
        else:
            self.consecutive_failures['api'] = 0

            # Get detailed health report
            health_report = await self.get_detailed_health()

            if health_report:
                overall_status = health_report.get('overall_status')
                logger.info(f"Overall system status: {overall_status}")

                # Check individual components
                checks = health_report.get('checks', {})

                for component, status in checks.items():
                    component_status = status.get('status')

                    if component_status == 'unhealthy':
                        self.consecutive_failures[component] = self.consecutive_failures.get(component, 0) + 1
                        logger.warning(f"{component} is unhealthy: {status.get('message')}")
                    else:
                        self.consecutive_failures[component] = 0

                # Trigger recovery if needed
                needs_recovery = any(
                    failures >= MAX_CONSECUTIVE_FAILURES
                    for failures in self.consecutive_failures.values()
                )

                current_time = time.time()
                time_since_last_recovery = current_time - self.last_recovery_time

                if needs_recovery and time_since_last_recovery > RECOVERY_COOLDOWN:
                    logger.warning("System needs recovery, attempting auto-recovery...")

                    # Try API recovery first
                    recovery_success = await self.trigger_api_recovery()

                    if not recovery_success:
                        # Fallback to local recovery
                        logger.info("API recovery failed, trying local recovery...")
                        recovery_success = await self.perform_local_recovery()

                    if recovery_success:
                        logger.info("Recovery completed successfully")
                        self.last_recovery_time = current_time
                        # Reset failure counts
                        for key in self.consecutive_failures:
                            self.consecutive_failures[key] = 0
                    else:
                        logger.error("Recovery failed! Manual intervention required.")
                elif needs_recovery:
                    logger.info(f"Recovery needed but in cooldown period ({time_since_last_recovery:.0f}s / {RECOVERY_COOLDOWN}s)")

    async def run(self):
        """Main watchdog loop."""
        logger.info(f"Watchdog started. Check interval: {CHECK_INTERVAL}s")
        logger.info(f"API URL: {API_URL}")

        iteration = 0

        while True:
            try:
                iteration += 1
                uptime = time.time() - self.start_time
                logger.info(f"=== Check #{iteration} (Uptime: {uptime/3600:.1f}h) ===")

                await self.check_and_recover()

                logger.info(f"Next check in {CHECK_INTERVAL}s")
                await asyncio.sleep(CHECK_INTERVAL)

            except KeyboardInterrupt:
                logger.info("Watchdog stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in watchdog loop: {e}", exc_info=True)
                # Continue running even on errors
                await asyncio.sleep(60)


async def main():
    """Entry point."""
    watchdog = Watchdog()
    await watchdog.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Watchdog terminated")
        sys.exit(0)
