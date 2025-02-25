FROM python:3.9-slim

WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install -r backend/requirements.txt

# Install frontend dependencies
COPY frontend/requirements.txt ./frontend/requirements.txt
RUN pip install -r frontend/requirements.txt

COPY . .

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]