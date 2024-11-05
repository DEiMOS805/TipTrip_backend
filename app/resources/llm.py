import openai
import pandas as pd
from os import getenv
from typing import Any
from pandas import DataFrame
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_experimental.agents.agent_toolkits import create_csv_agent

from app.resources.config import *


load_dotenv(DOTENV_ABSPATH)

df: DataFrame = pd.read_csv(DATASET_ABSPATH)
unicos_df: dict[str, Any] = {
	"nombres_sitios": df['name'].dropna().unique().tolist(),
	"classificaciones": df['classification'].dropna().unique().tolist(),
	"municipios": df['municipality'].dropna().unique().tolist(),
	"calles": df['street_number'].dropna().unique().tolist(),
	"colonias": df['colony'].dropna().unique().tolist(),
	"codigos_postales": df['cp'].dropna().astype(str).unique().tolist(),
	"precios": df['prices'].dropna().unique().tolist(),
	"servicios": df['services'].dropna().unique().tolist(),
	"actividades": df['activities'].dropna().unique().tolist(),
	"exhibiciones_temporales": df['temporal_exhibitions'].dropna().unique().tolist(),
	"exhibiciones_permanentes": df['permanent_exhibitions'].dropna().unique().tolist()
}


class AgenteConversacional:
	def __init__(self) -> None:
		self.llm = ChatOpenAI(temperature=TEMPERATURE, model=LLM_MODEL, api_key=getenv("OPENAI_API_KEY"))
		self.memory = ConversationBufferMemory(memory_key="chat_history")
		self.df = df
		self.prompt_template = PROMPT_TEMPLATE
		self.error_count = 0

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
		# Validación de temas relevantes para turismo
		return any(tema in pregunta.lower() for tema in TEMAS_VALIDOS) or \
			any(valor.lower() in pregunta.lower() for valores in unicos_df.values() for valor in valores)

	def manejar_errores(self, error) -> str:
		errores: dict = {
			openai.error.APIError: "Lo siento, hubo un problema de conexión con el servidor. Por favor, intenta de nuevo en unos momentos.",
			openai.error.InvalidRequestError: "Lo siento, no entendí completamente tu pregunta. ¿Podrías formularla de otra manera?",
			pd.errors.EmptyDataError: "Lo siento, parece que hubo un problema al procesar los datos. Intenta preguntar nuevamente."
		}
		self.error_count += 1
		return errores.get(type(error), "Lo siento, ocurrió un error inesperado. Por favor, intenta de nuevo.")

	def consultar_agente(self, pregunta: str) -> str:
		if self.error_count >= MAX_ERROR_COUNT:
			return "Lo siento, por el momento no puedo ayudarte. Por favor, intenta de nuevo más tarde."

		if not self.es_pregunta_valida(pregunta):
			return "Lo siento, solo puedo proporcionarte información sobre turismo en la Ciudad de México."

		try:
			if "cuantos sitios" in pregunta.lower():
				return f"Hay un total de {len(self.df)} sitios turísticos en la Ciudad de México."

			resultados: DataFrame = self.df[self.df['description'].str.contains("CDMX", case=False, na=False)]
			data: str = resultados.to_string(index=False)

			response = self.agent_executor.invoke(f"{pregunta}\nAquí tienes la información relevante:\n{data}")
			self.error_count = 0  # Reiniciar el contador de errores si la consulta es exitosa
			return response['output']

		except Exception as e:
			return self.manejar_errores(e)
