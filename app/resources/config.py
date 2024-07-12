PROJECT_NAME: str = "Tip_Trip"

LOGGING_FORMAT: str = "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"

SCHEMA: str = "public"
DB_DATA: dict = {
	"user": "postgres",
	"password": "root",
	"host": "localhost",
	"port": 5432,
	"db": "tip_trip",
}

GENERAL_ERROR_MESSAGE: str = "Ocurrió un problema mientras se procesaba la petición"

API_USERNAME: str = "admin"
API_PASSWORD: str = "admin"
