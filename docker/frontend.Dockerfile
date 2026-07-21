# ─────────────────────────────────────────────────────────────────
# Frontend — served by Nginx
# ─────────────────────────────────────────────────────────────────
FROM nginx:1.25-alpine

LABEL maintainer="TaskFlow Team"
LABEL description="TaskFlow Frontend (Nginx)"

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY ./docker/nginx.conf /etc/nginx/conf.d/app.conf

# Copy frontend static files
COPY ./frontend /usr/share/nginx/html

# Expose HTTP
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
