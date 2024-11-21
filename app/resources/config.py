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
TEXT_REPLACEMENTS: dict[str, str] = {
	'&': 'y',
	'%': "por ciento",
	'@': "arroba",
	'°': "grados",
	'€': "euros",
	'¢': "centavo"
}

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
    "museos", "monumentos", "cultura", "arquitectura", "parques", "cerca",
    "zonas arqueologicas", "turismo", "sitios turisticos", "atracciones", "experiencias",
    "historia de mexico", "centros culturales", "museo", "catedral", "edificio", "mural",
    "centro religioso", "plazas", "hola", "buenos dias", "buenas tardes", "buenas noches",
    "que tal", "como estas", "que onda", "hey", "tripbot",
    "esculturas", "centros historicos", "recintos", "exposiciones", "lugares",
    "rutas turisticas", "miradores", "jardines", "paseos", "iglesias", "recomiendame",
    "templos", "museo nacional", "zoologico", "parque natural", "auditorios", "calles",
    "sitios", "hacer en la ciudad", "categorias", "nombre", "clasificaciones", "municipio", "municipios", "calle",
    "codigo postal", "sitio web", "historia", "precios", "precio", "servicios", "permanente", "permanentes",
    "exhibiciones permanentes", "temporal", "temporales", "exhibiciones temporales", "recomendarme", "llamas", "nombre",
    "gracias", "de nada", "por favor", "adios", "chao", "nos vemos", "hasta luego", "que puedes hacer", "cual es tu proposito", "cuales son tus limites",
    "informacion de contacto", "ubicacion", "horarios", "costo", "boletos", "promociones", "historia del lugar", "actividades familiares"
]
DIC_UB: list[str] = [
    "cerca de mi", "cerca de mi ubicacion", "cerca de donde estoy", "cerca de aqui", "cerca de mi posicion",
    "alrededor", "en mi area", "alrededor de mi", "en mi ubicacion", "desde mi ubicacion",
    "en mi posicion actual", "alrededor de donde estoy", "alrededor de mi ubicacion",
    "en las cercanias", "cerca de mi zona", "en mi zona", "cerca de este lugar", "cerca de este sitio",
    "alrededor de este sitio", "en los alrededores", "cerca de mi direccion", "en esta area", "en esta ubicacion",
    "en mi proximidad", "en mi entorno", "en esta zona", "cerca de mi lugar actual", "cerca de donde me encuentro",
    "en el area de mi ubicacion", "cerca del punto donde estoy", "en mi vecindad", "por aqui",
    "en los alrededores de aqui", "en los alrededores de mi posicion", "en esta proximidad", "en las inmediaciones",
    "en mi posicion geografica", "donde me encuentro ahora", "en mi ubicacion actual", "cerca de mi lugar",
    "cerca de la ubicacion actual", "en mi posicion geolocalizada", "en las cercanias de aqui",
    "en el area alrededor de mi", "donde estoy ahora", "cerca del lugar donde estoy", "por mi area",
    "en este lugar", "por mi ubicacion", "en el sitio donde estoy", "en este mismo lugar", "por los alrededores",
    "en esta area geografica", "cerca de mi posicion exacta", "en el entorno donde estoy", "en mi lugar actual",
    "alrededor de este punto", "donde me encuentro en este momento", "en esta zona especifica",
    "cerca de aqui mismo", "cerca de esta ubicacion exacta", "en las proximidades de aqui", "alrededor de donde me ubico",
    "en el area cercana a mi", "en los alrededores de mi sitio", "alrededor de esta area",
    "cerca del lugar donde me encuentro", "en mi ubicacion de ahora", "alrededor de mi punto actual",
    "en el lugar donde me ubico", "cerca de este punto exacto", "en las cercanias donde estoy",
    "alrededor de esta posicion", "dentro de mi radio", "en la vecindad de aqui", "en los alrededores inmediatos",
    "por donde estoy ahora", "cerca de este lugar preciso", "en las cercanias de esta posicion",
    "cerca del sitio donde estoy", "en mi ubicacion especifica", "por los alrededores donde me ubico",
    "en este punto exacto", "en la zona donde me encuentro", "en la proximidad donde estoy", "por la ubicacion actual",
    "en el sitio exacto donde estoy"
]
