# 🐳 Docker Development Setup Guide

## Quick Start

Run the entire application stack with one command:

```bash
cd /home/mortadha/Desktop/AI-News-Analyzer
docker-compose up
```

**Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- MongoDB: localhost:27017

## 📋 What's Included

### Services

1. **MongoDB** (`mongo:7.0`)
   - Official MongoDB database
   - Data persists in Docker volume `mongodb_data`
   - Port: 27017

2. **Backend** (Python 3.10 + Django)
   - Runs with `python3.10 manage.py runserver`
   - Uses CPU-only PyTorch for smaller image size
   - Port: 8000

3. **Frontend** (Node 18 + Vite)
   - Runs with `npm run dev`
   - Hot reload enabled
   - Port: 5173

### Images Built

✅ `mortadhajemai/ai-news-backend:dev` (1.56GB)
✅ `mortadhajemai/ai-news-frontend:dev` (297MB)

## 🚀 Pushing to DockerHub

### 1. Login to DockerHub

```bash
docker login --username mortadhajemai
```

Enter your Docker Hub password when prompted.

### 2. Push Images

The images are already tagged correctly, just push them:

```bash
# Push backend image
docker push mortadhajemai/ai-news-backend:dev

# Push frontend image
docker push mortadhajemai/ai-news-frontend:dev
```

### 3. Verify on DockerHub

Visit https://hub.docker.com/u/mortadhajemai to verify the images are uploaded.

## 📦 Running from DockerHub

Anyone can now pull and run your application:

```bash
# Pull images
docker-compose pull

# Run application
docker-compose up
```

Or pull individual images:

```bash
docker pull mortadhajemai/ai-news-backend:dev
docker pull mortadhajemai/ai-news-frontend:dev
```

## 🛠️ Common Commands

### Build Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

### Start Services

```bash
# Start in foreground (see logs)
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# Start specific service
docker-compose up backend
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes database data)
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb

# Follow logs (live)
docker-compose logs -f backend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

## 🔍 Troubleshooting

### Backend won't start

Check if MongoDB is ready:
```bash
docker-compose logs mongodb
```

### Port already in use

If ports 5173, 8000, or 27017 are already in use, either:
1. Stop the conflicting service running on your host
2. Or modify `docker-compose.yml` to use different host ports:
   ```yaml
   ports:
     - "5174:5173"  # Use port 5174 on host instead
   ```

### Frontend can't connect to backend

Make sure both services are running:
```bash
docker-compose ps
```

All services should show status "Up".

### Clear everything and start fresh

```bash
# Stop containers
docker-compose down

# Remove images
docker rmi mortadhajemai/ai-news-backend:dev
docker rmi mortadhajemai/ai-news-frontend:dev

# Rebuild
docker-compose build --no-cache

# Start again
docker-compose up
```

## 📝 Files Modified

The following files were updated for Docker compatibility:

1. **`backend/Dockerfile`** - Uses Python 3.10, runs development server
2. **`frontend/Dockerfile.dev`** - New file for Vite dev server  
3. **`frontend/vite.config.js`** - Changed port from 3000 to 5173
4. **`docker-compose.yml`** - Complete rewrite for development setup

**No application code was changed** - your Django and React code remains untouched!

## 🎯 Production Deployment

For production, consider:
- Using `gunicorn` instead of Django dev server
- Building static frontend instead of dev server
- Adding nginx reverse proxy
- Setting up proper environment variables
- Using Docker secrets for sensitive data

The current setup is optimized for **development** and **demonstration** purposes.
