FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias do sistema para Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Playwright browsers in shared chown-able location
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Playwright e navegador (as root, then make readable to app user)
RUN playwright install chromium --with-deps && \
    chmod -R a+rX /ms-playwright

# Copiar codigo da aplicacao
COPY . .

# Non-root user, data dir, pycache
RUN groupadd -r app -g 10001 && useradd -r -u 10001 -g app -d /app -s /sbin/nologin app && \
    mkdir -p /app/data /tmp/pycache /home/app/.cache && \
    chown -R app:app /app /tmp/pycache /home/app

ENV CACHE_DB_PATH=/app/data/scrape_cache.db
ENV PYTHONPYCACHEPREFIX=/tmp/pycache
ENV HOME=/home/app

USER app

# Expor porta
EXPOSE 8000

# Comando para iniciar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
