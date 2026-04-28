FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY cloudflare_deploy/requirements.txt /app/cloudflare_deploy/requirements.txt
RUN pip install --no-cache-dir -r /app/cloudflare_deploy/requirements.txt

COPY . /app

RUN chmod +x /app/cloudflare_deploy/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/cloudflare_deploy/entrypoint.sh"]
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000", "cloudflare_deploy.cloudflare_main:app"]
