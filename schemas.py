from pydantic import BaseModel
from typing import List


class ZoneForecast(BaseModel):
    zone_id: int
    current_temp_c: float
    projected_temp_c: float
    time_to_threshold_sec: float
    warming_rate_c_per_min: float


class Forecast(BaseModel):
    timestamp: str
    zones: List[ZoneForecast]