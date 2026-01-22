# Manual de Implementación Técnica: Power BI & FinanceDataHub

**Versión:** 3.1 (Enero 2026)  
**Desarrollador:** Juancito Peña  
**Tecnologías:** Power BI • DAX • HTML/CSS (Visual HTML Content) • Python • SVG

---

## 🌟 Contexto del Proyecto: Finance Data Hub

Este ecosistema ha sido diseñado para transformar datos crudos en **inteligencia financiera visual**. El objetivo principal es superar las limitaciones estéticas de Power BI mediante el uso de tecnologías web (HTML5, CSS3 y SVG) integradas directamente en el modelo de datos.

### 🔗 Link al Dashboard en Vivo
👉 **[Ver Dashboard Power BI Online](https://app.powerbi.com/view?r=eyJrIjoiNmNhNTg3MzctMTkzMC00Mjk5LTk3NTctYTQxNjFjNTg4ZTRmIiwidCI6IjMwOTE4NjllLTFiNWMtNDlhNy1iZWQwLTA1ODJiMjBlYzg0NSIsImMiOjJ9)**

### 🧠 ¿Qué solucionamos?
1.  **Automatización:** Eliminamos la carga manual de datos. Un "bot" en Python extrae información de Yahoo Finance y la sincroniza con GitHub.
2.  **Impacto Visual:** Sustituimos los visuales nativos por componentes personalizados que permiten:
    *   **Micro-charts (Sparklines):** Gráficos de tendencia dentro de tarjetas.
    *   **Diseño Dark Mode:** Estética moderna y profesional.
    *   **Lógica de Negocio Visual:** Colores y emojis que reaccionan a los datos en tiempo real.

---

## 🛠️ Fase 1: Configuración del Entorno y Datos

### 1. Visual "HTML Content"
Es el intérprete que permite que Power BI entienda nuestro código.
*   **Instalación:** `Visualizaciones` -> `Obtener más objetos visuales` -> Buscar `HTML Content`.

### 2. Tabla de Riesgo (Segmentación)
Utilizada para clasificar activos según su volatilidad anualizada.
*   **Creación:** `Modelado` -> `Nueva Tabla`.

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

### 3. Registro de Actualización Real (Power Query)
**Importante:** Captura el momento exacto en que se presionó el botón de actualizar.
1.  En Power BI: `Transformar datos`.
2.  `Nueva fuente` -> `Consulta en blanco`.
3.  En la barra de fórmulas: `= #table(type table[UltimaCarga=datetime], {{DateTime.LocalNow()}})`
4.  Nombre de la consulta: `Refresh_Log`.

---

## 🧠 Fase 2: Medidas DAX (La Inteligencia)

### A. KPIs de Mercado
Estas medidas calculan los valores numéricos base.

```dax
// Calcula el último precio disponible para el activo seleccionado
Precio Actual = 
VAR _UltimaFecha = LASTDATE('financial_market_data'[Date])
RETURN
CALCULATE(SUM('financial_market_data'[Close]), _UltimaFecha)

// Variación entre el primer y el último precio del periodo visible
Variación % = 
VAR PrecioInicio = CALCULATE(SUM('financial_market_data'[Close]), FIRSTDATE('financial_market_data'[Date]))
VAR PrecioFin = [Precio Actual]
RETURN
DIVIDE(PrecioFin - PrecioInicio, PrecioInicio)
```

### B. Análisis Técnico
```dax
// Promedio del RSI (Relative Strength Index)
RSI Actual = 
VAR _UltimaFecha = LASTDATE('financial_market_data'[Date])
RETURN
CALCULATE(AVERAGE('financial_market_data'[RSI_14]), _UltimaFecha)

// Determina si el activo está en Sobrecompra o Sobreventa
Estado RSI = 
VAR _RSI = [RSI Actual]
RETURN
SWITCH(TRUE(),
    ISBLANK(_RSI), "N/A",
    _RSI >= 70, "Sobrecompra",
    _RSI <= 30, "Sobreventa",
    "Neutral"
)
```

---

## ✨ Fase 3: Visualizaciones Maestras (HTML/CSS/SVG)

Explicación detallada de cómo construimos la interfaz.

### 📋 1. Tabla Ejecutiva v3 (High Contrast)
**Solución:** Reemplaza las tablas aburridas por una lista estilizada con logos, badges de colores y emojis de satisfacción basados en la tendencia.
*   **HTML:** Estructura de filas y celdas usando `div`.
*   **CSS:** Uso de `flexbox` para alineación perfecta y `badges` con bordes redondeados.
*   **Lógica:** Cambia el emoji (`😊`, `☹️`, `⚖️`) según la SMA (Media Móvil).

```dax
HTML_Table_Executive_Clean_v3 = 
VAR _Filas = 
    CONCATENATEX(
        FILTER(VALUES('financial_market_data'[Ticker]), NOT(ISBLANK('financial_market_data'[Ticker])) && [Precio Actual] > 0),
        VAR _Ticker = 'financial_market_data'[Ticker]
        VAR _Precio = [Precio Actual]
        VAR _Var = [Variación %]
        VAR _RSI = [RSI Actual]
        VAR _Vol = [Volatilidad Promedio]
        VAR _Trend = [Tendencia SMA]
        VAR _ColorVar = IF(_Var >= 0, "#00ff9d", "#ff3d5d")
        VAR _ColorRSI = [Color RSI]
        VAR _TrendColor = SWITCH(_Trend, "Bullish", "#00ff9d", "Bearish", "#ff3d5d", "#ffffff")
        VAR _TrendEmoji = SWITCH(_Trend, "Bullish", "😊", "Bearish", "☹️", "⚖️")
        VAR _LogoUrl = SWITCH(_Ticker, "AAPL", "...", "MSFT", "...", "TSLA", "...", "NVDA", "...", "BTC-USD", "...", "ETH-USD", "...", "https://cdn-icons-png.flaticon.com/256/5588/5588146.png")
        RETURN
        "<div class='t-row'>
            <div class='t-cell cell-ticker'><img src='" & _LogoUrl & "' class='t-logo'><span>" & _Ticker & "</span></div>
            <div class='t-cell cell-price'>$" & FORMAT(_Precio, "#,##0.00") & "</div>
            <div class='t-cell cell-var' style='color:" & _ColorVar & ";'>" & IF(_Var >= 0, "+", "") & FORMAT(_Var, "0.00%") & "</div>
            <div class='t-cell cell-rsi'><span class='rsi-badge' style='background:" & _ColorRSI & "33; color:" & _ColorRSI & "; border: 1px solid " & _ColorRSI & ";'>" & FORMAT(_RSI, "0.0") & "</span></div>
            <div class='t-cell cell-vol' style='color: #ffffff; font-weight: 800;'>" & FORMAT(_Vol, "0.0%") & "</div>
            <div class='t-cell cell-trend' style='color:" & _TrendColor & "; font-weight: 900;'>" & _TrendEmoji & " " & UPPER(_Trend) & "</div>
        </div>", ""
    )
RETURN
"<style>
    .t-container { font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #ffffff; border-radius: 12px; border: 1px solid #30363d; }
    .t-header { display: flex; background: #161b22; padding: 15px 20px; font-size: 13px; font-weight: 900; border-bottom: 2px solid #ffffff44; }
    .t-row { display: flex; padding: 12px 20px; border-bottom: 1px solid #21262d; align-items: center; }
    .t-cell { flex: 1; font-size: 14px; display: flex; align-items: center; }
    .cell-ticker { flex: 1.5; font-weight: 800; gap: 10px; }
    .t-logo { width: 26px; height: 26px; background: white; border-radius: 4px; padding: 2px; }
    .rsi-badge { padding: 3px 8px; border-radius: 4px; font-weight: 900; }
</style>
<div class='t-container'><div class='t-header'><div style='flex:1.5;'>Activo</div><div style='flex:1.2;'>Precio Cierre</div><div style='flex:1;'>Variación</div><div style='flex:1; text-align:center;'>RSI</div><div style='flex:1;'>Volatilidad</div><div style='flex:1.5;'>Tendencia SMA</div></div>" & _Filas & "</div>"
```

### 💎 2. Visual Impacto Master (Super Card)
**Solución:** Centraliza toda la información de un activo en una tarjeta de lujo.
*   **SVG Line Chart:** Calculamos dinámicamente las coordenadas `x,y` de los últimos 30 días para dibujar una línea de tendencia suavizada.
*   **Gradientes:** Usamos un `linearGradient` en el SVG que cambia de intensidad según si el activo sube o baja.
*   **Grid CSS:** Organiza las métricas (Tendencia, Volatilidad, RSI) en una cuadrícula limpia.

```dax
Visual_Impacto_Master_Con_Logos = 
VAR _Ticker = SELECTEDVALUE('financial_market_data'[Ticker], "Market")
VAR _Precio = [Precio Actual]
VAR _Var = [Variación %]
VAR _ColorVar = IF(_Var >= 0, "#00ff9d", "#ff3d5d")
// ... Lógica de SVG y Puntos ...
RETURN
"<style>
    .card-container { font-family: 'Segoe UI', sans-serif; background: #0d1117; padding: 25px; border-radius: 20px; border: 1px solid #30363d; }
    .main-price { font-size: 58px; font-weight: 800; }
    .grid-stats { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; border-top: 1px solid #30363d; padding-top: 20px; }
    .stat-box { background: #161b22; padding: 12px; border-radius: 12px; }
</style>
<div class='card-container'>
    <div class='main-price'>$" & FORMAT(_Precio, "#,##0.00") & "</div>
    <div class='grid-stats'>
        <div class='stat-box'><div>TENDENCIA</div><div>" & [Tendencia SMA] & "</div></div>
        <div class='stat-box'><div>VOLATILIDAD</div><div>" & FORMAT([Volatilidad Promedio], "0.0%") & "</div></div>
        <div class='stat-box'><div>RSI</div><div>" & [RSI Actual] & "</div></div>
    </div>
    <svg viewBox='0 0 400 80'>...</svg>
</div>"
```

### ⏱️ 3. Última Actualización (Máxima Nitidez)
**Solución:** Evita la ambigüedad de los datos mostrando exactamente cuándo se cargó el reporte.
*   **Estilo:** Blanco puro (#ffffff) con fuente de peso 900 para visibilidad total.
*   **JS/Dinámico:** Aunque es estático tras el refresh, se siente vivo gracias al prefijo `[LIVE_SYSTEM_TIME]`.

```dax
HTML_LastUpdate_Brilliant = 
VAR _FechaHora = MAX('Refresh_Log'[UltimaCarga])
RETURN
"<div style='font-family: ""Segoe UI"", sans-serif; color: #ffffff; font-weight: 900; font-size: 14px; letter-spacing: 1px; display: flex; align-items: center; gap: 10px;'>
    <span style='color: #58a6ff; text-shadow: 0 0 5px #58a6ff88;'>[LIVE_SYSTEM_TIME]</span> 
    <span style='text-transform: uppercase;'>" & FORMAT(_FechaHora, "dd/MM/yyyy HH:mm:ss") & "</span>
</div>"
```

---

## 🚀 Resumen de Implementación
1.  **Python:** Extrae y sube a GitHub.
2.  **Power BI:** Conecta al Raw CSV de GitHub.
3.  **DAX:** Procesa KPIs técnicos.
4.  **HTML Content:** Renderiza la interfaz de usuario de alto nivel.

Este sistema no es solo un reporte, es una **consola financiera profesional**.