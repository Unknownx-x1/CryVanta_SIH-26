import React from 'react';
import { MapPin, Navigation, CornerUpRight } from 'lucide-react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';

// Custom Leaflet Markers
const currentPosIcon = L.divIcon({
  className: 'custom-map-icon',
  html: `<div style="background:#0284c7; width:16px; height:16px; border-radius:50%; border:3px solid #ffffff; box-shadow:0 0 10px #0284c7;"></div>`,
});

const coldDepotIcon = L.divIcon({
  className: 'custom-map-icon',
  html: `<div style="background:#f59e0b; width:16px; height:16px; border-radius:50%; border:3px solid #ffffff; box-shadow:0 0 10px #f59e0b;"></div>`,
});

export default function RouteMap({ state }) {
  const { decision, telemetry, primaryRoute, alternateRouteB } = state;
  const isRerouted = decision?.recommended_route === 'ALTERNATE_ROUTE_B';
  const currentPos = [telemetry?.gps?.lat ?? 12.9716, telemetry?.gps?.lng ?? 77.5946];

  return (
    <div className="card-container" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div className="card-header">
        <div className="card-title">
          <Navigation size={18} color="#38bdf8" />
          <span>GPS Route & Predictive Rerouting</span>
        </div>
        <span className={`badge ${isRerouted ? 'badge-high' : 'badge-low'}`}>
          {isRerouted ? 'DYNAMIC REROUTE ACTIVE' : 'PRIMARY ROUTE'}
        </span>
      </div>

      {/* Reroute Alert Callout */}
      {isRerouted && (
        <div
          style={{
            background: 'rgba(245, 158, 11, 0.15)',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            borderRadius: '8px',
            padding: '0.5rem 0.75rem',
            marginBottom: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            fontSize: '0.75rem',
            color: '#f59e0b',
          }}
        >
          <CornerUpRight size={16} />
          <span>
            <strong>Predictive Reroute Triggered:</strong> Diverting shipment to Cold Storage Depot B (ETA: 12 mins).
          </span>
        </div>
      )}

      {/* Leaflet Map */}
      <div style={{ flex: 1, minHeight: 220, borderRadius: '8px', overflow: 'hidden', border: '1px solid #1e293b' }}>
        <MapContainer center={currentPos} zoom={12} style={{ width: '100%', height: '100%', background: '#0f172a' }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Current GPS Marker */}
          <Marker position={currentPos} icon={currentPosIcon}>
            <Popup>
              <strong>Shipment #PF-8842</strong>
              <br />
              Current GPS: {currentPos[0].toFixed(4)}, {currentPos[1].toFixed(4)}
            </Popup>
          </Marker>

          {/* Cold Depot B Marker if rerouted */}
          {isRerouted && (
            <Marker position={[12.9550, 77.5750]} icon={coldDepotIcon}>
              <Popup>
                <strong>Cold Storage Depot B</strong>
                <br />
                Refrigerated Warehouse (Temp: 4.0°C)
              </Popup>
            </Marker>
          )}

          {/* Primary Route Polyline (Blue) */}
          <Polyline positions={primaryRoute} color="#0284c7" weight={4} opacity={isRerouted ? 0.3 : 0.8} dashArray={isRerouted ? '5 5' : null} />

          {/* Alternate Route B Polyline (Amber/Red) */}
          {isRerouted && <Polyline positions={alternateRouteB} color="#f59e0b" weight={5} opacity={0.9} />}
        </MapContainer>
      </div>
    </div>
  );
}
