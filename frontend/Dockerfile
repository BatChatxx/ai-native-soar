# Frontend Dockerfile (React + Vite)
FROM node:18-alpine AS build

# Set environment variables
ENV NODE_ENV=production
ENV CI=true

# Set work directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY index.html ./
COPY src ./src

# Build the application
RUN npx --yes vite build

# Final stage: nginx to serve files
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
