# MyMaps 🗺️
**Sistema Inteligente de Optimización Dinámica de Rutas Logísticas usando IA**

Calcula la ruta óptima de reparto en Sevilla teniendo en cuenta:
- Incidencias de tráfico en tiempo real (API DGT)
- Condiciones meteorológicas (API OpenWeatherMap)
- Algoritmo TSP con Google OR-Tools
- Mapa interactivo con React + Leaflet

---

## Requisitos previos

- Python 3.11 o superior
- Node.js 18 o superior
- Cuenta gratuita en [openweathermap.org](https://openweathermap.org) para la API key del clima

---

## Instalación

**1. Clona o descarga el proyecto y entra en la carpeta:**
```bash
cd MyMaps
```

**2. Crea el entorno virtual de Python:**
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

**4. Instala las dependencias Python:**
```bash
pip install -r requirements.txt
```

**5. Configura las variables de entorno:**
```bash
cp .env.example .env
```
Abre `.env` y añade tu API key de OpenWeatherMap:
```
OPENWEATHER_API_KEY=tu_api_key_aqui
```

**6. Instala las dependencias del frontend:**
```bash
cd frontend
npm install
cd ..
```

---

## Arranque

### Opción A — Un solo comando (recomendado)
```bash
python arrancar.py
```
Arranca el backend y el frontend automáticamente. Funciona en Mac y Windows.

### Opción B — Por separado

**Terminal 1 — Backend:**
```bash
source venv/bin/activate   # Mac/Linux
uvicorn api.servidor:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Abre el navegador en: `http://localhost:5173`

---

## Uso

1. Escribe la dirección del **almacén** en el panel izquierdo
2. Añade las **paradas de entrega** una por una
3. Pulsa **Calcular Ruta Óptima**
4. El sistema calcula la ruta óptima teniendo en cuenta tráfico y clima en tiempo real

---

## Estructura del proyecto

```
MyMaps/
├── arrancar.py                # Arranca backend y frontend juntos
├── calcular.py                # Script de rutas por consola
├── requirements.txt           # Dependencias Python
├── .env.example               # Plantilla de variables de entorno
├── apis/
│   ├── clima.py               # Conexión OpenWeatherMap
│   ├── dgt.py                 # Conexión API DGT
│   ├── doverpass.py           # Conexión incidentes sevilla centro
│   └── geocodificador.py      # Conversión dirección → coordenadas
├── sevilla/
│   ├── reglas.py              # Reglas de penalización
│   └── tsp.py                 # Algoritmo TSP con OR-Tools
├── api/
│   └── servidor.py            # API REST con FastAPI
└── frontend/
    └── src/
        ├── App.jsx
        ├── components/
        │   ├── Mapa.jsx
        │   ├── Panel.jsx
        │   └── Panel.css
        └── services/
            └── api.js
```

---

## Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/estado` | Verifica que el servidor está activo |
| GET | `/clima` | Clima actual en Sevilla |
| GET | `/incidencias` | Incidencias de tráfico en Sevilla |
| GET | `/geocodificar?direccion=...` | Convierte dirección a coordenadas |
| POST | `/ruta` | Calcula la ruta óptima |

Documentación interactiva: `http://localhost:8000/docs`

---

## Si mueves la carpeta del proyecto

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
| Python 3.11 | Backend |
| FastAPI | API REST |
| OR-Tools | Algoritmo TSP |
| Nominatim (OSM) | Geocodificación |
| API DGT | Tráfico en tiempo real |
| OpenWeatherMap | Clima en tiempo real |
| React + Vite | Frontend |
| Leaflet | Mapa interactivo |

---

## ⚠️ Seguridad — qué NO subir a GitHub

| Archivo/Carpeta | Motivo |
|----------------|--------|
| `.env` | Contiene tu API key |
| `venv/` | Entorno virtual Python |
| `frontend/node_modules/` | Dependencias Node |
| `ruta_*.csv` | Archivos generados |
