---
id: setup-seed
title: Configuración y Seed (PostgreSQL)
sidebar_position: 1
---
# VuelaData Operaciones - Seed Reproducible (HU-03)

Este directorio contiene el script de siembra (Seed) para poblar las bases de datos operacionales del proyecto VuelaData. El script garantiza la reproducibilidad de los datos mediante una semilla fija, es idempotente (se puede ejecutar múltiples veces sin duplicar registros) y permite la inyección probabilística de defectos de calidad operacional.

## Despliegue Rápido con Docker Compose (Recomendado)

Si dispones de Docker y Docker Compose, puedes levantar todo el entorno (Base de datos PostgreSQL, ejecución del Seed y Documentación) con un solo comando sin necesidad de instalar dependencias locales:

```bash
docker compose up -d --build
```

* **PostgreSQL:** Disponible en `localhost:5432` con el esquema operacional ya creado.
* **Seed:** Ejecutado automáticamente una vez que la base de datos está saludable.
* **Documentación Docusaurus:** Accesible en `http://localhost:3000`.

Para ejecutar un Seed personalizado con Docker:
```bash
docker compose run --rm seed python seed.py --volumen full --tasa-defectos 0.15
```

## Requisitos Previos (Ejecución Local)

1. **Python 3.9+** instalado en tu sistema.
2. **Archivos CSV Base:** Asegúrate de tener los archivos `airlines.csv` y `airports.csv` en el mismo directorio que el script `seed.py`.
3. **Base de datos:** Una instancia de PostgreSQL corriendo con el esquema operacional (`schema_postgresql.sql`) previamente ejecutado.

### Instalación de dependencias

Ejecuta el siguiente comando para instalar las librerías necesarias:

```bash
pip install psycopg2-binary python-dotenv pandas faker
```

(Nota: En caso de mover este programa a dentro de otro, asegurarse de instalar las dependecias en el entorno en el que trabajara, puedes encontrarla en requirements.txt).

## Configuración del Entorno

El script utiliza variables de entorno para proteger las credenciales de la base de datos (cumpliendo con las normas de seguridad del proyecto).

Crea un archivo llamado `.env` en la misma ruta que `seed.py` con la siguiente estructura:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vueladata
DB_USER=postgres
DB_PASSWORD=tu_contrasena_aqui
```


## Ejecución del Script

El script funciona mediante una interfaz de línea de comandos (CLI) que permite configurar el volumen de datos y la tasa de defectos.

### Comandos disponibles:

* **`--volumen`**: Define la cantidad de datos transaccionales a generar.
  * `small`: (Por defecto) Lote pequeño para desarrollo rápido (10 vuelos, 50 pasajeros).
  * `full`: Lote masivo para pruebas de estrés y volumetría (1000 vuelos, 5000 pasajeros).
* **`--tasa-defectos`**: Probabilidad de ensuciar los datos operacionales para simular el caos de la vida real. Acepta un decimal entre `0.0` y `1.0`. Por defecto es `0.0` (datos limpios).

### Ejemplos de uso:

**1. Modo desarrollo (Rápido y limpio):**

```bash
python seed.py
```

**2. Modo completo con 15% de defectos operacionales:**

```bash
python seed.py --volumen=full --tasa-defectos=0.15
```

## Limpieza de la Base de Datos (Reset Completo)

Si necesitas borrar todos los datos generados para empezar desde cero, **NO elimines las tablas ni el esquema**.

Abre tu consola SQL (pgAdmin, DBeaver) conectada a la base de datos `vueladata` y ejecuta el siguiente comando:

```sql
TRUNCATE TABLE 
    pais, 
    aerolinea, 
    estado_vuelo, 
    causa, 
    pasajero, 
    reserva 
RESTART IDENTITY CASCADE;
```

**¿Por qué se debe usar este comando exacto?**

* `CASCADE`: Elimina automáticamente todos los registros de las tablas que dependen de estas (vuelos, eventos, itinerarios, etc.).
* `RESTART IDENTITY`: Reinicia todos los contadores de las llaves primarias (`id`) a 1. Esto es vital para garantizar que las próximas ejecuciones del seed sean 100% idénticas y reproducibles.

## Verificación de Defectos Inyectados

Como los eventos entran en estado `PENDIENTE` por defecto, puedes usar estas consultas SQL para validar que la inyección de defectos (`--tasa-defectos`) funcionó correctamente:

**1. Identificar causas inválidas (ERROR_99, N/A):**

```sql
SELECT id_vuelo, codigo_evento, codigo_causa_original 
FROM vueladata.evento_operacional 
WHERE codigo_causa_original IN ('N/A', 'CAUSA_DESCONOCIDA', 'ERROR_99');
```

**2. Identificar vuelos con eventos OOOI faltantes:**

```sql
SELECT id_vuelo, COUNT(id_evento) AS total_eventos
FROM vueladata.evento_operacional
GROUP BY id_vuelo
HAVING COUNT(id_evento) < 4;
```

**3. Identificar vuelos con llegadas erróneas cruzando la medianoche:**

```sql
SELECT 
    e_in.id_vuelo, 
    e_out.fecha_hora_evento_utc AS salida_out, 
    e_in.fecha_hora_evento_utc AS llegada_in_erronea
FROM vueladata.evento_operacional e_in
JOIN vueladata.evento_operacional e_out ON e_in.id_vuelo = e_out.id_vuelo
WHERE e_in.codigo_evento = 'IN' 
  AND e_out.codigo_evento = 'OUT'
  AND e_in.fecha_hora_evento_utc < e_out.fecha_hora_evento_utc;
```
