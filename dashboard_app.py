import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import datetime

# --- CONFIGURACIÓN DE ESTILO ---
COLOR_BG = "#1e1e1e"        # Fondo oscuro
COLOR_PANEL = "#2d2d2d"     # Paneles
COLOR_TEXT = "#ffffff"      # Texto blanco
COLOR_ACCENT = "#007acc"    # Azul corporativo
COLOR_SUCCESS = "#4caf50"   # Verde
COLOR_DANGER = "#f44336"    # Rojo

class FinancialDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FinanceDataHub - Executive Dashboard")
        self.geometry("1400x850")
        self.configure(bg=COLOR_BG)
        
        # Ruta del CSV
        self.data_path = os.path.join(os.path.dirname(__file__), "data", "financial_market_data.csv")
        self.df_original = pd.DataFrame()
        self.df_filtered = pd.DataFrame()
        
        # Inicializar UI
        self._setup_styles()
        self._build_sidebar()
        self._build_main_area()
        
        # Cargar datos iniciales
        self.load_data()

    def _setup_styles(self):
        """Configura el tema oscuro personalizado para TTK"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuración general
        style.configure(".", background=COLOR_BG, foreground=COLOR_TEXT, font=("Segoe UI", 10))
        style.configure("TFrame", background=COLOR_BG)
        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT)
        style.configure("TButton", background=COLOR_ACCENT, foreground="white", borderwidth=0, focuscolor=COLOR_PANEL)
        style.map("TButton", background=[("active", "#005f9e")])
        
        # Estilo para Treeview (Tabla)
        style.configure("Treeview", 
                        background=COLOR_PANEL, 
                        foreground="white", 
                        fieldbackground=COLOR_PANEL,
                        rowheight=25)
        style.configure("Treeview.Heading", 
                        background="#333333", 
                        foreground="white", 
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", COLOR_ACCENT)])

    def _build_sidebar(self):
        """Panel lateral de filtros"""
        sidebar = tk.Frame(self, bg=COLOR_PANEL, width=250, padx=20, pady=20)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False) # Evitar que se encoja

        # Título
        tk.Label(sidebar, text="FILTROS", bg=COLOR_PANEL, fg="white", font=("Segoe UI", 16, "bold")).pack(pady=(0, 20))
        
        # Filtro: Cliente (Ticker)
        tk.Label(sidebar, text="Cliente / Activo:", bg=COLOR_PANEL, fg="#aaaaaa").pack(anchor="w")
        self.combo_ticker = ttk.Combobox(sidebar, state="readonly")
        self.combo_ticker.pack(fill=tk.X, pady=(5, 15))
        
        # Filtro: Año
        tk.Label(sidebar, text="Año Fiscal:", bg=COLOR_PANEL, fg="#aaaaaa").pack(anchor="w")
        self.combo_year = ttk.Combobox(sidebar, state="readonly")
        self.combo_year.pack(fill=tk.X, pady=(5, 15))
        
        # Filtro: Mes
        tk.Label(sidebar, text="Mes:", bg=COLOR_PANEL, fg="#aaaaaa").pack(anchor="w")
        self.combo_month = ttk.Combobox(sidebar, state="readonly")
        self.combo_month.pack(fill=tk.X, pady=(5, 20))
        
        # Botones de Acción
        btn_apply = tk.Button(sidebar, text="Aplicar Filtros", bg=COLOR_ACCENT, fg="white", 
                              font=("Segoe UI", 10, "bold"), relief="flat", padx=10, pady=5,
                              command=self.apply_filters)
        btn_apply.pack(fill=tk.X, pady=5)
        
        btn_reset = tk.Button(sidebar, text="🔄 Recargar Datos", bg="#444", fg="white", 
                              relief="flat", padx=10, pady=5, command=self.load_data)
        btn_reset.pack(fill=tk.X, pady=5)

    def _build_main_area(self):
        """Área principal con KPIs y Gráficos"""
        main_frame = tk.Frame(self, bg=COLOR_BG)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # --- 1. SECCIÓN KPIs ---
        self.kpi_frame = tk.Frame(main_frame, bg=COLOR_BG)
        self.kpi_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Crear widgets para KPIs (placeholders)
        self.card_1 = self._create_kpi_card(self.kpi_frame, "Precio Actual", "$0.00", COLOR_ACCENT)
        self.card_2 = self._create_kpi_card(self.kpi_frame, "Retorno Promedio", "0.00%", COLOR_SUCCESS)
        self.card_3 = self._create_kpi_card(self.kpi_frame, "Riesgo (Volatilidad)", "0.00%", COLOR_DANGER)
        self.card_4 = self._create_kpi_card(self.kpi_frame, "Señales Compra", "0", "#9c27b0")

        # --- 2. SECCIÓN VISUALIZACIÓN ---
        # Notebook (Pestañas)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 1: Gráficos
        self.tab_charts = tk.Frame(notebook, bg=COLOR_BG)
        notebook.add(self.tab_charts, text="📊 Análisis Gráfico")
        
        # Canvas de Matplotlib
        self.figure = plt.Figure(figsize=(10, 5), dpi=100, facecolor=COLOR_BG)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(COLOR_BG)
        
        self.canvas = FigureCanvasTkAgg(self.figure, self.tab_charts)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Pestaña 2: Datos Detallados (Tabla)
        self.tab_data = tk.Frame(notebook, bg=COLOR_BG)
        notebook.add(self.tab_data, text="📋 Datos Detallados")
        
        # Treeview (Tabla)
        columns = ("Date", "Ticker", "Close", "Daily_Return_Pct", "RSI_14", "Signal_Trend")
        self.tree = ttk.Treeview(self.tab_data, columns=columns, show="headings")
        
        # Definir encabezados
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
            
        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(self.tab_data, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_kpi_card(self, parent, title, value, color):
        """Crea una tarjeta KPI estilizada"""
        card = tk.Frame(parent, bg=COLOR_PANEL, padx=20, pady=15)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        lbl_title = tk.Label(card, text=title.upper(), bg=COLOR_PANEL, fg="#aaaaaa", font=("Segoe UI", 9))
        lbl_title.pack(anchor="w")
        
        lbl_value = tk.Label(card, text=value, bg=COLOR_PANEL, fg=color, font=("Segoe UI", 20, "bold"))
        lbl_value.pack(anchor="w")
        
        return lbl_value # Retornamos la etiqueta del valor para actualizarla después

    def load_data(self):
        """Carga datos desde el CSV y actualiza los filtros"""
        if not os.path.exists(self.data_path):
            messagebox.showerror("Error", f"No se encontró el archivo: {self.data_path}")
            return
            
        try:
            # Cargar CSV
            self.df_original = pd.read_csv(self.data_path)
            
            # Procesar Fechas
            self.df_original['Date'] = pd.to_datetime(self.df_original['Date'])
            self.df_original['Year'] = self.df_original['Date'].dt.year
            self.df_original['Month'] = self.df_original['Date'].dt.month_name()
            
            # Poblar Filtros
            tickers = sorted(self.df_original['Ticker'].unique().tolist())
            years = sorted(self.df_original['Year'].unique().tolist(), reverse=True)
            months = self.df_original['Month'].unique().tolist()
            
            self.combo_ticker['values'] = ["Todos"] + tickers
            self.combo_year['values'] = ["Todos"] + years
            self.combo_month['values'] = ["Todos"] + months
            
            # Valores por defecto
            self.combo_ticker.current(0)
            self.combo_year.current(0)
            self.combo_month.current(0)
            
            # Aplicar filtro inicial (mostrar todo)
            self.apply_filters()
            messagebox.showinfo("Éxito", "Datos recargados correctamente.")
            
        except Exception as e:
            messagebox.showerror("Error Crítico", f"Falló la carga de datos:\n{str(e)}")

    def apply_filters(self):
        """Filtra el DataFrame según la selección del usuario"""
        df = self.df_original.copy()
        
        # Obtener valores
        sel_ticker = self.combo_ticker.get()
        sel_year = self.combo_year.get()
        sel_month = self.combo_month.get()
        
        # Aplicar lógica
        if sel_ticker != "Todos":
            df = df[df['Ticker'] == sel_ticker]
            
        if sel_year != "Todos":
            df = df[df['Year'] == int(sel_year)]
            
        if sel_month != "Todos":
            df = df[df['Month'] == sel_month]
            
        self.df_filtered = df
        
        # Actualizar UI
        self.update_kpis()
        self.update_charts()
        self.update_table()

    def update_kpis(self):
        """Recalcula KPIs basados en la data filtrada"""
        if self.df_filtered.empty:
            return

        # 1. Último Precio (Promedio si hay varios tickers)
        last_price = self.df_filtered['Close'].iloc[-1]
        self.card_1.config(text=f"${last_price:,.2f}")
        
        # 2. Retorno Promedio
        avg_return = self.df_filtered['Daily_Return_Pct'].mean()
        color = COLOR_SUCCESS if avg_return >= 0 else COLOR_DANGER
        self.card_2.config(text=f"{avg_return:.2f}%", fg=color)
        
        # 3. Volatilidad Promedio
        avg_vol = self.df_filtered['Volatility_Annualized'].mean()
        self.card_3.config(text=f"{avg_vol:.2f}%", fg=COLOR_DANGER)
        
        # 4. Señales de Compra (Conteo)
        # Contamos cuántas veces aparece "COMPRA" o "BULLISH"
        bullish_count = self.df_filtered['Signal_Trend'].str.contains('BULLISH', case=False, na=False).sum()
        self.card_4.config(text=f"{bullish_count}")

    def update_charts(self):
        """Dibuja el gráfico con Matplotlib"""
        self.ax.clear()
        
        if self.df_filtered.empty:
            self.canvas.draw()
            return
            
        # Agrupar por Ticker para dibujar líneas separadas
        tickers = self.df_filtered['Ticker'].unique()
        
        for ticker in tickers:
            data = self.df_filtered[self.df_filtered['Ticker'] == ticker]
            self.ax.plot(data['Date'], data['Close'], label=ticker)
            
        # Estilizado del gráfico
        self.ax.set_title("Evolución de Precios", color="white", fontsize=12)
        self.ax.set_xlabel("Fecha", color="white")
        self.ax.set_ylabel("Precio de Cierre ($)", color="white")
        self.ax.tick_params(axis='x', colors='white', rotation=45)
        self.ax.tick_params(axis='y', colors='white')
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.ax.legend(facecolor=COLOR_PANEL, labelcolor="white")
        
        self.figure.tight_layout()
        self.canvas.draw()

    def update_table(self):
        """Actualiza la tabla Treeview"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Insertar nuevas filas (limitado a las últimas 100 para rendimiento)
        # Ordenamos descendente por fecha
        df_show = self.df_filtered.sort_values(by='Date', ascending=False).head(200)
        
        for _, row in df_show.iterrows():
            # Formatear fecha
            date_str = row['Date'].strftime('%Y-%m-%d')
            vals = (date_str, row['Ticker'], f"{row['Close']:.2f}", 
                    f"{row['Daily_Return_Pct']:.2f}%", f"{row['RSI_14']:.1f}", 
                    row['Signal_Trend'])
            self.tree.insert("", "end", values=vals)

if __name__ == "__main__":
    app = FinancialDashboard()
    app.mainloop()
