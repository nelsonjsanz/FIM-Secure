import os
import sys
import subprocess
import sqlite3

# Rutas absolutas seguras basadas en la ubicación del script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
C_BIN = os.path.normpath(os.path.join(BASE_DIR, "..", "build", "fim_hasher.exe"))
DB_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "database", "fim_baseline.db"))

def inicializar_bd():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS archivo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ruta_absoluta TEXT UNIQUE NOT NULL,
            tamano_bytes INTEGER NOT NULL,
            sha256_base TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def registrar_linea_base(ruta_archivo):
    inicializar_bd()
    path_abs = os.path.abspath(ruta_archivo)
    
    if not os.path.exists(path_abs):
        print(f"[ERROR] El archivo no existe en la ruta: {path_abs}")
        sys.exit(1)
    
    if not os.path.exists(C_BIN):
        print(f"[ERROR] No se encuentra el binario compilado en: {C_BIN}. Compílalo primero.")
        sys.exit(1)

    try:
        # Invocar el motor en C pasando la ruta absoluta limpia
        resultado = subprocess.run(
            [C_BIN, path_abs],
            capture_output=True,
            text=True,
            check=True
        )
        hash_sha256 = resultado.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] El motor en C falló: {e.stderr.strip()}")
        sys.exit(1)

    tamano_bytes = os.path.getsize(path_abs)

    # Inserción segura usando consultas parametrizadas (Mitigación SQLi)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO archivo (ruta_absoluta, tamano_bytes, sha256_base)
        VALUES (?, ?, ?)
    """, (path_abs, tamano_bytes, hash_sha256))
    conn.commit()
    conn.close()

    print(f"[OK] Línea base registrada para: {path_abs}")
    print(f"     SHA-256: {hash_sha256}")

def verificar_integridad(ruta_archivo):
    path_abs = os.path.abspath(ruta_archivo)
    
    if not os.path.exists(path_abs):
        print(f"[!] El archivo ya no existe: {path_abs}")
        return

    try:
        resultado = subprocess.run(
            [C_BIN, path_abs],
            capture_output=True,
            text=True,
            check=True
        )
        hash_actual = resultado.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] El motor en C falló: {e.stderr.strip()}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT sha256_base FROM archivo WHERE ruta_absoluta = ?", (path_abs,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"[!] El archivo no tiene una línea base registrada: {path_abs}")
        return

    hash_base = row[0]

    if hash_actual == hash_base:
        print(f"[OK] El archivo está íntegro. No ha sufrido alteraciones.")
        print(f"     Hash actual: {hash_actual}")
    else:
        print(f"[¡ALERTA!] ¡Se detectó una modificación no autorizada en el archivo!")
        print(f"  - Hash Base (Original): {hash_base}")
        print(f"  - Hash Actual (Alterado): {hash_actual}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso correcto:")
        print("  Registrar línea base: python src/fim_orchestrator.py --baseline <archivo>")
        print("  Verificar integridad:  python src/fim_orchestrator.py --check <archivo>")
        sys.exit(1)

    accion = sys.argv[1]
    archivo = sys.argv[2]

    if accion == "--baseline":
        registrar_linea_base(archivo)
    elif accion == "--check":
        verificar_integridad(archivo)
    else:
        print(f"Acción desconocida: {accion}")
        sys.exit(1)