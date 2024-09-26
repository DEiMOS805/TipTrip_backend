import torch
from os import getcwd
from os.path import join


PROJECT_NAME: str = "Tip_Trip"
LOGGING_FORMAT: str = "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
GENERAL_ERROR_MESSAGE: str = "Ocurrió un problema mientras se procesaba la petición"
TEMP_FILE_NAME: str = "temp_audio.wav"

# Speech recognition variables
SAMPLING_RATE: int = 16_000
CHANNELS: int = 1
FRAMES_PER_BUFFER: int = 8_192
FRAMES_FLOW: int = 4_096
CUTOFF: int = 3_000
ORDER: int = 6
VOSK_MODEL_NAME = "vosk-model-small-es-0.42"

# TTS variables
DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"
TTS_MODEL_NAME: str = "tts_models/es/css10/vits"

# Project paths
PROJECT_DIR_ABSPATH: str = getcwd()
DOTENV_ABSPATH: str = join(PROJECT_DIR_ABSPATH, ".env")
TEMP_ABSPATH: str = join(PROJECT_DIR_ABSPATH, "temp")
AI_MODELS_ABSPATH: str = join(PROJECT_DIR_ABSPATH, "app", "resources", "models")
VOSK_ABSPATH: str = join(AI_MODELS_ABSPATH, VOSK_MODEL_NAME)
