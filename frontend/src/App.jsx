import React, { useState, useEffect } from 'react';
import { streamService } from './services/dataStream';
import Header from './components/Header';
import ZoneMatrix from './components/ZoneMatrix';
import ForecastChart from './components/ForecastChart';
import CountdownPotencyCard from './components/CountdownPotencyCard';
import RouteMap from './components/RouteMap';
import NarrationFeed from './components/NarrationFeed';

export default function App() {
  const [streamState, setStreamState] = useState(null);

  useEffect(() => {
    const unsubscribe = streamService.subscribe((data) => {
      setStreamState(data);
    });
    streamService.start(1500);

    return () => {
      unsubscribe();
      streamService.stop();
    };
  }, []);

  const handleSelectScenario = (scenario) => {
    streamService.setScenario(scenario);
  };

  if (!streamState) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0b0f19' }}>
        <div style={{ fontSize: '1rem', color: '#94a3b8', fontWeight: 600 }}>Initializing PredictFuse Dashboard...</div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '1.5rem 1rem' }}>
      
      {/* Header Bar & Scenario Switcher */}
      <Header state={streamState} onSelectScenario={handleSelectScenario} />

      {/* Spatial Zone & Vial Matrix Grid */}
      <ZoneMatrix telemetry={streamState.telemetry} forecast={streamState.forecast} />

      {/* Middle Grid: Forecast Chart + Time-to-Threshold */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
        <div style={{ gridColumn: 'span 2' }}>
          <ForecastChart telemetry={streamState.telemetry} forecast={streamState.forecast} />
        </div>
        <div>
          <CountdownPotencyCard forecast={streamState.forecast} potency={streamState.potency} />
        </div>
      </div>

      {/* Bottom Grid: Route Map + Narration & Actuation Feed */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        <div>
          <RouteMap state={streamState} />
        </div>
        <div>
          <NarrationFeed narration={streamState.narration} actuation={streamState.actuation} />
        </div>
      </div>

    </div>
  );
}
