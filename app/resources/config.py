from os import getcwd
from os.path import join


PROJECT_NAME: str = "Tip_Trip"
LOGGING_FORMAT: str = "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
GENERAL_ERROR_MESSAGE: str = "Ocurrió un problema mientras se procesaba la petición"

# Speech recognition variables
SAMPLING_RATE: int = 16_000
CHANNELS: int = 1
FRAMES_PER_BUFFER: int = 8_192
FRAMES_FLOW: int = 4_096
CUTOFF: int = 3_000
ORDER: int = 6
TEMP_FILE_NAME: str = "temp_audio.wav"
VOSK_MODEL_NAME = "vosk-model-es-0.42"

# Project paths
PROJECT_DIR_ABSPATH: str = getcwd()
DOTENV_ABSPATH: str = join(PROJECT_DIR_ABSPATH, ".env")
TEMP_ABSPATH: str = join(PROJECT_DIR_ABSPATH, "app", "temp")
VOSK_ABSPATH: str = join(
	PROJECT_DIR_ABSPATH,
	"app",
	"resources",
	"models",
	VOSK_MODEL_NAME
)
