from app.services.DataBase_connect.database import get_db

# 这是一个简单的别名，方便在路由中导入
# 实际的依赖注入逻辑在 database.py 的 get_db 函数中
def get_db_session():
    """
    提供一个 FastAPI 依赖，用于获取数据库会话。
    """
    yield from get_db()

