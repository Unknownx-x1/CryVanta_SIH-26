import React from 'react';
import { MessageSquareText, Cpu, Fan, Volume2 } from 'lucide-react';

export default function NarrationFeed({ narration, actuation }) {
  const briefing = narration?.briefing || 'System operating under normal environmental conditions.';
  const peltierState = actuation?.peltier_state || 'OFF';
  const ventState = actuation?.servo_vent_position || 'CLOSED';
  const buzzerState = actuation?.alert_buzzer || 'OFF';

  return (
    <div className="card-container" style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div className="card-header">
        <div className="card-title">
          <MessageSquareText size={18} color="#a855f7" />
          <span>LLM System Briefing & Actuation Status</span>
        </div>
        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Grounded JSON Feed</span>
      </div>

      {/* Narration Text Box */}
      <div
        style={{
          background: '#0f172a',
          border: '1px solid #1e293b',
          borderRadius: '10px',
          padding: '0.875rem',
          marginBottom: '1rem',
          fontSize: '0.8125rem',
          color: '#e2e8f0',
          lineHeight: '1.5',
        }}
      >
        <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: '#a855f7', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
          BRIEFING NARRATION
        </div>
        <p style={{ margin: 0 }}>"{briefing}"</p>
      </div>

      {/* Actuation Status Panel */}
      <div style={{ background: '#0f172a', borderRadius: '10px', padding: '0.875rem', border: '1px solid #1e293b' }}>
        <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
          PHYSICAL ACTUATION STATUS (ESP32)
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
          {/* Peltier */}
          <div style={{ background: '#1e293b', padding: '0.5rem', borderRadius: '6px', textAlign: 'center' }}>
            <Cpu size={14} color={peltierState === 'ON' ? '#06b6d4' : '#64748b'} style={{ marginBottom: '2px' }} />
            <div style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>Peltier</div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: peltierState === 'ON' ? '#06b6d4' : '#64748b' }}>
              {peltierState}
            </div>
          </div>

          {/* Servo Vent */}
          <div style={{ background: '#1e293b', padding: '0.5rem', borderRadius: '6px', textAlign: 'center' }}>
            <Fan size={14} color={ventState === 'OPEN' ? '#10b981' : '#64748b'} style={{ marginBottom: '2px' }} />
            <div style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>Servo Vent</div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: ventState === 'OPEN' ? '#10b981' : '#64748b' }}>
              {ventState}
            </div>
          </div>

          {/* Buzzer */}
          <div style={{ background: '#1e293b', padding: '0.5rem', borderRadius: '6px', textAlign: 'center' }}>
            <Volume2 size={14} color={buzzerState === 'ON' ? '#ef4444' : '#64748b'} style={{ marginBottom: '2px' }} />
            <div style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>Buzzer Alarm</div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: buzzerState === 'ON' ? '#ef4444' : '#64748b' }}>
              {buzzerState}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
