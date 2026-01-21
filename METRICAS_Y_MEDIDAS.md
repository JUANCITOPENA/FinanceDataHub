# Guía de Implementación en Power BI - FinanceDataHub

Esta guía detalla cómo configurar Power BI para consumir los datos generados por el script Python y las métricas clave para analizar el mercado.

## 1. Conexión a los Datos (Fuente)

Para asegurar que Power BI se actualice automáticamente desde GitHub (o localmente):

### Opción A: Conexión Local (Desarrollo)
1. Abrir Power BI Desktop.
2. `Obtener datos` -> `Texto/CSV`.
3. Seleccionar el archivo: `FinanceDataHub/data/financial_market_data.csv`.

### Opción B: Conexión GitHub (Producción/Nube)
1. Hacer Push de los datos a GitHub.
2. Ir al archivo `.csv` en GitHub -> Clic en botón **Raw**.
3. Copiar la URL (ej: `https://raw.githubusercontent.com/.../financial_market_data.csv`).
4. En Power BI: `Obtener datos` -> `Web` -> Pegar la URL.

---

## 2. Modelado de Datos

Asegúrate de que las columnas tengan el tipo correcto:
- **Date:** Tipo Fecha (Date).
- **Close, Open, High, Low:** Tipo Número Decimal (Decimal Number).
- **Daily_Return_Pct:** Tipo Porcentaje (Percentage) o Decimal.
- **RSI_14:** Número entero o decimal.

**Recomendación:** Crea una tabla calendario (`DimDate`) y relacionala con la columna `Date` de tus datos.

---

## 3. Medidas DAX (Measures) Sugeridas

Copia y pega estas fórmulas en tu modelo de Power BI.

### A. Precios y Variación
```dax
// Precio de Cierre más reciente
Precio Actual = 
CALCULATE(
    SUM('financial_market_data'[Close]),
    LASTDATE('financial_market_data'[Date])
)

// Retorno Diario Promedio
Retorno Promedio = AVERAGE('financial_market_data'[Daily_Return_Pct])

// Variación Total (Selección Actual)
Variación % = 
VAR PrecioInicio = CALCULATE(SUM('financial_market_data'[Close]), FIRSTDATE('financial_market_data'[Date]))
VAR PrecioFin = [Precio Actual]
RETURN
DIVIDE(PrecioFin - PrecioInicio, PrecioInicio)
```

### B. Indicadores Técnicos
```dax
// Último RSI registrado
RSI Actual = 
CALCULATE(
    AVERAGE('financial_market_data'[RSI_14]),
    LASTDATE('financial_market_data'[Date])
)

// Volatilidad Promedio (Riesgo)
Volatilidad Promedio = AVERAGE('financial_market_data'[Volatility_Annualized])
```

### C. Semáforos (KPIs)
```dax
// Estado del RSI (Para formato condicional o Tarjetas)
Estado RSI = 
SWITCH(
    TRUE(),
    [RSI Actual] >= 70, "Sobrecompra (Vender)",
    [RSI Actual] <= 30, "Sobreventa (Comprar)",
    "Neutral"
)

// Tendencia de Mercado (Basado en SMA)
Tendencia SMA = 
CALCULATE(
    MAX('financial_market_data'[Signal_Trend]),
    LASTDATE('financial_market_data'[Date])
)
```

---

## 4. Formatos Condicionales y Visualización

### Reglas para Colores (Fondo o Fuente)

**1. Retorno Diario (%)**
- **Estilo:** Gradiente o Reglas.
- **Regla:**
    - Si valor > 0 -> **Verde** (Ganancia).
    - Si valor < 0 -> **Rojo** (Pérdida).
    - Si valor = 0 -> **Gris**.

**2. RSI (Semáforo de Riesgo)**
- Aplicar a la columna o tarjeta de RSI.
- **Regla:**
    - Si RSI >= 70 -> **Rojo Oscuro** (Peligro/Venta).
    - Si RSI <= 30 -> **Verde Oscuro** (Oportunidad/Compra).
    - Entre 30 y 70 -> **Amarillo/Transparente** (Normal).

### Gráficos Recomendados
1. **Gráfico de Líneas:**
   - Eje X: `Date`
   - Eje Y: `Close`
   - Leyenda: `Ticker`
   - *Objetivo: Ver la evolución del precio.*

2. **Gráfico de Dispersión (Riesgo vs Retorno):**
   - Eje X: `Volatilidad Promedio`
   - Eje Y: `Retorno Promedio`
   - Leyenda: `Ticker`
   - *Objetivo: Comparar qué activo paga mejor por el riesgo asumido.*

3. **Matriz de Correlación (Avanzado):**
   - Usar visuales de Python/R en Power BI para ver correlación entre activos.
