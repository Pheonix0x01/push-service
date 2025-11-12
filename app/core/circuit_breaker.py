import time

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_time=30):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.last_failure_time = 0
        self.open = False

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.open = True
            self.last_failure_time = time.time()

    def can_call(self):
        if not self.open:
            return True
        if time.time() - self.last_failure_time > self.recovery_time:
            self.open = False
            self.failure_count = 0
            return True
        return False

circuit_breaker = CircuitBreaker()