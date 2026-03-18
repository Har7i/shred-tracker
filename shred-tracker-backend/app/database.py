from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# 1. 定义数据库文件路径（sqlite + aiosqlite 协议）
# 这里的 ./test.db 会在项目根目录生成一个文件
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./data/shred_tracker.db"

# 2. 创建异步引擎
# check_same_thread=False 是 SQLite特有的，允许异步任务跨线程访问
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 3. 创建会话工厂（用来产生每次请求所需的数据库连接）
SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

# 4. 定义模型基类 (所有的数据库表模型都要继承它)
class Base(DeclarativeBase):
    pass

# 5. 定义一个 Dependency (用于 FastAPI 路由注入)
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

