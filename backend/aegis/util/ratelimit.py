import asyncio
import time

class TokenBucket:
    def __init__(self, rate_per_s: float, burst: int):
        self.rate_per_s = rate_per_s
        self.burst = burst
        self.tokens = float(burst)
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, n: int = 1):
        while True:
            async with self._lock:
                now = time.monotonic()
                elapsed = now - self.last_refill
                self.tokens = min(float(self.burst), self.tokens + elapsed * self.rate_per_s)
                self.last_refill = now

                if self.tokens >= n:
                    self.tokens -= n
                    return
            
            # Wait a bit before trying again
            await asyncio.sleep(0.1)
