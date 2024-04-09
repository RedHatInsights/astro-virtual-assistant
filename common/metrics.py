from typing import Optional

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
    CLOSING = "closing"
    CLOSING_ANYTHING_ELSE = "closing_anything_else"
    FEEDBACK = "feedback"


def flow_started_count(flow_name: Flow):
    print(f"flow started {flow_name}")
    _flows_started_count.labels(flow_name=str(flow_name)).inc()


def flow_finished_count(flow_name: Flow, sub_flow_name: Optional[str] = None):
    print(f"flow finished {flow_name}")
    _flows_finished_count.labels(
        flow_name=str(flow_name), sub_flow_name=sub_flow_name
    ).inc()
