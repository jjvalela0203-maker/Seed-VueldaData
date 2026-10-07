import argparse
import random
import pandas as pd
from faker import Faker
import datetime

# Inicializamos Faker para fechas y números de vuelo
fake = Faker()

def configurar_semillas(semilla=42):
    """Fija la semilla para garantizar la reproducibilidad de los datos."""
    Faker.seed(semilla)
    random.seed(semilla)
    print(f"[*] Semilla de generación fijada en: {semilla}")

def cargar_catalogos():
    """Carga los catálogos reales desde los CSVs."""
    try:
        csv_aerolineas = pd.read_csv("airlines.csv")
        csv_aeropuertos = pd.read_csv("airports.csv")
        # CORRECCIÓN: .tolist() es obligatorio para que random.choice no falle
        aerolineas = csv_aerolineas["IATA_CODE"].tolist()
        aeropuertos = csv_aeropuertos["IATA_CODE"].tolist()
    except FileNotFoundError:
        print("[!] Advertencia: No se encontraron los CSV. Usando datos de respaldo...")
        aerolineas = ['UA', 'AA', 'DL', 'AV']
        aeropuertos = ['BOG', 'BAQ', 'MDE', 'CLO']
        
    causas_retraso = ['técnica', 'clima', 'tripulación', 'aeropuerto', 'seguridad', 'aeronave anterior']
    
    return aerolineas, aeropuertos, causas_retraso

def generar_tiempos_oooi(fecha_programada, causa_retraso, tasa_defectos):
    """Calcula los tiempos OOOI secuenciales e inyecta eventos faltantes."""
    minutos_retraso = random.randint(15, 180) if causa_retraso else random.randint(-5, 10)
    out_time = fecha_programada + datetime.timedelta(minutes=minutos_retraso)
    
    taxi_out = random.randint(10, 25)
    off_time = out_time + datetime.timedelta(minutes=taxi_out)
    
    air_time = random.randint(45, 240)
    on_time = off_time + datetime.timedelta(minutes=air_time)
    
    taxi_in = random.randint(5, 15)
    in_time = on_time + datetime.timedelta(minutes=taxi_in)
    
    eventos_oooi = {
        "OUT_TIME": out_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "OFF_TIME": off_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ON_TIME": on_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "IN_TIME": in_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    if random.random() < tasa_defectos:
        evento_perdido = random.choice(list(eventos_oooi.keys()))
        eventos_oooi[evento_perdido] = None
        
    return eventos_oooi

def generar_evento_vuelo(aerolineas, aeropuertos, causas_retraso, tasa_defectos):
    """Genera un evento de vuelo e inyecta defectos probabilísticamente."""
    aerolinea = random.choice(aerolineas)
    origen = random.choice(aeropuertos)
    destino = random.choice([a for a in aeropuertos if a != origen])
    
    fecha_base = fake.date_time_between(start_date='-1y', end_date='now').replace(microsecond=0)
    hora_salida = fecha_base.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    causa = random.choice(causas_retraso) if random.random() < 0.3 else None
    tiempos_oooi = generar_tiempos_oooi(fecha_base, causa, tasa_defectos)

    if random.random() < tasa_defectos:
        hora_salida = fecha_base.strftime("%Y-%m-%dT%H:%M:%S") 
        
    if causa and random.random() < tasa_defectos:
        causa = random.choice(["N/A", "CAUSA_DESCONOCIDA", "ERROR_99"])

    evento = {
        "AIRLINE": aerolinea,
        "FLIGHT_NUMBER": fake.random_int(min=10, max=9999),
        "ORIGIN_AIRPORT": origen,
        "DESTINATION_AIRPORT": destino,
        "SCHEDULED_DEPARTURE": hora_salida,
        **tiempos_oooi,
        "DELAY_REASON": causa
    }
    return evento

def main():
    parser = argparse.ArgumentParser(description="Script de Seed para VuelaData Operaciones")
    # Controla el tamaño del dataset generado
    parser.add_argument("--volumen", choices=["small", "full"], default="small")
    # Controla la tasa de defectos a inyectar en los datos
    parser.add_argument("--tasa-defectos", type=float, default=0.0)
    # Controla si se muestra la vista completa de los datos generados
    parser.add_argument("--vista-completa", action="store_true", help="Mostrar vista completa de los datos")
    args = parser.parse_args()

    configurar_semillas(42)
    aerolineas, aeropuertos, causas_retraso = cargar_catalogos()

    cantidad_generar = 10 if args.volumen == "small" else 1000
    print(f"[*] Generando {cantidad_generar} eventos (Modo: {args.volumen}, Tasa defectos: {args.tasa_defectos*100}%)...")
    
    eventos = []
    for _ in range(cantidad_generar + 1):
        eventos.append(generar_evento_vuelo(aerolineas, aeropuertos, causas_retraso, args.tasa_defectos))

        # Validación de defectos inyectados
    defectos_encontrados = 0
    correctos_impresos = 0 
        
    for e in eventos:
        # Detectar explícitamente si es un defecto
        if (not e['SCHEDULED_DEPARTURE'].endswith('Z') or 
            e['DELAY_REASON'] in ["N/A", "CAUSA_DESCONOCIDA", "ERROR_99"] or
            None in [e['OUT_TIME'], e['OFF_TIME'], e['ON_TIME'], e['IN_TIME']]):
            
            defectos_encontrados += 1
            # Si el usuario quiere ver todo, imprimimos el defecto
            if args.vista_completa:
                print(f"[DEFECTO] {e}")
        else:
            # Lógica corregida para imprimir los buenos
            if args.vista_completa:
                print(f"[OK]      {e}")
            elif correctos_impresos < 5:
                print(f"[OK]      {e}")
                correctos_impresos += 1
                
    print(f"\n[*] Resumen: Se generaron {cantidad_generar} eventos.")
    print(f"[*] Se inyectaron defectos en {defectos_encontrados} registros aproximadamente.")
    if not args.vista_completa:
        print("[*] (Mostrando solo los primeros 5 registros correctos de muestra. Usa --vista-completa=True para ver todo)")

if __name__ == "__main__":
    main()