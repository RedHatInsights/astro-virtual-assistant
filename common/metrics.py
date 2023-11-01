from prometheus_client import Counter

# Counters
action_custom_action_count = Counter(
    "virtual_assistant_custom_action_count",
    "Total number of custom actions triggered",
    ["action_type"],
)
