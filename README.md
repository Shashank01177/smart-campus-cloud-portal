# Smart Campus Cloud Portal using Microsoft Azure

A comprehensive, cloud-native university management web portal and digital twin deployed on **Microsoft Azure**, integrating containerization, relational database management, role-based access control, and continuous monitoring.

🔗 **Live Deployment:** [https://campusos-sasank.azurewebsites.net](https://campusos-sasank.azurewebsites.net)

---

## 🏛️ Architecture Overview

The system is architected following cloud-native best practices across compute, storage, containerization, and monitoring:

```
[ User Browser (Student / Faculty / Admin) ]
                    │
                    ▼  HTTPS
[ Azure App Service (Linux Web App) ]
         │ (Gunicorn WSGI + Flask API)
         ├────────────────────────────────────────┐
         ▼                                        ▼
[ Azure Database for PostgreSQL ]        [ Azure Application Insights ]
  (Flexible Server - Relational Data)      (Azure Monitor Live Telemetry)
         ▲
         │ (Built & Packaged Image)
[ Azure Container Registry (ACR) ]
  (campusosacr24026.azurecr.io)
         ▲
         │ (Automated CI/CD Workflow)
[ GitHub Actions Pipeline ]
```

### Cloud Services & Technologies Used:
* **Web Hosting & Compute:** Azure App Service (Linux F1 / Python 3.11 Runtime)
* **Containerization:** Docker & Azure Container Registry (`campusosacr24026.azurecr.io`)
* **Relational Database:** Azure Database for PostgreSQL Flexible Server (`campusos-db-sasank.postgres.database.azure.com`)
* **Monitoring & Telemetry:** Azure Monitor & Application Insights (`campusos-insights`)
* **CI/CD Automation:** GitHub Actions (`.github/workflows/docker-acr-deploy.yml`)
* **Backend:** Python Flask REST API with Gunicorn WSGI
* **Frontend:** Interactive 3D Digital Twin UI (HTML5, Vanilla CSS3, Modern JavaScript)

---

## 🛡️ Role-Based Access Control (RBAC)

The portal implements strict role-based permission tiers:

| Role | Access Permissions | Student Management Capabilities |
| :--- | :--- | :--- |
| **Admin** | Full system overview, statistics, department/course metrics, database SQL console. | **Full Control:** Can add new students (`+ Add student`) and delete students (`Delete`). |
| **Faculty** | Class lists, course schedules, attendance overview, grading metrics. | **Read-Only:** Student management controls are hidden and API-level blocked (`HTTP 403 Forbidden`). |
| **Student** | Personal academic dashboard, enrolled courses, attendance tracking, marks/CGPA, fee status. | **Read-Only:** No administrative permissions. |

---

## 📁 Repository Structure

```
├── .github/
│   └── workflows/
│       └── docker-acr-deploy.yml   # CI/CD pipeline building & pushing container to ACR
├── assets/
│   ├── app.js                     # Frontend interactive application logic & state management
│   └── style.css                  # UI theme, design system, and isometric campus styling
├── Dockerfile                     # Multi-stage production container definition
├── .dockerignore                  # Docker build context exclusions
├── index.html                     # Single-Page Application (SPA) entrypoint
├── requirements.txt               # Backend Python dependencies
├── server.py                      # Flask REST API, authentication, and PostgreSQL handlers
├── start.bat                      # Local launch script
└── README.md                      # Project documentation
```

---

## 🐳 Docker Containerization

The backend and frontend are containerized via the included `Dockerfile`:

```dockerfile
# Build image locally
docker build -t campusos:v1 .

# Run container locally on port 8000
docker run -p 8000:8000 -e CAMPUSOS_DB_HOST=<db-host> campusos:v1
```

---

## 🔄 CI/CD Pipeline

The `.github/workflows/docker-acr-deploy.yml` action triggers on every commit to `main`:
1. Checks out repository code.
2. Authenticates to **Azure Container Registry** (`campusosacr24026.azurecr.io`).
3. Builds and tags the Docker container image.
4. Pushes image to ACR and deploys directly to **Azure App Service**.

---

## 📈 Monitoring & Telemetry

Connected with **Azure Application Insights** (`campusos-insights`):
* Real-time server request rates, response times, and HTTP status tracking.
* SQL query latency and dependency mapping.
* Cloud diagnostic logging and automated health checks.
