import time
import os
import sys
from git import Repo, GitCommandError
from src.market_fetcher import MarketFetcher
from src.finance_manager import FinanceManager, InventoryManager

# CONFIGURACIÓN
# ¡¡¡ CAMBIA ESTO POR TU URL DE GITHUB !!!
GITHUB_REPO_URL = "https://github.com/TU_USUARIO/FinanceDataHub.git" 
INTERVALO_MINUTOS = 5
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_DIR, "data")

def git_push_changes():
    try:
        repo = Repo(PROJECT_DIR)
        
        # 1. Add all changes
        print("GIT: Agregando cambios...")
        repo.git.add('--all')
        
        # 2. Check if there are changes to commit
        if repo.is_dirty(untracked_files=True):
            # 3. Commit
            print("GIT: Haciendo commit...")
            repo.index.commit(f"Auto-update: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 4. Push
            # Nota: Esto requiere que tengas credenciales configuradas o SSH
            print("GIT: Subiendo a GitHub (Push)...")
            origin = repo.remote(name='origin')
            origin.push()
            print("GIT: ¡Éxito! Datos sincronizados.")
        else:
            print("GIT: No hay cambios nuevos.")
            
    except Exception as e:
        print(f"ERROR GIT: {e}")

def main():
    print("=== INICIANDO SISTEMA DE DATOS FINANCIEROS ===")
    print(f"Directorio: {PROJECT_DIR}")
    print(f"Intervalo: {INTERVALO_MINUTOS} minutos")
    
    # Inicializar módulos
    market = MarketFetcher(DATA_DIR)
    finance = FinanceManager(DATA_DIR)
    inventory = InventoryManager(DATA_DIR)
    
    while True:
        print(f"\n[{time.strftime('%H:%M:%S')}] Ejecutando ciclo de actualización...")
        
        # 1. Obtener Datos
        market.fetch_data()
        finance.generate_dummy_data()
        inventory.generate_dummy_data()
        
        # 2. Sincronizar con GitHub
        git_push_changes()
        
        # 3. Esperar
        print(f"Durmiendo {INTERVALO_MINUTOS} minutos...")
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == "__main__":
    main()
