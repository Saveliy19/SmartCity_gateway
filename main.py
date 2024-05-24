from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.logger import logger, LoggingMiddleware
import time
from starlette.requests import Request

# Настройка логирования
# setup_logging()  # Убираем вызов, так как логгер настроен при импорте

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Добавление логирующего middleware
app.add_middleware(LoggingMiddleware)

# Разрешить запросы с любых источников (*)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
