import React, { useEffect } from 'react'
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap, useMapEvents } from 'react-leaflet'
import L from 'leaflet'

// Iconos personalizados
const iconoOrigen = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41]
})

const iconoDestino = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41]
})

const crearIconoNumero = (numero) => L.divIcon({
  html: `<div style="
    background: rgba(10, 132, 255, 0.95); 
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    color: white; 
    border-radius: 50%; 
    width: 28px; 
    height: 28px; 
    display: flex; 
    justify-content: center; 
    align-items: center; 
    font-weight: 700; 
    font-size: 14px;
    border: 2px solid rgba(255,255,255,0.9); 
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
  ">${numero}</div>`,
  className: '',
  iconSize: [28, 28],
  iconAnchor: [14, 14]
})

const iconoIncidencia = L.divIcon({
  html: `<div style="
    background: rgba(255, 149, 0, 0.95);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    border-radius: 50%;
    width: 28px;
    height: 28px;
    display: flex;
    justify-content: center;
    align-items: center;
    border: 2px solid rgba(255,255,255,0.9);
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    font-size: 14px;
  ">🚧</div>`,
  className: '',
  iconSize: [28, 28],
  iconAnchor: [14, 14]
})

// Ajusta el zoom del mapa para encuadrar la ruta completa
function AjustarVista({ ruta, paradas, almacen }) {
  const mapa = useMap()
  useEffect(() => {
    if (ruta && ruta.length > 1) {
      const limites = ruta.map(c => [c.lat, c.lng])
      mapa.fitBounds(limites, { padding: [50, 50] })
    } else if (!ruta && almacen) {
      const limites = [[almacen.lat, almacen.lng]]
      if (paradas && paradas.length > 0) {
        paradas.forEach(p => limites.push([p.coords.lat, p.coords.lng]))
        mapa.fitBounds(limites, { padding: [50, 50] })
      } else {
        mapa.setView(limites[0], 13)
      }
    }
  }, [ruta, paradas, almacen, mapa])
  return null
}

// Captura clics en el mapa
function CapturadorClics({ modoSeleccion, alSeleccionar }) {
  const mapa = useMap()

  useMapEvents({
    click(e) {
      if (!modoSeleccion) return
      alSeleccionar({ lat: e.latlng.lat, lng: e.latlng.lng })
    }
  })

  useEffect(() => {
    const contenedor = mapa.getContainer()
    contenedor.style.cursor = modoSeleccion ? 'crosshair' : ''
  }, [modoSeleccion, mapa])

  return null
}

export default function Mapa({ ruta, trazadoCalles, incidencias, modoSeleccion, alSeleccionar, paradas, almacen }) {
  const coordenadasRuta = trazadoCalles 
    ? trazadoCalles.map(c => [c.lat, c.lng]) 
    : (ruta ? ruta.map(c => [c.lat, c.lng]) : [])

  return (
    <MapContainer
      center={[37.3891, -5.9845]}
      zoom={12}
      style={{ flex: 1, height: '100vh' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <CapturadorClics
        modoSeleccion={modoSeleccion}
        alSeleccionar={alSeleccionar}
      />

      {/* Línea de la ruta óptima (Resplandor exterior) */}
      {coordenadasRuta.length > 1 && (
        <Polyline
          positions={coordenadasRuta}
          color="#0A84FF"
          weight={12}
          opacity={0.3}
          lineCap="round"
          lineJoin="round"
        />
      )}
      {/* Línea de la ruta óptima (Centro) */}
      {coordenadasRuta.length > 1 && (
        <Polyline
          positions={coordenadasRuta}
          color="#0A84FF"
          weight={5}
          opacity={1}
          lineCap="round"
          lineJoin="round"
        />
      )}

      {/* Marcadores de la ruta ya calculada */}
      {ruta && ruta.map((parada, i) => {
        const esAlmacen = i === 0 || i === ruta.length - 1
        const icono = esAlmacen
          ? (i === 0 ? iconoOrigen : iconoDestino)
          : crearIconoNumero(i)

        return (
          <Marker
            key={i}
            position={[parada.lat, parada.lng]}
            icon={icono}
          >
            <Popup>
              {esAlmacen ? '🏭 Almacén' : `📦 Parada ${i}`}<br />
              {parada.nombre}
            </Popup>
          </Marker>
        )
      })}

      {/* Marcadores previos a calcular la ruta */}
      {!ruta && almacen && (
        <Marker position={[almacen.lat, almacen.lng]} icon={iconoOrigen}>
          <Popup>
            🏭 Almacén Central<br />
            {almacen.direccion}
          </Popup>
        </Marker>
      )}

      {!ruta && paradas && paradas.map((parada, i) => (
        <Marker key={`p-${i}`} position={[parada.coords.lat, parada.coords.lng]} icon={crearIconoNumero(i + 1)}>
          <Popup>
            📦 {parada.nombre}<br />
            {parada.direccion.split(',')[0]}
          </Popup>
        </Marker>
      ))}

      {/* Marcadores de incidencias */}
      {incidencias && incidencias.map((inc, i) => (
        <Marker
          key={`inc-${i}`}
          position={[inc.lat, inc.lng]}
          icon={iconoIncidencia}
        >
          <Popup>
            <strong>⚠️ {inc.tipo.toUpperCase()}</strong><br />
            Carretera: {inc.carretera}<br />
            Municipio: {inc.municipio}<br />
            Gravedad: {'⚠️'.repeat(inc.gravedad)}
          </Popup>
        </Marker>
      ))}

      <AjustarVista ruta={ruta} paradas={paradas} almacen={almacen} />
    </MapContainer>
  )
}