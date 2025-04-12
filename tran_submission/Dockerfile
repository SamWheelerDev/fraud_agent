FROM python:3.9-slim

WORKDIR /app

COPY pyproject.toml .
RUN uv sync

COPY . .

EXPOSE 5000

ENV FLASK_APP=main.py

CMD ["flask", "run", "--host=0.0.0.0"]