import os

POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "123")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "prod_mainapi")
REDIS_HOST = os.getenv("REDIS_HOST", 'localhost')
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

IMAGES_MAXSIZE = int(os.getenv("IMAGES_MAXSIZE", "5000000"))
IMAGES_FILETYPES = os.getenv("IMAGES_FILETYPES", "png,jpg,jpeg,tiff,gif,webp,bmp").split(",")

MAINAPI_HOST = os.getenv("MAINAPI_HOST", "REDACTED")
UPLOAD_DIR_DOCS = os.getenv("UPLOAD_DIR_DOCS", "../data/uploads/docs")
UPLOAD_DIR_AVATAR = os.getenv("UPLOAD_DIR_AVATARS", "../data/uploads/avatars")
UPLOAD_DIR_FLOORS = os.getenv("UPLOAD_DIR_FLOORS", "../data/uploads/floors")
UPLOAD_DIR_BUILDINGS = os.getenv("UPLOAD_DIR_BUILDINGS", "../data/uploads/buildings")
SECRET_KEY = "ZБАНКПОБЕДА"
ALGORITHM = "HS256"

ADMIN_ROLES = ["ADMIN", "SUPER_ADMIN"]

UPLOAD_DIR_IMGS = os.getenv("UPLOAD_DIR_IMGS", "./data/uploads/imgs")