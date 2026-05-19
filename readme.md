# MyMaps 🗺️
**Sistema Inteligente de Optimización Dinámica de Rutas Logísticas usando IA**

Calcula la ruta óptima de reparto en Sevilla teniendo en cuenta:
- Incidencias de tráfico en tiempo real (API DGT)
- Condiciones meteorológicas (API OpenWeatherMap)
- Algoritmo TSP con Google OR-Tools

---

## Requisitos previos

- Python 3.11 o superior
- Cuenta gratuita en [openweathermap.org](https://openweathermap.org) para obtener la API key del clima

---

## Instalación

**1. Clona o descarga el proyecto y entra en la carpeta:**
```bash
cd MyMaps
```

**2. Crea el entorno virtual:**
```bash
python -m venv venv
```

**3. Actívalo:**
```bash
# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**4. Instala las dependencias:**
```bash
pip install -r requirements.txt
```

**5. Configura las variables de entorno:**
```bash
cp .env.example .env
```
Abre el archivo `.env` y añade tu API key de OpenWeatherMap:
```
OPENWEATHER_API_KEY=tu_api_key_aqui
```
La API de la DGT no necesita key, es pública.

---

## Uso

### Calcular una ruta por consola
```bash
python calcular.py
```
El programa te pedirá cuántas paradas tienes y las direcciones una por una.
Al terminar genera un CSV con el resultado.

### Arrancar el servidor API
```bash
uvicorn api.servidor:app --reload
```
El servidor estará disponible en `http://localhost:8000`

Endpoints disponibles:
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/estado` | Verifica que el servidor está activo |
| GET | `/clima` | Clima actual en Sevilla |
| GET | `/incidencias` | Incidencias de tráfico en Sevilla |
| POST | `/ruta` | Calcula la ruta óptima |

Documentación interactiva: `http://localhost:8000/docs`

---

## Scripts de prueba

Verifica que cada componente funciona por separado:

```bash
python probar_clima.py          # Prueba la API del tiempo
python probar_dgt.py            # Prueba la API de la DGT
python probar_geocodificador.py # Prueba el geocodificador
python probar_reglas.py         # Prueba el sistema de reglas
python probar_tsp.py            # Prueba el algoritmo TSP
```

---

## Estructura del proyecto

```
MyMaps/
├── .env.example               # Plantilla de variables de entorno
├── requirements.txt           # Dependencias Python
├── calcular.py                # Script principal por consola
├── probar_clima.py            # Test API clima
├── probar_dgt.py              # Test API DGT
├── probar_geocodificador.py   # Test geocodificador
├── probar_reglas.py           # Test sistema de reglas
├── probar_tsp.py              # Test algoritmo TSP
├── apis/
│   ├── clima.py               # Conexión OpenWeatherMap
│   ├── dgt.py                 # Conexión API DGT
│   └── geocodificador.py      # Conversión dirección → coordenadas
├── sevilla/
│   ├── reglas.py              # Reglas de penalización por tráfico y clima
│   └── tsp.py                 # Algoritmo TSP con OR-Tools
└── api/
    └── servidor.py            # API REST con FastAPI
```

---

## Si mueves la carpeta del proyecto

El entorno virtual tiene rutas absolutas, hay que recrearlo:

```bash
rm -rf venv
python -m venv venv
source venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
```

---

## Tecnologías

| Tecnología | Uso |
|-----------|-----|
| Python 3.11 | Lenguaje principal |
| FastAPI | API REST |
| OR-Tools | Algoritmo TSP |
| Nominatim (OSM) | Geocodificación de direcciones |
| API DGT | Incidencias de tráfico en tiempo real |
| OpenWeatherMap | Clima en tiempo real |