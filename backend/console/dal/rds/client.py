from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 格式: mysql+pymysql://用户名:密码@地址:端口/数据库名
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:lkhdsg@localhost:3306/StarRoll"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True, # 自动重连，防止连接断开
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()