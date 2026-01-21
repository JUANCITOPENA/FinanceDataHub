import os
import sys
from git import Repo

# Agregar ruta correcta al sys.path para importar desde src
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'src'))

from market_analytics import MarketAnalytics

# Configuración
DATA_DIR = os.path.join(project_root, "data")

def force_sync():
    print("=== INICIANDO LIMPIEZA Y CARGA FORZADA (INTENTO 2) ===")
    
    # 1. Generar los datos
    engine = MarketAnalytics(DATA_DIR)
    success = engine.run_analysis()
    
    if not success:
        print("Error al generar los datos.")
        return

    # 2. Operaciones Git
    try:
        repo = Repo(project_root)
        print("GIT: Agregando archivos...")
        repo.git.add(all=True)
        
        # Verificar si hay cambios antes de hacer commit
        if repo.is_dirty() or repo.untracked_files:
            print("GIT: Creando commit...")
            repo.index.commit("FORCE RESET: Datos Financieros Maestros")
            
            print("GIT: Empujando a GitHub (Push)...")
            origin = repo.remote(name='origin')
            origin.push()
            print("=== ÉXITO: GITHUB ACTUALIZADO ===")
        else:
            print("GIT: Nada nuevo que subir. Asegurando push...")
            origin = repo.remote(name='origin')
            origin.push()

    except Exception as e:
        print(f"Error en Git: {e}")

if __name__ == "__main__":
    force_sync()