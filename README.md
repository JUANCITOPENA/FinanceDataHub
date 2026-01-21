# Finance Data Hub

Este proyecto automatiza la extracción de datos financieros y los sincroniza con GitHub para su consumo en Power BI.

## Módulos
1. **Mercado:** Descarga precios de AAPL, MSFT, BTC, ETH desde Yahoo Finance.
2. **Finanzas:** Registro de ingresos y gastos (Simulado para demo).
3. **Inventario:** Control de stock y valoración (Simulado para demo).

## Cómo funciona
1. El script `main_loop.py` se ejecuta localmente.
2. Descarga/Genera archivos CSV en la carpeta `data/`.
3. Hace un `git push` automático a este repositorio.
4. Power BI conecta a los archivos CSV vía web ("Raw GitHub").

## Instalación
1. Crear entorno: `python -m venv venv`
2. Instalar: `pip install -r requirements.txt`
3. Ejecutar: `python main_loop.py`
