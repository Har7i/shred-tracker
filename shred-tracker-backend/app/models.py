from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime
from app.database import Base
from typing import Optional, List

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    # 【关系映射】：一个用户拥有多个 logs
    # back_populates 确保了两边模型的同步
    logs: Mapped[List["DailyLog"]] = relationship(back_populates="owner", cascade="all, delete-orphan")

class DailyLog(Base):
    # 1.数据库里的实际表名
    __tablename__ = "daily_logs"

    # 2. 定义字段 (使用 SQLALchemy 的 Mapped 语法)
    # id 是主键 会递增
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 注意：这里去掉了 date 的 unique=True
    # 因为现在是多用户系统，用户A和用户B都可以有 2026-03-17 的记录
    # 我们之后会在“联合唯一索引”或业务逻辑里处理单用户当天的唯一性
    # 日期字段, unique=True 表示一天只能有一条记录，index=True 方便快速查询
    date: Mapped[datetime.date] = mapped_column(index=True)

    # 体重，使用 float，允许为空
    weight: Mapped[float] = mapped_column(nullable=True)

    # 每天摄入的蛋白质、碳水、脂肪以及总热量，默认值为0
    calories: Mapped[int] = mapped_column(default=0)
    protein: Mapped[int] = mapped_column(default=0)
    fat: Mapped[int] = mapped_column(default=0)
    carb: Mapped[int] = mapped_column(default=0)

    # 备注
    notes: Mapped[str] = mapped_column(nullable=True)

    # --- 新增外键关联 ---
    # 存储所属用户的 ID
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # 【关系映射】：每一条记录都属于一个 owner
    owner: Mapped["User"] = relationship(back_populates="logs")

