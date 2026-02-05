# Build stage - Force rebuild 2026-02-05
FROM node:20-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build arg for API URL
ARG VITE_API_URL=https://backend-production-0217.up.railway.app/api/v1
ENV VITE_API_URL=$VITE_API_URL

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port (Railway will use $PORT)
EXPOSE 80

# Start nginx with port from environment
CMD sh -c "sed -i 's/listen 80/listen ${PORT:-80}/' /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"
