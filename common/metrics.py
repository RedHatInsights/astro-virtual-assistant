from prometheus_client import Counter
from enum import Enum

# Counters
action_custom_action_count = Counter(
    "virtual_assistant_custom_action_count",
    "Total number of custom actions triggered",
    ["action_type"],
)

_flows_started_count = Counter(
    "virtual_assistant_flows_started_count",
    "Total number of flows started",
    ["flow_name"],
)

_flows_finished_count = Counter(
    "virtual_assistant_flows_finished_count",
    "Total number of flows started",
    ["flow_name", "sub_flow_name"],
)


class Flow(Enum):
    ADVISOR = "advisor"
    CLOSING = "closing"
    CLOSING_ANYTHING_ELSE = "closing_anything_else"
    FEEDBACK = "feedback"
    IMAGE_BUILDER_GETTING_STARTED = "image_builder_getting_started"
    IMAGE_BUILDER_CUSTOM_CONTENT = "image_builder_custom_content"
    VULNERABILITY = "vulnerability"


def flow_started_count(flow_name: Flow):
    _flows_started_count.labels(flow_name=flow_name.value).inc()


def flow_finished_count(flow_name: Flow, sub_flow_name: str = ""):
    _flows_finished_count.labels(
        flow_name=flow_name.value, sub_flow_name=sub_flow_name
    ).inc()
