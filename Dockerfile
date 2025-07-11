# Step 1: Build the frontend
FROM node:20 AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Step 2: Build backend and install dependencies
FROM python:3.12-slim AS backend
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 3: Copy backend code and built frontend
COPY backend/ .
COPY --from=frontend /frontend/dist ./frontend/dist

# Step 4: Run FastAPI (will serve both API and frontend)
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
