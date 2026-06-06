import os

class Settings:
    PROJECT_NAME: str = "ShopLens AI"
    ACTIVE_MODE: str = os.getenv("ACTIVE_MODE", "local")  # "local" or "production"
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./shoplens.db")
    
    # Redis Cache Settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    
    # S3 Storage Settings
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "mock-key")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "mock-secret")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "shoplens-bucket")
    
    # Path settings
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    LOCAL_STORAGE_DIR: str = os.getenv("LOCAL_STORAGE_DIR", os.path.join(BASE_DIR, "storage"))
    
    # Kafka Message Queue Settings
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    # MLflow tracking
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "shoplens-super-secret-key-123456")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 1 day

settings = Settings()

# Ensure local storage directories exist
os.makedirs(settings.LOCAL_STORAGE_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.LOCAL_STORAGE_DIR, "images"), exist_ok=True)
os.makedirs(os.path.join(settings.LOCAL_STORAGE_DIR, "models"), exist_ok=True)
os.makedirs(os.path.join(settings.LOCAL_STORAGE_DIR, "datasets"), exist_ok=True)
os.makedirs(os.path.join(settings.LOCAL_STORAGE_DIR, "reports"), exist_ok=True)
