## Dockerization Guide (Backend Only)

This document outlines how we Dockerized the **FastAPI** backend in a monorepo and provides a standalone `deployment.md` for production deployment.

---

### 1. Project Structure

```
/auth-backend-fastapi
├── auth/                 # API routes and authentication logic
├── utils/                # Utility modules (security, email, token)
├── database.py           # SQLAlchemy setup
├── main.py               # FastAPI app entrypoint
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker build instructions for backend
├── docker-compose.yml    # Compose file including MySQL and backend
├── .dockerignore         # Files to exclude from the Docker build context
└── deployment.md         # Backend deployment instructions
```

---

### 2. Dockerfile (Backend)

```Dockerfile
# Dockerfile

# 1. Base image
FROM python:3.11-slim

# 2. Set working directory
WORKDIR /app

# 3. Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy application code
COPY . .

# 5. Expose FastAPI port
EXPOSE 9080

# 6. Launch FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9080", "--reload"]
```

---

### 3. .dockerignore

```
# Python artifacts
venv/
__pycache__/
*.pyc

# Environment
.env

# Editor
.vscode/
.DS_Store
```

---

### 4. docker-compose.yml (Backend + MySQL)

```yaml
version: '3.9'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: auth_db
      MYSQL_USER: user
      MYSQL_PASSWORD: password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "9080:9080"
    environment:
      DB_HOST: db
      DB_PORT: 3306
      DB_USER: user
      DB_PASSWORD: password
      DB_NAME: auth_db
    depends_on:
      - db

volumes:
  mysql_data:
```

---

## deployment.md

Below is the content for `deployment.md` focused solely on deploying the **FastAPI backend** in production.

````markdown
# Backend Deployment Instructions

## Prerequisites

- Docker & Docker Compose installed
- Git repository cloned
- Access to a container registry (e.g., Docker Hub, GitHub Container Registry)

## 1. Build & Push Backend Image

1. Build the backend service:
   ```bash
   docker-compose build backend
````

2. Tag and push to your registry:

   ```bash
   docker tag auth-backend-fastapi_backend:latest yourrepo/backend:latest
   docker push yourrepo/backend:latest
   ```

## 2. Production Deployment

### A. Virtual Private Server (VPS)

1. Provision a VPS (DigitalOcean, AWS EC2, etc.).
2. Install Docker & Docker Compose on the server.
3. Clone your repo (or copy `docker-compose.yml` and `.env.production`).
4. Create `.env.production` with:

   ```env
   DB_HOST=prod-db-host
   DB_PORT=3306
   DB_USER=prod_user
   DB_PASSWORD=prod_pass
   DB_NAME=prod_db
   ```
5. Start the backend:

   ```bash
   docker-compose pull backend
   docker-compose up -d --build backend
   ```
6. (Optional) Configure NGINX or another reverse proxy to route `api.yourdomain.com` → `localhost:9080` and obtain SSL.

### B. PaaS (Heroku)

1. Install and log into the Heroku CLI.
2. Create an app:

   ```bash
   heroku create your-backend-app
   ```
3. Set config vars:

   ```bash
   heroku config:set DB_HOST=... DB_USER=... DB_PASSWORD=... DB_NAME=...
   ```
4. Deploy via Docker:

   ```bash
   heroku stack:set container
   docker build -t registry.heroku.com/your-backend-app/web .
   docker push registry.heroku.com/your-backend-app/web
   heroku release web
   ```

## 3. Verify Deployment

* API documentation: `https://api.yourdomain.com/docs`
* Health check: `https://api.yourdomain.com/health`

## 4. Database Migrations

```bash
docker exec -it <backend_container_name> alembic upgrade head
```

## 5. Rolling Updates

```bash
# Pull latest image
docker-compose pull backend
# Restart backend with zero downtime
docker-compose up -d --no-deps --build backend
```

## 6. Common Docker Commands

For local development or quick management of your backend service, use:

```bash
# Build/rebuild the backend image
docker-compose build backend

# Start the backend container (in detached mode)
docker-compose up -d backend

# View logs
docker-compose logs -f backend

# Stop and remove containers, networks, and volumes
docker-compose down
```

*End of documentation.*
