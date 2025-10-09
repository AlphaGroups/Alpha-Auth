# Backend Deployment Instructions

## Prerequisites

- Docker & Docker Compose installed
- Git repository cloned
- Access to a container registry (e.g., Docker Hub, GitHub Container Registry)

## 1. Build & Push Backend Image

1. Build the backend service:
   ```bash
   docker-compose build backend
   ```

2. Tag and push to your registry:
   ```bash
   docker tag auth-backend-fastapi_backend:latest yourrepo/backend:latest
   docker push yourrepo/backend:latest
   ```

## 2. Build-time Data Seeding

Before starting the application, you need to ensure that the required classes (1-12) are present in the database. This is essential for the application to function properly.

To seed the classes during the build process, run:
```bash
python init_db.py
```

Or if using within a Docker environment:
```bash
docker exec -it <container_name> python init_db.py
```

## 3. Production Deployment

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
5. Run the class seeding script to ensure classes exist:
   ```bash
   python build_seed_classes.py
   ```
6. Start the backend:
   ```bash
   docker-compose pull backend
   docker-compose up -d --build backend
   ```
7. (Optional) Configure NGINX or another reverse proxy to route `api.yourdomain.com` → `localhost:9080` and obtain SSL.

### B. Platform Deployment (Render, Heroku, etc.)

When deploying to platforms like Render, ensure the build_seed_classes.py runs during the build process by adding it to your startup commands or build script. For Render, you could use the "Build Command" field to run:
```
python build_seed_classes.py
```

## 4. Verify Deployment

* API documentation: `https://api.yourdomain.com/docs`
* Health check: `https://api.yourdomain.com/health`

## 5. Database Migrations

```bash
docker exec -it <backend_container_name> python create_tables.py
```

## 6. Rolling Updates

```bash
# Pull latest image
docker-compose pull backend
# Run initialization
docker exec -it <backend_container_name> python init_db.py
# Restart backend with zero downtime
docker-compose up -d --no-deps --build backend
```

## 7. Common Docker Commands

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

# Run database initialization in a running container
docker exec -it <backend_container_name> python init_db.py
```

*End of documentation.*