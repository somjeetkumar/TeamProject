# TaskFlow API

TaskFlow is a backend API for managing organizations, teams, and projects.

This project is built for Week 1 of the Advanced Backend & DevOps Track and focuses on core data models, CRUD APIs, validation, and API documentation.

## Tech Stack

- Python
- Django 5.2.17
- Django REST Framework
- SQLite
- drf-spectacular (Swagger/OpenAPI)

## Project Structure

```text
TeamProject/
├── manage.py
├── db.sqlite3
├── TaskFlow API.yaml
├── Task/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
└── TeamProject/
    ├── settings.py
    ├── urls.py
    ├── asgi.py
    └── wsgi.py
```

## Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd TeamProject
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

Install the required packages:

```bash
pip install django djangorestframework drf-spectacular
```

Or, if you create a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Start the server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

## API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/api/docs/
```

OpenAPI schema:

```text
http://127.0.0.1:8000/api/schema/
```

## API Endpoints

### Organizations

| Method | Endpoint |
|---|---|
| POST | `/organizations/` |
| GET | `/organizations/` |
| PUT | `/organization/<id>/` |
| DELETE | `/organization/<id>/` |

### Teams

| Method | Endpoint |
|---|---|
| POST | `/teams/` |
| GET | `/teams/` |
| PUT | `/team/<id>/` |
| DELETE | `/team/<id>/` |

### Projects

| Method | Endpoint |
|---|---|
| POST | `/projects/` |
| GET | `/projects/` |
| PUT | `/project/<id>/` |
| DELETE | `/project/<id>/` |

Use Swagger to see the request/response schemas and test the endpoints.

## Architecture

The project is organized around a layered backend approach:

```text
Request
   ↓
View
   ↓
Service / Business Logic
   ↓
ORM / Database
   ↓
Response
```

The purpose of this structure is to keep API handling, business logic, and database operations separated so the project can be extended with additional entities in future weeks.

## Current Scope

Week 1 focuses on:

- Organization CRUD
- Team CRUD
- Project CRUD
- User/model relationships required for future work
- Request/response validation
- API documentation

Authentication, JWT, and RBAC enforcement are planned for Week 2.

## Development

Run the Django development server with:

```bash
python manage.py runserver
```

Before submitting, verify that the APIs work and that the Swagger documentation is accessible.
