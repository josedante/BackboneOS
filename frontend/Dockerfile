# Use Node.js 20 for development and production
FROM node:20

# Set the working directory
WORKDIR /app

# Copy package.json and lock file
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of your app's source code
COPY . .

# Expose the port Nuxt will run on
EXPOSE 3000

# Default command for development (can be overridden in docker-compose)
CMD ["npm", "run", "dev"]