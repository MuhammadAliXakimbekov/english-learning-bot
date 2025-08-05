import time
from collections import defaultdict
from config import RATE_LIMIT_PER_USER, RATE_LIMIT_WINDOW_MS

class RateLimiter:
    def __init__(self):
        self.user_requests = defaultdict(list)
    
    def is_rate_limited(self, user_id):
        """Check if user is rate limited"""
        now = time.time() * 1000  # Convert to milliseconds
        user_requests = self.user_requests[user_id]
        
        # Remove requests older than the window
        valid_requests = [
            timestamp for timestamp in user_requests 
            if now - timestamp < RATE_LIMIT_WINDOW_MS
        ]
        
        # Check if user has exceeded the limit
        if len(valid_requests) >= RATE_LIMIT_PER_USER:
            return True
        
        # Add current request
        valid_requests.append(now)
        self.user_requests[user_id] = valid_requests
        
        return False
    
    def get_remaining_requests(self, user_id):
        """Get remaining requests for user"""
        now = time.time() * 1000
        user_requests = self.user_requests[user_id]
        valid_requests = [
            timestamp for timestamp in user_requests 
            if now - timestamp < RATE_LIMIT_WINDOW_MS
        ]
        
        return max(0, RATE_LIMIT_PER_USER - len(valid_requests))
    
    def get_time_until_reset(self, user_id):
        """Get time until rate limit resets"""
        user_requests = self.user_requests[user_id]
        if not user_requests:
            return 0
        
        now = time.time() * 1000
        oldest_request = min(user_requests)
        reset_time = oldest_request + RATE_LIMIT_WINDOW_MS
        return max(0, reset_time - now)

# Create a global instance
rate_limiter = RateLimiter() 