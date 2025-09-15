# ---- Stage 1: Build ----
# Use a specific Node.js version with a full OS for building
FROM node:20 AS builder

# Set the working directory
WORKDIR /app

# Copy package.json and lock file
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of your app's source code
COPY . .

# Build the Nuxt.js application for production
RUN npm run build


# ---- Stage 2: Production ----
# Use the lightweight alpine image for the final production stage
FROM node:20-alpine

# Set the working directory
WORKDIR /app

# Copy only the built artifacts from the 'builder' stage
COPY --from=builder /app/.output ./

# Expose the port Nuxt will run on
EXPOSE 3000

# Set the command to start the Nuxt server
CMD ["node", "./server/index.mjs"]