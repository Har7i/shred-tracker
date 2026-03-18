from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional

# 1. 共享基础字段（Base）
# 定义所有dailylog都会有的共同属性
class DailyLogBase(BaseModel):
    date: date
    weight: float = Field(..., gt=0, description="体重必须大于0") #gt=0 greater than 0
    calories: Optional[int] = Field(default=0, ge=0) # ge=0 greater equal than 0
    protein: Optional[int] = Field(default=0, ge=0)
    fat: Optional[int] = Field(default=0, ge=0)
    carb: Optional[int] = Field(default=0, ge=0)
    notes: Optional[str] = None

# 2. 创建时使用的Schema （Create）
# 用户在新增记录时发送的数据格式
class DailyLogCreate(DailyLogBase):
    pass # 目前和 Base 一致，如果以后有“创建时必填，平时可选”的字段再在这里改

# 3. 更新时使用的Scheme （Update）
# 所有字段都是Optional（可选），因为用户可能只想修改体重，不想改热量
class DailyLogUpdate(BaseModel):
    weight: Optional[float] = Field(None, gt=0)
    calories: Optional[int] = Field(None, ge=0) 
    protein: Optional[int] = Field(None, ge=0) 
    fat: Optional[int] = Field(None, ge=0) 
    carb: Optional[int] = Field(None, ge=0) 
    notes: Optional[str] = None

# 4. 返回给前端展示用的Schema (Read/Response)
# 包含数据库生成的ID
class DailyLogResponse(DailyLogBase):
    id: int

    # Pydantic V2 的配置：允许从SQLALchemy模型对象直接转换
    model_config = ConfigDict(from_attributes=True)

# 用户基础信息
class UserBase(BaseModel):
    username: str

# 注册时用的模型
class UserCreate(UserBase):
    password: str

# 返回给前端的用户信息（不带密码！）
class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

# Token 结构模型
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None