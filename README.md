# Backend Technical Assessment - Acumen Strategy

## Overview

Data pipeline with 3 Docker services for technical assessment.

## Architecture

```
Flask Mock Server (port 5000)
    ↓ (JSON data with pagination)
FastAPI Pipeline Service (port 8000)
    ↓ (ingest & upsert)
PostgreSQL (port 5432)
    ↓
API Response
```

## Services

### 1. Flask Mock Server
- **Framework:** Flask
- **Port:** 5000
- **Purpose:** Mock customer data server
- **Data:** 22 customers loaded from JSON file

#### Endpoints:
- `GET /api/customers?page=1&limit=10` - Paginated customer list
- `GET /api/customers/{id}` - Single customer by ID
- `GET /api/health` - Health check

### 2. FastAPI Pipeline Service
- **Framework:** FastAPI
- **Port:** 8000
- **Purpose:** Data ingestion pipeline

#### Endpoints:
- `POST /api/ingest` - Fetch data from Flask and upsert to PostgreSQL
- `GET /api/customers?page=1&limit=10` - Paginated list from database
- `GET /api/customers/{id}` - Single customer by ID
- `GET /api/health` - Health check with DB status

### 3. PostgreSQL
- **Image:** postgres:15
- **Port:** 5432
- **Database:** customer_db
- **User:** postgres / password

## Quick Start

### Prerequisites
- Docker Desktop (running)
- Docker Compose

### Start Services

```bash
docker-compose up -d
```

### Check Service Status

```bash
docker-compose ps
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f flask-mock-server
docker-compose logs -f fastapi-pipeline-service
docker-compose logs -f postgres
```

## Testing

### 1. Test Flask Mock Server

```bash
# Health check
curl http://localhost:5000/api/health

# Get customers (paginated)
curl "http://localhost:5000/api/customers?page=1&limit=5"

# Get single customer
curl http://localhost:5000/api/customers/CUST001
```

### 2. Test FastAPI Pipeline Service

```bash
# Health check
curl http://localhost:8000/api/health

# Ingest data from Flask to PostgreSQL
curl -X POST http://localhost:8000/api/ingest

# Get customers from database
curl "http://localhost:8000/api/customers?page=1&limit=5"

# Get single customer
curl http://localhost:8000/api/customers/CUST001
```

### 3. Test Database Connection

```bash
# Connect to PostgreSQL
docker exec -it postgres-db psql -U postgres -d customer_db

# Query customers table
SELECT * FROM customers LIMIT 5;

# Exit psql
\q
```

## Project Structure

```
backend-technical-assesment-acumen-strategy/
├── docker-compose.yml
├── LICENSE
├── README.md
├── flask-mock-server/
│   ├── app.py
│   ├── data/
│   │   └── customers.json (22 customers)
│   ├── Dockerfile
│   └── requirements.txt
└── fastapi-pipeline-service/
    ├── main.py
    ├── models/
    │   └── customer.py (SQLAlchemy model)
    ├── services/
    │   └── ingestion.py (ingestion & upsert logic)
    ├── database.py (DB connection)
    ├── Dockerfile
    └── requirements.txt
```

## Features

### Flask Mock Server
- ✅ Load data from JSON file (not hardcoded)
- ✅ Pagination support (page, limit params)
- ✅ 404 handling for missing customers
- ✅ Health check endpoint

### FastAPI Pipeline Service
- ✅ Auto-pagination from Flask API
- ✅ Upsert logic (update if exists, insert if new)
- ✅ SQLAlchemy ORM with PostgreSQL
- ✅ Async HTTP client for Flask API calls
- ✅ Error handling and rollback
- ✅ Health check with database status

### Docker Compose
- ✅ Health checks for all services
- ✅ Proper service dependencies
- ✅ Environment variables configuration
- ✅ Port mapping


## Stop Services

```bash
docker-compose down
```

## Remove All Data (including volumes)

```bash
docker-compose down -v
```

## License

This code is submitted exclusively for Acumen Strategy technical assessment purposes only.
