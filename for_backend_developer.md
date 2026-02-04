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
* > **Note**: Writing SQL queries here is strictly **forbidden**.




4. **Data Access Layer (`dal`)**: Executes database operations via ORM.
* > **Note**: All database interactions must occur **only** in this layer.




5. **Database**: Stores the final data.

---

## 2. Development Standards

### 2.1 General Rules

* **Language**: All variables, function names, class names, and comments within the code must be in **English**.
* **Async**: Handlers and Controllers should uniformly use `async def`.
* **Secrets**: Never hardcode passwords or keys in the source code. You must use a `.env` file combined with `os.getenv`.

### 2.2 Database & ORM (DAL Layer)

* **Table Creation**: All table creation scripts must be placed in `backend/console/dal/rds/sql`. The naming convention is `create_tablename.sql`.
* **File Location**: `backend/console/dal/rds/`.
* **Naming Convention**: Python files should be named after the entity (e.g., `user.py`, `order.py`).
* **Strict Encapsulation**: The Handler layer is **absolutely forbidden** from directly writing `db.query(...)`. All DB operations must be encapsulated as `@classmethod` inside the Model class.

**Correct Example (`user.py`):**

```python
class User(Base):
    # ... Field Definitions ...
    
    @classmethod
    def get_by_username(cls, db: Session, username: str):
        return db.query(cls).filter(cls.username == username).first()

```

### 2.3 Handler Layer

* **File Location**: `backend/console/handler/`
* **Primary Responsibilities**:
* Business-level parameter validation (beyond basic type checking).
* Business rule processing (e.g., "Email must be verified before login").
* Calling DAL layer methods to retrieve/save data.
* Generating response data.
* Error handling (raising `HTTPException`).



**Code Comparison (`user_login.py`):**

```python
# ✅ CORRECT: Call the DAO method
user = User.get_by_username(db, username)

# ❌ WRONG: Forbidden to write queries in Handler
user = db.query(User).filter(...).first() 

```

### 2.4 Authentication (JWT)

* **Mechanism**: Bearer Token.
* **Generation**: Use `backend.console.utils.auth.create_access_token` to generate tokens.
* **Validation**: Protected endpoints must verify the validity of the Token in the HTTP Header.

---

## 3. Development Workflow (How to Add a New Feature)

Follow these steps to complete the development of a new feature:

1. **Define API**:
* Modify the `idl/openapiv3.yaml` definition file to describe the new endpoint.


2. **Generate Code**:
* Use Docker to update the files in the `gen` directory.
* *Example command (Mac/Linux):*
```bash
docker run --rm \
    -v "${PWD}:/local" \
    openapitools/openapi-generator-cli generate \
    -i /local/idl/openapiv3.yaml \
    -g python-fastapi \
    -o /local/gen/py
```


* > **Windows Users**: Please adjust the path format in the command above or consult AI for the PowerShell version.




3. **Update Database (If needed)**:
* Add fields in `backend/console/dal/rds/user.py` (or other model files).
* Write the corresponding DAO methods (Create, Read, Update, Delete).


4. **Implement Handler**:
* Create a new file in `backend/console/handler/` (e.g., `your_new_feature.py`).
* Write the business logic.


5. **Connect Router**:
* Modify `openapi_server/impl/starroll_impl.py` to call your implemented Handler.


6. **Write Tests**:
* Add corresponding test cases in the `tests/` directory.



---

## 4. Testing Guide

We use **Pytest** combined with an **In-Memory SQLite** database to ensure tests are fast and environmentally isolated.

### 4.1 Setup

Test code is located in the `tests/` directory. The core configuration file, `conftest.py`, is responsible for intercepting real database connections and replacing them with the memory database.

### 4.2 Running Tests

Run the following commands in PowerShell from the project root:

```powershell
# Run all tests
pytest

# Run and show print output (for Debugging)
pytest -s

# Check Code Coverage
pytest --cov=backend tests/

```

### 4.3 Testing Checklist

Before submitting code, ensure your tests cover the following:

* [ ] **Happy Path**: Does functionality work with correct input?
* [ ] **Edge Cases**: Empty strings, extremely long text, illegal characters, etc.
* [ ] **Security**: Wrong passwords, expired Tokens, unauthorized access.
* [ ] **Exceptions**: Are the correct HTTP 4xx/5xx status codes returned?

---

## 5. Deployment & Configuration

### Environment Variables (`.env`)

Create a `.env` file in the project root directory.

> ⚠️ **WARNING**: NEVER commit this file to the Git repository!

```ini
# Database Configuration
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=starroll

# Security Configuration
JWT_SECRET=generated_secure_hex_string
JWT_ALGORITHM=HS256

```