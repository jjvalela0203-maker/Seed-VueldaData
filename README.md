# VuelaData - Base de Datos Transaccional y Seed

Este repositorio contiene la inicialización de la base de datos PostgreSQL (HU-03), el script de siembra de datos (Seed reproducible con inyección probabilística de defectos) y su respectiva documentación técnica interactiva construida con Docusaurus.

---

## 🚀 Inicio Rápido con Docker Compose (Recomendado)

Todo el stack del proyecto (Base de Datos PostgreSQL, Seed inicial y Documentación Web) está preparado para levantarse con un solo comando.

### 1. Levantar el proyecto completo

```bash
docker compose up -d --build
```

Esto iniciará los siguientes servicios:
- **`db` (PostgreSQL 15)**: Expuesto en el puerto `5432`. Crea automáticamente el esquema y las tablas operacionales a partir de `schema_postgresql.sql`.
- **`seed` (Población de datos)**: Espera a que la base de datos esté lista y ejecuta `seed.py` para cargar los catálogos y transacciones iniciales.
- **`docs` (Documentación Docusaurus)**: Disponible en [http://localhost:3000](http://localhost:3000).

### 2. Comandos útiles con Docker Compose

* **Ver logs en tiempo real:**
  ```bash
  docker compose logs -f
  ```

* **Ejecutar el Seed con parámetros personalizados:**
  ```bash
  # Ejemplo: volumen completo con 15% de defectos operacionales
  docker compose run --rm seed python seed.py --volumen full --tasa-defectos 0.15
  ```

* **Detener los contenedores:**
  ```bash
  docker compose down
  ```

* **Detener y reiniciar la base de datos limpia (borrando volúmenes):**
  ```bash
  docker compose down -v
  ```

---

## 🛠️ Ejecución Local Alternativa (Sin Docker)

Si prefieres ejecutar los componentes de forma manual en tu máquina local:

### 1. Base de datos y Seed

1. Asegúrate de tener PostgreSQL corriendo y crea la base de datos `vueladata`.
2. Configura las variables de entorno en un archivo `.env` basado en `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Instala las dependencias de Python:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecuta el script de Seed:
   ```bash
   python seed.py --volumen small --tasa-defectos 0.1
   ```

### 2. Documentación Técnica (Docusaurus)

1. Navegar a la carpeta `website`:
   ```bash
   cd website
   ```
2. Instalar los paquetes de Node:
   ```bash
   npm install
   ```
3. Levantar el servidor de desarrollo:
   ```bash
   npm run start
   ```

La documentación estará accesible en [http://localhost:3000](http://localhost:3000).