"""Async health checker — pings servers and updates their status."""
import asyncio
import logging
import time

import httpx

from models import Server

logger = logging.getLogger(__name__)


class HealthChecker:
    """Checks the health of servers over HTTP, asynchronously."""

    def __init__(self, timeout: float = 5.0, degraded_threshold_ms: float = 500.0):
        self.timeout = timeout
        self.degraded_threshold_ms = degraded_threshold_ms

    async def check(self, server: Server) -> Server:
        """Check a single server's /health endpoint.

        Status rules:
          UP       : HTTP 200 AND response time <= threshold
          DEGRADED : HTTP 200 BUT slow, OR non-200 response
          DOWN     : connection error or timeout
        """
        url = f"{server.base_url()}/health"
        start = time.perf_counter()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url)
            elapsed_ms = (time.perf_counter() - start) * 1000

            if resp.status_code == 200 and elapsed_ms <= self.degraded_threshold_ms:
                server.status = "UP"
            else:
                server.status = "DEGRADED"
            logger.info(
                "%-20s %-9s (%.0f ms, HTTP %d)",
                server.name, server.status, elapsed_ms, resp.status_code,
            )

        except (httpx.ConnectError, httpx.TimeoutException, httpx.ReadError) as e:
            server.status = "DOWN"
            logger.warning("%-20s DOWN — %s", server.name, type(e).__name__)

        return server

    async def check_all(self, servers: list[Server]) -> list[Server]:
        """Check all servers concurrently using asyncio.gather()."""
        return await asyncio.gather(*[self.check(s) for s in servers])
