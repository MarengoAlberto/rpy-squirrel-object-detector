from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MODEL_PATH: str = "runs/detect/train2/weights/last.pt" # "model/yolo26n.pt"
    DISTANCE_FUNCTION: str = "euclidean"
    DISTANCE_THRESHOLD: int = 150
    REID_HIT_COUNTER_MAX: int = 50


settings = Settings()