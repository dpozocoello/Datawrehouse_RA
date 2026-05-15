"""
Monitor ETL — Data Warehouse Regularización Ambiental
Frecuencia: cada 20 minutos
Alertas en: TRX_10_AREAS, SP_CARGA_DIM_AREA, SP_JERARQUIA_AREA
"""
import os
import sys
import time
import glob
import re
from datetime import datetime

LOG_DIR = r"D:\Datawrehouse_RA\logs"
INTERVALO_SEG = 20 * 60  # 20 minutos

# Pasos críticos que disparan alerta
PASOS_CRITICOS = {
    "TRX_10_AREAS",
    "TRX_10B_AREAS_TYPES",
    "SP_CARGA_DIM_AREA",
    "SP_JERARQUIA_AREA",
}

# Todos los pasos en orden (para calcular progreso)
PASOS_ORDEN = [
    "SP_ORQUESTAR_EXTRACCION",
    "TRX_01_SUIA_RCOA",
    "TRX_02_SUIA_COA",
    "TRX_03_JBPM_SECTOR",
    "TRX_04_JBPM_4CAT",
    "TRX_05_JBPM_HIDRO",
    "TRX_06_SNAP",
    "TRX_07_PAGOS_JBPM",
    "TRX_08_PAGOS_SUIA",
    "TRX_09_PAGOS_HIST",
    "TRX_10_AREAS",
    "TRX_10B_AREAS_TYPES",
    "TRX_11_GEOGRAFIA",
    "SETUP_REFERENCE_DATA",
    "SP_CONSOLIDAR_STAGING",
    "SP_CARGA_DIMENSIONES",
    "SP_CARGA_DIM_AREA",
    "SP_JERARQUIA_AREA",
    "SP_CARGA_HECHOS",
    "SP_CARGA_DIM_PAGO",
    "SP_CARGA_FACT_PAGO",
    "UPDATE_AREA_RESPONSABLE",
    "SP_BRIDGE_PROYECTO_GEO",
    "RECALCULO_MONTOS_JBPM",
    "SP_SECUENCIA_PAGOS",
    "SP_CARGA_PUENTE_AMBIENTAL",
    "INGESTA_WASTE_CHEMICAL",
    "SP_CARGA_WASTE_CHEMICAL",
    "INGESTA_INTERSECTION",
    "RECOVER_MISSING_PROJECTS",
    "SP_CARGA_DIM_INTERSECTION",
]

def encontrar_log_activo():
    """Busca el log ETL más reciente."""
    patron = os.path.join(LOG_DIR, "etl_completo_*.log")
    logs = sorted(glob.glob(patron), reverse=True)
    return logs[0] if logs else None

def analizar_log(ruta_log):
    """Analiza el log y retorna estado actual."""
    with open(ruta_log, encoding="utf-8", errors="replace") as f:
        lineas = f.readlines()

    completados = []
    en_curso = None
    registros = {}
    errores = []
    finalizado = False
    resultado_final = None

    for linea in lineas:
        linea = linea.strip()

        # Detectar paso completado
        m = re.search(r"\[(\w+)\] \[OK\] COMPLETADO en ([\d]+m [\d.]+s)", linea)
        if m:
            paso, duracion = m.group(1), m.group(2)
            completados.append((paso, duracion))

        # Detectar paso en inicio (en curso)
        m = re.search(r"\[(\w+)\] \[START\] INICIANDO\.\.\.", linea)
        if m:
            en_curso = m.group(1)

        # Detectar registros cargados
        m = re.search(r"\[(\w+)\] .* Completado: ([\d,]+) filas cargadas en (\S+)", linea)
        if m:
            registros[m.group(1)] = (m.group(2), m.group(3))

        # Detectar errores
        if "ERROR" in linea or "[FAIL]" in linea or "Exception" in linea:
            errores.append(linea[:120])

        # Detectar finalización
        if "RESULTADO: EXITOSO" in linea or "ETL COMPLETADO" in linea:
            finalizado = True
            resultado_final = "✅ EXITOSO"
        elif "RESULTADO: FALLIDO" in linea or "ETL FALLIDO" in linea:
            finalizado = True
            resultado_final = "❌ FALLIDO"

    return {
        "completados": completados,
        "en_curso": en_curso,
        "registros": registros,
        "errores": errores,
        "finalizado": finalizado,
        "resultado_final": resultado_final,
        "total_lineas": len(lineas),
    }

def imprimir_reporte(estado, ruta_log, ronda):
    """Imprime reporte de estado."""
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    completados = estado["completados"]
    en_curso = estado["en_curso"]
    n_completados = len(completados)
    total = len(PASOS_ORDEN)
    pct = round(n_completados / total * 100, 1)

    barra = "█" * (n_completados * 20 // total) + "░" * (20 - n_completados * 20 // total)

    print("\n" + "=" * 70)
    print(f"  🔍 MONITOR ETL — Ronda #{ronda}  |  {ahora}")
    print(f"  Log: {os.path.basename(ruta_log)}")
    print("=" * 70)
    print(f"\n  Progreso: [{barra}] {n_completados}/{total} ({pct}%)\n")

    # Últimos 3 completados
    if completados:
        print("  ✅ Últimos pasos completados:")
        for paso, dur in completados[-3:]:
            regs = estado["registros"].get(paso, ("", ""))
            regs_str = f"  → {regs[0]} filas en {regs[1]}" if regs[0] else ""
            print(f"     • {paso:<35} ({dur}){regs_str}")

    # Paso en curso
    if en_curso and not estado["finalizado"]:
        critico = " ⚠️  PASO CRÍTICO" if en_curso in PASOS_CRITICOS else ""
        print(f"\n  🔄 EN EJECUCIÓN AHORA: {en_curso}{critico}")

    # Próximos pasos críticos pendientes
    pasos_hechos = {p for p, _ in completados}
    criticos_pendientes = [p for p in PASOS_ORDEN if p in PASOS_CRITICOS and p not in pasos_hechos]
    if criticos_pendientes:
        print(f"\n  ⏳ Pasos críticos pendientes:")
        for p in criticos_pendientes:
            estado_paso = "🔄 EN CURSO" if p == en_curso else "⏳ Pendiente"
            print(f"     • {p} — {estado_paso}")

    # Alertas
    if en_curso in PASOS_CRITICOS:
        print(f"\n  {'!'*60}")
        print(f"  🚨 ALERTA: El paso crítico [{en_curso}] ESTÁ EN EJECUCIÓN AHORA")
        print(f"  {'!'*60}")

    # Pasos críticos recién completados (últimos 5)
    for paso, dur in completados[-5:]:
        if paso in PASOS_CRITICOS:
            print(f"\n  🎯 PASO CRÍTICO COMPLETADO: [{paso}] en {dur}")

    # Errores
    if estado["errores"]:
        print(f"\n  ❌ ERRORES DETECTADOS ({len(estado['errores'])}):")
        for err in estado["errores"][:5]:
            print(f"     {err}")

    # Finalizado
    if estado["finalizado"]:
        print(f"\n  {'='*60}")
        print(f"  RESULTADO FINAL: {estado['resultado_final']}")
        print(f"  Total pasos completados: {n_completados}")
        total_regs = sum(int(v[0].replace(",", "")) for v in estado["registros"].values() if v[0])
        print(f"  Total registros cargados: {total_regs:,}")
        print(f"  {'='*60}")

    print()
    return estado["finalizado"]

def main():
    print("=" * 70)
    print("  MONITOR ETL — Regularización Ambiental v3.0")
    print(f"  Frecuencia: cada 20 minutos")
    print(f"  Pasos críticos vigilados: {', '.join(PASOS_CRITICOS)}")
    print(f"  Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    ronda = 0
    while True:
        ronda += 1
        ruta_log = encontrar_log_activo()

        if not ruta_log:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ⚠️  No se encontró log ETL activo en {LOG_DIR}")
        else:
            estado = analizar_log(ruta_log)
            finalizado = imprimir_reporte(estado, ruta_log, ronda)
            if finalizado:
                print("✓ ETL finalizado. Monitor detenido.")
                break

        # Contar regresivamente
        print(f"  Próxima verificación en 20 minutos... (Ctrl+C para detener)\n")
        for mins_restantes in range(20, 0, -1):
            sys.stdout.write(f"\r  ⏱  Próxima verificación en: {mins_restantes:02d} min...")
            sys.stdout.flush()
            time.sleep(60)
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Monitor detenido manualmente.")
