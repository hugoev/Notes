from rest_framework.throttling import AnonRateThrottle

class AuthenticationThrottle(AnonRateThrottle):
    rate = '5/minute'  # More strict rate limit for authentication attempts 