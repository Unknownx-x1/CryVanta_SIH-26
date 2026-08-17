/**
 * PredictFuse - Data Stream Service
 * Simulates real-time MQTT data stream adhering strictly to SYSTEM_CONTRACT.md.
 * Evaluates predictions, potency loss, and dynamic rerouting logic.
 */

export class DataStreamService {
  constructor() {
    self = this;
    this.listeners = [];
    this.scenario = "NORMAL";
    this.stepCount = 0;
    this.coolingActive = false;

    // Internal state
    this.ambientTemp = 6.2;
    this.ambientHumidity = 41.0;
    this.zoneTemps = { 1: 5.5, 2: 5.8, 3: 5.2 };
    this.fuseTriggered = { 1: false, 2: false, 3: false };
    this.zonePotencyLoss = { 1: 0.0, 2: 0.0, 3: 0.0 };

    // GPS coordinates
    this.gps = { lat: 12.9716, lng: 77.5946 };
    
    // Default routes
    this.primaryRoute = [
      [12.9716, 77.5946],
      [12.9800, 77.6000],
      [12.9900, 77.6100],
      [13.0000, 77.6200],
    ];

    this.alternateRouteB = [
      [12.9716, 77.5946],
      [12.9650, 77.5850],
      [12.9550, 77.5750], // Cold Storage Facility B
    ];

    this.timer = null;
  }

  setScenario(scenario) {
    this.scenario = scenario;
    this.stepCount = 0;
    this.coolingActive = false;
    if (scenario === "NORMAL") {
      this.zoneTemps = { 1: 5.5, 2: 5.8, 3: 5.2 };
      this.fuseTriggered = { 1: false, 2: false, 3: false };
      this.zonePotencyLoss = { 1: 0.0, 2: 0.0, 3: 0.0 };
    }
    this.emit();
  }

  subscribe(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter((cb) => cb !== callback);
    };
  }

  start(intervalMs = 1500) {
    if (this.timer) clearInterval(this.timer);
    this.timer = setInterval(() => this.tick(), intervalMs);
    this.emit();
  }

  stop() {
    if (this.timer) clearInterval(this.timer);
  }

  tick() {
    this.stepCount++;
    const nowIso = new Date().toISOString();

    // Ambient fluctuations
    this.ambientTemp += 0.02 * (this.stepCount % 3 - 1);
    this.gps.lat += 0.0002;
    this.gps.lng += 0.0002;

    // Zone 1 and 3 stay stable
    this.zoneTemps[1] = Math.max(4.8, Math.min(6.2, 5.5 + 0.1 * (this.stepCount % 5 - 2)));
    this.zoneTemps[3] = Math.max(4.5, Math.min(6.0, 5.2 + 0.1 * (self.stepCount % 4 - 2)));

    // Zone 2 scenario behavior
    if (this.scenario === "NORMAL") {
      this.zoneTemps[2] = Math.max(5.0, Math.min(6.5, 5.8 + 0.1 * (this.stepCount % 3 - 1)));
    } else if (this.scenario === "LOCALIZED_WARMING" || this.scenario === "COOLING_FAILURE") {
      this.zoneTemps[2] += 0.45;
      if (this.zoneTemps[2] >= 15.0) {
        this.fuseTriggered[2] = true;
      }
    } else if (this.scenario === "COOLING_SUCCESS") {
      if (this.stepCount <= 4) {
        this.zoneTemps[2] += 0.4;
      } else {
        this.coolingActive = true;
        this.zoneTemps[2] = Math.max(5.5, this.zoneTemps[2] - 0.35);
      }
    }

    // Update Potency Loss
    Object.keys(this.zoneTemps).forEach((id) => {
      const temp = this.zoneTemps[id];
      if (temp > 8.0) {
        this.zonePotencyLoss[id] += 0.002 * Math.pow(temp - 8.0, 1.2);
      }
    });

    this.emit(nowIso);
  }

  emit(timestamp = new Date().toISOString()) {
    // 1. Build Telemetry
    const telemetry = {
      timestamp,
      ambient: {
        temp_c: Number(this.ambientTemp.toFixed(1)),
        humidity_pct: Number(this.ambientHumidity.toFixed(1)),
      },
      gps: { ...this.gps },
      zones: [1, 2, 3].map((id) => {
        const zData = {
          zone_id: id,
          temp_c: Number(this.zoneTemps[id].toFixed(1)),
          fuse_triggered: this.fuseTriggered[id],
        };
        if (id === 2 && this.fuseTriggered[2]) {
          zData.vial_id = "V17";
          zData.fuse_level = 2;
          zData.trigger_temp_c = 15.0;
        }
        return zData;
      }),
    };

    // 2. Build Forecast & Time-to-Threshold
    const z2Temp = this.zoneTemps[2];
    const z2WarmingRate = z2Temp > 6.5 ? 0.45 : 0.02;
    let z2TimeToThreshold = 1200;
    if (z2Temp >= 12.0) {
      z2TimeToThreshold = 0;
    } else if (z2WarmingRate > 0.05) {
      z2TimeToThreshold = Math.max(0, Math.round(((12.0 - z2Temp) / z2WarmingRate) * 60));
    }

    const forecast = {
      timestamp,
      zones: [
        { zone_id: 1, current_temp_c: Number(this.zoneTemps[1].toFixed(1)), projected_temp_c: 6.2, time_to_threshold_sec: 1200, warming_rate_c_per_min: 0.02 },
        { zone_id: 2, current_temp_c: Number(z2Temp.toFixed(1)), projected_temp_c: Number((z2Temp + 3.2).toFixed(1)), time_to_threshold_sec: z2TimeToThreshold, warming_rate_c_per_min: z2WarmingRate },
        { zone_id: 3, current_temp_c: Number(this.zoneTemps[3].toFixed(1)), projected_temp_c: 6.0, time_to_threshold_sec: 1200, warming_rate_c_per_min: 0.01 },
      ],
    };

    // 3. Build Potency
    const zonePotencies = [1, 2, 3].map((id) => ({
      zone_id: id,
      potency_pct: Number(Math.max(0, 100 - this.zonePotencyLoss[id] * 100).toFixed(1)),
    }));
    const overallPotency = Number((zonePotencies.reduce((acc, curr) => acc + curr.potency_pct, 0) / 3).toFixed(1));

    const potency = {
      timestamp,
      overall_potency_pct: overallPotency,
      zones: zonePotencies,
    };

    // 4. Build Decision & Actuation
    let riskLevel = "LOW";
    let actionSelected = "NONE";
    let recommendedRoute = "CURRENT_ROUTE";
    let reasoning = "All zones operating within normal target ranges (2.0°C - 8.0°C).";

    if (z2Temp >= 12.0 || z2TimeToThreshold <= 60) {
      riskLevel = "CRITICAL";
      actionSelected = "COOLING_ON_SERVO_OPEN";
      recommendedRoute = "ALTERNATE_ROUTE_B";
      reasoning = "Zone 2 breached critical 12.0°C limit! Peltier cooling active & rerouting to Cold Depot B.";
    } else if (z2TimeToThreshold < 300) {
      riskLevel = "HIGH";
      actionSelected = "COOLING_ON_SERVO_OPEN";
      recommendedRoute = "ALTERNATE_ROUTE_B";
      reasoning = `Zone 2 projected to breach threshold in ${z2TimeToThreshold}s. Peltier cooling active & recommending reroute.`;
    } else if (z2Temp > 7.5) {
      riskLevel = "MEDIUM";
      actionSelected = "COOLING_ON";
      reasoning = "Zone 2 experiencing mild warming. Peltier cooling activated.";
    }

    const decision = {
      timestamp,
      risk_level: riskLevel,
      primary_zone_affected: 2,
      action_selected: actionSelected,
      recommended_route: recommendedRoute,
      vials_at_risk_count: z2Temp > 8.0 ? 8 : 0,
      reasoning,
    };

    const actuation = {
      timestamp,
      target_zone_id: 2,
      peltier_state: (actionSelected.includes("COOLING") || this.coolingActive) ? "ON" : "OFF",
      servo_vent_position: (actionSelected.includes("SERVO") || this.coolingActive) ? "OPEN" : "CLOSED",
      alert_buzzer: riskLevel === "CRITICAL" ? "ON" : "OFF",
    };

    // 5. Build LLM Narration
    let briefing = `Shipment operating normally. All zones within safe limits. Overall potency is ${overallPotency}%.`;
    if (riskLevel === "CRITICAL") {
      briefing = `CRITICAL ALERT: Zone 2 reached ${z2Temp.toFixed(1)}°C. Peltier cooling and vents fully opened. Rerouting to Cold Facility B. Passive fuse triggered for Vial V17.`;
    } else if (riskLevel === "HIGH") {
      briefing = `WARNING: Zone 2 localized warming detected (${z2Temp.toFixed(1)}°C). Time to threshold: ${z2TimeToThreshold} seconds. Peltier cooling & venting activated. Alternate route recommended.`;
    } else if (this.coolingActive) {
      briefing = `INTERVENTION ACTIVE: Peltier cooling in Zone 2 taking effect. Temperature stabilizing (${z2Temp.toFixed(1)}°C).`;
    }

    const narration = {
      timestamp,
      briefing,
      is_fallback: false,
    };

    const fullState = {
      scenario: this.scenario,
      telemetry,
      forecast,
      potency,
      decision,
      actuation,
      narration,
      primaryRoute: this.primaryRoute,
      alternateRouteB: this.alternateRouteB,
    };

    this.listeners.forEach((cb) => cb(fullState));
  }
}

export const streamService = new DataStreamService();
