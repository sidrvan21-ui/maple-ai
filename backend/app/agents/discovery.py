from app.agents.catalog import SPECS
from app.agents.runner import run_stage
from app.schemas.gate import GatePack

DISCOVERY_MISSION = SPECS[1].mission
DISCOVERY_LESSON = SPECS[1].lesson


def run_discovery() -> GatePack:
    return run_stage(1, admitted_stages=[1])
