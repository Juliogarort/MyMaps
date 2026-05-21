import subprocess
import sys
import os
import platform

ES_WINDOWS = platform.system() == "Windows"

RAIZ     = os.path.dirname(os.path.abspath(__file__))
FRONTEND = os.path.join(RAIZ, "frontend")

if ES_WINDOWS:
    UVICORN = os.path.join(RAIZ, "venv", "Scripts", "uvicorn.exe")
    NPM     = "npm.cmd"
else:
    UVICORN = os.path.join(RAIZ, "venv", "bin", "uvicorn")
    NPM     = "npm"


def verificar_entorno():
    if not os.path.exists(UVICORN):
        print("❌ Entorno virtual no encontrado.")
        print("   Ejecuta primero:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  (Mac/Linux)")
        print("   pip install -r requirements.txt")
        sys.exit(1)

    if not os.path.exists(os.path.join(FRONTEND, "node_modules")):
        print("❌ node_modules no encontrado.")
        print("   Ejecuta primero dentro de frontend/:")
        print("   npm install")
        sys.exit(1)


def arrancar():
    verificar_entorno()

    print("=" * 45)
    print("   MyMaps — Arrancando servicios")
    print("=" * 45)

    print("\n🚀 Arrancando backend  → http://localhost:8000")
    backend = subprocess.Popen(
        [UVICORN, "api.servidor:app", "--reload"],
        cwd=RAIZ
    )

    print("🌐 Arrancando frontend → http://localhost:5173")
    frontend = subprocess.Popen(
        [NPM, "run", "dev"],
        cwd=FRONTEND
    )

    print("\n✅ Todo arrancado.")
    print("   Backend:  http://localhost:8000")
    print("   Frontend: http://localhost:5173")
    print("   API docs: http://localhost:8000/docs")
    print("\n   Pulsa Ctrl+C para detener todo.\n")

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\n⛔ Deteniendo servicios...")
        backend.terminate()
        frontend.terminate()
        print("✅ Servicios detenidos.")


if __name__ == "__main__":
    arrancar()