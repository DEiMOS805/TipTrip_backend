import openai
import unicodedata
import pandas as pd
from os import getenv
from typing import Optional
from pandas import DataFrame
from dotenv import load_dotenv
from logging import getLogger, Logger
from langchain_openai import ChatOpenAI
from werkzeug.exceptions import NotFound
from langchain.memory import ConversationBufferMemory
from langchain_experimental.agents.agent_toolkits import create_csv_agent

from app.resources.config import *
from app.resources.models import User
from app.resources.functions import get_place_distance


logger: Logger = getLogger(f"{PROJECT_NAME}.llm")
load_dotenv(DOTENV_ABSPATH)

df: DataFrame = pd.read_csv(DATASET_ABSPATH)
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

unicos_df: dict = {
	"nombres_sitios": [
		word for name in df['name'].dropna().unique().tolist()
		for word in name.lower().split()
	],
	"classificaciones": [
		word for classification in df['classification'].dropna().unique().tolist()
		for word in classification.lower().split()
	],
	"municipios": [
		word for municipio in df['municipality'].dropna().unique().tolist()
		for word in municipio.lower().split()
	],
	"calles": [
		word for calle in df['street_number'].dropna().unique().tolist()
		for word in calle.lower().split()
	],
	"colonias": [
		word for colonia in df['colony'].dropna().unique().tolist()
		for word in colonia.lower().split()
	],
	"codigos_postales": [
		cp.lower() for cp in df['cp'].dropna().astype(str).unique().tolist()
	],
	"precios": [
		word for precio in df['prices'].dropna().unique().tolist()
		for word in precio.lower().split()
	],
	"servicios": [
		word for servicio in df['services'].dropna().unique().tolist()
		for word in servicio.lower().split()
	],
	"actividades": [
		word for actividad in df['activities'].dropna().unique().tolist()
		for word in actividad.lower().split()
	],
	"exhibiciones_temporales": [
		word for exhibicion in df['temporal_exhibitions'].dropna().unique().tolist()
		for word in exhibicion.lower().split()
	],
	"exhibiciones_permanentes": [
		word for exhibicion in df['permanent_exhibitions'].dropna().unique().tolist()
		for word in exhibicion.lower().split()
	]
}


def eliminar_acentos(texto: str) -> str:
	return "".join(
		c for c in unicodedata.normalize('NFD', texto)
		if unicodedata.category(c) != 'Mn'
	)


class AgenteConversacional:
	def __init__(self) -> None:
		self.llm = ChatOpenAI(temperature=TEMPERATURE, model=LLM_MODEL, api_key=getenv("OPENAI_API_KEY"))
		self.memory = ConversationBufferMemory(memory_key="chat_history")
		self.df: DataFrame = df
		self.prompt_template: str = PROMPT_TEMPLATE
		self.error_count: int = 0

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

	def es_pregunta_valida(self, pregunta: str) -> bool:
		pregunta_normalizada = eliminar_acentos(pregunta.lower())
		return any(tema in pregunta_normalizada  for tema in TEMAS_VALIDOS) or \
				any(valor.lower() in pregunta_normalizada .lower() for valores in unicos_df.values() for valor in valores)

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

	def recomendar_sitios_cercanos(self, lat: float, lon: float, radio_km: int) -> str | list:
		sitios_cercanos: DataFrame = self.df.dropna(subset=['latitude', 'longitude']).copy()
		sitios_cercanos['distancia'] = sitios_cercanos.apply(
			lambda row: get_place_distance((lat, lon), (row['latitude'], row['longitude'])),
			axis=1
		)
		sitios_cercanos = sitios_cercanos[sitios_cercanos['distancia'] <= radio_km].sort_values(by='distancia')

		if sitios_cercanos.empty:
			return "Lo siento, no encontré sitios turísticos en el radio especificado."

		recomendacion = "Te recomiendo los siguientes lugares cercanos a tu ubicación:\n"
		for _, row in sitios_cercanos.iterrows():
			recomendacion += f"- {row['name']} a {row['distancia']:.2f} km\n"
		return recomendacion

	def consultar_agente(self, pregunta: str, user_id: int, radio_km: int = 7) -> str:
		if self.error_count >= MAX_ERROR_COUNT:
			return "Lo siento, por el momento no puedo ayudarte. Por favor, intenta de nuevo más tarde."

		pregunta_normalizada : str = eliminar_acentos(pregunta.lower())

		if not self.es_pregunta_valida(pregunta_normalizada ) and not any(expresion in pregunta_normalizada  for expresion in DIC_UB):
			return "Lo siento, solo puedo proporcionarte información sobre turismo en la Ciudad de México."

		#sitios cercanos
		if any(expresion in pregunta_normalizada  for expresion in DIC_UB):
			lat, lon = self.obtener_ubicacion_usuario(user_id=user_id)  # Llama al endpoint para obtener la ubicación del usuario
			if lat is not None and lon is not None:
				try:
					radio_km = 7
					if 1 <= radio_km <= 15:
						return self.recomendar_sitios_cercanos(lat, lon, radio_km)
					else:
						return "Por favor, ingresa un radio de búsqueda entre 1 y 15 kilómetros."
				except ValueError:
					return "Por favor, ingresa un valor numérico válido para el radio de búsqueda."
			else:
				return "No se pudo obtener la ubicación del usuario."

		# Consultas generales
		try:
			resultados: DataFrame = self.df[self.df['description'].str.contains("CDMX", case=False, na=False)]
			data: str = resultados.to_string(index=False)
			response = self.agent_executor.invoke(f"{pregunta}\nAquí tienes la información relevante:\n{data}")
			self.error_count = 0  # Reiniciar el contador de errores si la consulta es exitosa
			return response['output']

		except Exception as e:
			return self.manejar_errores(e)
