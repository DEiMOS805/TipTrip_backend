import openai
import difflib
import unicodedata
import pandas as pd
from os import getenv
from typing import Optional
from pandas import DataFrame
from dotenv import load_dotenv
from geopy.distance import geodesic
from logging import getLogger, Logger
from langchain_openai import ChatOpenAI
from werkzeug.exceptions import NotFound
from langchain.memory import ConversationBufferMemory
from langchain_experimental.agents.agent_toolkits import create_csv_agent

from app.resources.config import *
from app.resources.models import User
from app.resources.config import CATEGORIAS, DEFAULT_KM_RATIUS


logger: Logger = getLogger(f"{PROJECT_NAME}.llm")
load_dotenv(DOTENV_ABSPATH)

df: DataFrame = pd.read_csv(DATASET_ABSPATH)
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')


class AgenteConversacional:
	def __init__(self) -> None:
		self.llm = ChatOpenAI(temperature=TEMPERATURE, model=LLM_MODEL, api_key=getenv("OPENAI_API_KEY"))
		self.memory = ConversationBufferMemory(memory_key="chat_history")
		self.df: DataFrame = df
		self.prompt_template: str = PROMPT_TEMPLATE
		self.error_count: int = 0
		self.lugares_mostrados = set()  # Registro de lugares ya mostrados

		# Configuración del agente
		self.agent_executor = create_csv_agent(
			llm=self.llm,
			path=DATASET_ABSPATH,
			verbose=False,
			agent_type="openai-functions",
			allow_dangerous_code=True,
			prompt_template=self.prompt_template,
			memory=self.memory,
			handle_parsing_errors=True
		)

	def normalizar_texto(self, texto) -> str:
		texto = texto.lower()
		texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
		return texto

	def manejar_errores(self, error) -> str:
		logger.error(f"Error encontrado: {error}")
		errores: dict = {
			openai.error.APIError: "Lo siento, hubo un problema de conexión con el servidor. Por favor, intenta de nuevo en unos momentos.",
			openai.error.InvalidRequestError: "Lo siento, no entendí completamente tu pregunta. ¿Podrías formularla de otra manera?",
			pd.errors.EmptyDataError: "Lo siento, parece que hubo un problema al procesar los datos. Intenta preguntar nuevamente."
		}
		self.error_count += 1
		return errores.get(type(error), "Lo siento, ocurrió un error inesperado. Por favor, intenta de nuevo.")

	def obtener_ubicacion_usuario(self, user_id: int) -> Optional[tuple[float, float]]:
		"""Obtiene la ubicación del usuario desde el backend."""
		logger.debug("Checking if user exists...")
		try:
			user: User = User.query.get_or_404(user_id)

		except NotFound:
			logger.error("User not found. Aborting request...")
			return None, None

		except Exception as e:
			logger.error(f"Error getting user data: {e}. Aborting request...")
			return None, None

		return user.latitude, user.longitude

	def calcular_distancia_geopy(self, lat1, lon1, lat2, lon2):
		try:
			origen: tuple = (lat1, lon1)
			destino: tuple = (lat2, lon2)
			distancia: float = geodesic(origen, destino).kilometers
			return distancia

		except ValueError:
			logger.error("Error en el cálculo de distancia: coordenadas inválidas.")
			return float('inf')

	# ---------------------------- INTENCIONES --------------------------------------
	def analizar_intencion_llm(self, mensaje: str) -> str:
		logger.debug("Analizando la intención del usuario...")
		prompt_intencion: str = f"""
		Analiza el siguiente mensaje y responde con una palabra clave que describa su intención, basándote en las siguientes categorías:

		- Responde: 'saludo', Si el mensaje es un saludo o muestra intención de iniciar una conversación.
			Ejemplos de mensajes: hola, buenos días, ¿cómo estás?, ¿qué tal?, etc.

		- Responde: 'despedida', Si el mensaje es una despedida o indica que la conversación está terminando.
			Ejemplos de mensajes: adiós, hasta luego, gracias por tu ayuda, nos vemos, etc.

		- Responde: 'ubicacion', Si el mensaje trata que quiere saber de sitios cercanos al usuario y no menciona la categoría, nombre de algún sitio.
			Ejemplos de preguntas: Qué lugares hay cerca de mí, Qué me queda cerca, Qué es lo más cercano a mí, Qué lugares hay cerca de mi ubicación actual.

		- Responde: 'ubicacion_cercana', Si el mensaje trata que quiere saber de sitios cercanos al usuario y menciona que quiere saber con respecto a alguna categoría en especial.
			Ejemplos de preguntas: Recomiéndame zonas arqueológicas cerca de mí, ¿Cuál es la iglesia más cercana a mi ubicación?, ¿Qué planetario me queda cerca?, ¿Qué museos me quedan cerca?, ¿Qué centros culturales están por mi zona?

		- Responde: 'lugares_referencia', Si el mensaje trata que quiere saber de sitios cercanos a otros sitios y menciona que quiere saber.
			Ejemplos de preguntas: ¿Qué lugares hay cerca del Zócalo?, ¿Qué lugares hay cerca del Ángel?

		- Responde: 'informacion_general', Si el mensaje trata sobre información turística general como museos, estatuas, esculturas, murales, arquitectura, centros culturales, zonas arqueológicas, jardines, iglesias o centros religiosos, nombres de esos sitios, agradecimientos por la información.
			Ejemplos de preguntas: ¿Qué es Acroyoga?, ¿Qué me puedes decir sobre Acroyoga, Pan y Circo?, ¿Hay visitas nocturnas en el Castillo de Chapultepec?, ¿Qué me recomiendas de esculturas?, ¿Cuál es el museo mejor calificado?, ¿Cuántos museos hay en la Ciudad?, etc.

		- Responde: 'irrelevante', Si el mensaje no tiene que ver con los temas anteriores.
			Ejemplos de preguntas: ¿Qué es Python?, ¿Qué es la ESCOM?, ¿Qué son las matemáticas?, ¿Qué es la contabilidad?, etc.

		Mensaje: "{mensaje}"
		"""
		response = self.llm.invoke(prompt_intencion)
		logger.debug(f"Intención detectada por LLM: {response.content}")  # Depuración

		return response.content.strip().lower()

	# ---------------------------- FUNCIONES AUXILIARES --------------------------------------
	def obtener_lista_lugares(self):
		""" Obtiene la lista de nombres de lugares únicos del dataset. """
		return self.df['name'].dropna().unique().tolist()

	def determinar_categoria_llm(self, mensaje):
		""" Utiliza un LLM para determinar la categoría del mensaje del usuario. """
		prompt: str = f"""
		Dada la siguiente lista de categorías o clasificaciones:
		{', '.join(CATEGORIAS)}

		Determina a cuál de estas categorías pertenece el siguiente mensaje del usuario. Responde solo con el nombre exacto de la categoría de la lista, sin agregar nada más.

		Mensaje del usuario: "{mensaje}"
		"""
		response = self.llm.invoke(prompt)
		categoria = response.content.strip()
		# Validar que la categoría esté en la lista conocida
		if categoria in CATEGORIAS:
			return categoria
		else:
			return None

	def determinar_lugar_referencia_difflib(self, mensaje):
		""" Utiliza difflib para determinar a qué lugar del dataset se refiere el mensaje del usuario. """
		mensaje_normalizado = self.normalizar_texto(mensaje)
		nombres_lugares = self.df['name'].dropna().unique().tolist()
		nombres_normalizados = [self.normalizar_texto(nombre) for nombre in nombres_lugares]

		# Extraer palabras significativas del mensaje
		palabras_mensaje = set(mensaje_normalizado.split())
		posibles_lugares = []
		for nombre, nombre_norm in zip(nombres_lugares, nombres_normalizados):
			palabras_nombre = set(nombre_norm.split())
			if palabras_mensaje & palabras_nombre:
				posibles_lugares.append(nombre)

		if posibles_lugares:
			# Buscar la mejor coincidencia
			mejor_coincidencia = difflib.get_close_matches(mensaje_normalizado, [self.normalizar_texto(lugar) for lugar in posibles_lugares], n=1, cutoff=0.5)
			if mejor_coincidencia:
				indice = [self.normalizar_texto(lugar) for lugar in posibles_lugares].index(mejor_coincidencia[0])
				return posibles_lugares[indice]

		return None

	def obtener_coordenadas_lugar(self, nombre_lugar):
		""" Obtiene las coordenadas (latitud y longitud) de un lugar dado su nombre. """
		lugar = self.df[self.df['name'].str.lower() == nombre_lugar.lower()]
		if not lugar.empty:
			lat = lugar.iloc[0]['latitude']
			lon = lugar.iloc[0]['longitude']
			return lat, lon
		else:
			return None, None

	# ---------------------------- UBICACION --------------------------------------
	def recomendar_sitios_cercanos(self, lat, lon, radio_km) -> str:
		sitios_cercanos = self.df.dropna(subset=['latitude', 'longitude']).copy()
		sitios_cercanos['distancia'] = sitios_cercanos.apply(
			lambda row: self.calcular_distancia_geopy(lat, lon, row['latitude'], row['longitude']),
			axis=1
		)

		sitios_cercanos = sitios_cercanos[sitios_cercanos['distancia'] <= radio_km].sort_values(by='distancia')

		if sitios_cercanos.empty:
			return "Lo siento, no encontré sitios turísticos en el radio especificado."

		recomendacion = "Te recomiendo los siguientes lugares cercanos a tu ubicación:\n"
		for _, row in sitios_cercanos.iterrows():
			recomendacion += f"- {row['name']} a {row['distancia']:.2f} km\n"

		return recomendacion

	# ---------------------------- LUGARES POR CATEGORIA -----------------------------
	def recomendar_sitios_cercanos_categoria(self, lat, lon, radio_km, categoria) -> str:
		""" Recomienda sitios cercanos a una ubicación específica y de una categoría dada. """
		sitios_cercanos: DataFrame = self.df.dropna(subset=['latitude', 'longitude']).copy()
		sitios_cercanos = sitios_cercanos[sitios_cercanos['classification'].str.contains(categoria, case=False, na=False)]
		sitios_cercanos['distancia'] = sitios_cercanos.apply(
			lambda row: self.calcular_distancia_geopy(lat, lon, row['latitude'], row['longitude']),
			axis=1
		)
		sitios_cercanos = sitios_cercanos[sitios_cercanos['distancia'] <= radio_km].sort_values(by='distancia')

		if sitios_cercanos.empty:
			return f"Lo siento, no encontré sitios de la categoría '{categoria}' en el radio especificado."

		recomendacion: str = f"Te recomiendo los siguientes lugares de la categoría '{categoria}' cercanos a tu ubicación:\n"

		for _, row in sitios_cercanos.iterrows():
			recomendacion += f"- {row['name']} a {row['distancia']:.2f} km \n{row['foto_1']}\n{row['punctuation']}\n {row['description']} \n\n"

		return recomendacion

	def manejar_ubicacion_cercana(self, mensaje, user_id) -> str:
		""" Maneja la intención 'ubicacion_cercana'. """
		# Usar el LLM para determinar la categoría
		categoria = self.determinar_categoria_llm(mensaje)
		if categoria:
			try:
				lat, lon = self.obtener_ubicacion_usuario(user_id=user_id)
				if lat is not None and lon is not None:
					return self.recomendar_sitios_cercanos_categoria(lat, lon, DEFAULT_KM_RATIUS, categoria)

				else:
					return "No se pudo obtener la ubicación del usuario."

			except ValueError:
				return "Por favor, ingresa coordenadas válidas y un número para el radio de búsqueda."

		else:
			return "Lo siento, no pude determinar la categoría de sitio que te interesa. Por favor, especifica una categoría como 'Museo', 'Monumento', 'Centro cultural', etc."

	#----------------------------- LUGARES POR REFERENCIA --------------------------------
	def manejar_lugares_referencia(self, mensaje):
		""" Maneja la intención 'lugares_referencia'. """
		lugar_referencia = self.determinar_lugar_referencia_difflib(mensaje)
		if lugar_referencia:
			try:
				lat_ref, lon_ref = self.obtener_coordenadas_lugar(lugar_referencia)
				if lat_ref is not None and lon_ref is not None:
					return self.recomendar_sitios_cercanos(lat_ref, lon_ref, DEFAULT_KM_RATIUS)

				else:
					return f"No pude encontrar la ubicación de {lugar_referencia}."

			except ValueError:
				return "Tengo dificultades por interpretar el lugar de referencia, trata de ser más específico con su nombre."

		else:
			return "Por favor, especifica un lugar de referencia."

	# --------------------------------- AGENTE --------------------------------------
	def consultar_agente(self, pregunta: str, user_id: int, radio_km: int = 7) -> str:
		if self.error_count >= MAX_ERROR_COUNT:
			return "Lo siento, por el momento no puedo ayudarte. Por favor, intenta de nuevo más tarde."

		pregunta_corregida: str = pregunta
		intencion: str = self.analizar_intencion_llm(pregunta_corregida)

		if intencion == 'saludo':
			return "¡Hola! ¿En qué puedo ayudarte hoy con información turística sobre la Ciudad de México?"

		elif intencion == 'despedida':
			return "Gracias por usar TripBot. ¡Espero que tengas un excelente día! 😊"

		elif intencion == 'ubicacion':
			lat, lon = self.obtener_ubicacion_usuario(user_id=user_id)
			if lat is not None and lon is not None:
				try:
					if 1 <= radio_km <= 15:
						return self.recomendar_sitios_cercanos(lat, lon, radio_km)

					else:
						return "Por favor, ingresa un radio de búsqueda entre 1 y 15 kilómetros."

				except ValueError:
					return "Por favor, ingresa un valor numérico válido para el radio de búsqueda."

			else:
				return "No se pudo obtener la ubicación del usuario."

		elif intencion == 'ubicacion_cercana':
			return self.manejar_ubicacion_cercana(pregunta_corregida, user_id)

		elif intencion == 'lugares_referencia':
			return self.manejar_lugares_referencia(pregunta_corregida)

		elif intencion == 'informacion_general':
			try:
				# Filtrar resultados que contengan palabras clave de la pregunta
				palabras_clave: list[str] = pregunta.lower().split()
				resultados: DataFrame = self.df[self.df['description'].str.contains('|'.join(palabras_clave), case=False, na=False)]

				# Si no hay datos, responde adecuadamente
				if resultados.empty:
					return "Lo siento, no tengo información específica sobre ese tema, pero puedo recomendarte lugares turísticos en la Ciudad de México."

				prompt_template_informacion: str = f"""
				Eres un guía turístico experto y apasionado, especializado en brindar información sobre destinos turísticos de la Ciudad de México. Tu tono debe ser amable, entusiasta y profesional.
				Tu objetivo es ofrecer información, datos precisos, datos interesantes y brindar una buena experiencia.
				Usa un lenguaje inclusivo y acogedor, manteniendo siempre una actitud servicial y paciente. Si la consulta está fuera de tu ámbito, guía al usuario amablemente hacia los temas que puedes abordar.

				Pregunta del usuario: "{pregunta}"
				Responde al usuario de manera informativa y útil.
				"""
				logger.debug("Construyendo respuesta...")

				# Generar la respuesta usando el LLM
				response = self.llm.invoke(prompt_template_informacion)
				self.error_count = 0
				return response.content.strip()
			except Exception as e:
				return self.manejar_errores(e)

		elif intencion == 'irrelevante':
			return "Lo siento, no estoy seguro de haber entendido tu pregunta. Recuerda que estoy aquí para proporcionarte información sobre turismo en la Ciudad de México. ¡No dudes en intentarlo de nuevo!"

		else:
			return "Lo siento, no pude entender tu intención. Por favor, intenta formular tu pregunta de otra manera."
