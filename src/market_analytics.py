import yfinance as yf
import pandas as pd
import numpy as np
import os
import datetime

class MarketAnalytics:
    """
    Motor de análisis financiero que descarga datos de Yahoo Finance,
    calcula indicadores técnicos y genera un dataset consolidado para Power BI.
    """
    def __init__(self, output_dir):
        self.output_dir = output_dir
        # Tickers solicitados explícitamente por el usuario
        self.tickers = ["AAPL", "MSFT", "TSLA", "NVDA", "BTC-USD", "ETH-USD"]
        
    def calculate_rsi(self, series, period=14):
        """Calcula el Índice de Fuerza Relativa (RSI)."""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def run_analysis(self):
        print(f"[{datetime.datetime.now()}] --- INICIANDO ANÁLISIS DE MERCADO ---")
        try:
            # 1. Descarga Masiva de Datos
            # Se descargan 2 años de historia para tener suficiente data para las medias móviles largas (200 días)
            print(f"Descargando datos para: {self.tickers}...")
            data = yf.download(
                self.tickers, 
                period="2y", 
                interval="1d", 
                group_by='ticker', 
                auto_adjust=True, 
                progress=False,
                threads=True
            )
            
            if data.empty:
                print("ERROR: No se descargaron datos. Verifique su conexión a internet.")
                return False

            all_data = []

            # 2. Procesamiento de cada Ticker
            for ticker in self.tickers:
                try:
                    # Manejo de estructura de datos de yfinance
                    # Si solo hay 1 ticker, la estructura es diferente (no hay nivel superior de columnas)
                    if len(self.tickers) == 1:
                        df = data.copy()
                    else:
                        if ticker not in data.columns.levels[0]:
                            print(f"WARN: No se encontraron datos para {ticker}")
                            continue
                        df = data[ticker].copy()

                    df = df.dropna()

                    if df.empty:
                        print(f"WARN: Datos vacíos para {ticker}")
                        continue

                    # --- CÁLCULO DE KPIs E INDICADORES ---
                    
                    # a) Retornos
                    df['Daily_Return_Pct'] = df['Close'].pct_change() * 100
                    df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
                    
                    # b) Tendencias (Medias Móviles)
                    df['SMA_20'] = df['Close'].rolling(window=20).mean()   # Corto Plazo
                    df['SMA_50'] = df['Close'].rolling(window=50).mean()   # Medio Plazo
                    df['SMA_200'] = df['Close'].rolling(window=200).mean() # Largo Plazo (Tendencia Secular)
                    
                    # c) Volatilidad Histórica (Anualizada basada en ventana de 20 días)
                    # Volatilidad = Desv. Est. de retornos * Raíz cuadrada de (252 días de trading)
                    df['Volatility_Annualized'] = df['Daily_Return_Pct'].rolling(window=20).std() * np.sqrt(252)
                    
                    # d) RSI (Oscilador de Momento)
                    df['RSI_14'] = self.calculate_rsi(df['Close'])

                    # e) Señales de Trading (Cruce Dorado / Cruce de la Muerte)
                    df['Signal_Trend'] = np.where(df['SMA_50'] > df['SMA_200'], 'BULLISH (Alcista)', 'BEARISH (Bajista)')
                    
                    # f) Metadatos para Power BI
                    df['Ticker'] = ticker
                    df['Date'] = df.index
                    df['Last_Updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Reset index para que 'Date' sea una columna normal y no el índice
                    # Esto facilita la lectura en Power BI
                    all_data.append(df)
                    print(f"-> Procesado OK: {ticker}")
                    
                except KeyError as e:
                    print(f"ERROR procesando {ticker}: {e}")
                except Exception as e:
                    print(f"ERROR inesperado en {ticker}: {e}")

            # 3. Consolidación y Exportación
            if not all_data:
                print("ERROR: No se procesó ningún dato correctamente.")
                return False

            final_df = pd.concat(all_data)
            
            # Selección y orden de columnas final
            cols = [
                'Date', 'Ticker', 'Close', 'Open', 'High', 'Low', 'Volume', 
                'Daily_Return_Pct', 'Volatility_Annualized', 'RSI_14', 
                'SMA_20', 'SMA_50', 'SMA_200', 'Signal_Trend', 'Last_Updated'
            ]
            
            # Aseguramos que existan las columnas (por si alguna falló, aunque no debería)
            cols_to_export = [c for c in cols if c in final_df.columns]
            final_df = final_df[cols_to_export].round(4) # Redondeo a 4 decimales para precisión financiera
            
            # Crear directorio si no existe
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

            output_path = os.path.join(self.output_dir, "financial_market_data.csv")
            final_df.to_csv(output_path, index=False)
            
            print(f"ÉXITO: Dataset maestro generado en: {output_path}")
            print(f"Total registros: {len(final_df)}")
            return True
            
        except Exception as e:
            print(f"ERROR CRÍTICO EN MOTOR DE ANÁLISIS: {e}")
            import traceback
            traceback.print_exc()
            return False
