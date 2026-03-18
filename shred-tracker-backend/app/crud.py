from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from .core import security
from app import models, schemas
from datetime import date

# 1. 【查】根据日期获取单条记录
# 作用：在新增前检查是否已存在，或者查询某天的进度
async def get_log_by_date(db: AsyncSession, log_date: date, user_id: int):
    result = await db.execute(
        select(models.DailyLog).where(
            models.DailyLog.date == log_date,
            models.DailyLog.owner_id == user_id
        )
    )
    return result.scalars().first()

async def get_all_logs(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    """
    skip: 跳过前 N 条 (offset)
    limit: 最多取 N 条
    """
    result = await db.execute(
        select(models.DailyLog)
        .where(models.DailyLog.owner_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

# 2. 【增】创建新记录
# 作用：将用户提交的有效数据存入数据库
async def create_log(db: AsyncSession, log: schemas.DailyLogCreate, user_id: int):
    db_log = models.DailyLog(
        **log.model_dump(),
        owner_id=user_id
    )
    db.add(db_log)
    db.add(db_log) # 放入暂存区
    try:
        await db.commit() # 提交到硬盘
        await db.refresh(db_log) # 刷新对象， 获取数据库生成的ID
        return db_log
    except Exception as e:
        await db.rollback() # 发生任何意外都要回滚，保证数据库“洁癖”
        raise e

# 3. 【改】更新现有记录
# 作用：如果用户发现称错体重了，可以修改
async def update_log(db: AsyncSession, log_date: date, log_update: schemas.DailyLogUpdate, user_id: int):
    # 确保查出的 db_log 是属于当前用户的
    db_log = await get_log_by_date(db, log_date, user_id)
    
    if not db_log:
        return None
    # 过滤掉用户没有传的空字段 (exclude_unset=True 是关键)
    update_data = log_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_log, key, value)

    await db.commit()
    await db.refresh(db_log)
    return db_log

# 4. 【删】根据日期删除记录
async def delete_log(db: AsyncSession, log_date: date, user_id: int):
    # 增加 owner_id 过滤，防止删掉别人的数据
    query = delete(models.DailyLog).where(
        models.DailyLog.date == log_date,
        models.DailyLog.owner_id == user_id
    )

    # 2. 执行删除
    result = await db.execute(query)

    # 3. 提交更改到硬盘
    await db.commit()

    # 4. 返回受影响的行数（result.rowcount），如果删除了 1 行说明成功，0 行说明那天本来就没数据
    return result.rowcount

# --- 用户系统新增函数 ---

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    """
    注意：这里的参数名必须叫 'user'，或者在 main.py 调用时保持一致。
    """
    # 1. 密码加密
    hashed_pwd = security.get_password_hash(user.password)
    
    # 2. 创建模型对象
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_pwd
    )
    
    # 3. 存入数据库
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
