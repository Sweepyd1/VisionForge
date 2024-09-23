from environs import Env

env = Env()
env.read_env()

JWT_TOKEN_SECRET = env.str("JWT_TOKEN_SECRET")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = env.int("JWT_ACCESS_TOKEN_EXP", default=30)
JWT_REFRESH_TOKEN_EXPIRE_MINUTES = env.int("JWT_REFRESH_TOKEN_EXP", default=60)
JWT_ALGORITHM = env.str("JWT_ALGORITHM", default="HS256")

API_HOST = env.str("API_HOST")
API_PORT = env.int("API_PORT")

db_host = env.str("DB_HOST")
db_port = env.int("DB_PORT")
db_username = env.str("DB_USERNAME")
db_password = env.str("DB_PASSWORD")
db_name = env.str("DB_NAME")


