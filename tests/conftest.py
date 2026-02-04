import pytest
import sys
import os
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

# 将项目根目录加入路径，确保能导入 backend 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openapi_server.main import app
from backend.console.dal.rds.user import Base

# 1. 配置测试用的 SQLite 内存数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    为每个测试函数创建一个新的数据库会话。
    测试开始前建表，测试结束后删表。
    """
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # 清理数据库
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """
    创建一个测试用的 HTTP 客户端。
    并使用 patch 拦截 handler 中的 get_db 调用。
    """
    def override_get_db():
        yield db_session

    # 关键点：因为你的 handler 内部直接调用了 get_db，我们需要 mock 掉它
    # 注意：这里的路径 'backend.console.dal.rds.client.get_db' 必须和你代码里的 import 路径一致
    with patch("backend.console.dal.rds.client.get_db", side_effect=override_get_db):
        with TestClient(app) as c:
            yield c