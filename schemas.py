from typing import List, Literal, Optional

from pydantic import BaseModel, Field


RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
ActionSelected = Literal[
    "NONE",
    "COOLING_ON",
    "SERVO_OPEN",
    "COOLING_ON_SERVO_OPEN",
    "ALERT_ONLY",
]
RecommendedRoute = Literal[
    "CURRENT_ROUTE",
    "ALTERNATE_ROUTE_A",
    "ALTERNATE_ROUTE_B",
    "IMMEDIATE_STOP",
]
SwitchState = Literal["ON", "OFF"]
VentPosition = Literal["OPEN", "CLOSED"]


class AmbientTelemetry(BaseModel):
    temp_c: float
    humidity_pct: float


class GpsPoint(BaseModel):
    lat: float
    lng: float


class ZoneTelemetry(BaseModel):
    zone_id: int
    temp_c: Optional[float] = None
    fuse_triggered: bool
    vial_id: Optional[str] = None
    fuse_level: Optional[int] = None
    trigger_temp_c: Optional[float] = None


class Telemetry(BaseModel):
    timestamp: str
    ambient: AmbientTelemetry
    gps: GpsPoint
    zones: List[ZoneTelemetry] = Field(default_factory=list)


class ZoneForecast(BaseModel):
    zone_id: int
    current_temp_c: float
    projected_temp_c: float
    time_to_threshold_sec: float
    warming_rate_c_per_min: float


class Forecast(BaseModel):
    timestamp: str
    zones: List[ZoneForecast] = Field(default_factory=list)


class ZonePotency(BaseModel):
    zone_id: int
    potency_pct: float


class Potency(BaseModel):
    timestamp: str
    overall_potency_pct: float
    zones: List[ZonePotency] = Field(default_factory=list)


class Decision(BaseModel):
    timestamp: str
    risk_level: RiskLevel
    primary_zone_affected: Optional[int]
    action_selected: ActionSelected
    recommended_route: RecommendedRoute
    vials_at_risk_count: int
    reasoning: str


class ActuationCommand(BaseModel):
    timestamp: str
    target_zone_id: Optional[int]
    peltier_state: SwitchState
    servo_vent_position: VentPosition
    alert_buzzer: SwitchState
