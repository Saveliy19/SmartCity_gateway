import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.exceptions import HTTPException as StarletteHTTPException
import os

# Создание именованного логгера
logger = logging.getLogger("my_logger")
logger.setLevel(logging.ERROR)

# Формат логирования
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Обработчик для логирования в файл
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

# Обработчик для логирования в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(formatter)

# Добавление обработчиков к логгеру
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        inf = f"Запрос: {request.method} {request.url} Headers: {request.headers} Body: {await request.body()}"
        try:
            response = await call_next(request)
        except StarletteHTTPException as exc:
            execution_time = time.time() - start_time
            logger.error(f"Ошибка: {exc.status_code} {request.method} {request.url} Время выполнения: {execution_time:.2f} сек, {inf}")
            raise
        except Exception as exc:
            execution_time = time.time() - start_time
            logger.error(f"Ошибка: 500 {request.method} {request.url} Время выполнения: {execution_time:.2f} сек, {inf}")
            raise

        if response.status_code >= 400:
            execution_time = time.time() - start_time
            logger.error(f"Ошибка: {response.status_code} {request.method} {request.url} Время выполнения: {execution_time:.2f} сек, {inf}")
        
        return response

def setup_logging():
    # Вызываем настройку логгера
    pass  # Эта функция больше не нужна, так как логгер настроен при импорте
