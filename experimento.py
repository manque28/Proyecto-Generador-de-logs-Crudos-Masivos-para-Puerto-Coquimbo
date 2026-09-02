import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Importamos la lógica original intacta sin alterar tus archivos base
from src.main import worker_shard

# Configuración del experimento basado en los requisitos
EVENTOS_TOTALES = 100_000
CARPETA_SALIDA = Path("data/raw")
SEMILLA_BASE = 42

def ejecutar_secuencial():
    """Generador secuencial pura de la Semana 3."""
    print("--> Ejecutando Generador Secuencial (1 Worker, 100k eventos)...")
    inicio = time.perf_counter()
    
    # Llama directamente al shard secuencial original
    stats = worker_shard(wid=0, n_eventos=EVENTOS_TOTALES, carpeta=CARPETA_SALIDA, semilla=SEMILLA_BASE)
    
    tiempo = time.perf_counter() - inicio
    print(f"Secuencial completado: {stats['eventos']:,} eventos en {tiempo:.4f} segundos.")
    print(f"Rendimiento Secuencial: {stats['eventos'] / tiempo:,.0f} eventos/s\n")
    return tiempo

def ejecutar_hilos(n_workers=4):
    """Experimento utilizando Hilos (Multi-threading)."""
    print(f"--> Ejecutando Experimento con HILOS ({n_workers} Workers)...")
    eventos_por_worker = EVENTOS_TOTALES // n_workers
    inicio = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        # Enviamos las tareas en paralelo usando hilos
        futuros = [
            executor.submit(worker_shard, i, eventos_por_worker, CARPETA_SALIDA, SEMILLA_BASE)
            for i in range(n_workers)
        ]
        resultados = [f.result() for f in futuros]
    
    tiempo = time.perf_counter() - inicio
    total_ev = sum(r['eventos'] for r in resultados)
    print(f"Hilos completado: {total_ev:,} eventos en {tiempo:.4f} segundos.")
    print(f"Rendimiento Hilos: {total_ev / tiempo:,.0f} eventos/s\n")
    return tiempo

def ejecutar_procesos(n_workers=4):
    """Experimento utilizando PROCESOS (Multi-processing - Opción B)."""
    print(f"--> Ejecutando Experimento con PROCESOS ({n_workers} Workers)...")
    eventos_por_worker = EVENTOS_TOTALES // n_workers
    inicio = time.perf_counter()
    
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        # Enviamos las tareas en paralelo usando procesos pesados independientes
        futuros = [
            executor.submit(worker_shard, i, eventos_por_worker, CARPETA_SALIDA, SEMILLA_BASE)
            for i in range(n_workers)
        ]
        resultados = [f.result() for f in futuros]
    
    tiempo = time.perf_counter() - inicio
    total_ev = sum(r['eventos'] for r in resultados)
    print(f"Procesos completado: {total_ev:,} eventos en {tiempo:.4f} segundos.")
    print(f"Rendimiento Procesos: {total_ev / tiempo:,.0f} eventos/s\n")
    return tiempo

if __name__ == "__main__":
    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    
    print("=== INICIANDO EXPERIMENTO DE LA SEMANA 3 ===\n")
    
    # 1. Generador Secuencial exigido
    t_sec = ejecutar_secuencial()
    
    # 2. Experimento de rendimiento comparativo (4 Workers concurrentes)
    t_hilos = ejecutar_hilos(n_workers=4)
    t_proc = ejecutar_procesos(n_workers=4)
    
    # 3. Entrega de métricas finales en consola
    print("=== RESULTADOS DEL ANALISIS FISICO ===")
    print(f"Tiempo Secuencial: {t_sec:.4f}s")
    print(f"Tiempo Multihilo:  {t_hilos:.4f}s (Bloqueado parcialmente por el GIL de Python)")
    print(f"Tiempo Procesos:   {t_proc:.4f}s (Aprovecha la Opción B de archivos separados)")
    
    if t_proc < t_hilos:
        print(f"\nGanador: PROCESOS es {t_hilos/t_proc:.2f}x más rápido que Hilos para esta carga de E/S.")
    else:
        print(f"\nGanador: HILOS es {t_proc/t_hilos:.2f}x más rápido en este entorno específico.")
