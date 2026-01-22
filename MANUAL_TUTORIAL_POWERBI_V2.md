# 📘 Manual de Implementación Técnica: Power BI & FinanceDataHub

**Versión:** 5.0 (Definitiva - Enero 2026)  
**Desarrollador:** Juancito Peña  
**Tecnologías:** Power BI • DAX • HTML/CSS (Visual HTML Content) • Python • SVG

---

## 🌟 1. Introducción y Contexto

### Planteamiento del Problema
Los dashboards financieros estándar en Power BI suelen carecer de flexibilidad visual y dependen de actualizaciones manuales. Las tablas nativas son rígidas y los gráficos estándar no permiten personalizaciones avanzadas como micro-gráficos SVG o layouts web complejos.

### Solución Propuesta: Finance Data Hub
Hemos desarrollado una arquitectura híbrida:
1.  **Backend (Python):** Un script (`main_loop.py`) automatiza la extracción de datos de Yahoo Finance y la sincronización con GitHub.
2.  **Frontend (Power BI + HTML):** Utilizamos el visual personalizado `HTML Content` para renderizar interfaces web dentro de Power BI, permitiendo un control total sobre el diseño (gradientes, sombras, tipografía).

### 🔗 Dashboard en Vivo
👉 **[Acceder al Reporte Online](https://app.powerbi.com/view?r=eyJrIjoiNmNhNTg3MzctMTkzMC00Mjk5LTk3NTctYTQxNjFjNTg4ZTRmIiwidCI6IjMwOTE4NjllLTFiNWMtNDlhNy1iZWQwLTA1ODJiMjBlYzg0NSIsImMiOjJ9)**

---

## ⚙️ 2. Configuración del Modelo de Datos

Antes de las medidas, necesitamos estructuras auxiliares.

### Tabla de Riesgo (Segmentación)
*   **Propósito:** Crear una tabla desconectada para definir rangos de volatilidad sin filtrar los datos transaccionales.
*   **Creación:** Pestaña *Modelado* > *Nueva Tabla*.

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

## 🧠 3. Definición de Medidas DAX (Core)

A continuación, se detallan las medidas fundamentales.

### 💰 Medida: Precio Actual
*   **Propósito:** Obtener el valor de cierre más reciente del activo en el contexto seleccionado.
*   **Uso:** Tarjetas principales, cálculos de variación y encabezados.
*   **Contexto:** Evalúa la fecha máxima visible (`LASTDATE`) para asegurar que siempre se muestre el dato "al día", ignorando fechas anteriores en el rango.
*   **Fórmula:**
```dax
Precio Actual = 
VAR _UltimaFecha = LASTDATE('financial_market_data'[Date])
RETURN
CALCULATE(SUM('financial_market_data'[Close]), _UltimaFecha)
```

### 📉 Medida: Variación Porcentual
*   **Propósito:** Calcular el rendimiento del activo durante el periodo seleccionado.
*   **Uso:** Indicadores de color (Verde/Rojo) y flechas de tendencia.
*   **Contexto:** Compara el precio en la `LASTDATE` contra el precio en la `FIRSTDATE` del contexto de filtro actual.
*   **Fórmula:**
```dax
Variación % = 
VAR PrecioInicio = CALCULATE(SUM('financial_market_data'[Close]), FIRSTDATE('financial_market_data'[Date]))
VAR PrecioFin = [Precio Actual]
RETURN
DIVIDE(PrecioFin - PrecioInicio, PrecioInicio)
```

### 📊 Medida: RSI Actual (Indicador Técnico)
*   **Propósito:** Mostrar el Índice de Fuerza Relativa (RSI) actual.
*   **Uso:** Badges de estado y semáforos de compra/venta.
*   **Contexto:** Promedia el RSI a la fecha de corte más reciente.
*   **Fórmula:**
```dax
RSI Actual = 
VAR _UltimaFecha = LASTDATE('financial_market_data'[Date])
RETURN
CALCULATE(AVERAGE('financial_market_data'[RSI_14]), _UltimaFecha)
```

### 🚦 Medida: Estado RSI (Semáforo)
*   **Propósito:** Traducir el número RSI a lenguaje de negocio legible.
*   **Uso:** Etiquetas de texto en las tarjetas.
*   **Contexto:** Lógica condicional: >70 (Sobrecompra/Venta), <30 (Sobreventa/Compra).
*   **Fórmula:**
```dax
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

### 🎨 Medida: Color RSI (Hexadecimal)
*   **Propósito:** Proveer el código de color dinámico para CSS.
*   **Uso:** Estilos `color:` o `background-color:` en las medidas HTML.
*   **Contexto:** Retorna strings hexadecimales (#RRGGBB).
*   **Fórmula:**
```dax
Color RSI = 
VAR _RSI = [RSI Actual]
RETURN
SWITCH(TRUE(),
    _RSI >= 70, "#ff1744", // Rojo
    _RSI <= 30, "#00c853", // Verde
    "#ffea00"              // Amarillo
)
```

### ⚡ Medida: Volatilidad Promedio
*   **Propósito:** Medir el riesgo del activo.
*   **Uso:** Gráficos de barras de riesgo.
*   **Contexto:** Promedio simple de la columna `Volatility_Annualized`.
*   **Fórmula:**
```dax
Volatilidad Promedio = AVERAGE('financial_market_data'[Volatility_Annualized])
```

### 🧭 Medida: Tendencia SMA
*   **Propósito:** Indicar la dirección del mercado (Alcista/Bajista) basada en Medias Móviles.
*   **Uso:** Emojis y texto de tendencia.
*   **Contexto:** Extrae el último valor calculado por Python en la columna `Signal_Trend`.
*   **Fórmula:**
```dax
Tendencia SMA = 
VAR _UltimaFecha = LASTDATE('financial_market_data'[Date])
RETURN
CALCULATE(MAX('financial_market_data'[Signal_Trend]), _UltimaFecha)
```

---

## ⏱️ 4. Indicador de Última Actualización (3 Métodos)

Para garantizar la confianza en el dato, implementamos una solución robusta en 3 pasos/métodos complementarios.

### Método 1: Fuente de Verdad (Power Query)
*   **Propósito:** Capturar la hora del sistema *al momento de la recarga*, no del dato.
*   **Pasos:**
    1.  `Transformar datos` -> `Nueva fuente` -> `Consulta en blanco`.
    2.  Fórmula: `= #table(type table[UltimaCarga=datetime], {{DateTime.LocalNow()}})`
    3.  Nombre: `Refresh_Log`.

### Método 2: Cálculo DAX (Formato)
*   **Propósito:** Formatear la fecha capturada para su visualización.
*   **Fórmula:**
```dax
Ultima_Actualizacion_Real = 
"ÚLTIMA ACTUALIZACIÓN: " & UPPER(FORMAT(MAX('Refresh_Log'[UltimaCarga]), "dd/MM/yyyy HH:mm:ss"))
```

### Método 3: Visualización HTML (Brillante)
*   **Propósito:** Renderizar el dato con alto contraste y estilo "Live".
*   **Tecnología:** HTML + CSS text-shadow.
*   **Fórmula:**
```dax
HTML_LastUpdate_Brilliant = 
VAR _FechaHora = MAX('Refresh_Log'[UltimaCarga])
RETURN
"
<div style='font-family: ""Segoe UI"", sans-serif; color: #ffffff; font-weight: 900; font-size: 14px; letter-spacing: 1px; display: flex; align-items: center; gap: 10px;'>
    <span style='color: #58a6ff; text-shadow: 0 0 5px #58a6ff88;'>[LIVE_SYSTEM_TIME]</span> 
    <span style='text-transform: uppercase;'>" & FORMAT(_FechaHora, "dd/MM/yyyy HH:mm:ss") & "</span>
</div>
"
```

---

## 🎨 5. Detalle de Visuales Avanzados (HTML/CSS)

### 🟦 Visual A: Barra Superior (Ticker Tape)
*   **Tipo:** Tarjetas Horizontales (Scrollable).
*   **Definición:** Una cinta que muestra el resumen rápido de todos los activos disponibles.
*   **Tecnología:** HTML5 Flexbox.
*   **Creación:** Usar medida `HTML_TopBar_Cards1`.
*   **Uso:** Cabecera del reporte.
*   **Código:**
```dax
HTML_TopBar_Cards1 = 
VAR _Filas = CONCATENATEX( ... ) // (Ver código completo en versiones anteriores o archivo adjunto)
// ... Código CSS Flexbox ...
```

### 📋 Visual B: Tabla Ejecutiva v3 (Clean)
*   **Tipo:** Tabla HTML Personalizada.
*   **Definición:** Listado detallado de activos con badges de colores para RSI y emojis para tendencia.
*   **Tecnología:** CSS Grid/Flex, HTML Divs.
*   **Creación:** Usar medida `HTML_Table_Executive_Clean_v3`.
*   **Uso:** Panel central principal. Reemplaza la matriz nativa.
*   **Código:**
```dax
HTML_Table_Executive_Clean_v3 = 
VAR _Filas = 
    CONCATENATEX(
        FILTER(VALUES('financial_market_data'[Ticker]), NOT(ISBLANK('financial_market_data'[Ticker])) && [Precio Actual] > 0),
        VAR _Ticker = 'financial_market_data'[Ticker]
        // ... Variables de lógica ...
        VAR _TrendEmoji = SWITCH(_Trend, "Bullish", "😊", "Bearish", "☹️", "⚖️")
        
        RETURN
        "<div class='t-row'> ... </div>", ""
    )
RETURN
" <style> ... </style> <div class='t-container'> ... " & _Filas & " </div> "
```

### 💎 Visual C: Super Card Master (SVG Chart)
*   **Tipo:** Tarjeta de KPI con Gráfico Integrado.
*   **Definición:** Tarjeta de alto impacto para el activo seleccionado, incluye un gráfico de área con gradiente.
*   **Tecnología:** SVG (Scalable Vector Graphics) generado dinámicamente con DAX.
*   **Creación:** Usar medida `Visual_Impacto_Master_Con_Logos`.
*   **Uso:** Panel de detalle (Drill-down).
*   **Código:**
```dax
Visual_Impacto_Master_Con_Logos = 
// ... Cálculo de coordenadas SVG ...
VAR _Points = CONCATENATEX( ... )
RETURN
" <style> ... </style> <div class='card-container'> ... <svg> ... </svg> </div> "
```

### 📊 Visual D: Barras de Riesgo
*   **Tipo:** Gráfico de Barras HTML.
*   **Definición:** Visualización comparativa de volatilidad.
*   **Tecnología:** CSS width % calculado.
*   **Creación:** Usar medida `HTML_BarChart_Riesgo_Final`.
*   **Uso:** Panel lateral de análisis de riesgo.

### 📈 Visual E: Performance (+/-)
*   **Tipo:** Gráfico de Barras Bidireccional.
*   **Definición:** Muestra ganancias (Verde) y pérdidas (Rojo) desde un eje central.
*   **Tecnología:** Lógica condicional DAX aplicada a estilos CSS background.
*   **Creación:** Usar medida `HTML_BarChart_Performance_Final`.
*   **Uso:** Panel lateral de rendimiento.

---

**Fin del Manual Técnico.**