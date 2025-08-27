# FastAPI Hexagonal Architecture Application

🌐 **[Русская версия / Russian Version](README.md)**

A modern FastAPI application implementing hexagonal architecture (ports and adapters) with database persistence, Dishka dependency injection, comprehensive testing, and proper separation of concerns.

## 🏗️ Architecture

This project follows **Hexagonal Architecture** principles with clear **Ports and Adapters** pattern, ensuring:
- **Domain isolation**: Business logic is completely independent of external concerns
- **Inversion of dependencies**: Domain defines interfaces, infrastructure implements them
- **Testability**: Easy to mock and test each layer independently
- **Flexibility**: Can swap databases, APIs, or frameworks without changing business logic
- **Maintainability**: Clear boundaries and responsibilities for each component

### Hexagonal Architecture Layers

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        INBOUND ADAPTERS                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │   FastAPI REST   │  │   Health Check   │  │   Future: CLI    │      │
│  │   Controllers    │  │   Controllers    │  │   GraphQL, gRPC  │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                             ┌─────────────┐
                             │ INBOUND     │
                             │ PORTS       │ ← Interface contracts
                             │ (Services)  │   for use cases
                             └─────────────┘
                                   │
┌──────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │   Item Service   │  │   DTOs & Data    │  │   Application    │      │
│  │   (Use Cases)    │  │   Transfer       │  │   Exceptions     │      │
│  │   Business Flow  │  │   Objects        │  │   & Validation   │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────────────────────────────────────────────┐
│                           DOMAIN LAYER                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │   Item Entity    │  │   Value Objects  │  │   Domain         │      │
│  │   (Core Business │  │   (Immutable     │  │   Exceptions     │      │
│  │    Rules)        │  │    Values)       │  │   & Rules        │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                             ┌─────────────┐
                             │ OUTBOUND    │
                             │ PORTS       │ ← Interface contracts
                             │ (Repository │   for external deps
                             │  & Cache)   │
                             └─────────────┘
                                   │
┌──────────────────────────────────────────────────────────────────────────┐
│                       OUTBOUND ADAPTERS                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │   SQLAlchemy     │  │   Redis Cache    │  │   Future: Event  │      │
│  │   Database       │  │   Adapter        │  │   Streaming,     │      │
│  │   Adapter        │  │   (Prepared)     │  │   External APIs  │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────────────────────────────────────────────┐
│                       INFRASTRUCTURE                                    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │   Database       │  │   Dishka DI      │  │   Configuration  │      │
│  │   Configuration  │  │   Container      │  │   & Settings     │      │
│  │   & Models       │  │   & Providers    │  │   Management     │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
└──────────────────────────────────────────────────────────────────────────┘
```

## 🌟 Features

### Architecture & Design
- **True Hexagonal Architecture**: Ports and adapters with clear boundaries
- **Dependency Inversion**: Domain layer defines interfaces, infrastructure implements
- **SOLID Principles**: Single responsibility, open/closed, dependency inversion
- **Clean Code**: Separation of concerns with testable components

### Technical Features
- **Database Persistence**: SQLite with async SQLAlchemy 2.0 ORM
- **Advanced Dependency Injection**: Dishka DI container with provider pattern
- **Full Async Support**: End-to-end async/await implementation
- **Database Migrations**: Alembic for schema versioning and management
- **Type Safety**: Complete type annotations with Pydantic v2 models
- **Input Validation**: Comprehensive validation with custom error handling
- **API Documentation**: Auto-generated OpenAPI 3.0 docs with examples
- **Health Monitoring**: System and database connectivity health checks
- **Error Handling**: Domain-specific exceptions with proper HTTP responses
- **Configuration Management**: Environment-based settings with Pydantic Settings

### Testing & Quality
- **Comprehensive Testing**: Unit, integration, and API tests with pytest
- **Test Isolation**: Proper mocking and dependency injection for tests
- **Code Coverage**: Coverage reporting and analysis
- **Factory Pattern**: Test data generation with Factory Boy
- **Async Testing**: Full async test support with pytest-asyncio

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

**Option A: Using existing conda environment (recommended for this project)**
```bash
conda activate beta2
```

**Option B: Using Python venv**
```bash
python -m venv venv
```

**Option C: Using new conda environment**
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

The project follows a strict hexagonal architecture with clear separation of layers:

```
q_betatest/
├── src/
│   ├── domain/                           # 🏛️ DOMAIN LAYER (Core Business Logic)
│   │   ├── entities/
│   │   │   ├── item.py                      # Item entity with business rules
│   │   │   └── value_objects.py             # Immutable value objects
│   │   ├── ports/                        # 🔌 PORTS (Interface Contracts)
│   │   │   ├── inbound/                     # Driving side interfaces
│   │   │   │   └── services/
│   │   │   │       ├── __init__.py
│   │   │   │       └── item_service_port.py # Service interface (use cases)
│   │   │   └── outbound/                    # Driven side interfaces
│   │   │       ├── repositories/
│   │   │       │   └── item_repository.py   # Repository interface
│   │   │       └── cache/
│   │   │           └── item_cache_port.py   # Cache interface
│   │   └── exceptions.py                 # Domain-specific exceptions
│   │
│   ├── application/                      # 🎯 APPLICATION LAYER (Use Cases)
│   │   ├── services/
│   │   │   └── item_service.py              # Service implementation (orchestration)
│   │   ├── dtos/
│   │   │   └── item_dtos.py                 # Data Transfer Objects
│   │   └── exceptions.py                 # Application exceptions
│   │
│   └── infrastructure/                   # 🔧 INFRASTRUCTURE LAYER
│       ├── adapters/                     # 🔌 ADAPTERS (External Interface Implementations)
│       │   ├── inbound/                     # REST API, CLI, etc.
│       │   │   └── rest/
│       │   │       ├── item_controller.py   # FastAPI REST controllers
│       │   │       ├── health_controller.py # Health check endpoints
│       │   │       └── exception_handlers.py # HTTP error handling
│       │   └── outbound/                    # Database, Cache, External APIs
│       │       ├── database/
│       │       │   └── sql/
│       │       │       └── item_repository_adapter.py # SQLAlchemy implementation
│       │       └── cache/
│       │           └── redis/               # Redis cache implementation (prepared)
│       ├── config/
│       │   └── settings.py                  # Application configuration
│       ├── database/
│       │   ├── config.py                    # Database connection setup
│       │   └── models.py                    # SQLAlchemy ORM models
│       ├── di/
│       │   └── container.py                 # Dishka dependency injection container
│       ├── logging/
│       │   ├── __init__.py
│       │   └── config.py                    # Logging configuration
│       └── repositories/
│           └── item_repository_impl.py      # Legacy repository (being migrated)
│
├── tests/                                # 🧪 COMPREHENSIVE TEST SUITE
│   ├── unit/                                # Unit tests for isolated components
│   │   ├── test_item_repository.py             # Repository layer tests
│   │   ├── test_dishka_container.py            # DI container tests
│   │   └── test_input_validation.py            # Input validation tests
│   ├── integration/                         # Integration tests
│   │   └── test_item_repository.py             # Database integration tests
│   └── conftest.py                          # Pytest configuration and fixtures
│
├── alembic/                              # 📊 DATABASE MIGRATIONS
│   ├── versions/
│   │   └── 385f34aedcb2_initial_migration.py   # Database schema migrations
│   ├── env.py                               # Alembic environment configuration
│   └── README                               # Migration instructions
│
├── main.py                               # 🚀 Application entry point
├── init_db.py                            # 🗄️ Database initialization script
├── debug_test.py                         # 🐛 Debug utilities
├── test_api.py                           # 🔍 Manual API testing script
├── alembic.ini                           # ⚙️ Alembic configuration
├── pytest.ini                            # 🧪 Pytest configuration
├── requirements.txt                       # 📦 Python dependencies
└── README.md                             # 📖 This documentation
```

### 🏗️ Architecture Explanation

#### Domain Layer (Core)
- **Entities**: Business objects with identity and lifecycle
- **Value Objects**: Immutable objects representing concepts
- **Ports**: Interface contracts defining what the domain needs (outbound) and provides (inbound)
- **Exceptions**: Domain-specific error definitions

#### Application Layer (Orchestration)
- **Services**: Implement inbound ports, orchestrate domain operations
- **DTOs**: Data transfer objects for application boundaries
- **Exceptions**: Application-level error handling

#### Infrastructure Layer (Technical Details)
- **Inbound Adapters**: REST controllers, CLI handlers, message consumers
- **Outbound Adapters**: Database repositories, cache implementations, external APIs
- **Configuration**: Settings, database setup, dependency injection
- **Cross-cutting Concerns**: Logging, monitoring, security

### 🔄 Dependency Flow
```
Inbound Adapters → Inbound Ports → Application Services → Outbound Ports → Outbound Adapters
      ↓                ↓                   ↓                 ↓                ↓
  REST API      Service Interface    Use Case Logic    Repository      Database
   (FastAPI)    (item_service_port)   (ItemService)    Interface      (SQLAlchemy)
```

## 🧪 Testing

The hexagonal architecture with dependency injection makes testing comprehensive and maintainable:

### Test Structure
- **Unit Tests**: Test individual components in isolation with mocked dependencies
- **Integration Tests**: Test adapter implementations against real external systems
- **API Tests**: End-to-end testing through REST endpoints
- **Contract Tests**: Verify that adapters correctly implement port interfaces

### Running Tests

**Run all tests:**
```bash
pytest
```

**Run with coverage:**
```bash
pytest --cov=src --cov-report=html
```

**Run specific test categories:**
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Async tests with detailed output
pytest -v -s tests/
```

### Test Features
- **Dishka DI Testing**: Proper dependency injection testing with container validation
- **Async Test Support**: Full async/await testing with pytest-asyncio
- **Database Testing**: In-memory SQLite for fast, isolated database tests
- **Factory Pattern**: Consistent test data generation with Factory Boy
- **Mocking**: Strategic mocking of external dependencies at port boundaries

### Testing Strategy
The architecture enables testing at multiple levels:
1. **Domain Layer**: Pure unit tests with no external dependencies
2. **Application Layer**: Service tests with mocked repositories
3. **Adapter Layer**: Integration tests with real external systems
4. **End-to-End**: Full application tests through REST API

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

### 🏛️ Clean Architecture Principles
1. **Domain Independence**: Core business logic is completely isolated from external concerns
2. **Dependency Inversion**: High-level modules don't depend on low-level modules
3. **Interface Segregation**: Well-defined, focused interfaces at architectural boundaries
4. **Single Responsibility**: Each layer and component has a clear, single purpose

### 🔧 Technical Advantages
1. **Testability**: Easy unit testing with dependency injection and mocking at port boundaries
2. **Flexibility**: Swap databases, APIs, or frameworks without touching business logic
3. **Maintainability**: Clear separation makes code easy to understand, modify, and extend
4. **Scalability**: Well-defined boundaries enable horizontal and vertical scaling
5. **Technology Independence**: Domain layer free from framework-specific code
6. **Parallel Development**: Teams can work independently on different adapters

### 🚀 Modern Development Features
1. **Type Safety**: Full type annotations prevent runtime errors
2. **Async Performance**: Non-blocking I/O for high throughput
3. **Dependency Injection**: Dishka provides enterprise-grade DI with lifecycle management
4. **Configuration Management**: Environment-based configuration with validation
5. **Database Migrations**: Versioned schema changes with rollback support

## 🔮 Future Enhancements

### 🔐 Security & Authentication
- [ ] JWT-based authentication system
- [ ] Role-based access control (RBAC)
- [ ] API key management
- [ ] Rate limiting and throttling

### 📊 Performance & Scaling
- [ ] Redis caching layer implementation
- [ ] Database connection pooling optimization
- [ ] Async background task processing
- [ ] Horizontal scaling with load balancing

### 🗄️ Database Support
- [ ] PostgreSQL adapter implementation
- [ ] MySQL adapter implementation
- [ ] MongoDB adapter for document storage
- [ ] Database sharding strategies

### 🔍 Observability
- [ ] Structured logging with correlation IDs
- [ ] Prometheus metrics collection
- [ ] Distributed tracing with OpenTelemetry
- [ ] Health check enhancements

### 🛠️ Development Experience
- [ ] Docker containerization
- [ ] Kubernetes deployment manifests
- [ ] CI/CD pipeline with GitHub Actions
- [ ] API versioning strategy
- [ ] GraphQL adapter implementation
- [ ] Event-driven architecture with message queues

### 🧪 Testing Improvements
- [ ] Property-based testing with Hypothesis
- [ ] Load testing with Locust
- [ ] Contract testing between services
- [ ] Mutation testing for test quality

### 📚 Documentation
- [ ] Architecture Decision Records (ADRs)
- [ ] API documentation with examples
- [ ] Development guides and tutorials
- [ ] Deployment and operations manual