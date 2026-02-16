# syntax=docker/dockerfile:1

### Build stage: compile Vite app
FROM node:18-alpine AS build
WORKDIR /app

# Install dependencies
# Prefer reproducible install when lockfile exists; fallback for environments
# where package-lock.json is missing in build context.
COPY package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy source
COPY . .

# Build-time env vars for Vite (can be overridden via build args)
ARG VITE_API_BASE_URL
ARG VITE_API_TIMEOUT=30000
ARG VITE_AI_TIMEOUT=120000
ARG VITE_SYNC_TIMEOUT=300000
ARG VITE_THIRD_PARTY_TIMEOUT=90000
ARG VITE_GOOGLE_CUSTOMER_ID
ARG VITE_GOOGLE_PROXY_URL
ENV \
  VITE_API_BASE_URL=${VITE_API_BASE_URL} \
  VITE_API_TIMEOUT=${VITE_API_TIMEOUT} \
  VITE_AI_TIMEOUT=${VITE_AI_TIMEOUT} \
  VITE_SYNC_TIMEOUT=${VITE_SYNC_TIMEOUT} \
  VITE_THIRD_PARTY_TIMEOUT=${VITE_THIRD_PARTY_TIMEOUT} \
  VITE_GOOGLE_CUSTOMER_ID=${VITE_GOOGLE_CUSTOMER_ID} \
  VITE_GOOGLE_PROXY_URL=${VITE_GOOGLE_PROXY_URL}

# Build static assets
RUN npm run build

### Runtime stage: serve with nginx
FROM nginx:alpine

# Use project nginx config (defaults to listen 5173)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 5173
CMD ["nginx", "-g", "daemon off;"]
