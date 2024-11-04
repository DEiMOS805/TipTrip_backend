import pandas as pd
from os import getenv
from pandas import DataFrame
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_experimental.agents.agent_toolkits import create_csv_agent

from app.resources.config import *


load_dotenv(DOTENV_ABSPATH)


class AgenteConversacional:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            temperature=TEMPERATURE,
            model=LLM_MODEL,
            api_key=getenv("OPENAI_API_KEY")
        )
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.df: DataFrame = pd.read_csv(DATASET_ABSPATH)
        self.prompt_template: str = PROMP_TEMPLATE

        self.agent_executor = create_csv_agent(
            llm=self.llm,
            path=DATASET_ABSPATH,
            verbose=False,  # Para deshabilitar mensajes detallados
            agent_type="openai-functions",  # Tipo de agente
            allow_dangerous_code=True,  # Permite la ejecución de código inseguro (si es necesario)
            prompt_template=self.prompt_template,  # Usa el template personalizado
            memory=self.memory  # Añade la memoria de conversación
        )

    def consultar_agente(self, pregunta: str) -> str:
        pregunta = pregunta.lower()
        # if not any(tema in pregunta for tema in TEMAS_VALIDOS):
        #     return "Lo siento, solo puedo proporcionarte información sobre sitios turísticos en la Ciudad de México."

        resultados: DataFrame = self.df[self.df["description"].str.contains("CDMX", case=False, na=False)]

        data = resultados.to_string(index=False)
        response = self.agent_executor.invoke(f"{pregunta}\nAquí tienes la información:\n{data}")
        agent_response_text = response["output"]

        return agent_response_text
