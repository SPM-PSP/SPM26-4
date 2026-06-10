from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库连接字符串
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:157613@localhost:3306/interviewdata"

# 创建数据库引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

# 创建一个 SessionLocal 类，每个请求都会创建一个独立的数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明性基类，用于定义 ORM 模型
Base = declarative_base()

# 数据库会话依赖
def get_db():
    """
    一个生成器函数，用于在 FastAPI 路由中获取数据库会话。
    它确保在请求结束后正确关闭数据库会话。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

