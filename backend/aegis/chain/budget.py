import time

class CuBudget:
    def __init__(self, daily_limit: int, monthly_limit: int):
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit
        self.spent_daily = 0
        self.spent_monthly = 0

    def can_spend(self, cu: int, priority: int) -> bool:
        """
        priority: 0 = watched/liveness, 1 = eval, 2 = firehose
        """
        if self.daily_limit <= 0 or self.monthly_limit <= 0:
            return True # No budget enforcement if limits are 0

        new_daily = self.spent_daily + cu
        new_monthly = self.spent_monthly + cu

        daily_pct = new_daily / self.daily_limit
        monthly_pct = new_monthly / self.monthly_limit

        if priority == 2 and daily_pct >= 0.70:
            return False
        if priority == 1 and daily_pct >= 0.90:
            return False
        if daily_pct > 1.0:
            return False
        
        if priority == 2 and monthly_pct >= 0.97:
            return False
        if monthly_pct > 1.0:
            return False

        return True

    def spend(self, cu: int):
        self.spent_daily += cu
        self.spent_monthly += cu

    def snapshot(self) -> dict:
        return {
            "spent_daily": self.spent_daily,
            "spent_monthly": self.spent_monthly,
            "daily_limit": self.daily_limit,
            "monthly_limit": self.monthly_limit
        }
