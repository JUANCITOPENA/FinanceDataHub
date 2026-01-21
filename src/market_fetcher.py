import yfinance as yf
import pandas as pd
import os

class MarketFetcher:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.tickers = ["AAPL", "MSFT", "TSLA", "NVDA", "BTC-USD", "ETH-USD"]
        
    def fetch_data(self):
        print("--- Iniciando descarga de Mercado ---")
        try:
            data = yf.download(self.tickers, period="2y", interval="1d", ignore_tz=True, progress=False)
            
            if data.empty:
                print("ADVERTENCIA: No se descargaron datos.")
                return False

            # Procesamiento robusto
            df_close = data['Close'].stack().reset_index()
            df_close.columns = ['Date', 'Ticker', 'Close_Price']
            
            df_vol = data['Volume'].stack().reset_index()
            df_vol.columns = ['Date', 'Ticker', 'Volume']
            
            final_df = pd.merge(df_close, df_vol, on=['Date', 'Ticker'])
            final_df['Date'] = pd.to_datetime(final_df['Date']).dt.date
            final_df['Ticker'] = final_df['Ticker'].astype(str)
            
            # Guardar CSV
            output_path = os.path.join(self.output_dir, "market_data.csv")
            final_df.to_csv(output_path, index=False)
            print(f"ÉXITO: Datos de mercado guardados en {output_path}")
            return True
            
        except Exception as e:
            print(f"ERROR FATAL en MarketFetcher: {e}")
            return False
