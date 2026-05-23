# -*- coding: utf-8 -*-
"""
Script para detectar drift (deriva) en los datos que llegan a la API.
Compara los datos actuales con la baseline generada en el Sprint 2.
Genera reportes JSON y opcionalmente envía alertas a CloudWatch.
"""

import json
import os
import pandas as pd
import numpy as np
from datetime import datetime

# -------------------------------------------------------------
# Configuración
# -------------------------------------------------------------
BASELINE_FILE = "models/c_baseline_stats.json"   # Archivo con estadísticas de entrenamiento
REPORTS_DIR = "reports"                           # Carpeta donde guardar reportes
REPORT_PREFIX = "drift_report"                    # Prefijo para los reportes
DRIFT_THRESHOLD = 0.2                             # 20% de variables fuera de rango = drift
USE_CLOUDWATCH = False                            # Cambiar a True si tienes AWS configurado

# -------------------------------------------------------------
# Funciones auxiliares
# -------------------------------------------------------------
def crear_baseline_si_no_existe():
    """Si no existe el archivo baseline, lo crea con valores por defecto (basados en los contratos)."""
    if os.path.exists(BASELINE_FILE):
        print(f"Usando baseline existente: {BASELINE_FILE}")
        return
    
    print(f"No se encontró {BASELINE_FILE}. Creando baseline por defecto...")
    baseline_default = {
        "Administrative": {"min": 0, "max": 10, "mean": 2.5, "std": 2.0},
        "Administrative_Duration": {"min": 0, "max": 500, "mean": 80, "std": 100},
        "Informational": {"min": 0, "max": 5, "mean": 0.5, "std": 1.0},
        "Informational_Duration": {"min": 0, "max": 300, "mean": 20, "std": 50},
        "ProductRelated": {"min": 0, "max": 50, "mean": 15, "std": 10},
        "ProductRelated_Duration": {"min": 0, "max": 2000, "mean": 500, "std": 400},
        "BounceRates": {"min": 0, "max": 0.8, "mean": 0.3, "std": 0.2},
        "ExitRates": {"min": 0, "max": 0.8, "mean": 0.2, "std": 0.15},
        "PageValues": {"min": 0, "max": 20, "mean": 2, "std": 3},
        "SpecialDay": {"min": 0, "max": 1, "mean": 0.05, "std": 0.1}
    }
    os.makedirs(os.path.dirname(BASELINE_FILE), exist_ok=True)
    with open(BASELINE_FILE, "w") as f:
        json.dump(baseline_default, f, indent=2)
    print(f"Baseline creada en {BASELINE_FILE}")

def cargar_baseline():
    """Carga el archivo baseline JSON."""
    with open(BASELINE_FILE, "r") as f:
        return json.load(f)

def guardar_reporte(reporte):
    """Guarda el reporte como JSON en la carpeta reports/ con timestamp."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{REPORT_PREFIX}_{fecha}.json"
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    print(f"Reporte guardado en: {filepath}")
    return filepath

def enviar_a_cloudwatch(reporte):
    """Envía el reporte a CloudWatch Logs (opcional, requiere boto3 y credenciales)."""
    if not USE_CLOUDWATCH:
        return
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError
        log_group = "/sprint6/drift_monitor"
        log_stream = datetime.now().strftime("%Y-%m-%d")
        logs = boto3.client("logs")
        # Crear log group si no existe
        try:
            logs.create_log_group(logGroupName=log_group)
        except logs.exceptions.ResourceAlreadyExistsException:
            pass
        # Crear log stream si no existe
        try:
            logs.create_log_stream(logGroupName=log_group, logStreamName=log_stream)
        except logs.exceptions.ResourceAlreadyExistsException:
            pass
        # Enviar evento
        event = {
            "timestamp": int(datetime.now().timestamp() * 1000),
            "message": json.dumps(reporte)
        }
        logs.put_log_events(
            logGroupName=log_group,
            logStreamName=log_stream,
            logEvents=[event]
        )
        print("Reporte enviado a CloudWatch Logs")
    except ImportError:
        print("boto3 no instalado. No se pudo enviar a CloudWatch.")
    except NoCredentialsError:
        print("Credenciales AWS no encontradas. No se pudo enviar a CloudWatch.")
    except Exception as e:
        print(f"Error enviando a CloudWatch: {e}")

def revisar_drift(datos, baseline, umbral=DRIFT_THRESHOLD):
    """
    Revisa si hay drift en los datos.
    - datos: DataFrame con las mismas columnas que el modelo
    - baseline: dict con estadísticas de entrenamiento
    - umbral: porcentaje de variables fuera de rango que dispara drift
    Retorna un dict con el reporte.
    """
    reporte = {
        "timestamp": datetime.now().isoformat(),
        "total_filas": len(datos),
        "drift_detectado": False,
        "variables_con_drift": [],
        "detalles": []
    }
    
    variables_fuera = 0
    for col in datos.columns:
        if col in baseline:
            minimo = baseline[col]["min"]
            maximo = baseline[col]["max"]
            media_esperada = baseline[col]["mean"]
            # Calcular cuántos valores están fuera del rango esperado
            fuera_rango = ((datos[col] < minimo) | (datos[col] > maximo)).sum()
            if fuera_rango > 0:
                # Calcular la media real para comparar
                media_real = datos[col].mean()
                reporte["detalles"].append({
                    "variable": col,
                    "rango_esperado": [minimo, maximo],
                    "media_esperada": media_esperada,
                    "media_real": round(media_real, 2),
                    "registros_fuera": int(fuera_rango),
                    "porcentaje_fuera": round(100 * fuera_rango / len(datos), 1)
                })
                variables_fuera += 1
                if fuera_rango / len(datos) > 0.05:  # más del 5% de registros fuera
                    reporte["variables_con_drift"].append(col)
    
    if variables_fuera > len(baseline) * umbral:
        reporte["drift_detectado"] = True
        reporte["mensaje"] = "Drift significativo detectado. Revisar distribuciones."
    else:
        reporte["mensaje"] = "Sin drift significativo."
    
    return reporte

# -------------------------------------------------------------
# Main
# -------------------------------------------------------------
if __name__ == "__main__":
    # 1. Asegurar que existe baseline
    crear_baseline_si_no_existe()
    baseline_stats = cargar_baseline()
    
    # 2. Cargar datos de prueba (aquí deberían venir de logs reales)
    # Por ahora usamos un DataFrame de ejemplo con datos fuera de rango
    print("Cargando datos de prueba...")
    datos_prueba = pd.DataFrame({
        "Administrative": [12, 1, 5, 3, 8],      # 12 fuera del rango 0-10
        "ProductRelated": [20, 55, 45, 30, 25],  # 55 fuera del rango 0-50
        "BounceRates": [0.1, 0.9, 0.2, 0.3, 0.05] # 0.9 fuera del rango 0-0.8
    })
    
    # 3. Revisar drift
    resultado = revisar_drift(datos_prueba, baseline_stats)
    
    # 4. Mostrar en consola
    print("\n=== RESULTADO DEL MONITOREO DE DRIFT ===\n")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    
    # 5. Guardar reporte en disco
    archivo_reporte = guardar_reporte(resultado)
    
    # 6. Enviar a CloudWatch si está configurado
    enviar_a_cloudwatch(resultado)
    
    # 7. Salir con código de error si hay drift (útil para CI/CD)
    if resultado["drift_detectado"]:
        print("\n⚠️  Se detectó drift. El script termina con error (código 1).")
        exit(1)
    else:
        print("\n✅ Sin drift. Todo normal.")
        exit(0)