import React from 'react';
import { Clock, HeartPulse, AlertCircle } from 'lucide-react';

export default function CountdownPotencyCard({ forecast, potency }) {
  const z2Forecast = forecast?.zones?.find((z) => z.zone_id === 2);
  const timeToThreshold = z2Forecast?.time_to_threshold_sec ?? 1200;
  const isCritical = timeToThreshold < 300;

  const overallPotency = potency?.overall_potency_pct ?? 100.0;

  return (
    <div className="card-container" style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div className="card-header">
        <div className="card-title">
          <Clock size={18} color="#f59e0b" />
          <span>Time-to-Threshold & Potency</span>
        </div>
        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Kinetic Exposure</span>
      </div>

      {/* Countdown Card */}
      <div
        style={{
          background: isCritical ? 'rgba(239, 68, 68, 0.15)' : '#0f172a',
          border: `1px solid ${isCritical ? 'rgba(239, 68, 68, 0.4)' : '#1e293b'}`,
          borderRadius: '10px',
          padding: '1rem',
          marginBottom: '1rem',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.75rem', color: isCritical ? '#f87171' : '#94a3b8', fontWeight: 600 }}>
            ZONE 2 COUNTDOWN TO 12.0°C
          </span>
          {isCritical && <AlertCircle size={16} color="#ef4444" />}
        </div>

        <div style={{ fontSize: '2rem', fontWeight: 800, color: isCritical ? '#ef4444' : '#f8fafc', margin: '0.25rem 0' }}>
          {timeToThreshold === 0 ? 'BREACHED (0s)' : `${timeToThreshold} seconds`}
        </div>

        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
          {timeToThreshold < 300
            ? '⚡ Imminent thermal breach predicted. Actuation recommended.'
            : 'Zone operating within safe time buffer.'}
        </div>
      </div>

      {/* Potency Progress Gauge */}
      <div style={{ background: '#0f172a', borderRadius: '10px', padding: '1rem', border: '1px solid #1e293b' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8125rem', fontWeight: 600, color: '#e2e8f0' }}>
            <HeartPulse size={16} color="#10b981" />
            <span>Overall Drug Potency</span>
          </div>
          <span style={{ fontSize: '0.9375rem', fontWeight: 800, color: '#10b981' }}>{overallPotency}%</span>
        </div>

        {/* Progress Bar */}
        <div style={{ width: '100%', height: '8px', background: '#1e293b', borderRadius: '4px', overflow: 'hidden', marginBottom: '0.75rem' }}>
          <div
            style={{
              width: `${overallPotency}%`,
              height: '100%',
              background: overallPotency > 95 ? '#10b981' : overallPotency > 85 ? '#f59e0b' : '#ef4444',
              transition: 'width 0.3s ease',
            }}
          />
        </div>

        {/* Per-zone breakdown */}
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', color: '#94a3b8' }}>
          {potency?.zones?.map((z) => (
            <span key={z.zone_id}>
              Z{z.zone_id}: <strong>{z.potency_pct}%</strong>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
