FROM node:22-bookworm-slim AS base
WORKDIR /app
ENV NODE_ENV=production

FROM base AS deps
COPY services/web/package.json services/web/package-lock.json ./
RUN npm ci --no-audit --no-fund

FROM deps AS dev
ENV NODE_ENV=development
ENV CHOKIDAR_USEPOLLING=1
VOLUME /app/node_modules
COPY services/web ./
EXPOSE 3000
CMD ["npm", "run", "dev"]

FROM deps AS builder
ENV NODE_ENV=production
COPY services/web ./
RUN npm run build

FROM node:22-bookworm-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app .
EXPOSE 3000
CMD ["npm", "run", "start"]


