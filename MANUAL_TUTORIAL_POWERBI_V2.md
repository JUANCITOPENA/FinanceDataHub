# Manual de Implementación Técnica: Power BI & FinanceDataHub

**Versión:** 2.1 (Enero 2026)  
**Desarrollador:** Juancito Peña  
**Tecnologías:** Power BI • DAX • HTML/CSS (Visual HTML Content) • Python

---

## 🌟 Contexto del Proyecto: Finance Data Hub

Este manual es parte del ecosistema **Finance Data Hub**, un proyecto que automatiza la inteligencia financiera. Antes de entrar en las medidas DAX, es crucial entender de dónde vienen los datos.

### ¿Cómo funciona la arquitectura?
1.  **Módulo Mercado (Python):** Un script local (`main_loop.py`) descarga precios de Yahoo Finance (AAPL, MSFT, BTC, etc.) cada 5 minutos.
2.  **Sincronización (Git):** Los datos se guardan en CSV y se suben automáticamente a este repositorio de GitHub.
3.  **Power BI (Frontend):** Conectamos el reporte a los archivos CSV de GitHub. Esto permite que el reporte se alimente de datos frescos sin intervención manual.

---

## 🛠️ Fase 1: Preparación en Power BI

### 1. Instalación del Visual "HTML Content"
Para lograr el impacto visual de las tarjetas y barras personalizadas, utilizamos HTML y CSS renderizado dentro de Power BI.

1.  En Power BI Desktop, ve al panel de **Visualizaciones**.
2.  Clic en los tres puntos `(...)` -> **Obtener más objetos visuales**.
3.  Busca: `HTML Content` (Certificado).
4.  Agrégalo a tu caja de herramientas.

### 2. Modelado de Datos (Tablas Auxiliares)
Necesitamos una tabla desconectada para crear segmentadores de riesgo personalizados.

*   Ve a la pestaña **Modelado** -> **Nueva tabla** y pega:

```dax
Tab_Riesgo = DATATABLE(
    "Nivel", STRING, "Orden", INTEGER, "Min", DOUBLE, "Max", DOUBLE,
    {
        {"Bajo Riesgo", 1, 0.00, 0.25},
        {"Riesgo Medio", 2, 0.25, 0.45},
        {"Riesgo Alto", 3, 0.45, 10.00}
    }
)
```

---

## 🧠 Fase 2: Medidas DAX Fundamentales

Crea una tabla vacía llamada `_Medidas` y organiza allí el siguiente código.

### A. Precios y Variaciones
```dax
// 1. Precio de Cierre más reciente
Precio Actual = 
VAR _UltimaFecha = LASTDATE('financial_market_data'[Date])
RETURN
CALCULATE(SUM('financial_market_data'[Close]), _UltimaFecha)

// 2. Variación porcentual del activo
Variación % = 
VAR PrecioInicio = CALCULATE(SUM('financial_market_data'[Close]), FIRSTDATE('financial_market_data'[Date]))
VAR PrecioFin = [Precio Actual]
RETURN
DIVIDE(PrecioFin - PrecioInicio, PrecioInicio)
```

### B. Indicadores Técnicos
```dax
// 3. Indicador de Fuerza Relativa (RSI)
RSI Actual = 
VAR _UltimaFecha = LASTDATE('financial_market_data'[Date])
RETURN
CALCULATE(AVERAGE('financial_market_data'[RSI_14]), _UltimaFecha)

// 4. Semáforo Técnico
Estado RSI = 
VAR _RSI = [RSI Actual]
RETURN
SWITCH(TRUE(),
    ISBLANK(_RSI), "N/A",
    _RSI >= 70, "Sobrecompra",
    _RSI <= 30, "Sobreventa",
    "Neutral"
)

// 5. Color Dinámico para HTML
Color RSI = 
VAR _RSI = [RSI Actual]
RETURN
SWITCH(TRUE(),
    _RSI >= 70, "#ff1744", // Rojo (Venta)
    _RSI <= 30, "#00c853", // Verde (Compra)
    "#ffea00"              // Amarillo (Neutral)
)
```

### C. Métricas de Riesgo
```dax
// 6. Volatilidad Promedio
Volatilidad Promedio = AVERAGE('financial_market_data'[Volatility_Annualized])

// 7. Señal de Tendencia (Texto)
Tendencia SMA = 
VAR _UltimaFecha = LASTDATE('financial_market_data'[Date])
RETURN
CALCULATE(MAX('financial_market_data'[Signal_Trend]), _UltimaFecha)
```

---

## ✨ Fase 3: Visuales Avanzados (HTML/CSS)

Estas medidas generan código web que el visual "HTML Content" interpreta. Copia y pega exactamente como están.

### 🟦 Visual 1: Barra Superior (Ticker Tape)
*Crea una medida llamada `HTML_TopBar_Cards1`:*

```dax
HTML_TopBar_Cards1 = 
VAR _Filas =
    CONCATENATEX(
        FILTER(VALUES('financial_market_data'[Ticker]), NOT(ISBLANK('financial_market_data'[Ticker])) && [Precio Actual] > 0),
        VAR _Ticker = 'financial_market_data'[Ticker]
        VAR _Var = [Variación %]
        VAR _Precio = [Precio Actual]
        VAR _Color = IF(_Var >= 0, "#00ff9d", "#ff3d5d")
        VAR _Icono = IF(_Var >= 0, "▲", "▼")
        VAR _Logo = SWITCH(_Ticker,
            "AAPL", "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg",
            "MSFT", "https://trendlyne-media-mumbai-new.s3.amazonaws.com/profilepicture/1554053_profilepicture.png",
            "TSLA", "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Tesla_logo.png/500px-Tesla_logo.png",
            "NVDA", "https://companieslogo.com/img/orig/NVDA-220e1e03.png?t=1722952498",
            "BTC-USD", "https://www.criptonoticias.com/wp-content/uploads/2023/10/BC_Logo_.png",
            "ETH-USD", "https://logokit.com/icons/ETH.png",
            "https://cdn-icons-png.flaticon.com/256/5588/5588146.png"
        )
        RETURN
        "<div class='mini-card'>
            <img src='" & _Logo & "' class='mini-logo'>
            <div class='info'>
                <div class='ticker'>" & _Ticker & "</div>
                <div class='price'>$" & FORMAT(_Precio, "#,##0.00") & "</div>
                <div class='change' style='color: " & _Color & ";'>" & _Icono & " " & FORMAT(ABS(_Var), "0.0%") & "</div>
            </div>
        </div>", ""
    )
RETURN
"<style>
    .top-bar { display: flex; gap: 15px; overflow-x: auto; padding: 10px; font-family: 'Segoe UI', sans-serif; }
    .mini-card { min-width: 170px; background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 12px; display: flex; align-items: center; gap: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .mini-logo { width: 35px; height: 35px; object-fit: contain; background: white; border-radius: 6px; padding: 4px; }
    .info { display: flex; flex-direction: column; line-height: 1.2; }
    .ticker { font-size: 11px; font-weight: 800; color: #8b949e; text-transform: uppercase; }
    .price { font-size: 16px; font-weight: bold; color: #f0f6fc; }
    .change { font-size: 11px; font-weight: 900; }
    .top-bar::-webkit-scrollbar { display: none; }
</style>
<div class='top-bar'>" & _Filas & "</div>"
```

### 📊 Visual 2: Barras de Riesgo con Gradiente
*Crea la medida `HTML_BarChart_Riesgo_Final`:*

```dax
HTML_BarChart_Riesgo_Final = 
VAR _MaxVolGlobal = CALCULATE(MAXX(VALUES('financial_market_data'[Ticker]), [Volatilidad Promedio]), ALLSELECTED('financial_market_data'))
VAR _Filas = CONCATENATEX(
    FILTER(VALUES('financial_market_data'[Ticker]), NOT(ISBLANK('financial_market_data'[Ticker])) && [Volatilidad Promedio] > 0),
    VAR _Ticker = 'financial_market_data'[Ticker]
    VAR _Vol = [Volatilidad Promedio]
    VAR _AnchoBarra = DIVIDE(_Vol, _MaxVolGlobal) * 100
    VAR _LogoUrl = SWITCH(_Ticker,
        "AAPL", "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg",
        "MSFT", "https://trendlyne-media-mumbai-new.s3.amazonaws.com/profilepicture/1554053_profilepicture.png",
        "TSLA", "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Tesla_logo.png/500px-Tesla_logo.png",
        "NVDA", "https://companieslogo.com/img/orig/NVDA-220e1e03.png?t=1722952498",
        "BTC-USD", "https://www.criptonoticias.com/wp-content/uploads/2023/10/BC_Logo_.png",
        "ETH-USD", "https://logokit.com/icons/ETH.png",
        "https://cdn-icons-png.flaticon.com/256/5588/5588146.png"
    )
    RETURN
    "<div class='row'>
        <div class='identity'><img src='" & _LogoUrl & "' class='logo'><span class='ticker-name'>" & _Ticker & "</span></div>
        <div class='bar-track'><div class='bar-fill' style='width: " & FORMAT(_AnchoBarra, "0") & "%;'></div></div>
        <div class='value-label'>" & FORMAT(_Vol, "0.00%") & "</div>
    </div>", "", [Volatilidad Promedio], DESC
)
RETURN
"<style>
    .panel { font-family: 'Segoe UI', sans-serif; background: #0d1117; padding: 25px; border-radius: 20px; color: white; border: 1px solid #30363d; }
    .header { font-size: 14px; font-weight: bold; color: #58a6ff; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 2px; }
    .row { display: flex; align-items: center; margin-bottom: 18px; gap: 15px; }
    .identity { width: 130px; display: flex; align-items: center; gap: 12px; }
    .logo { width: 32px; height: 32px; border-radius: 6px; background: white; padding: 4px; object-fit: contain; }
    .ticker-name { font-weight: 700; font-size: 15px; color: #f0f6fc; }
    .bar-track { flex-grow: 1; background: #21262d; height: 12px; border-radius: 6px; overflow: hidden; }
    .bar-fill { height: 100%; background: linear-gradient(90deg, #1d4ed8 0%, #3b82f6 100%); box-shadow: 0 0 15px rgba(59, 130, 246, 0.4); }
    .value-label { width: 70px; text-align: right; font-size: 14px; font-weight: bold; color: #3b82f6; }
</style>
<div class='panel'><div class='header'>⚡ Riesgo y Volatilidad</div>" & _Filas & "</div>"
```

### 📈 Visual 3: Performance (Barras + / -)
*Crea la medida `HTML_BarChart_Performance_Final`:*

```dax
HTML_BarChart_Performance_Final = 
VAR _MaxVarGlobal = CALCULATE(MAXX(VALUES('financial_market_data'[Ticker]), ABS([Variación %])), ALLSELECTED('financial_market_data'))
VAR _Filas = CONCATENATEX(
    FILTER(VALUES('financial_market_data'[Ticker]), NOT(ISBLANK('financial_market_data'[Ticker])) && [Precio Actual] > 0),
    VAR _Ticker = 'financial_market_data'[Ticker]
    VAR _Var = [Variación %]
    VAR _Precio = [Precio Actual]
    VAR _AnchoBarra = DIVIDE(ABS(_Var), _MaxVarGlobal) * 100
    VAR _Color = IF(_Var >= 0, "#00c853", "#ff1744")
    VAR _LogoUrl = SWITCH(_Ticker,
            "AAPL", "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg",
            "MSFT", "https://trendlyne-media-mumbai-new.s3.amazonaws.com/profilepicture/1554053_profilepicture.png",
            "TSLA", "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Tesla_logo.png/500px-Tesla_logo.png",
            "NVDA", "https://companieslogo.com/img/orig/NVDA-220e1e03.png?t=1722952498",
            "BTC-USD", "https://www.criptonoticias.com/wp-content/uploads/2023/10/BC_Logo_.png",
            "ETH-USD", "https://logokit.com/icons/ETH.png",
            "https://cdn-icons-png.flaticon.com/256/5588/5588146.png"
    )
    RETURN
    "<div class='row'>
        <div class='identity'><img src='" & _LogoUrl & "' class='logo'><span class='ticker-name'>" & _Ticker & "</span></div>
        <div class='bar-track'><div class='bar-fill' style='width: " & FORMAT(_AnchoBarra, "0") & "%; background: " & _Color & ";'></div></div>
        <div class='info-box'><div class='price-text'>$" & FORMAT(_Precio, "#,##0.00") & "</div><div class='pct-text' style='color: " & _Color & ";'>" & IF(_Var>=0,"+","") & FORMAT(_Var, "0.0%") & "</div></div>
    </div>", "", [Variación %], DESC
)
RETURN
"<style>
    .panel { font-family: 'Segoe UI', sans-serif; background: #0d1117; padding: 25px; border-radius: 20px; color: white; border: 1px solid #30363d; }
    .header { font-size: 14px; font-weight: bold; color: #00c853; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 2px; }
    .row { display: flex; align-items: center; margin-bottom: 20px; gap: 15px; }
    .identity { width: 130px; display: flex; align-items: center; gap: 12px; }
    .logo { width: 32px; height: 32px; border-radius: 50%; background: white; padding: 3px; object-fit: contain; border: 1px solid #30363d; }
    .ticker-name { font-weight: 800; font-size: 16px; color: #ffffff; }
    .bar-track { flex-grow: 1; background: #161b22; height: 14px; border-radius: 7px; overflow: hidden; border: 1px solid #30363d; }
    .bar-fill { height: 100%; transition: width 1s ease-in-out; }
    .info-box { width: 110px; text-align: right; line-height: 1.1; }
    .price-text { font-size: 15px; font-weight: bold; color: #f0f6fc; }
    .pct-text { font-size: 12px; font-weight: 800; }
</style>
<div class='panel'><div class='header'>📈 Performance del Mercado</div>" & _Filas & "</div>"
```

### 💎 Visual 4: Super Card Ultimate (SVG Chart)
*Crea la medida `Visual_SuperCard_Chart_Ultimate`. Esta medida genera un gráfico de líneas SVG dentro de la tarjeta.*

```dax
Visual_SuperCard_Chart_Ultimate = 
VAR _Ticker = SELECTEDVALUE('financial_market_data'[Ticker], "Resumen de Mercado")
VAR _Precio = [Precio Actual]
VAR _Var = [Variación %]
VAR _RSI = [RSI Actual]
VAR _EstadoRSI = [Estado RSI]
VAR _ColorRSI = [Color RSI]
VAR _Volatilidad = [Volatilidad Promedio]
VAR _Tendencia = [Tendencia SMA]
VAR _ColorVar = IF(_Var >= 0, "#00fa9a", "#ff4d4d")
VAR _IconoVar = IF(_Var >= 0, "🔼", "🔽")

// SVG Sparkline Lógica
VAR _NumDiasChart = 30
VAR _RefDate = LASTDATE('financial_market_data'[Date])
VAR _StartDate = _RefDate - _NumDiasChart
VAR _ChartTable = CALCULATETABLE(
        SUMMARIZE('financial_market_data', 'financial_market_data'[Date], "ClosePrice", SUM('financial_market_data'[Close])),
        'financial_market_data'[Date] > _StartDate && 'financial_market_data'[Date] <= _RefDate,
        ALLSELECTED('financial_market_data')
    )
VAR _MinP = MINX(_ChartTable, [ClosePrice])
VAR _MaxP = MAXX(_ChartTable, [ClosePrice])
VAR _RangeP = IF(_MaxP - _MinP = 0, 1, _MaxP - _MinP)
VAR _SvgW = 500
VAR _SvgH = 60
VAR _SvgPathStr = CONCATENATEX(_ChartTable, VAR _DayIdx = DATEDIFF(_StartDate, 'financial_market_data'[Date], DAY) VAR _X = INT((_DayIdx / _NumDiasChart) * _SvgW) VAR _Y = INT(_SvgH - (([ClosePrice] - _MinP) / _RangeP * _SvgH)) RETURN _X & "," & _Y, " L ", 'financial_market_data'[Date], ASC)
VAR _FinalPath = IF(ISEMPTY(_ChartTable), "", "M " & _SvgPathStr)

RETURN
"<style>
    .super-container { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #131324 0%, #1c2a4a 100%); color: white; padding: 25px 30px; border-radius: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.6); display: flex; flex-direction: column; gap: 20px; border-top: 2px solid #4e73df88; }
    .top-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
    .ticker-name { font-size: 20px; color: #ffffff; font-weight: 700; letter-spacing: 1px; }
    .ticker-badge { background: #4e73df; font-size: 11px; padding: 3px 8px; border-radius: 10px; font-weight: bold;}
    .main-content { display: flex; align-items: baseline; gap: 25px; }
    .price-big { font-size: 72px; font-weight: 800; letter-spacing: -2px; line-height: 1; color: #ffffff;}
    .change-box { font-size: 26px; font-weight: 600; color: " & _ColorVar & "; }
    .metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; border-top: 1px solid #ffffff33; padding-top: 20px; }
    .metric-item { display: flex; flex-direction: column; gap: 5px; }
    .m-label { font-size: 10px; text-transform: uppercase; color: #8fa1b8; letter-spacing: 1px; font-weight: 700; }
    .m-val { font-size: 18px; font-weight: 700; }
    .chart-area { margin-top: 10px; filter: drop-shadow(0 0 8px " & _ColorVar & "55); }
</style>
<div class='super-container'>
    <div class='top-row'><div class='ticker-name'>" & _Ticker & "</div><div class='ticker-badge'>LIVE</div></div>
    <div class='main-content'><div class='price-big'>$" & FORMAT(_Precio, "#,##0.00") & "</div><div class='change-box'>" & _IconoVar & " " & FORMAT(ABS(_Var), "0.0%") & "</div></div>
    <div class='chart-area'>
        <svg viewBox='0 0 500 60' preserveAspectRatio='none' width='100%' height='80'>
            <defs><linearGradient id='gradLine' x1='0' y1='0' x2='1' y2='0'><stop offset='0%' stop-color='" & _ColorVar & "' stop-opacity='0.4'/><stop offset='100%' stop-color='" & _ColorVar & "' stop-opacity='1'/></linearGradient></defs>
            <path d='" & _FinalPath & "' fill='none' stroke='url(#gradLine)' stroke-width='3' stroke-linecap='round' vector-effect='non-scaling-stroke' />
        </svg>
    </div>
    <div class='metrics-grid'>
        <div class='metric-item'><span class='m-label'>RSI (14)</span><span class='m-val' style='color: " & _ColorRSI & "'>" & FORMAT(_RSI, "0") & "</span></div>
        <div class='metric-item'><span class='m-label'>Volatilidad</span><span class='m-val'>" & FORMAT(_Volatilidad, "0.0%") & "</span></div>
        <div class='metric-item'><span class='m-label'>Tendencia</span><span class='m-val' style='font-size: 14px;'>" & _Tendencia & "</span></div>
    </div>
</div>"
```

---

## 🚀 Implementación Final

1.  Arrastra el visual **HTML Content** al lienzo.
2.  Pon la medida deseada en el campo **Values**.
3.  Ajusta el tamaño y repite para los 4 visuales.

¡Tu dashboard tendrá ahora una interfaz de nivel profesional!