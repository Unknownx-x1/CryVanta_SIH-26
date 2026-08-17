import React from 'react';
import { Activity, ShieldAlert, Thermometer, Droplets, Zap } from 'lucide-react';

export default function Header({ state, onSelectScenario }) {
  const { decision, potency, telemetry, scenario } = state;
  const riskLevel = decision?.risk_level || 'LOW';

  const riskBadgeClass = {
    LOW: 'badge-low',
    MEDIUM: 'badge-medium',
    HIGH: 'badge-high',
    CRITICAL: 'badge-critical',
  }[riskLevel] || 'badge-low';

  const scenarios = [
    { id: 'NORMAL', label: '1. Normal State' },
    { id: 'LOCALIZED_WARMING', label: '2. Localized Zone 2 Warming' },
    { id: 'COOLING_SUCCESS', label: '3. Intervention Cooling Success' },
    { id: 'COOLING_FAILURE', label: '4. Cooling Hardware Failure' },
  ];

  return (
    <header className="card-container" style={{ marginBottom: '1.5rem', borderRadius: '14px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        
        {/* Title & Core Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ background: '#0284c7', padding: '0.6rem', borderRadius: '10px', display: 'flex' }}>
            <Activity size={24} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <h1 style={{ fontSize: '1.35rem', fontWeight: 700, letterSpacing: '-0.02em' }}>PREDICTFUSE</h1>
              <span className={`badge ${riskBadgeClass}`}>RISK: {riskLevel}</span>
            </div>
            <p style={{ fontSize: '0.8125rem', color: '#94a3b8', marginTop: '2px' }}>
              Shipment ID: <strong style={{ color: '#cbd5e1' }}>#PF-8842</strong> | Cold-Chain Autonomous Safety System
            </p>
          </div>
        </div>

        {/* Ambient Metrics & Potency Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#0f172a', padding: '0.5rem 0.875rem', borderRadius: '8px', border: '1px solid #1e293b' }}>
            <Thermometer size={16} color="#06b6d4" />
            <div>
              <div style={{ fontSize: '0.6875rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>Ambient Temp</div>
              <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: '#f1f5f9' }}>{telemetry?.ambient?.temp_c ?? 6.2}°C</div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#0f172a', padding: '0.5rem 0.875rem', borderRadius: '8px', border: '1px solid #1e293b' }}>
            <Droplets size={16} color="#3b82f6" />
            <div>
              <div style={{ fontSize: '0.6875rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>Humidity</div>
              <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: '#f1f5f9' }}>{telemetry?.ambient?.humidity_pct ?? 41.0}%</div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#0f172a', padding: '0.5rem 0.875rem', borderRadius: '8px', border: '1px solid #1e293b' }}>
            <Zap size={16} color="#10b981" />
            <div>
              <div style={{ fontSize: '0.6875rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>Overall Potency</div>
              <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: '#10b981' }}>{potency?.overall_potency_pct ?? 100.0}%</div>
            </div>
          </div>

        </div>
      </div>

      {/* Demo Scenario Switcher Bar */}
      <div style={{ marginTop: '1rem', paddingTop: '0.875rem', borderTop: '1px solid #1e293b', display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600, marginRight: '0.25rem' }}>TEST SCENARIOS:</span>
        {scenarios.map((sc) => (
          <button
            key={sc.id}
            onClick={() => onSelectScenario(sc.id)}
            className={`btn ${scenario === sc.id ? 'btn-active' : 'btn-secondary'}`}
          >
            {sc.label}
          </button>
        ))}
      </div>
    </header>
  );
}
