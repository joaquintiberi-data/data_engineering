# ============================================================
# GENERADOR DE DATOS FICTICIOS - SENSORES IoT AGRÍCOLAS (JSON)
# Diseñado para ejecutarse en Google Colab
# Genera 5 archivos .json DESNORMALIZADOS (duplicados, nulos,
# IDs repetidos, formatos inconsistentes), listos para subir a
# un repositorio de GitHub y usarse como "API" simulada.
# ============================================================

import pandas as pd
import numpy as np
import random
import zipfile
import os
from datetime import datetime, timedelta

# Semilla para reproducibilidad (podés comentarla si querés datos distintos cada vez)
random.seed(42)
np.random.seed(42)

# ------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ------------------------------------------------------------
N_AGRICULTORES    = 100
N_PARCELAS        = 120
N_SENSORES        = 150
N_LECTURAS        = 600
N_MANTENIMIENTOS  = 110

OUTPUT_DIR = "datos_iot_agricola_json"
ZIP_NAME   = "datos_iot_agricola_json.zip"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ------------------------------------------------------------
# UTILIDADES PARA "ENSUCIAR" LOS DATOS (desnormalización)
# ------------------------------------------------------------

def con_nulos(serie, prob=0.08):
    serie = list(serie)
    for i in range(len(serie)):
        if random.random() < prob:
            serie[i] = None
    return serie

def duplicar_filas(df, prob=0.06):
    filas_dup = df.sample(frac=prob, replace=False, random_state=random.randint(0, 9999))
    return pd.concat([df, filas_dup], ignore_index=True)

def inconsistencia_texto(valor):
    if pd.isna(valor):
        return valor
    opcion = random.choice(["normal", "mayus", "minus", "espacios"])
    if opcion == "mayus":
        return str(valor).upper()
    elif opcion == "minus":
        return str(valor).lower()
    elif opcion == "espacios":
        return f"  {valor}  "
    return valor

def fecha_formato_random(fecha):
    formatos = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]
    return fecha.strftime(random.choice(formatos))

def id_texto_random(prefijo, numero):
    formatos = [
        f"{prefijo}{numero:04d}",
        f"{prefijo}-{numero}",
        f"{prefijo.lower()}{numero}",
        f"{prefijo}_{numero:03d}",
    ]
    return random.choice(formatos)

# ------------------------------------------------------------
# 1) AGRICULTORES
# ------------------------------------------------------------
nombres = ["Juan", "María", "Carlos", "Ana", "Luis", "Sofía", "Pedro", "Lucía",
           "Miguel", "Valentina", "Diego", "Camila", "Jorge", "Paula", "Andrés"]
apellidos = ["Gómez", "Rodríguez", "Fernández", "López", "Martínez", "Pérez",
             "García", "Sánchez", "Romero", "Torres", "Flores", "Díaz"]
provincias = ["Buenos Aires", "Córdoba", "Santa Fe", "Mendoza", "Entre Ríos",
              "Tucumán", "Chaco", "La Pampa"]

agricultores = []
for i in range(1, N_AGRICULTORES + 1):
    agricultores.append({
        "id_agricultor": f"AGR{i:04d}",
        "nombre": random.choice(nombres),
        "apellido": random.choice(apellidos),
        "email": f"agricultor{i}@correo.com" if random.random() > 0.05 else None,
        "telefono": f"+54 9 {random.randint(1100000000, 3999999999)}",
        "provincia": inconsistencia_texto(random.choice(provincias)),
        "fecha_alta": fecha_formato_random(datetime(2019, 1, 1) + timedelta(days=random.randint(0, 2000))),
    })

df_agricultores = pd.DataFrame(agricultores)
df_agricultores["email"] = con_nulos(df_agricultores["email"], prob=0.05)
df_agricultores = duplicar_filas(df_agricultores, prob=0.07)

# ------------------------------------------------------------
# 2) PARCELAS (denormalizada con datos del agricultor)
# ------------------------------------------------------------
tipos_cultivo = ["Soja", "Maíz", "Trigo", "Girasol", "Vid", "Algodón", "Alfalfa"]

parcelas = []
for i in range(1, N_PARCELAS + 1):
    agricultor = df_agricultores.sample(1).iloc[0]
    parcelas.append({
        "id_parcela": id_texto_random("PAR", i),
        "nombre_parcela": f"Campo {random.choice(['Norte','Sur','Este','Oeste','Central'])} {i}",
        "id_agricultor": agricultor["id_agricultor"],
        "nombre_agricultor": inconsistencia_texto(f"{agricultor['nombre']} {agricultor['apellido']}"),
        "provincia": inconsistencia_texto(agricultor["provincia"]),
        "cultivo_principal": random.choice(tipos_cultivo),
        "superficie_ha": round(random.uniform(2, 500), 2) if random.random() > 0.06 else None,
        "fecha_siembra": fecha_formato_random(datetime(2023, 6, 1) + timedelta(days=random.randint(0, 400))),
    })

df_parcelas = pd.DataFrame(parcelas)
df_parcelas = duplicar_filas(df_parcelas, prob=0.08)

# ------------------------------------------------------------
# 3) SENSORES (denormalizada con datos de la parcela)
# ------------------------------------------------------------
tipos_sensor = ["Humedad de suelo", "Temperatura", "Humedad ambiente",
                "pH de suelo", "Luminosidad", "Pluviómetro", "Velocidad de viento"]
marcas = ["AgroSense", "FarmTech", "CropIoT", "SoilLink", "GreenNet"]
estados = ["Activo", "Inactivo", "Mantenimiento", "activo", "ACTIVO", None]

sensores = []
for i in range(1, N_SENSORES + 1):
    parcela = df_parcelas.sample(1).iloc[0]
    sensores.append({
        "id_sensor": id_texto_random("SEN", i),
        "tipo_sensor": random.choice(tipos_sensor),
        "marca": random.choice(marcas),
        "id_parcela": parcela["id_parcela"],
        "nombre_parcela": parcela["nombre_parcela"],
        "cultivo_asociado": parcela["cultivo_principal"],
        "fecha_instalacion": fecha_formato_random(datetime(2022, 1, 1) + timedelta(days=random.randint(0, 900))),
        "estado": random.choice(estados),
        "latitud": round(random.uniform(-40, -22), 6) if random.random() > 0.05 else None,
        "longitud": round(random.uniform(-68, -57), 6) if random.random() > 0.05 else None,
    })

df_sensores = pd.DataFrame(sensores)
df_sensores = duplicar_filas(df_sensores, prob=0.10)

# ------------------------------------------------------------
# 4) LECTURAS (denormalizada con datos del sensor)
# ------------------------------------------------------------
lecturas = []
base_time = datetime(2025, 1, 1)
for i in range(1, N_LECTURAS + 1):
    sensor = df_sensores.sample(1).iloc[0]
    timestamp = base_time + timedelta(minutes=random.randint(0, 200000))
    lecturas.append({
        "id_lectura": i,
        "id_sensor": sensor["id_sensor"],
        "tipo_sensor": sensor["tipo_sensor"],
        "nombre_parcela": sensor["nombre_parcela"],
        "timestamp": random.choice([
            timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            timestamp.strftime("%d/%m/%Y %H:%M"),
            timestamp.isoformat(),
        ]),
        "temperatura_c": round(random.uniform(-5, 42), 1) if random.random() > 0.07 else None,
        "humedad_suelo_%": round(random.uniform(5, 95), 1) if random.random() > 0.07 else None,
        "humedad_ambiente_%": round(random.uniform(10, 100), 1) if random.random() > 0.10 else None,
        "ph_suelo": round(random.uniform(4.5, 8.5), 2) if random.random() > 0.15 else None,
        "bateria_%": random.randint(0, 100) if random.random() > 0.05 else None,
    })

df_lecturas = pd.DataFrame(lecturas)
df_lecturas = duplicar_filas(df_lecturas, prob=0.12)

# ------------------------------------------------------------
# 5) MANTENIMIENTOS (denormalizada con datos del sensor)
# ------------------------------------------------------------
tipos_mantenimiento = ["Cambio de batería", "Calibración", "Limpieza",
                        "Reemplazo de sensor", "Revisión de conectividad"]
tecnicos = ["Equipo Norte", "Equipo Sur", "Contratista externo", "Soporte remoto"]

mantenimientos = []
for i in range(1, N_MANTENIMIENTOS + 1):
    sensor = df_sensores.sample(1).iloc[0]
    mantenimientos.append({
        "id_mantenimiento": id_texto_random("MNT", i),
        "id_sensor": sensor["id_sensor"],
        "tipo_sensor": sensor["tipo_sensor"],
        "nombre_parcela": sensor["nombre_parcela"],
        "tipo_mantenimiento": random.choice(tipos_mantenimiento),
        "tecnico_responsable": inconsistencia_texto(random.choice(tecnicos)),
        "fecha_mantenimiento": fecha_formato_random(datetime(2023, 1, 1) + timedelta(days=random.randint(0, 900))),
        "costo_usd": round(random.uniform(5, 300), 2) if random.random() > 0.10 else None,
        "observaciones": random.choice([
            "Sin novedades", "Sensor con ruido en lectura", None,
            "  Reemplazo parcial  ", "PENDIENTE REVISION", None
        ]),
    })

df_mantenimientos = pd.DataFrame(mantenimientos)
df_mantenimientos = duplicar_filas(df_mantenimientos, prob=0.09)

# ------------------------------------------------------------
# VERIFICACIÓN DE MÍNIMOS (100 registros por tabla)
# ------------------------------------------------------------
tablas = {
    "agricultores.json": df_agricultores,
    "parcelas.json": df_parcelas,
    "sensores.json": df_sensores,
    "lecturas.json": df_lecturas,
    "mantenimientos.json": df_mantenimientos,
}

for nombre, df in tablas.items():
    print(f"{nombre}: {len(df)} registros")
    assert len(df) >= 100, f"{nombre} tiene menos de 100 registros"

# ------------------------------------------------------------
# GUARDAR JSON (un array de objetos por archivo -> cada archivo
# será un "endpoint" cuando lo subas a GitHub)
# ------------------------------------------------------------
for nombre, df in tablas.items():
    ruta = os.path.join(OUTPUT_DIR, nombre)
    # NaN -> None -> null en JSON. orient="records" = lista de objetos.
    df.where(pd.notnull(df), None).to_json(
        ruta, orient="records", indent=2, force_ascii=False
    )

# Además, un único db.json con todas las tablas combinadas
# (útil si tu profe pide un solo archivo tipo "json-server")
db_combinado = {
    "agricultores": df_agricultores.where(pd.notnull(df_agricultores), None).to_dict(orient="records"),
    "parcelas": df_parcelas.where(pd.notnull(df_parcelas), None).to_dict(orient="records"),
    "sensores": df_sensores.where(pd.notnull(df_sensores), None).to_dict(orient="records"),
    "lecturas": df_lecturas.where(pd.notnull(df_lecturas), None).to_dict(orient="records"),
    "mantenimientos": df_mantenimientos.where(pd.notnull(df_mantenimientos), None).to_dict(orient="records"),
}
import json
with open(os.path.join(OUTPUT_DIR, "db.json"), "w", encoding="utf-8") as f:
    json.dump(db_combinado, f, indent=2, ensure_ascii=False)

# ------------------------------------------------------------
# COMPRIMIR EN .ZIP
# ------------------------------------------------------------
with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zipf:
    for archivo in os.listdir(OUTPUT_DIR):
        zipf.write(os.path.join(OUTPUT_DIR, archivo), arcname=archivo)

print(f"\n✅ Archivo '{ZIP_NAME}' generado con {len(tablas)} JSON + db.json combinado.")

# ------------------------------------------------------------
# DESCARGA AUTOMÁTICA (solo funciona dentro de Google Colab)
# ------------------------------------------------------------
try:
    from google.colab import files
    files.download(ZIP_NAME)
except ImportError:
    print("⚠️ No estás en Google Colab: el .zip quedó guardado en el directorio actual, "
          "descargalo manualmente.")