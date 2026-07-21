# ⚡ TaskFlow — Full Stack Task Management System

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)
![Kubernetes](https://img.shields.io/badge/Kubernetes-ready-blue?logo=kubernetes)
![CI/CD](https://img.shields.io/badge/CI/CD-GitHub_Actions-black?logo=github-actions)

A production-ready, full-stack Task Management System built to demonstrate modern software engineering, DevOps, containerisation, and cloud deployment skills.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Local Development](#local-development)
- [Docker Setup](#docker-setup)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Render Deployment](#render-deployment)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Security](#security)
- [Architecture](#architecture)

---

## Features

| Module | Features |
|--------|----------|
| **Auth** | Register, Login, JWT tokens, bcrypt passwords, Role-based access (Admin/User) |
| **Tasks** | Create, Read, Update, Delete, Soft-delete, Filter, Search, Sort, Paginate |
| **Dashboard** | Stats cards, Doughnut/Bar/Gauge charts, Completion rate |
| **Profile** | Edit profile, Change password, Avatar upload |
| **Admin Panel** | List users, Activate/Deactivate, Delete users |
| **UI** | Dark/Light mode, Responsive (mobile → desktop), Toast notifications, Loading spinners |

---

## Tech Stack

### Backend
- **Python 3.11** + **FastAPI** — async REST API
- **SQLAlchemy 2** — ORM with relationship management
- **Pydantic v2** — request/response validation
- **python-jose** — JWT token creation & verification
- **passlib[bcrypt]** — secure password hashing
- **slowapi** — rate limiting middleware
- **Alembic** — database migrations (ready to use)

### Frontend
- Vanilla **HTML5 / CSS3 / JavaScript** (no build step required)
- **Chart.js 4** — dashboard visualisations
- CSS custom properties for dark/light theming
- Fully responsive via CSS Grid + Flexbox

### Database
- **SQLite** — zero-config local development
- **PostgreSQL 15** — production target (Docker Compose / Render)

### DevOps
- **Docker** + **Docker Compose** — containerised local stack
- **Kubernetes** — production orchestration manifests
- **GitHub Actions** — automated CI/CD pipeline
- **Render** — cloud deployment target
- **Docker Hub** — container image registry

---

## Project Structure

```
task-manager/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py             # App factory, lifespan, middleware
│   │   ├── config.py           # Pydantic Settings (env vars)
│   │   ├── database.py         # SQLAlchemy engine & session
│   │   ├── models/             # SQLAlchemy ORM models
│   │   │   ├── user.py         # User model (roles, avatar, bio)
│   │   │   └── task.py         # Task model (status, priority, soft-delete)
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   │   ├── user.py
│   │   │   ├── task.py
│   │   │   └── common.py
│   │   ├── routers/            # Route handlers
│   │   │   ├── auth.py         # /auth/register  /auth/login
│   │   │   ├── tasks.py        # /tasks  CRUD + stats
│   │   │   └── users.py        # /profile  /admin/users
│   │   ├── services/           # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── task_service.py
│   │   │   └── user_service.py
│   │   ├── middleware/
│   │   │   ├── logging_middleware.py
│   │   │   └── security_headers.py
│   │   └── utils/
│   │       ├── security.py     # JWT + bcrypt helpers
│   │       ├── dependencies.py # FastAPI dependency injection
│   │       └── logger.py       # Logging configuration
│   ├── tests/
│   │   ├── conftest.py         # Shared fixtures (in-memory SQLite)
│   │   ├── test_auth.py        # Auth endpoint tests
│   │   ├── test_tasks.py       # Task CRUD + ownership tests
│   │   └── test_profile.py     # Profile + admin tests
│   ├── uploads/                # Avatar storage (gitignored)
│   ├── requirements.txt
│   └── pytest.ini
│
├── frontend/                   # Static SPA
│   ├── index.html              # Full app shell (auth + dashboard + pages)
│   ├── css/
│   │   └── style.css           # Design tokens, components, responsive layout
│   └── js/
│       ├── api.js              # Centralised HTTP client (fetch + JWT)
│       ├── auth.js             # Login / Register logic
│       ├── dashboard.js        # Stats cards + Chart.js charts
│       ├── tasks.js            # Task list, filters, modal CRUD
│       ├── profile.js          # Profile edit + avatar upload
│       ├── admin.js            # Admin user management table
│       └── app.js              # Bootstrap, routing, theme toggle, toasts
│
├── docker/
│   ├── backend.Dockerfile      # Multi-stage Python build → slim runtime
│   ├── frontend.Dockerfile     # Nginx static file server
│   └── nginx.conf              # Nginx reverse proxy config
│
├── kubernetes/
│   ├── namespace.yaml          # taskflow namespace
│   ├── configmap.yaml          # Non-secret config + nginx config
│   ├── secret.yaml             # Secrets (base64-encoded placeholders)
│   ├── deployment.yaml         # Backend + Frontend Deployments + Postgres StatefulSet
│   ├── service.yaml            # ClusterIP + LoadBalancer services
│   ├── ingress.yaml            # Nginx Ingress with host routing
│   └── autoscaling.yaml        # HPA for backend and frontend
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml           # GitHub Actions CI/CD pipeline
│
├── render.yaml                 # Render blueprint for cloud deployment
├── docker-compose.yml          # Full local stack (Postgres + Backend + Frontend)
├── .gitignore
└── README.md
```

---

## Local Development

### Prerequisites
- Python 3.11+
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/taskflow.git
cd taskflow/task-manager

# 2. Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. Install backend dependencies
cd backend
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env — the defaults work for local SQLite development

# 5. Start the backend (SQLite is created automatically)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 6. Open the frontend
# In a browser, open: frontend/index.html
# OR use VS Code Live Server extension
# The default API URL is http://localhost:8000
```

The API docs are available at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

Default admin credentials (auto-seeded on first run):
- Email: `admin@taskmanager.com`
- Password: `Admin@123456`

---

## Docker Setup

### Prerequisites
- Docker Desktop (includes Docker Compose)

### Run the full stack

```bash
# From the task-manager/ directory
docker compose up --build

# Detached mode
docker compose up --build -d

# View logs
docker compose logs -f backend

# Stop everything
docker compose down

# Stop and remove volumes (⚠ destroys database data)
docker compose down -v
```

Services available after startup:
| Service | URL |
|---------|-----|
| Frontend (Nginx) | http://localhost:80 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/api/docs |
| PostgreSQL | localhost:5432 |

### Environment variables (Docker Compose)

Create a `.env` file in the `task-manager/` root:

```bash
SECRET_KEY=your-secret-key-min-32-chars-change-this
POSTGRES_USER=taskflow
POSTGRES_PASSWORD=strongpassword
POSTGRES_DB=taskmanager
FIRST_ADMIN_EMAIL=admin@taskmanager.com
FIRST_ADMIN_PASSWORD=Admin@123456
```

---

## Kubernetes Deployment

### Prerequisites
- kubectl configured against a cluster
- A Docker Hub account with the images pushed
- Ingress controller installed

### Steps

```bash
# 1. Push images to Docker Hub (replace YOUR_USERNAME)
docker build -t YOUR_USERNAME/taskflow-backend:latest -f docker/backend.Dockerfile ./backend
docker build -t YOUR_USERNAME/taskflow-frontend:latest -f docker/frontend.Dockerfile .
docker push YOUR_USERNAME/taskflow-backend:latest
docker push YOUR_USERNAME/taskflow-frontend:latest

# 2. Update image names in kubernetes/deployment.yaml
#    Replace DOCKER_HUB_USERNAME with your actual username

# 3. Update secrets in kubernetes/secret.yaml
#    Generate base64 values: echo -n "your-value" | base64
#    Then paste into the secret.yaml data fields

# 4. Apply all manifests
kubectl apply -f kubernetes/

# 5. Verify everything is running
kubectl get all -n taskflow

# 6. Watch rollout
kubectl rollout status deployment/taskflow-backend -n taskflow
kubectl rollout status deployment/taskflow-frontend -n taskflow

# 7. Access the app
kubectl get svc taskflow-frontend-svc -n taskflow
# Note the EXTERNAL-IP from the LoadBalancer service
```

### Useful kubectl commands

```bash
# View pods
kubectl get pods -n taskflow

# View logs
kubectl logs -f deployment/taskflow-backend -n taskflow

# Scale manually
kubectl scale deployment taskflow-backend --replicas=3 -n taskflow

# View HPA status
kubectl get hpa -n taskflow

# Port-forward for local testing
kubectl port-forward svc/taskflow-backend-svc 8000:8000 -n taskflow
```

### Local Kubernetes (Minikube)

```bash
minikube start
minikube addons enable ingress
kubectl apply -f kubernetes/
minikube tunnel  # In a separate terminal to expose LoadBalancer
```

---

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) runs on every push:

```
Push to main
    │
    ├─► Job 1: test-backend
    │       Install Python dependencies
    │       Run pytest suite
    │       Lint with Ruff
    │
    ├─► Job 2: build-and-push  (only on main push, after tests pass)
    │       Build backend Docker image
    │       Build frontend Docker image
    │       Push both to Docker Hub with :latest and :<sha> tags
    │
    ├─► Job 3: deploy-render  (only on main push)
    │       Trigger Render deploy hook
    │
    └─► Job 4: notify
            Print final pipeline status
```

### Required GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|--------|-------------|
| `DOCKER_HUB_USERNAME` | Your Docker Hub username |
| `DOCKER_HUB_TOKEN` | Docker Hub access token (not your password) |
| `RENDER_DEPLOY_HOOK_URL` | Deploy hook URL from Render dashboard |

---

## Render Deployment

### Prerequisites
- [Render account](https://render.com)
- GitHub repository connected to Render

### Steps

1. Push your code to GitHub
2. In Render: **New → Blueprint**
3. Connect your GitHub repo
4. Render detects `render.yaml` and provisions:
   - PostgreSQL database
   - Backend web service
   - Frontend static service
5. Every push to `main` triggers an automatic redeploy

### Environment variables on Render

Render auto-generates `SECRET_KEY` (marked `generateValue: true` in `render.yaml`).  
The database `DATABASE_URL` is injected automatically from the linked PostgreSQL service.

---

## API Documentation

Interactive docs: http://localhost:8000/api/docs

### Endpoints Summary

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/auth/register` | ❌ | Register new user |
| `POST` | `/api/v1/auth/login` | ❌ | Login and receive JWT |
| `GET` | `/api/v1/tasks` | ✅ | List tasks (filter/sort/paginate) |
| `POST` | `/api/v1/tasks` | ✅ | Create a task |
| `GET` | `/api/v1/tasks/stats` | ✅ | Dashboard statistics |
| `GET` | `/api/v1/tasks/{id}` | ✅ | Get single task |
| `PUT` | `/api/v1/tasks/{id}` | ✅ | Update a task |
| `DELETE` | `/api/v1/tasks/{id}` | ✅ | Soft-delete a task |
| `GET` | `/api/v1/profile` | ✅ | Get current user profile |
| `PUT` | `/api/v1/profile` | ✅ | Update profile |
| `PUT` | `/api/v1/profile/password` | ✅ | Change password |
| `POST` | `/api/v1/profile/avatar` | ✅ | Upload avatar image |
| `GET` | `/api/v1/admin/users` | 🛡 Admin | List all users |
| `DELETE` | `/api/v1/admin/users/{id}` | 🛡 Admin | Delete a user |
| `PATCH` | `/api/v1/admin/users/{id}/toggle-active` | 🛡 Admin | Activate/deactivate user |
| `GET` | `/health` | ❌ | Health check |

### Authentication

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@taskmanager.com","password":"Admin@123456"}'

# 2. Use returned token
curl http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <your_token>"
```

---

## Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage report
pip install pytest-cov
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_auth.py -v

# Run only fast tests
pytest -m "not slow" -v
```

The test suite uses:
- **In-memory SQLite** — tests never touch the real database
- **TestClient** — synchronous ASGI test client from FastAPI
- **Fixtures** — pre-seeded users and auth tokens for every test
- **Transaction rollback** — each test gets a fresh DB state

---

## Security

| Measure | Implementation |
|---------|---------------|
| Password hashing | bcrypt via `passlib` |
| Authentication | JWT signed with HS256 |
| Authorisation | Role-based (admin/user) dependency injection |
| Input validation | Pydantic v2 validators with regex |
| SQL injection | SQLAlchemy ORM (parameterised queries) |
| CORS | Configured via `fastapi.middleware.cors` |
| Rate limiting | `slowapi` middleware (60 req/min default) |
| Security headers | Custom middleware (X-Frame-Options, CSP, HSTS, etc.) |
| Secrets management | Environment variables, never hardcoded |
| File uploads | MIME type validation, size limits, UUID filenames |
| Soft deletes | Tasks are never permanently deleted immediately |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                             │
│   HTML5 / CSS3 / Vanilla JS  ←→  Chart.js                  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP (JSON / JWT)
┌──────────────────────▼──────────────────────────────────────┐
│                      Nginx (port 80)                        │
│   Serves static files · Reverse-proxies /api → backend      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                FastAPI Backend (port 8000)                  │
│   Middleware: CORS · Rate Limit · Logging · Security Headers│
│                                                             │
│   Routers → Services → SQLAlchemy ORM                       │
│   auth  │  tasks  │  users/profile/admin                   │
└──────────────────────┬──────────────────────────────────────┘
                       │ SQLAlchemy
┌──────────────────────▼──────────────────────────────────────┐
│         SQLite (dev)  /  PostgreSQL 15 (prod)               │
└─────────────────────────────────────────────────────────────┘
```

---

## License

MIT License — free to use, modify, and distribute.

---

> Built with ❤ to demonstrate production-ready full-stack development, DevOps automation, and cloud deployment in a single portfolio project.
