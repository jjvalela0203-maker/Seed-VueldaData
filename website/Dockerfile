FROM node:20-alpine

WORKDIR /app

# Instalar dependencias de Node.js
COPY package*.json ./
RUN npm install

# Copiar el código fuente de la documentación
COPY . .

EXPOSE 3000

# Iniciar servidor de desarrollo en host 0.0.0.0
CMD ["npm", "run", "start", "--", "--host", "0.0.0.0", "--port", "3000"]
