# ── Build stage ──
FROM node:20-slim AS build-stage

WORKDIR /app

# Install dependencies first (cached layer)
COPY package*.json ./
RUN npm ci --prefer-offline

# Copy source and build
COPY . .
RUN npm run build

# ── Production stage ──
FROM nginx:stable-alpine AS production-stage

# Copy built assets
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy nginx config from within the build context
# NOTE: nginx.conf must be at frontend/nginx.conf (copied below)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
