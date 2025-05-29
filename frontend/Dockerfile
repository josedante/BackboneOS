# Dockerfile para Vue.js + Vite
FROM node:18-alpine

# Establecer directorio de trabajo
WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código
COPY . .

# Exponer el puerto 5173 (puerto por defecto de Vite)
EXPOSE 5173

# Comando para ejecutar la aplicación en modo desarrollo
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
