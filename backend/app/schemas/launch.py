from pydantic import BaseModel, Field


class LaunchArtifacts(BaseModel):
    launch_plan: str
    demand_gen: str
    messaging: str
    channel_readiness: str
    day0_metrics: list[str]
    sentiment: list[str]
    missed_alerts: list[str]
    post_launch_actions: list[str] = Field(default_factory=list)
