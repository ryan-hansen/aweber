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
- Poetry (for dependency management) - **Note**: Poetry needs to be installed globally first

### About Poetry
Poetry is a modern dependency management tool for Python. Unlike traditional packages, Poetry should be installed globally on your system (not as a project dependency) to bootstrap the project setup. See installation instructions below.

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd aweber
```

### 2. Install Poetry (if not already installed)

**Option A: Official installer (recommended)**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Option B: Via pip (global installation)**
```bash
pip install poetry
```

**Option C: Via pipx (isolated installation)**
```bash
pipx install poetry
```

For more installation options, see: https://python-poetry.org/docs/#installation

### 3. Install dependencies with Poetry
```bash
poetry install
```

### 4. Activate the virtual environment
```bash
poetry shell
```

### 5. Set up pre-commit hooks (for development)
```bash
pre-commit install
```

### 6. Run database migrations
```bash
alembic upgrade head
```

## 🔄 Alternative Installation (without Poetry)

If you prefer not to use Poetry, you can use Python's built-in venv and pip:

```bash
# Create virtual environment
python3 -m venv aweberenv

# Activate virtual environment
source aweberenv/bin/activate  # On Windows: aweberenv\Scripts\activate

# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (for testing, linting, etc.)
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run database migrations
alembic upgrade head
```

**Note:** The Poetry approach is recommended as it provides better dependency resolution and lock file management.

## 🏃‍♂️ Running the Application

### Development Server
```bash
# Activate virtual environment first (if not already activated)
poetry shell

# Default (secure localhost binding)
poetry run python src/main.py

# Or with uvicorn directly
poetry run uvicorn src.app.main:app --reload

# For network access (Docker, external devices)
HOST=0.0.0.0 PORT=8000 poetry run python src/main.py
```

The API will be available at:
- **Application**: http://localhost:8000
- **Interactive Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `127.0.0.1` | Server host binding (use `0.0.0.0` for network access) |
| `PORT` | `8000` | Server port number |
| `DATABASE_URL` | `sqlite:///./widgets.db` | Database connection URL |
| `DEBUG` | `true` | Enable debug mode |
| `LOG_LEVEL` | `info` | Logging level |

## 🧪 Testing

```bash
# Activate virtual environment (if not already activated)
poetry shell

# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test files
poetry run pytest tests/test_widget_model.py -v

# View coverage report
open htmlcov/index.html  # On macOS
```

## 🔧 Development Tools

### Automated Quality Checks
All code quality tools run automatically on every commit via pre-commit hooks:

```bash
# One-time setup (after installing dependencies)
pre-commit install

# Manual formatting (if needed)
poetry run black src/ tests/
poetry run isort src/ tests/

# Manual checks (if needed)
poetry run flake8 src/ tests/
poetry run mypy src/
poetry run bandit -r src/
```

The pre-commit hooks will automatically:
- Sort imports (isort)
- Format code (black)
- Check style (flake8)
- Analyze security (bandit)
- Verify types (mypy)

## 📊 API Endpoints

### Root
| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/` | API information | `{"message": "Welcome to Widget CRUD API", "version": "1.0.0", "docs": "/docs"}` |

### Health Check
| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/health` | Application health status | `{"status": "healthy", "service": "Widget CRUD API"}` |

### Widget Operations
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/widgets/` | Create a new widget |
| `GET` | `/widgets/` | List all widgets (with pagination) |
| `GET` | `/widgets/{widget_id}` | Get widget by ID |
| `PUT` | `/widgets/{widget_id}` | Update widget by ID |
| `DELETE` | `/widgets/{widget_id}` | Delete widget by ID |

## 📝 API Usage Examples

### Create a Widget
```bash
curl -X POST http://localhost:8000/widgets/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Super Widget",
    "number_of_parts": 42
  }'
```

### Get All Widgets
```bash
curl http://localhost:8000/widgets/
```

### Get Widget by ID
```bash
curl http://localhost:8000/widgets/1
```

### Update a Widget
```bash
curl -X PUT http://localhost:8000/widgets/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Widget",
    "number_of_parts": 50
  }'
```

### Delete a Widget
```bash
curl -X DELETE http://localhost:8000/widgets/1
```

### Health Check
```bash
curl http://localhost:8000/health
```

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
aweber/
├── src/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application setup
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database connection and session management
│   │   ├── exception_handlers.py # Global exception handling
│   │   ├── exceptions.py        # Custom exceptions
│   │   ├── logging_config.py    # Logging configuration
│   │   ├── middleware.py        # Custom middleware
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── widget.py        # Widget SQLAlchemy model
│   │   ├── repositories/        # Data access layer
│   │   ├── routers/            # API route handlers
│   │   └── schemas/            # Pydantic models
│   ├── main.py                 # Application entry point
│   └── __init__.py
├── tests/                      # Test files
├── alembic/                    # Database migration files
├── docs/                       # Documentation files
├── pyproject.toml             # Poetry dependencies and project config
├── poetry.lock                # Poetry lock file
├── .flake8                    # Flake8 configuration
├── bandit.yaml               # Bandit security configuration
├── .pre-commit-config.yaml   # Pre-commit hooks configuration
├── pytest.ini               # Pytest configuration
└── README.md                 # This file
```

## 🚀 Production Deployment

### Production Requirements
- Set `DEBUG=false` in environment
- Configure production database URL
- Set up proper logging
- Use production ASGI server (Gunicorn + Uvicorn recommended)

### Environment Variables for Production
```bash
DATABASE_URL=postgresql://user:password@localhost/widgets
DEBUG=false
LOG_LEVEL=warning
HOST=0.0.0.0
PORT=8000
```

## 🔧 Development Workflow

1. **Activate virtual environment**: `poetry shell`
2. **Create feature branch**: `git checkout -b feature/your-feature`
3. **Make changes** and write tests
4. **Run tests**: `poetry run pytest`
5. **Check code quality**: `pre-commit run --all-files`
6. **Commit changes**: `git commit -m "feat: your feature"`
7. **Push branch**: `git push origin feature/your-feature`
8. **Create Pull Request**

## 🆘 Troubleshooting

### Virtual Environment Issues

**Problem**: Virtual environment not found or activation fails
```bash
# Solution: Recreate virtual environment with Poetry
poetry env remove python
poetry install
poetry shell
```

**Problem**: Dependencies not installing
```bash
# Solution: Check Python version and clear Poetry cache
python --version  # Should be 3.12+
poetry cache clear pypi --all
poetry install
```

### Database Issues

**Problem**: Database connection errors
```bash
# Solution: Run migrations
poetry run alembic upgrade head

# If database is corrupted, reset it
rm widgets.db test_widgets.db
poetry run alembic upgrade head
```

**Problem**: Migration conflicts
```bash
# Solution: Reset migration history
poetry run alembic stamp head
poetry run alembic revision --autogenerate -m "reset migration"
poetry run alembic upgrade head
```

### Development Server Issues

**Problem**: Server won't start or port conflicts
```bash
# Solution: Check if port is in use
lsof -i :8000

# Kill existing process
kill -9 <PID>

# Or use different port
PORT=8080 poetry run python src/main.py
```

**Problem**: Import errors
```bash
# Solution: Check virtual environment and reinstall
poetry shell
poetry install
poetry run python src/main.py
```

### Testing Issues

**Problem**: Tests failing due to database
```bash
# Solution: Clean test database
rm test_widgets.db
poetry run pytest

# Or run tests with verbose output
poetry run pytest -v -s
```

**Problem**: Pre-commit hooks failing
```bash
# Solution: Run hooks manually and fix issues
pre-commit run --all-files

# Update pre-commit hooks
pre-commit autoupdate
```

### Code Quality Issues

**Problem**: Linting errors
```bash
# Solution: Auto-format code
poetry run black src/ tests/
poetry run isort src/ tests/
poetry run flake8 src/ tests/  # Check remaining issues
```

**Problem**: Type checking errors
```bash
# Solution: Check mypy output and add type annotations
poetry run mypy src/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install dependencies (`poetry install`)
4. Activate virtual environment (`poetry shell`)
5. Set up pre-commit hooks (`pre-commit install`)
6. Make your changes and add tests
7. Run tests and quality checks (`poetry run pytest && pre-commit run --all-files`)
8. Commit your changes (`git commit -m 'Add amazing feature'`)
9. Push to the branch (`git push origin feature/amazing-feature`)
10. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions, please open an issue in the GitHub repository.
