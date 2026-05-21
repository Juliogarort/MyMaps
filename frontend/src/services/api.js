import axios from 'axios'

const cliente = axios.create({
  baseURL: 'http://localhost:8000'
})

/**
 * Calcula la ruta óptima enviando las paradas al backend.
 * @param {Object} almacen - Objeto del almacén con nombre, direccion, lat, lng
 * @param {Array} paradas - Lista de paradas con nombre, direccion, lat, lng
 */
export const calcularRuta = async (almacen, paradas) => {
  const { data } = await cliente.post('/ruta', {
    almacen,
    paradas
  })
  return data
}

/**
 * Obtiene las incidencias de tráfico activas en Sevilla.
 */
export const obtenerIncidencias = async () => {
  const { data } = await cliente.get('/incidencias')
  return data
}

/**
 * Obtiene el clima actual en Sevilla.
 */
export const obtenerClima = async () => {
  const { data } = await cliente.get('/clima')
  return data
}