from prometheus_client import Counter

# Counters
action_session_start = Counter(
    "virtual_assistant_action_session_start_count", "Total number of session starts"
)
