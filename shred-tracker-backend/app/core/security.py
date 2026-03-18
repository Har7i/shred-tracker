from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# 1. 配置加密算法
# scheme="bcrypt" 是目前行业标准的推荐做法
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__ident="2b"  # 强制使用 2b 标识符，这是最现代且兼容性最好的
)

# 2. JWT 配置（面试时会被问到这些参数的意义）
SECRET_KEY = "your-super-secret-key-change-it-in-production" # 签名用的私钥
ALGORITHM = "HS256" # 对称加密算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Token 有效期 30 分钟

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码是否与数据库中的哈希值匹配"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """将明文密码转换成 bcrypt 哈希值"""
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """生成 JWT Token"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # sub (Subject) 通常存放用户 ID 或用户名
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt