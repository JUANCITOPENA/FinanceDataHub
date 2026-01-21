import pandas as pd
import os
import random
from datetime import datetime, timedelta

class FinanceManager:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        
    def generate_dummy_data(self):
        # Si el archivo ya existe, no lo sobrescribimos para no borrar tus cambios manuales
        output_path = os.path.join(self.output_dir, "finanzas_personales.csv")
        if os.path.exists(output_path):
            print("INFO: Archivo de finanzas ya existe. Saltando generación.")
            return

        print("--- Generando Finanzas Personales (Simulado) ---")
        data = []
        categorias = ["Salario", "Freelance", "Renta", "Comida", "Transporte", "Servicios", "Inversión"]
        tipo = {"Salario": "Ingreso", "Freelance": "Ingreso", "Renta": "Egreso", "Comida": "Egreso", "Transporte": "Egreso", "Servicios": "Egreso", "Inversión": "Egreso"}
        
        start_date = datetime.now() - timedelta(days=365)
        for i in range(100):
            cat = random.choice(categorias)
            monto = random.randint(50, 2000) if tipo[cat] == "Egreso" else random.randint(3000, 8000)
            fecha = start_date + timedelta(days=random.randint(0, 365))
            
            data.append({
                "Fecha": fecha.strftime("%Y-%m-%d"),
                "Categoria": cat,
                "Tipo": tipo[cat],
                "Monto": monto,
                "Descripcion": f"Movimiento simulado {i+1}"
            })
            
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        print(f"ÉXITO: Finanzas guardadas en {output_path}")

class InventoryManager:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        
    def generate_dummy_data(self):
        output_path = os.path.join(self.output_dir, "inventario.csv")
        if os.path.exists(output_path):
             print("INFO: Archivo de inventario ya existe. Saltando generación.")
             return

        print("--- Generando Inventario (Simulado) ---")
        productos = [
            {"ID": "P001", "Nombre": "Laptop Gamer", "Costo": 800, "Precio": 1200},
            {"ID": "P002", "Nombre": "Mouse Inalámbrico", "Costo": 10, "Precio": 25},
            {"ID": "P003", "Nombre": "Monitor 4K", "Costo": 200, "Precio": 450},
            {"ID": "P004", "Nombre": "Teclado Mecánico", "Costo": 40, "Precio": 90},
            {"ID": "P005", "Nombre": "Auriculares", "Costo": 30, "Precio": 70},
        ]
        
        data = []
        for p in productos:
            stock = random.randint(0, 50)
            p["Stock"] = stock
            p["Valor_Total"] = stock * p["Costo"]
            data.append(p)
            
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        print(f"ÉXITO: Inventario guardado en {output_path}")
