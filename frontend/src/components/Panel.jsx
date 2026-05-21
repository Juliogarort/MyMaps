import React, { useState, useEffect } from 'react'
import './Panel.css'

// Obtener dirección a partir de coordenadas
const obtenerDireccionDeCoords = async (lat, lng) => {
  try {
    const res = await fetch(`http://localhost:8000/reversa?lat=${lat}&lng=${lng}`)
    if (!res.ok) return null
    const dato = await res.json()
    return dato.direccion
  } catch (e) {
    return null
  }
}

// Busca direcciones usando Nominatim limitado a Sevilla
const buscarEnSevilla = async (texto) => {
  const res = await fetch(`http://localhost:8000/geocodificar?direccion=${encodeURIComponent(texto)}`)
  if (!res.ok) return []
  const dato = await res.json()
  return [{ lat: dato.lat, lon: dato.lng, display_name: dato.nombre }]
}

// Componente de búsqueda reutilizable
function BuscadorDireccion({ etiqueta, emoji, alSeleccionar, modoClicActivo, alActivarClic, valorExterno }) {
  const [texto, setTexto] = useState('')
  const [sugerencias, setSugerencias] = useState([])
  const [buscando, setBuscando] = useState(false)
  const [seleccionado, setSeleccionado] = useState(null)

  useEffect(() => {
    if (valorExterno) {
      setTexto(valorExterno)
      setSeleccionado(valorExterno)
    }
  }, [valorExterno])

  useEffect(() => {
    const timeout = setTimeout(async () => {
      if (texto.length >= 3 && texto !== seleccionado) {
        setBuscando(true)
        try {
          const resultados = await buscarEnSevilla(texto)
          setSugerencias(resultados)
        } finally {
          setBuscando(false)
        }
      } else {
        setSugerencias([])
      }
    }, 600)
    return () => clearTimeout(timeout)
  }, [texto, seleccionado])

  const manejarCambio = (valor) => {
    setTexto(valor)
    setSeleccionado(null)
  }

  const elegirSugerencia = (lugar) => {
    const coords = { lat: parseFloat(lugar.lat), lng: parseFloat(lugar.lon) }
    const nombre = lugar.display_name.split(',').slice(0, 2).join(',')
    alSeleccionar(coords, nombre)
    if (etiqueta === 'Nueva parada') {
      setTexto('')
      setSeleccionado(null)
    } else {
      setTexto(nombre)
      setSeleccionado(nombre)
    }
    setSugerencias([])
  }

  return (
    <div className="panel-seccion">
      <h3>{emoji} {etiqueta}</h3>
      <div className="buscador">
        <input
          type="text"
          placeholder={`Buscar ${etiqueta.toLowerCase()}...`}
          value={texto}
          onChange={e => manejarCambio(e.target.value)}
        />
        {buscando && <span className="buscando">Buscando...</span>}
      </div>
      {sugerencias.length > 0 && (
        <ul className="sugerencias">
          {sugerencias.map((lugar, i) => (
            <li key={i} onClick={() => elegirSugerencia(lugar)}>
              {lugar.display_name.split(',').slice(0, 3).join(',')}
            </li>
          ))}
        </ul>
      )}
      <button
        className={`btn-mapa ${modoClicActivo ? 'activo' : ''}`}
        onClick={alActivarClic}
      >
        {modoClicActivo ? '🖥️ Haz clic en el mapa...' : '📌 Seleccionar en el mapa'}
      </button>
      {seleccionado && <p className="seleccionado">✅ {seleccionado}</p>}
    </div>
  )
}

export default function Panel({ alCalcular, resultado, cargando, modoSeleccion, alActivarClic, coordsSeleccionadas, paradas, agregarParada, eliminarParada, almacen }) {
  useEffect(() => {
    const procesarCoords = async () => {
      if (coordsSeleccionadas) {
        const { tipo, coords } = coordsSeleccionadas
        const dir = await obtenerDireccionDeCoords(coords.lat, coords.lng)
        const nombre = dir || `${coords.lat.toFixed(4)}, ${coords.lng.toFixed(4)}`
        
        if (tipo === 'parada') {
          agregarParada(coords, nombre)
        }
      }
    }
    procesarCoords()
  }, [coordsSeleccionadas])

  const manejarCalculo = () => {
    if (paradas.length === 0) { alert('Añade al menos una parada'); return }
    alCalcular(almacen, paradas.map(p => ({
      nombre: p.nombre,
      direccion: p.direccion,
      lat: p.coords.lat,
      lng: p.coords.lng
    })))
  }

  return (
    <aside className="panel">
      <div className="panel-cabecera">
        <h1>🗺️ MyMaps</h1>
        <p>Rutas Inteligentes con IA</p>
      </div>

      {/* Almacén Fijo */}
      <div className="panel-seccion">
        <h3>🏭 Almacén</h3>
        <div className="almacen-fijo" style={{ padding: '10px', background: '#f5f5f5', borderRadius: '8px', border: '1px solid #ddd' }}>
          <p style={{ margin: '0 0 5px 0' }}><strong>{almacen.nombre}</strong></p>
          <p style={{ margin: 0, fontSize: '0.9em', color: '#666' }}>{almacen.direccion}</p>
        </div>
      </div>

      {/* Paradas */}
      <BuscadorDireccion
        etiqueta="Nueva parada"
        emoji="📦"
        alSeleccionar={agregarParada}
        modoClicActivo={modoSeleccion === 'parada'}
        alActivarClic={() => alActivarClic('parada')}
      />

      {/* Lista de paradas añadidas */}
      {paradas.length > 0 && (
        <div className="panel-seccion">
          <h3>📋 Paradas ({paradas.length})</h3>
          <ul className="lista-paradas">
            {paradas.map((p, i) => (
              <li key={i}>
                <span>{p.direccion.split(',')[0]}</span>
                <button onClick={() => eliminarParada(i)}>✕</button>
              </li>
            ))}
          </ul>
        </div>
      )}

      <button
        className="btn-calcular"
        onClick={manejarCalculo}
        disabled={cargando || paradas.length === 0}
      >
        {cargando ? '⏳ Calculando...' : '🔍 Calcular Ruta Óptima'}
      </button>

      {/* Resultado */}
      {resultado && (
        <div className="resultado">
          <h3>📊 Resumen de Ruta</h3>
          <div className="resultado-grid">
            <span>Distancia Total:</span>
            <strong>{resultado.coste_total} km</strong>
            <span>Paradas:</span>
            <strong>{resultado.ruta_ordenada.length - 2}</strong>
          </div>
          
          <div className="justificacion">
            <strong>🧠 Lógica (Prolog):</strong>
            <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.8rem', background: 'rgba(0,0,0,0.2)', padding: '8px', borderRadius: '6px' }}>{resultado.justificacion}</pre>
          </div>
        </div>
      )}
    </aside>
  )
}