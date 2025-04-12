FROM python:3.9-slim

WORKDIR /app

# Install uv and Flask directly
RUN pip install uv flask

COPY pyproject.toml .

# Run uv sync for other dependencies
RUN uv sync

COPY . .

EXPOSE 5000

ENV FLASK_APP=main.py

# Use the flask command from the global installation
CMD ["flask", "run", "--host=0.0.0.0"]