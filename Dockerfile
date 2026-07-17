FROM node:22-alpine AS web

WORKDIR /src
COPY package.json package-lock.json ./
RUN npm ci
COPY app ./app
COPY public ./public
COPY styles.css ./
COPY next.config.mjs ./
ENV NEXT_PUBLIC_TONELEAF_API=same-origin
ENV TONELEAF_STATIC_EXPORT=1
RUN npm run build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TONELEAF_HOST=0.0.0.0 \
    PORT=8080 \
    TONELEAF_STATIC_DIR=/app/static \
    TONELEAF_TRUSTED_HOSTS="*"

WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY --from=web /src/out ./static

RUN useradd --create-home --uid 10001 toneleaf && chown -R toneleaf:toneleaf /app
USER toneleaf

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8080') + '/health', timeout=3)"

CMD ["python", "-m", "backend.run"]
