from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from datetime import date
from typing import List
from contextlib import asynccontextmanager
from app.database import engine, Base, get_db
from app.core import security
from app import models, schemas, crud


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 【启动时执行】
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 【关闭时执行】
    await engine.dispose()

# 创建fastapi实例
app = FastAPI(title="Shred Tracker", lifespan=lifespan)

origins = [
    "http://localhost:5173", # Vite 默认的前端地址
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义 OAuth2 方案，告诉 FastAPI Token 从哪个接口获取
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- 1. 【安保插件】获取当前登录用户 ---
async def get_current_user(
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码 Token
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = await crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# --- 2. 用户认证接口 ---

@app.post("/auth/register", response_model=schemas.UserResponse, status_code=201)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await crud.create_user(db=db, user=user)

@app.post("/auth/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = security.create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}

# --- 3. 业务接口（现在全部带锁了！） ---
# --- 1. 【增】创建打卡记录 ---
@app.post("/logs/", response_model=schemas.DailyLogResponse, status_code=status.HTTP_201_CREATED)
async def create_log_entry(
    log: schemas.DailyLogCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # 注入锁
):
    # 增加 user_id 参数进行过滤检查
    db_log = await crud.get_log_by_date(db, log_date=log.date, user_id=current_user.id)
    if db_log:
        raise HTTPException(status_code=400, detail="那天已经有记录啦，请使用更新接口。")
    # 传给 crud 时带上主人 ID
    return await crud.create_log(db=db, log=log, user_id=current_user.id)

# --- 2. 【查】获取该用户所有记录 ---
@app.get("/logs/", response_model=List[schemas.DailyLogResponse])
async def read_all_log(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return await crud.get_all_logs(db, user_id=current_user.id, skip=skip, limit=limit)

# --- 3. 【查】获取特定日期记录 ---
@app.get("/logs/{log_date}", response_model=schemas.DailyLogResponse)
async def read_log_by_date(
    log_date: date, 
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 确保只能查到自己的
    db_log = await crud.get_log_by_date(db, log_date=log_date, user_id=current_user.id)
    if not db_log:
        raise HTTPException(status_code=404, detail="找不到那天的打卡数据。")
    return db_log

# --- 4. 【改】更新记录（保留你的 try-except 守卫） ---
@app.patch("/logs/{log_date}", response_model=schemas.DailyLogResponse)
async def update_log_entry(
    log_date: date, 
    log_update: schemas.DailyLogUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        # 传参增加 user_id
        updated_log = await crud.update_log(
            db=db, log_date=log_date, log_update=log_update, user_id=current_user.id
        )
        if not updated_log:
            raise HTTPException(status_code=404, detail="未找到记录或无权修改")
        return updated_log
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# --- 5. 【删】删除记录 ---
@app.delete("/logs/{log_date}")
async def delete_log_entry(
    log_date: date, 
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 增加 user_id，防止删掉别人的
    deleted_count = await crud.delete_log(db, log_date=log_date, user_id=current_user.id)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="未找到该日期的记录或无权删除。")
    return {"status": "success", "message": f"Deleted log for {log_date}"}