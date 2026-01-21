import yfinance as yf
import pandas as pd
import numpy as np
import os

class MarketAnalytics:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.tickers = ["AAPL", "MSFT", "TSLA", "NVDA", "BTC-USD", "ETH-USD"]
        
    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def run_analysis(self):
        print("--- [ANALIZADOR FINANCIERO PRO] Iniciando Motor ---")
        try:
            # 1. Descarga Masiva (Datos Históricos)
            data = yf.download(self.tickers, period="2y", interval="1d", ignore_tz=True, progress=False, group_by='ticker', auto_adjust=True)
            
            if data.empty:
                print("ERROR: No data downloaded.")
                return False

            all_data = []

            # 2. Procesamiento Individual por Activo
            for ticker in self.tickers:
                try:
                    # Extraer dataframe de cada ticker
                    df = data[ticker].copy()
                    df = df.dropna()

                    # --- INDICADORES TÉCNICOS ---
                    
                    # 1. Retorno Diario (%)
                    df['Daily_Return_Pct'] = df['Close'].pct_change() * 100
                    
                    # 2. Medias Móviles (Tendencias)
                    df['SMA_20'] = df['Close'].rolling(window=20).mean()   # Corto plazo
                    df['SMA_50'] = df['Close'].rolling(window=50).mean()   # Medio plazo
                    df['SMA_200'] = df['Close'].rolling(window=200).mean() # Largo plazo
                    
                    # 3. Volatilidad (Riesgo a 20 días)
                    df['Volatility_20d'] = df['Close'].pct_change().rolling(window=20).std() * np.sqrt(20) * 100
                    
                    # 4. RSI (Fuerza Relativa)
                    df['RSI_14'] = self.calculate_rsi(df['Close'])

                    # 5. Señal de Trading (Estrategia Simple Cruce de Medias)
                    # Compra si la tendencia corta (50) cruza arriba de la larga (200) -> "Golden Cross"
                    # Venta si cruza abajo -> "Death Cross"
                    # Neutral si no hay cruce claro
                    df['Signal'] = np.where(df['SMA_50'] > df['SMA_200'], 'COMPRA (Bullish)', 'VENTA (Bearish)')
                    
                    # Añadir columna identificadora
                    df['Ticker'] = ticker
                    df['Date'] = df.index
                    
                    # Reset index para unir todo
                    all_data.append(df)
                    print(f"-> Procesado: {ticker}")
                    
                except KeyError:
                    print(f"WARN: Datos incompletos para {ticker}")

            # 3. Consolidación
            final_df = pd.concat(all_data)
            
            # Limpieza final de columnas
            cols = ['Date', 'Ticker', 'Close', 'Volume', 'Daily_Return_Pct', 'RSI_14', 'Volatility_20d', 'SMA_50', 'SMA_200', 'Signal']
            final_df = final_df[cols].round(2)
            
            # Guardar CSV Maestro
            output_path = os.path.join(self.output_dir, "financial_analysis_master.csv")
            final_df.to_csv(output_path, index=False)
            
            print(f"ÉXITO: Análisis completado. Guardado en {output_path}")
            return True
            
        except Exception as e:
            print(f"ERROR CRÍTICO: {e}")
            import traceback
            traceback.print_exc()
            return False
