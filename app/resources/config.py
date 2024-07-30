import os

PROJECT_NAME: str = "Tip_Trip"

LOGGING_FORMAT: str = "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"

GENERAL_ERROR_MESSAGE: str = "Ocurrió un problema mientras se procesaba la petición"

PROJECT_DIR_ABSPATH: str = os.getcwd()
DOTENV_ABSPATH: str = os.path.join(PROJECT_DIR_ABSPATH, ".env")
