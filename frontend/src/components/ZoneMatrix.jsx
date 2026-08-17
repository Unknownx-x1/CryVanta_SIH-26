import React, { useState } from 'react';
import { Layers, AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react';

export default function ZoneMatrix({ telemetry, forecast }) {
  const [selectedZone, setSelectedZone] = useState(2);
  const zones = telemetry?.zones || [];

  return (
    <div className="card-container" style={{ marginBottom: '1.5rem' }}>
      <div className="card-header">
        <div className="card-title">
          <Layers size={18} color="#38bdf8" />
          <span>Spatial Zone & Vial Matrix</span>
        </div>
        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Target Ceiling: 8.0°C | Fuse Breach: 15.0°C</span>
      </div>

      {/* Spatial Zones Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', marginBottom: '1.25rem' }}>
        {zones.map((zone) => {
          const zForecast = forecast?.zones?.find((f) => f.zone_id === zone.zone_id);
          const isWarning = zone.temp_c > 8.0;
          const isBreached = zone.fuse_triggered || zone.temp_c >= 15.0;

          let cardBorder = '#1e293b';
          let statusBg = 'rgba(16, 185, 129, 0.1)';
          let statusColor = '#10b981';
          let statusText = 'SAFE';

          if (isBreached) {
            cardBorder = 'rgba(239, 68, 68, 0.5)';
            statusBg = 'rgba(239, 68, 68, 0.2)';
            statusColor = '#ef4444';
            statusText = 'FUSE BREACHED';
          } else if (isWarning) {
            cardBorder = 'rgba(245, 158, 11, 0.5)';
            statusBg = 'rgba(245, 158, 11, 0.2)';
            statusColor = '#f59e0b';
            statusText = 'LOCALIZED WARMING';
          }

          return (
            <div
              key={zone.zone_id}
              onClick={() => setSelectedZone(zone.zone_id)}
              style={{
                background: selectedZone === zone.zone_id ? '#1e293b' : '#0f172a',
                border: `1.5px solid ${cardBorder}`,
                borderRadius: '10px',
                padding: '1rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.875rem', fontWeight: 700, color: '#f8fafc' }}>ZONE {zone.zone_id}</span>
                <span style={{ fontSize: '0.6875rem', fontWeight: 700, padding: '0.2rem 0.5rem', borderRadius: '4px', background: statusBg, color: statusColor }}>
                  {statusText}
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', margin: '0.5rem 0' }}>
                <span style={{ fontSize: '1.75rem', fontWeight: 800, color: isWarning ? statusColor : '#f8fafc' }}>
                  {zone.temp_c}°C
                </span>
                <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                  (Projected: {zForecast?.projected_temp_c ?? zone.temp_c}°C)
                </span>
              </div>

              {zone.fuse_triggered && (
                <div style={{ marginTop: '0.5rem', padding: '0.4rem 0.6rem', borderRadius: '6px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', color: '#f87171' }}>
                  <ShieldAlert size={14} />
                  <span>Vial <strong>{zone.vial_id || 'V17'}</strong> fuse breached at {zone.trigger_temp_c || 15.0}°C!</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Individual Vial Matrix Grid for Selected Zone */}
      <div style={{ background: '#0f172a', borderRadius: '10px', padding: '1rem', border: '1px solid #1e293b' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#cbd5e1' }}>
            Zone {selectedZone} Individual Vial Grid (Vials V{selectedZone * 10 - 9} to V{selectedZone * 10})
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
            Passive Fuse Verification Status
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(75px, 1fr))', gap: '0.5rem' }}>
          {Array.from({ length: 10 }).map((_, idx) => {
            const vialNum = (selectedZone - 1) * 10 + (idx + 1);
            const vialId = `V${vialNum}`;
            const isBreachedVial = selectedZone === 2 && vialId === 'V17' && (telemetry?.zones?.find((z) => z.zone_id === 2)?.fuse_triggered);

            return (
              <div
                key={vialId}
                style={{
                  background: isBreachedVial ? 'rgba(239, 68, 68, 0.25)' : '#1e293b',
                  border: `1px solid ${isBreachedVial ? '#ef4444' : '#334155'}`,
                  borderRadius: '6px',
                  padding: '0.5rem 0.25rem',
                  textAlign: 'center',
                  transition: 'all 0.2s ease',
                }}
              >
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: isBreachedVial ? '#f87171' : '#e2e8f0' }}>{vialId}</div>
                <div style={{ fontSize: '0.625rem', color: isBreachedVial ? '#ef4444' : '#10b981', fontWeight: 600, marginTop: '2px' }}>
                  {isBreachedVial ? 'BREACHED' : 'INTACT'}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
