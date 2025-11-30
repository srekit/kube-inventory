FROM python:3.14-slim

WORKDIR /app

COPY dist/ ./dist/

EXPOSE 8000

CMD ["python", "-m", "app"]
