import React, { useState, useEffect } from 'react';
import { TrendingUp } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

export default function ForecastChart({ telemetry, forecast }) {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (!telemetry?.timestamp) return;

    const timeLabel = new Date(telemetry.timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });

    const z1 = telemetry.zones?.find((z) => z.zone_id === 1)?.temp_c ?? 5.5;
    const z2 = telemetry.zones?.find((z) => z.zone_id === 2)?.temp_c ?? 5.8;
    const z3 = telemetry.zones?.find((z) => z.zone_id === 3)?.temp_c ?? 5.2;

    const z2Forecast = forecast?.zones?.find((z) => z.zone_id === 2)?.projected_temp_c ?? z2;

    const newPoint = {
      time: timeLabel,
      Zone1: z1,
      Zone2: z2,
      Zone3: z3,
      Zone2_Projected: z2Forecast,
    };

    setHistory((prev) => [...prev.slice(-14), newPoint]);
  }, [telemetry, forecast]);

  return (
    <div className="card-container" style={{ height: '100%' }}>
      <div className="card-header">
        <div className="card-title">
          <TrendingUp size={18} color="#06b6d4" />
          <span>Live Temperature & 10-Min Physics Forecast</span>
        </div>
        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Newton's Law Model</span>
      </div>

      <div style={{ width: '100%', height: 260 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={history} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 11 }} />
            <YAxis domain={[0, 20]} stroke="#64748b" tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '0.75rem' }}
            />
            <Legend wrapperStyle={{ fontSize: '0.75rem', paddingTop: '10px' }} />

            {/* Threshold Lines */}
            <ReferenceLine y={8.0} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: 'Target Max (8°C)', fill: '#f59e0b', fontSize: 10, position: 'insideTopRight' }} />
            <ReferenceLine y={12.0} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'Critical Limit (12°C)', fill: '#ef4444', fontSize: 10, position: 'insideTopRight' }} />

            {/* Zone Lines */}
            <Line type="monotone" dataKey="Zone1" stroke="#3b82f6" strokeWidth={2} dot={false} name="Zone 1" />
            <Line type="monotone" dataKey="Zone2" stroke="#f43f5e" strokeWidth={2.5} dot={false} name="Zone 2 (Active)" />
            <Line type="monotone" dataKey="Zone3" stroke="#10b981" strokeWidth={2} dot={false} name="Zone 3" />
            <Line type="monotone" dataKey="Zone2_Projected" stroke="#fb7185" strokeWidth={2} strokeDasharray="5 5" dot={false} name="Zone 2 Forecast" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
