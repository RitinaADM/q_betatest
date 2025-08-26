# FastAPI Hexagonal Architecture Application

A FastAPI application implementing hexagonal architecture (ports and adapters) with database persistence, dependency injection, and proper separation of concerns.

## 🏗️ Architecture

This project follows **Hexagonal Architecture** principles, ensuring:
- Clear separation between business logic and technical details
- Technology-agnostic domain layer
- Testable and maintainable code
- Flexibility to change infrastructure without affecting business logic

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Adapters (UI/API)                      │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │  FastAPI        │  │  Health Check   │                 │
│  │  Controllers    │  │  Controller     │                 │
│  └─────────────────┘  └─────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │  Item Service   │  │  DTOs           │                 │
│  │  (Use Cases)    │  │  (Data Transfer)│                 │
│  └─────────────────┘  └─────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                     Domain Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐│
│  │  Item Entity    │  │  Repository     │  │  Exceptions ││
│  │  (Business      │  │  Interfaces     │  │  (Domain    ││
│  │   Logic)        │  │  (Contracts)    │  │   Errors)   ││
│  └─────────────────┘  └─────────────────┘  └─────────────┘│
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │  SQLAlchemy     │  │  Database       │                 │
│  │  Repository     │  │  Configuration  │                 │
│  │  Implementation │  │  & Models       │                 │
│  └─────────────────┘  └─────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

## 🌟 Features

- **Hexagonal Architecture**: Clean separation of concerns
- **Database Persistence**: SQLite with SQLAlchemy ORM
- **Async Support**: Full async/await implementation
- **Database Migrations**: Alembic for schema management
- **Dependency Injection**: FastAPI's built-in DI system
- **Input Validation**: Pydantic models with validation
- **API Documentation**: Auto-generated OpenAPI docs
- **Health Checks**: System and database health monitoring
- **Error Handling**: Proper exception handling and HTTP responses

## 📋 API Endpoints

### Health & Info
- `GET /` - Welcome message
- `GET /health` - Health check with database connectivity

### Items Management
- `GET /items` - Get all items
- `GET /items/{item_id}` - Get item by ID
- `POST /items` - Create new item
- `PUT /items/{item_id}` - Update item
- `DELETE /items/{item_id}` - Delete item
- `GET /items/search/{query}` - Search items by name/description

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9 or higher
- Git

### 1. Clone & Navigate
```bash
cd path/to/your/project
```

### 2. Create Virtual Environment

**Option A: Using Python venv**
```bash
python -m venv venv
```

**Option B: Using conda (recommended)**
```bash
conda create -n fastapi-hex python=3.9
conda activate fastapi-hex
```

### 3. Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**If PowerShell execution policy is restricted:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Initialize Database

**Option A: Using initialization script (recommended)**
```bash
python init_db.py init --with-data
```

**Option B: Using Alembic migrations**
```bash
alembic upgrade head
python init_db.py seed  # Optional: add sample data
```

### 6. Run the Application

**Development mode (with auto-reload):**
```bash
python main.py
```

**Or using uvicorn directly:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🔎 Database Management

### Initialize Database
```bash
python init_db.py init          # Create tables only
python init_db.py init --with-data  # Create tables and add sample data
```

### Reset Database
```bash
python init_db.py reset         # Reset tables only
python init_db.py reset --with-data # Reset and add sample data
```

### Add Sample Data
```bash
python init_db.py seed
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📋 API Documentation

Once the server is running, access the interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📜 Project Structure

```
q_betatest/
├── src/
│   ├── domain/                 # Domain layer (business logic)
│   │   ├── entities/
│   │   │   ├── item.py            # Item entity with business rules
│   │   │   └── value_objects.py   # Value objects
│   │   ├── repositories/
│   │   │   └── item_repository.py # Repository interface
│   │   └── exceptions.py       # Domain exceptions
│   │
│   ├── application/            # Application layer (use cases)
│   │   ├── services/
│   │   │   └── item_service.py    # Application services
│   │   ├── dtos/
│   │   │   └── item_dtos.py       # Data Transfer Objects
│   │   └── exceptions.py       # Application exceptions
│   │
│   ├── infrastructure/         # Infrastructure layer (external concerns)
│   │   ├── database/
│   │   │   ├── config.py          # Database configuration
│   │   │   └── models.py          # SQLAlchemy models
│   │   └── repositories/
│   │       └── item_repository_impl.py # Repository implementation
│   │
│   └── adapters/               # Adapters layer (external interfaces)
│       └── api/
│           ├── item_controller.py  # FastAPI controllers
│           └── health_controller.py # Health check endpoints
│
├── alembic/                    # Database migrations
├── main.py                     # Application entry point
├── init_db.py                  # Database initialization script
├── alembic.ini                 # Alembic configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🧠 Testing

The hexagonal architecture makes testing straightforward by allowing easy mocking of dependencies.

### Manual API Testing

**Create an item:**
```bash
curl -X POST "http://localhost:8000/items" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Gaming Laptop",
       "description": "High-performance laptop for gaming",
       "price": 1299.99,
       "in_stock": true
     }'
```

**Get all items:**
```bash
curl "http://localhost:8000/items"
```

**Get item by ID:**
```bash
curl "http://localhost:8000/items/1"
```

**Update an item:**
```bash
curl -X PUT "http://localhost:8000/items/1" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Updated Gaming Laptop",
       "price": 1199.99
     }'
```

**Search items:**
```bash
curl "http://localhost:8000/items/search/laptop"
```

**Delete an item:**
```bash
curl -X DELETE "http://localhost:8000/items/1"
```

## 🐛 Troubleshooting

### PowerShell Execution Policy Issues
If you encounter PowerShell execution policy issues on Windows:

1. **Temporarily change execution policy:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Or use Command Prompt instead:**
   ```cmd
   venv\Scripts\activate.bat
   ```

### Database Issues

1. **Database file permissions:**
   - Ensure the application has write permissions in the project directory
   - The SQLite database file `items.db` will be created automatically

2. **Migration conflicts:**
   ```bash
   # Reset database and migrations
   python init_db.py reset
   alembic upgrade head
   ```

3. **Dependency installation issues:**
   - Use version ranges in requirements.txt to avoid compilation issues
   - Ensure you're using Python 3.9+ for compatibility

## 🎯 Architecture Benefits

1. **Testability**: Easy to unit test business logic without external dependencies
2. **Flexibility**: Can swap databases, APIs, or frameworks without changing business logic
3. **Maintainability**: Clear separation of concerns makes code easier to understand and modify
4. **Scalability**: Well-defined boundaries make it easier to scale and extend
5. **Technology Independence**: Domain layer is free from framework-specific code

## 🚀 Future Enhancements

- Add comprehensive unit tests
- Implement authentication and authorization
- Add caching layer
- Support for different databases (PostgreSQL, MySQL)
- Add logging and monitoring
- Implement event sourcing
- Add API versioning
- Container support (Docker)