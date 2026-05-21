import React, { useState, useEffect, useRef } from 'react'
import Mapa from './components/mapa'
import Panel from './components/Panel'
import { calcularRuta, obtenerIncidencias } from './services/api'

const ALMACEN_FIJO = {
  nombre: 'Almacén Central',
  direccion: 'Ilerna Sevilla',
  lat: 37.40689618341476,
  lng: -5.9298026794070875
}

export default function App() {
  const [ruta, setRuta]               = useState(null)
  const [incidencias, setIncidencias] = useState([])
  const [cargando, setCargando]       = useState(false)
  const [resultado, setResultado]     = useState(null)
  const [modoSeleccion, setModoSeleccion] = useState(null)
  const [paradas, setParadas]         = useState([])
  const [trazadoCalles, setTrazadoCalles] = useState(null)

  useEffect(() => {
    obtenerIncidencias()
      .then(setIncidencias)
      .catch(console.error)
  }, [])

  const activarClic = (tipo) => {
    setModoSeleccion(prev => prev === tipo ? null : tipo)
  }

  const [coordsSeleccionadas, setCoordsSeleccionadas] = useState(null)

  const alSeleccionarEnMapa = (coords) => {
    setCoordsSeleccionadas({ tipo: modoSeleccion, coords, id: Date.now() })
    setModoSeleccion(null)
  }

  const agregarParada = (coords, nombre) => {
    setParadas(prev => [...prev, {
      nombre: `Parada ${prev.length + 1}`,
      direccion: nombre,
      coords
    }])
    setRuta(null) 
    setTrazadoCalles(null)
    setResultado(null)
  }

  const eliminarParada = (indice) => {
    setParadas(prev => prev.filter((_, i) => i !== indice))
    setRuta(null)
    setTrazadoCalles(null)
    setResultado(null)
  }

  const manejarCalculo = async (almacen, paradas) => {
    setCargando(true)
    try {
      const data = await calcularRuta(almacen, paradas)
      setRuta(data.ruta_ordenada)
      setTrazadoCalles(data.trazado_calles || data.ruta_ordenada)
      setIncidencias(data.incidencias)
      setResultado(data)
    } catch (error) {
      alert('Error al calcular la ruta. ¿Está el backend activo en localhost:8000?')
      console.error(error)
    } finally {
      setCargando(false)
    }
  }

  return (
    <>
      <Panel
        alCalcular={manejarCalculo}
        resultado={resultado}
        cargando={cargando}
        modoSeleccion={modoSeleccion}
        alActivarClic={activarClic}
        coordsSeleccionadas={coordsSeleccionadas}
        paradas={paradas}
        agregarParada={agregarParada}
        eliminarParada={eliminarParada}
        almacen={ALMACEN_FIJO}
      />
      <Mapa
        ruta={ruta}
        trazadoCalles={trazadoCalles}
        incidencias={incidencias}
        modoSeleccion={modoSeleccion}
        alSeleccionar={alSeleccionarEnMapa}
        paradas={paradas}
        almacen={ALMACEN_FIJO}
      />
    </>
  )
}