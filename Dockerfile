FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TY_ENV=production \
    XDG_DATA_HOME=/var/lib

WORKDIR /app

RUN mkdir -p /var/lib/ty

COPY pyproject.toml README.md ./
COPY app ./app

RUN pip install --no-cache-dir .

VOLUME ["/var/lib/ty"]

EXPOSE 5001

CMD ["dev"]
