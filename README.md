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
- Virtual environment (aweberenv)

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd aweber
```

### 2. Set up the aweberenv virtual environment
```bash
# Create virtual environment
python3.12 -m venv aweberenv

# Activate virtual environment
source aweberenv/bin/activate  # On macOS/Linux
# or
aweberenv\Scripts\activate     # On Windows

# Upgrade pip
pip install --upgrade pip
```

### 3. Install dependencies
```bash
# Install all dependencies from pyproject.toml
pip install -e .

# Or install directly with pip
pip install fastapi uvicorn sqlalchemy alembic aiosqlite pydantic pydantic-settings
```

### 4. Install development dependencies (for development)
```bash
pip install pytest pytest-asyncio coverage httpx flake8 black bandit mypy pre-commit isort pytest-cov
```

### 5. Set up pre-commit hooks (for development)
```bash
pre-commit install
```

### 6. Run database migrations
```bash
alembic upgrade head
```

## 🏃‍♂️ Running the Application

### Development Server
```bash
# Activate virtual environment first
source aweberenv/bin/activate

# Default (secure localhost binding)
python src/main.py

# For network access (Docker, external devices)
HOST=0.0.0.0 PORT=8000 python src/main.py
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
# Activate virtual environment
source aweberenv/bin/activate

# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test files
pytest tests/test_widget_model.py -v

# View coverage report
open htmlcov/index.html  # On macOS
```

## 🔧 Development Tools

### Automated Quality Checks
All code quality tools run automatically on every commit via pre-commit hooks:

```bash
# One-time setup (after activating aweberenv)
pre-commit install

# Manual formatting (if needed)
black src/ tests/
isort src/ tests/

# Manual checks (if needed)
flake8 src/ tests/
mypy src/
bandit -r src/
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
├── aweberenv/                  # Virtual environment
├── docs/                       # Documentation files
├── pyproject.toml             # Poetry dependencies and project config
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

1. **Activate virtual environment**: `source aweberenv/bin/activate`
2. **Create feature branch**: `git checkout -b feature/your-feature`
3. **Make changes** and write tests
4. **Run tests**: `pytest`
5. **Check code quality**: `pre-commit run --all-files`
6. **Commit changes**: `git commit -m "feat: your feature"`
7. **Push branch**: `git push origin feature/your-feature`
8. **Create Pull Request**

## 🆘 Troubleshooting

### Virtual Environment Issues

**Problem**: `aweberenv` not found or activation fails
```bash
# Solution: Recreate virtual environment
rm -rf aweberenv
python3.12 -m venv aweberenv
source aweberenv/bin/activate
pip install --upgrade pip
pip install -e .
```

**Problem**: Dependencies not installing
```bash
# Solution: Check Python version and update pip
python --version  # Should be 3.12+
pip install --upgrade pip setuptools wheel
pip install -e .
```

### Database Issues

**Problem**: Database connection errors
```bash
# Solution: Run migrations
alembic upgrade head

# If database is corrupted, reset it
rm widgets.db test_widgets.db
alembic upgrade head
```

**Problem**: Migration conflicts
```bash
# Solution: Reset migration history
alembic stamp head
alembic revision --autogenerate -m "reset migration"
alembic upgrade head
```

### Development Server Issues

**Problem**: Server won't start or port conflicts
```bash
# Solution: Check if port is in use
lsof -i :8000

# Kill existing process
kill -9 <PID>

# Or use different port
PORT=8080 python src/main.py
```

**Problem**: Import errors
```bash
# Solution: Check virtual environment and PYTHONPATH
source aweberenv/bin/activate
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python src/main.py
```

### Testing Issues

**Problem**: Tests failing due to database
```bash
# Solution: Clean test database
rm test_widgets.db
pytest

# Or run tests with verbose output
pytest -v -s
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
black src/ tests/
isort src/ tests/
flake8 src/ tests/  # Check remaining issues
```

**Problem**: Type checking errors
```bash
# Solution: Check mypy output and add type annotations
mypy src/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Activate virtual environment (`source aweberenv/bin/activate`)
4. Install development dependencies (`pip install -e .`)
5. Set up pre-commit hooks (`pre-commit install`)
6. Make your changes and add tests
7. Run tests and quality checks (`pytest && pre-commit run --all-files`)
8. Commit your changes (`git commit -m 'Add amazing feature'`)
9. Push to the branch (`git push origin feature/amazing-feature`)
10. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions, please open an issue in the GitHub repository.
