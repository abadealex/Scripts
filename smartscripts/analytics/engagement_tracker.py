# analytics/engagement_tracker.py
import time

# Dummy store for engagement events
_engagement_events = []

def track_event(user_id: int, feature: str, action: str, metadata: dict = None):
    event = {
        'timestamp': time.time(),
        'user_id': user_id,
        'feature': feature,
        'action': action,
        'metadata': metadata or {}
    }
    _engagement_events.append(event)

def get_events():
    return _engagement_events
