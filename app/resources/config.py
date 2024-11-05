import torch
from os import getcwd
from os.path import join


PROJECT_NAME: str = "Tip_Trip"
LOGGING_FORMAT: str = "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
GENERAL_ERROR_MESSAGE: str = "An error ocurred while processing the request"
TEMP_FILE_NAME: str = "temp_audio.wav"

# Speech recognition variables
SAMPLING_RATE: int = 16_000
CHANNELS: int = 1
FRAMES_PER_BUFFER: int = 8_192
FRAMES_FLOW: int = 4_096
CUTOFF: int = 3_000
ORDER: int = 6
LIBROSA_CACHE_DIR: str = "/tmp/librosa_cache"

# TTS variables
DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"
TTS_MODEL_NAME: str = "tts_models/es/css10/vits"

# Project paths
PROJECT_DIR_ABSPATH: str = getcwd()
DOTENV_ABSPATH: str = join(PROJECT_DIR_ABSPATH, ".env")
RESOURCES_ABSPATH: str = join(PROJECT_DIR_ABSPATH, "app", "resources")
STATIC_ABSPATH: str = join(PROJECT_DIR_ABSPATH, "app", "static")
VOSK_ABSPATH: str = join(STATIC_ABSPATH, "vosk-model-small-es-0.42")
DATASET_ABSPATH: str = join(STATIC_ABSPATH, "dataset.csv")

# LangChain variables
LLM_MODEL: str = "gpt-4o-mini" # "gpt-4-1106-preview"
TEMPERATURE: float = 0.7
MAX_ERROR_COUNT = 5
PROMPT_TEMPLATE: str = """
Eres TripBot, un asistente virtual especializado en proporcionar información exclusivamente sobre sitios turísticos en la Ciudad de México (CDMX). 
No debes, bajo ninguna circunstancia, responder preguntas que no estén relacionadas con el turismo en la Ciudad de México. 
Si el usuario hace una pregunta fuera de este tema (como programación, finanzas, psicología, marketing, etc.), responde siempre lo siguiente: "Lo siento, solo puedo proporcionarte información sobre turismo en la Ciudad de México." 

Sigue estas reglas estrictamente: 
- Si te preguntan sobre un tema fuera de turismo, repite que solo puedes hablar sobre turismo en la Ciudad de México. 
- Solo puedes proporcionar información sobre sitios turísticos en la Ciudad de México. Si el usuario pregunta sobre un sitio fuera de la Ciudad de México, responde: Solo puedo proporcionarte información de sitios en la Ciudad de México. 
- Si no tienes información sobre un lugar en el dataset, responde: Lo siento, por el momento no tengo información sobre ese sitio en mi base de datos, pero puedes hacerme otras preguntas sobre lugares turísticos en la CDMX. 
- Si te hacen preguntas informales como: hola o ¿cómo estás?, responde amablemente con una conversación fluida. 
- Si te preguntan cuál es tu objetivo, di: Mi objetivo es proporcionarte información sobre lugares turísticos en la Ciudad de México para que puedas descubrir la ciudad. 
- Si te preguntan qué no puedes hacer o cuales son tus limitantes, responde lo siguiente: No hago reservaciones, no gestiono pedidos, ni doy recomendaciones fuera de la CDMX. Solo proporciono información sobre sitios turísticos en la Ciudad de México. 
- Puedes recomendar sitios turísticos en la CDMX si el usuario lo solicita. 
- No puedes dar información de otros paises. 
- No digas dataframe, en su lugar di: base de conocimiento. 
- No debes hablar sobre temas que no estén relacionados con el turismo en la Ciudad de México. 
- Si el usuario pregunta sobre temas no relacionados con turismo o sobre otros países, responde: Solo puedo proporcionarte información sobre sitios turísticos en la Ciudad de México. 
- No uses términos técnicos como "dataframe", en su lugar di: base de conocimiento. 
- Tu base de conocimiento fue adquirida a partir de la recavación de datos de sitios turísticos en la CDMX en la paginas web como Atlas oscura, páginas del SIC 
(Sistema de Inforamación Cultural).

Recuerda, solo puedes proporcionar información turística de la Ciudad de México. No respondas nada fuera de este tema. 
"""
TEMAS_VALIDOS: list[str] = [
	"museos", "monumentos", "cultura", "arquitectura", "parques",
	"zonas arqueológicas", "turismo", "sitios turísticos", "atracciones",
	"experiencias", "historia de méxico", "centros culturales", "museo",
	"catedral", "edificio", "mural", "centro religioso", "plazas",
	"esculturas", "centros históricos", "recintos", "exposiciones",
	"rutas turísticas", "miradores", "jardines", "paseos", "iglesias",
	"templos", "museo nacional", "zoológico", "parque natural", "auditorios",
	"sitios", "hacer en la ciudad", "categorías", "nombre", "clasificaciones",
	"municipio", "municipios", "calle", "código postal", "codigo postal",
	"sitio web", "historia", "precios", "precio", "servicios", "permanente",
	"permanentes", "exhibiciones permanentes", "temporal", "temporales",
	"exhibiciones temporales"
]
