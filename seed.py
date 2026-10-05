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
    """
    Simula la carga de los catálogos. En tu versión final, 
    aquí leerás los CSVs reales con pd.read_csv('aerolineas.csv')
    """
    # Catálogo simulado basado en tu input
    aerolineas = ['UA', 'AA', 'US', 'F9', 'B6', 'OO', 'AS', 'NK', 'WN', 'DL', 'EV', 'HA', 'MQ', 'VX']
    
    # Catálogo simulado de aeropuertos (IATA_CODE) basado en tu input
    aeropuertos = [
        'ABE', 'ABI', 'ABQ', 'ABR', 'ABY', 'ACK', 'ACT', 'ACV', 'ACY', 'ADK', 'ADQ', 'AEX', 'AGS', 'AKN',
        'ALB', 'ALO', 'AMA', 'ANC', 'APN', 'ASE', 'ATL', 'ATW', 'AUS', 'AVL', 'AVP', 'AZO', 'BDL', 'BET',
        'BFL', 'BGM', 'BGR', 'BHM', 'BIL', 'BIS', 'BJI', 'BLI', 'BMI', 'BNA', 'BOI', 'BOS', 'BPT', 'BQK'
    ]
    
    causas_retraso = ['técnica', 'clima', 'tripulación', 'aeropuerto', 'seguridad', 'aeronave anterior']
    
    return aerolineas, aeropuertos, causas_retraso

def generar_evento_vuelo(aerolineas, aeropuertos, causas_retraso, tasa_defectos):
    """Genera un evento de vuelo e inyecta defectos probabilísticamente."""
    
    # Seleccionamos datos aleatorios del catálogo real
    aerolinea = random.choice(aerolineas)
    origen = random.choice(aeropuertos)
    # Aseguramos que el destino sea diferente al origen
    destino = random.choice([a for a in aeropuertos if a != origen])
    
    # Generamos fecha base
    fecha_base = fake.date_time_between(start_date='-1y', end_date='now')
    
    # Formateo correcto (ISO 8601 con zona horaria UTC) por defecto
    hora_salida = fecha_base.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Asignamos causa solo si hay retraso (simulación básica del 30% de vuelos con retraso)
    causa = random.choice(causas_retraso) if random.random() < 0.3 else None

    # --- INYECCIÓN DE DEFECTOS (El Reto del Caos) ---
    
    # 1. Defecto: Horarios sin zona horaria explícita
    if random.random() < tasa_defectos:
        # Quitamos la 'Z' final que indica UTC
        hora_salida = fecha_base.strftime("%Y-%m-%dT%H:%M:%S") 
        
    # 2. Defecto: Códigos de causa vacíos o inválidos (solo si tenía causa asignada)
    if causa and random.random() < tasa_defectos:
        # Reemplazamos la causa real por un valor nulo o un string inválido
        causa = random.choice(["N/A", "CAUSA_DESCONOCIDA", "ERROR_99"])

    evento = {
        "AIRLINE": aerolinea,
        "FLIGHT_NUMBER": fake.random_int(min=10, max=9999),
        "ORIGIN_AIRPORT": origen,
        "DESTINATION_AIRPORT": destino,
        "SCHEDULED_DEPARTURE": hora_salida,
        "DELAY_REASON": causa
    }
    return evento

def main():
    # 1. Configuración de parámetros de consola
    parser = argparse.ArgumentParser(description="Script de Seed para VuelaData Operaciones")
    parser.add_argument(
        "--volumen", 
        choices=["small", "full"], 
        default="small", 
        help="Volumen de datos (small=10, full=1000)"
    )
    # Añadimos el parámetro para la tasa de defectos
    parser.add_argument(
        "--tasa-defectos", 
        type=float, 
        default=0.0, 
        help="Probabilidad de inyectar defectos (ej: 0.15 para 15%)"
    )
    parser.add_argument(
        "--vista-completa", 
        type=bool, 
        default=False, 
        help="Mostrar vista completa de los datos"
    )
    args = parser.parse_args()


    # 2. Forzamos la reproducibilidad
    configurar_semillas(42)

    # 3. Cargamos los catálogos "reales"
    aerolineas, aeropuertos, causas_retraso = cargar_catalogos()

    # 4. Generación de datos
    cantidad_generar = 10 if args.volumen == "small" else 1000
    print(f"[*] Generando {cantidad_generar} eventos (Modo: {args.volumen}, Tasa defectos: {args.tasa_defectos*100}%)...")
    
    eventos = []
    for _ in range(cantidad_generar):
        eventos.append(generar_evento_vuelo(aerolineas, aeropuertos, causas_retraso, args.tasa_defectos))

    # Imprimimos resultados para verificar
    defectos_encontrados = 0
    for e in eventos:
        # Verificamos si la fecha no termina en 'Z' (defecto de zona horaria) o la causa es inválida
        if not e['SCHEDULED_DEPARTURE'].endswith('Z') or e['DELAY_REASON'] in ["N/A", "CAUSA_DESCONOCIDA", "ERROR_99"]:
            defectos_encontrados += 1
            print(f"[DEFECTO] {e}")
        else:
            # Solo imprimimos los 5 primeros correctos para no saturar la consola
            if args.vista_completa or eventos.index(e) < 5:
                print(f"[OK]      {e}")
                
    print(f"\n[*] Resumen: Se inyectaron defectos en {defectos_encontrados} registros aproximadamente.")

if __name__ == "__main__":
    main()