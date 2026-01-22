import os
import sys
import shutil
import time

# --- PASO 1: CONFIGURAR GIT ANTES DE CUALQUIER OTRA COSA ---
# Esto debe ir arriba de todo para que GitPython no falle al importar
if os.name == 'nt': # Si es Windows
    git_path = shutil.which('git')
    if git_path:
        os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = git_path
    else:
        # Rutas manuales si no está en el PATH
        possible_paths = [
            r"C:\Program Files\Git\cmd\git.exe",
            r"C:\Program Files (x86)\Git\cmd\git.exe"
        ]
        for p in possible_paths:
            if os.path.exists(p):
                os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = p
                break

# --- PASO 2: AHORA SÍ IMPORTAR LOS MÓDULOS ---
try:
    from git import Repo
except ImportError as e:
    print("Error crítico: No se pudo inicializar Git. Asegúrate de que Git esté instalado.")
    sys.exit(1)

# Agregar ruta para importar desde src
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'src'))

from market_analytics import MarketAnalytics

# CONFIGURACIÓN
INTERVALO_MINUTOS = 5
DATA_DIR = os.path.join(project_root, "data")

def git_push_changes():
    try:
        repo = Repo(project_root)
        
        if not repo.is_dirty(untracked_files=True):
            print("GIT: No hay cambios nuevos para subir.")
            return

        print("GIT: Detectados nuevos datos. Sincronizando...")
        repo.git.add(all=True)
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        repo.index.commit(f"Auto-update: {timestamp}")
        
        origin = repo.remote(name='origin')
        
        # Pull para evitar el error de "failed to push some refs"
        print("GIT: Sincronizando con remoto (Pull)...")
        origin.pull(rebase=True)
        
        # Push final
        print("GIT: Subiendo a GitHub (Push)...")
        origin.push()
        print(f"GIT: Sincronización exitosa a las {timestamp}")

    except Exception as e:
        print(f"GIT ERROR: {e}")

def main():
    # --- CORRECCIÓN: Pasar DATA_DIR a la clase ---
    analytics = MarketAnalytics(output_dir=DATA_DIR)
    
    while True:
        print(f"\n[{time.strftime('%H:%M:%S')}] Iniciando escaneo de mercado...")
        
        try:
            # 1. Ejecutar análisis (el método en tu clase se llama run_analysis)
            success = analytics.run_analysis()
            
            # 2. Si se generó el CSV con éxito, sincronizar con Git
            if success:
                git_push_changes()
            
        except Exception as e:
            print(f"ERROR EN EL CICLO: {e}")

        print(f"Sistema en espera... Próxima actualización en {INTERVALO_MINUTOS} min.")
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == "__main__":
    print("=== SISTEMA DE INTELIGENCIA FINANCIERA (AUTO-BOT) ===")
    print("Monitor: ['AAPL', 'MSFT', 'TSLA', 'NVDA', 'BTC-USD', 'ETH-USD']")
    main()