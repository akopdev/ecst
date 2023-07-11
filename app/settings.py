from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_DSL: str = "mongodb://demo:demo@storage:27017/"
    DATABASE_NAME: str = "economic_calendar"


settings = Settings()
