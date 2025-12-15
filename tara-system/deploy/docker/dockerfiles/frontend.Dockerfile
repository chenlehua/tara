FROM node:20-alpine AS builder

WORKDIR /app

# Configure Chinese npm mirror
RUN npm config set registry https://registry.npmmirror.com

# Copy package files
COPY frontend/package.json frontend/pnpm-lock.yaml* ./

# Install pnpm and dependencies with Chinese mirror
RUN npm install -g pnpm --registry https://registry.npmmirror.com && \
    pnpm config set registry https://registry.npmmirror.com && \
    pnpm install --frozen-lockfile

# Copy source code
COPY frontend/ ./

# Build the application
RUN pnpm build

# Production stage
FROM nginx:1.25-alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY deploy/nginx/conf.d/frontend.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
