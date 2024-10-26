import pandas as pd
from os import getenv
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_experimental.agents.agent_toolkits import create_csv_agent

from app.resources.config import *


load_dotenv(DOTENV_ABSPATH)


class AgenteConversacional:
    def __init__(self, tts_function):
        self.tts_func = tts_function
        self.llm = ChatOpenAI(
            temperature=TEMPERATURE,
            model=LLM_MODEL,
            api_key=getenv("OPENAI_API_KEY")
        )
        self.agent_executor = create_csv_agent(self.llm, DATASET_PATH)
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.df = pd.read_csv(DATASET_PATH)
        self.prompt_template = PROMP_TEMPLATE
        self.agent_executor = AgentExecutor(llm=llm, memory=memory, prompt=prompt_template)  # Configurar el ejecutor del agente
    
    def consultar_agente(self, pregunta: str):
        pregunta = pregunta.lower()
        if not any(tema in pregunta for tema in TEMAS_VALIDOS):
            return "Lo siento, solo puedo proporcionarte información sobre sitios turísticos en la Ciudad de México."

        resultados = df[df['description'].str.contains("CDMX", case=False, na=False)]
        if len(resultados) > 5:
            resultados = resultados.head(5)

        data = resultados.to_string(index=False)
        response = self.agent_executor.invoke(f"{pregunta}\nAquí tienes la información:\n{data}")
        agent_response_text = response['output']
        audio_data = self.tts_func(agent_response_text)

        return {
            "agent_response": agent_response_text,
            "audio_data": audio_data
        }