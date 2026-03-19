# StarRoll Backend Development Documentation

## 1. Project Architecture

We follow a **Layered Architecture** principle. Each layer has a distinct responsibility, and **cross-layer bypassing is strictly forbidden**.

### 1.1 Directory Structure

```text
starroll/
├── backend/console/
│   ├── dal/                # Data Access Layer
│   │   ├── rds/
│   │   │   ├── sql/        # SQL scripts for table creation
│   │   │   ├── client.py   # DB Connection & Session Management
│   │   │   └── user.py     # ORM Model Definitions & DAO Methods
│   ├── handler/            # Business Logic Layer
│   │   ├── user_login.py   # Specific login logic implementation
│   │   └── ...
│   └── utils/              # Shared Utility Layer
│       └── auth.py         # JWT Token Generation Tools
├── openapi_server/         # Interface Layer (Auto-generated)
│   ├── apis/               # Router Definitions
│   └── impl/               # Implementation Glue Code
├── tests/                  # Unit & Integration Tests
└── .env                    # Environment Variables (⚠️ DO NOT COMMIT)

```

### 1.2 Request Flow

1. **Interface Layer (`openapi_server`)**: Receives the HTTP request and performs basic data schema validation (Pydantic).
2. **Implementation Layer (`impl`)**: Routes the request to the specific Handler.
3. **Handler Layer (`handler`)**: Executes core business logic (e.g., password hashing, logical checks, exception raising).

- > **Note**: Writing SQL queries here is strictly **forbidden**.

4. **Data Access Layer (`dal`)**: Executes database operations via ORM.

- > **Note**: All database interactions must occur **only** in this layer.

5. **Database**: Stores the final data.

## 2. Development Standards

### 2.1 General Rules

- **Language**: All variables, function names, class names, and comments within the code must be in **English**.
- **Async**: Handlers and Controllers should uniformly use `async def`.
- **Secrets**: Never hardcode passwords or keys in the source code. You must use a `.env` file combined with `os.getenv`.

### 2.2 Database & ORM (DAL Layer)

- **Table Creation**: All table creation scripts must be placed in `backend/console/dal/rds/sql`. The naming convention is `create_tablename.sql`.
- **File Location**: `backend/console/dal/rds/`.
- **Naming Convention**: Python files should be named after the entity (e.g., `user.py`, `order.py`).
- **Strict Encapsulation**: The Handler layer is **absolutely forbidden** from directly writing `db.query(...)`. All DB operations must be encapsulated as `@classmethod` inside the Model class.

**Correct Example (`user.py`):**

```python
class User(Base):
    # ... Field Definitions ...

    @classmethod
    def get_by_username(cls, db: Session, username: str):
        return db.query(cls).filter(cls.username == username).first()

```

### 2.3 Handler Layer

- **File Location**: `backend/console/handler/`
- **Primary Responsibilities**:
- Business-level parameter validation (beyond basic type checking).
- Business rule processing (e.g., "Email must be verified before login").
- Calling DAL layer methods to retrieve/save data.
- Generating response data.
- Error handling (raising `HTTPException`).

**Code Comparison (`user_login.py`):**

```python
# ✅ CORRECT: Call the DAO method
user = User.get_by_username(db, username)

# ❌ WRONG: Forbidden to write queries in Handler
user = db.query(User).filter(...).first()

```

### 2.4 Authentication (JWT)

- **Mechanism**: Bearer Token.
- **Generation**: Use `backend.console.utils.auth.create_access_token` to generate tokens.
- **Validation**: Protected endpoints must verify the validity of the Token in the HTTP Header.

## 3. Development Workflow (How to Add a New Feature)

Follow these steps to complete the development of a new feature:

1. **Define API**:

- Modify the `idl/openapiv3.yaml` definition file to describe the new endpoint.

2. **Generate Code**:

- Use Docker to update the files in the `gen` directory.
- _Example command (Mac/Linux):_

```bash
docker run --rm \
    -v "${PWD}:/local" \
    openapitools/openapi-generator-cli:v7.18.0 generate \
    -i /local/idl/openapiv3.yaml \
    -g python-fastapi \
    -o /local/gen/py
```

- > **Windows Users**: Please adjust the path format in the command above or consult AI for the PowerShell version.

3. **Update Database (If needed)**:

- Add fields in `backend/console/dal/rds/user.py` (or other model files).
- Write the corresponding DAO methods (Create, Read, Update, Delete).

4. **Implement Handler**:

- Create a new file in `backend/console/handler/` (e.g., `your_new_feature.py`).
- Write the business logic.

5. **Connect Router**:

- Modify `openapi_server/impl/starroll_impl.py` to call your implemented Handler.

6. **Write Tests**:

- Add corresponding test cases in the `tests/` directory.

## 4. Testing Guide

We use **Pytest** with a dedicated **MySQL test service** in UT to keep test behavior aligned with runtime SQL semantics.

## 5. Deployment & Configuration

This section provides a guide to setting up the test environment. The backend depends on the following services:

- mysql
- minio
- astronomy.net
- redis
- kafka

### Environment Variables (`.env`)

Create a `.env` file in the project root directory. Refer to the format in `backend/.env.example` and modify the values to match your test environment.

### mysql

You can quickly start a MySQL service using the following command:

```bash
docker run -d \
  --name mysql-starroll \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=your_password \
  mysql:latest
```

### minio

```bash
docker run -d \
  --name starroll-minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  minio/minio:latest \
  server /data --console-address ":9001"
```

### astronomy.net

```bash
docker run -d -p 8001:8000 dm90/astrometry
```

### redis

```bash
docker run --name starroll-redis -d \
  -p 6379:6379 \
  redis:latest \
  redis-server --requirepass "starroll"
```

### kafka

```bash
docker run -d \
  --name starroll-kafka \
  -p 9092:9092 \
  -e KAFKA_NODE_ID=1 \
  -e KAFKA_PROCESS_ROLES=broker,controller \
  -e KAFKA_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  -e KAFKA_CONTROLLER_QUORUM_VOTERS=1@localhost:9093 \
  -e KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT \
  apache/kafka:latest
```
