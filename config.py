import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, 'recipes.db')
    SQLITE_URI = f'sqlite:///{DATABASE_PATH}'
    DEBUG = True
    
    # Redis configuration
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    # Security settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    CSRF_ENABLED = True
    CSRF_SECRET_KEY = os.getenv('CSRF_SECRET_KEY', 'csrf-dev')
    
    # Rate limiting
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_STORAGE_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"