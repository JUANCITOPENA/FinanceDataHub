import time
import os
import sys
from git import Repo
from src.market_analytics import MarketAnalytics

# CONFIGURACIÓN
GITHUB_REPO_URL = "https://github.com/JUANCITOPENA/FinanceDataHub.git" 
INTERVALO_MINUTOS = 5
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_DIR, "data")

def git_push_changes():
    try:
        repo = Repo(PROJECT_DIR)
        
        # Verificar si hay cambios reales
        if not repo.is_dirty(untracked_files=True):
            print("GIT: No hay cambios nuevos en los datos.")
            return

        print("GIT: Detectados nuevos datos. Sincronizando...")
        
        # Git Add
        repo.git.add(all=True)
        
        # Git Commit
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        repo.index.commit(f"Auto-Update: Financial Analytics {timestamp}")
        
        # Git Push
        origin = repo.remote(name='origin')
        origin.push()
        print(f"GIT: Push completado exitosamente a las {timestamp}")
            
    except Exception as e:
        print(f"ERROR GIT: {e}")

def main():
    print("=== SISTEMA DE INTELIGENCIA FINANCIERA (AUTO-BOT) ===")
    print(f"Monitor: {MarketAnalytics(DATA_DIR).tickers}")
    print(f"Frecuencia: {INTERVALO_MINUTOS} minutos")
    
    # Inicializar motor
    engine = MarketAnalytics(DATA_DIR)
    
    while True:
        print(f"\n[{time.strftime('%H:%M:%S')}] Iniciando escaneo de mercado...")
        
        # 1. Ejecutar Análisis Financiero
        success = engine.run_analysis()
        
        # 2. Subir a la nube si todo salió bien
        if success:
            git_push_changes()
        
        # 3. Esperar
        print(f"Sistema en espera... Próxima actualización en {INTERVALO_MINUTOS} min.")
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == "__main__":
    main()