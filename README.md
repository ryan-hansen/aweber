# Widget CRUD API

A modern, production-ready CRUD REST API built with Python 3.12 and FastAPI for managing Widget resources.

## 🚀 Features

- **Full CRUD Operations** - Create, Read, Update, Delete widgets
- **FastAPI Framework** - High-performance, modern Python web framework
- **Async Database Operations** - SQLAlchemy 2.0 with async SQLite
- **Data Validation** - Pydantic models for request/response validation
- **Automatic Documentation** - OpenAPI/Swagger docs generated automatically
- **Database Migrations** - Alembic for schema versioning
- **Comprehensive Testing** - Unit and integration tests with high coverage
- **Code Quality Tools** - Linting, formatting, security analysis
- **Type Safety** - Full type annotations with mypy checking

## 📋 Requirements

- Python 3.12+
- Poetry (for dependency management)

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd aweber
```

### 2. Install dependencies with Poetry
```bash
poetry install
```

### 3. Activate the virtual environment
```bash
poetry shell
```

### 4. Run database migrations
```bash
alembic upgrade head
```

## 🏃‍♂️ Running the Application

### Development Server
```bash
# Default (secure localhost binding)
poetry run python src/main.py

# Or with uvicorn directly
poetry run uvicorn src.app.main:app --reload

# For network access (Docker, external devices)
HOST=0.0.0.0 PORT=8000 poetry run python src/main.py
```

The API will be available at:
- **Application**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `127.0.0.1` | Server host binding (use `0.0.0.0` for network access) |
| `PORT` | `8000` | Server port number |
| `DATABASE_URL` | `sqlite:///./widgets.db` | Database connection URL |
| `DEBUG` | `true` | Enable debug mode |
| `LOG_LEVEL` | `info` | Logging level |

## 🧪 Testing

### Run all tests
```bash
poetry run pytest
```

### Run tests with coverage
```bash
poetry run pytest --cov=src --cov-report=html
```

### Run specific test files
```bash
poetry run pytest tests/test_widget_model.py -v
```

## 🔧 Development Tools

### Code Formatting
```bash
poetry run black src/ tests/
```

### Linting
```bash
poetry run flake8 src/ tests/
```

### Type Checking
```bash
poetry run mypy src/
```

### Security Analysis
```bash
poetry run bandit -r src/
```

### Pre-commit Hooks
All quality checks run automatically on commit:
```bash
pre-commit install  # One-time setup
```

## 📊 API Endpoints

### Widget Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/widgets` | Create a new widget |
| `GET` | `/widgets` | List all widgets (with pagination) |
| `GET` | `/widgets/{id}` | Get widget by ID |
| `PUT` | `/widgets/{id}` | Update widget by ID |
| `DELETE` | `/widgets/{id}` | Delete widget by ID |

### Health Check
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Application health status |

## 📝 Widget Data Model

```json
{
  "id": 1,
  "name": "Super Widget",
  "number_of_parts": 42,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Field Specifications
- **id**: Auto-generated primary key (integer)
- **name**: Widget name (string, max 64 characters, required)
- **number_of_parts**: Number of parts (positive integer, required)
- **created_at**: Creation timestamp (auto-generated)
- **updated_at**: Last update timestamp (auto-updated)

## 📁 Project Structure

```
src/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application setup
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection and session management
│   └── models/
│       ├── __init__.py
│       └── widget.py        # Widget SQLAlchemy model
├── docs/                    # Documentation files
├── tests/                   # Test files
├── alembic/                 # Database migration files
├── pyproject.toml          # Poetry dependencies and project config
└── README.md               # This file
```

## 🚀 Deployment

### Production Requirements
- Set `DEBUG=false` in environment
- Configure production database URL
- Set up proper logging
- Use production WSGI server (Gunicorn recommended)

### Environment Variables
```bash
# Optional configuration
DATABASE_URL=sqlite:///./widgets.db
DEBUG=false
LOG_LEVEL=info
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests and quality checks (`poetry run pytest && pre-commit run --all-files`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions, please open an issue in the GitHub repository.
