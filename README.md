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

`NOTE:` Poetry is recommended, but not required.  All commands in this README include non-poetry alternatives.

### About Poetry
Poetry is a modern dependency management tool for Python. Unlike traditional packages, Poetry should be installed globally on your system (not as a project dependency) to bootstrap the project setup. See installation instructions below.

**Modern Poetry Usage**: Since Poetry 2.0, `poetry shell` was moved to a plugin. The current best practices are:
1. **`poetry run <command>`** - For individual commands (most reliable)
2. **`poetry env activate`** - Outputs activation command for shell integration
3. **`poetry-plugin-shell`** - Optional plugin to restore `poetry shell` command

The `poetry run` approach is preferred as it's more reliable and works consistently across different environments and CI/CD systems.

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

**Poetry 2.0+ Options:**

```bash
# Option 1: Use poetry run for individual commands (recommended)
poetry run python --version
poetry run pytest

# Option 2: Get activation command (Poetry 2.0+)
poetry env activate
# This outputs: source /path/to/venv/bin/activate
# You can use it like: $(poetry env activate)

# Option 3: Install the shell plugin (if you prefer the old poetry shell)
poetry self add poetry-plugin-shell
poetry shell
```

**Note**: Since Poetry 2.0, `poetry shell` was removed from core and is now a plugin. The recommended approaches are `poetry run` for individual commands or `poetry env activate` to get the activation command.

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

### Development Server - Poetry
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

### Development Server - Non-poetry
```bash
# Assuming active virtual env
python src/main.py

# Or direct uvicorn
python -m uvicorn src.app.main:app --reload
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

### Poetry
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

### Non-Poetry Alternative
```bash
# Activate virtual environment (if not already activated)
source aweberenv/bin/activate  # On Windows: aweberenv\Scripts\activate

# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test files
python -m pytest tests/test_widget_model.py -v

# View coverage report
open htmlcov/index.html  # On macOS
```

## 🔧 Development Tools

### Automated Quality Checks
All code quality tools run automatically on every commit via pre-commit hooks:

#### Poetry
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

#### Non-Poetry Alternative
```bash
# One-time setup (after installing dependencies)
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

### Poetry Workflow
1. **Run commands with Poetry**: `poetry run python --version` (recommended)
2. **Create feature branch**: `git checkout -b feature/your-feature`
3. **Make changes** and write tests
4. **Run tests**: `poetry run pytest`
5. **Check code quality**: `pre-commit run --all-files`
6. **Commit changes**: `git commit -m "feat: your feature"`
7. **Push branch**: `git push origin feature/your-feature`
8. **Create Pull Request**

**Note**: Use `poetry run <command>` instead of activating the shell. This is more reliable and avoids shell state issues.

### Non-Poetry Workflow
1. **Activate virtual environment**: `source aweberenv/bin/activate` (Windows: `aweberenv\Scripts\activate`)
2. **Create feature branch**: `git checkout -b feature/your-feature`
3. **Make changes** and write tests
4. **Run tests**: `python -m pytest`
5. **Check code quality**: `pre-commit run --all-files`
6. **Commit changes**: `git commit -m "feat: your feature"`
7. **Push branch**: `git push origin feature/your-feature`
8. **Create Pull Request**

## 🆘 Troubleshooting

### Virtual Environment Issues

**Problem**: Virtual environment not found or activation fails

#### Poetry Solution:
```bash
# Solution: Recreate virtual environment with Poetry
poetry env remove python
poetry install

# Test the environment
poetry run python --version

# If you need shell activation:
$(poetry env activate)  # Activates the environment
# OR install the shell plugin:
poetry self add poetry-plugin-shell
poetry shell
```

#### Non-Poetry Solution:
```bash
# Solution: Recreate virtual environment manually
rm -rf aweberenv
python3 -m venv aweberenv
source aweberenv/bin/activate  # On Windows: aweberenv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Problem**: Dependencies not installing

#### Poetry Solution:
```bash
# Solution: Check Python version and clear Poetry cache
python --version  # Should be 3.12+
poetry cache clear pypi --all
poetry install
```

#### Non-Poetry Solution:
```bash
# Solution: Check Python version and reinstall dependencies
python --version  # Should be 3.12+
pip cache purge
pip install -r requirements.txt -r requirements-dev.txt --force-reinstall
```

### Database Issues

**Problem**: Database connection errors
```bash
# Solution: Run migrations (works with both Poetry and non-Poetry)
alembic upgrade head

# If database is corrupted, reset it
rm widgets.db test_widgets.db
alembic upgrade head
```

**Problem**: Migration conflicts
```bash
# Solution: Reset migration history (works with both Poetry and non-Poetry)
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
```

#### Poetry Solution:
```bash
# Or use different port
PORT=8080 poetry run python src/main.py
```

#### Non-Poetry Solution:
```bash
# Or use different port
PORT=8080 python src/main.py
```

**Problem**: Import errors

#### Poetry Solution:
```bash
# Solution: Check virtual environment and reinstall
poetry shell
poetry install
poetry run python src/main.py
```

#### Non-Poetry Solution:
```bash
# Solution: Check virtual environment and reinstall
source aweberenv/bin/activate  # On Windows: aweberenv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
python src/main.py
```

### Testing Issues

**Problem**: Tests failing due to database
```bash
# Solution: Clean test database
rm test_widgets.db
```

#### Poetry Solution:
```bash
poetry run pytest

# Or run tests with verbose output
poetry run pytest -v -s
```

#### Non-Poetry Solution:
```bash
python -m pytest

# Or run tests with verbose output
python -m pytest -v -s
```

**Problem**: Pre-commit hooks failing
```bash
# Solution: Run hooks manually and fix issues (works with both Poetry and non-Poetry)
pre-commit run --all-files

# Update pre-commit hooks
pre-commit autoupdate
```

### Code Quality Issues

**Problem**: Linting errors

#### Poetry Solution:
```bash
# Solution: Auto-format code
poetry run black src/ tests/
poetry run isort src/ tests/
poetry run flake8 src/ tests/  # Check remaining issues
```

#### Non-Poetry Solution:
```bash
# Solution: Auto-format code
black src/ tests/
isort src/ tests/
flake8 src/ tests/  # Check remaining issues
```

**Problem**: Type checking errors

#### Poetry Solution:
```bash
# Solution: Check mypy output and add type annotations
poetry run mypy src/
```

#### Non-Poetry Solution:
```bash
# Solution: Check mypy output and add type annotations
mypy src/
```

## 🤝 Contributing

### Poetry Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install dependencies (`poetry install`)
4. Set up pre-commit hooks (`poetry run pre-commit install`)
5. Make your changes and add tests
6. Run tests and quality checks (`poetry run pytest && pre-commit run --all-files`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

**Note**: Use `poetry run <command>` for all commands instead of activating the shell with `poetry shell`.

### Non-Poetry Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Create and activate virtual environment (`python3 -m venv aweberenv && source aweberenv/bin/activate`)
4. Install dependencies (`pip install -r requirements.txt -r requirements-dev.txt`)
5. Set up pre-commit hooks (`pre-commit install`)
6. Make your changes and add tests
7. Run tests and quality checks (`python -m pytest && pre-commit run --all-files`)
8. Commit your changes (`git commit -m 'Add amazing feature'`)
9. Push to the branch (`git push origin feature/amazing-feature`)
10. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions, please open an issue in the GitHub repository.
