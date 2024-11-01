from os import getenv
from os.path import join
from dotenv import load_dotenv

import wave
import json
from TTS.api import TTS
from pyaudio import paInt16
from base64 import b64encode
from geopy.distance import geodesic
from cryptography.fernet import Fernet
from vosk import Model, KaldiRecognizer
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_experimental.agents.agent_toolkits import create_csv_agent

from app.resources.config import *
from app.resources.llm import AgenteConversacional

load_dotenv(DOTENV_ABSPATH)


###############################################################################
############################# Users Functions #################################
###############################################################################

def encrypt(string: str) -> bytes:
	encoded: bytes = string.encode()
	f: Fernet = Fernet(getenv("FERNET_SECRET_KEY"))
	return f.encrypt(encoded)


def decrypt(string: str) -> str:
	f: Fernet = Fernet(getenv("FERNET_SECRET_KEY"))
	decrypted: bytes = f.decrypt(string)
	return decrypted.decode()


###############################################################################
############################# Models Functions ################################
###############################################################################

def get_place_distance(
		current_position: tuple[float, float],
		place_position: tuple[float, float]
	) -> float:

	return geodesic(current_position, place_position).kilometers


def speech_recognition() -> str:
	with wave.open(join("/tmp", TEMP_FILE_NAME), "rb") as file:
		if not any([
			file.getnchannels() != CHANNELS,
			file.getsampwidth() != paInt16,
			file.getframerate() != SAMPLING_RATE
		]):
			raise ValueError("vosk_audio_file")

		model = Model(model_path=VOSK_ABSPATH)
		recognizer = KaldiRecognizer(model, SAMPLING_RATE)

		results = []
		while True:
			data = file.readframes(FRAMES_FLOW)
			if len(data) == 0:
				break
			if recognizer.AcceptWaveform(data):
				result = recognizer.Result()
				results.append(json.loads(result))

		final_result = recognizer.FinalResult()
		results.append(json.loads(final_result))

		text: str = f"{' '.join([res['text'] for res in results])}."
		return text

#!Agente conversacional

agente = AgenteConversacional(tts_function=tts_func)

def consultar_agente(pregunta: str) -> dict:
	respuesta = agente.consultar_agente(pregunta)
	agente_response_text = respuesta["agent_response"]

	#Generar el audio de la respuesta 
	audio_data = tts_func(agente_response_text)

	#Retorna respuesta y audio
	return{
		"agent_response": agente_response_text,
		"audio_data": audio_data
	}

def tts_func(text: str) -> dict:
	tts = TTS(model_name=TTS_MODEL_NAME, progress_bar=False).to(DEVICE)
	tts.tts_to_file(
		text=text,
		speaker_wav="my/cloning/audio.wav",
		file_path=join("/tmp", TEMP_FILE_NAME)
	)

	with wave.open(join("/tmp", TEMP_FILE_NAME), "rb") as file:
		nchannels = file.getnchannels()
		sampwidth = file.getsampwidth()
		framerate = file.getframerate()
		nframes = file.getnframes()
		comp_type = file.getcomptype()
		comp_name = file.getcompname()
		duration = nframes / float(framerate)

		audio = file.readframes(nframes)
		audio_base64: str = b64encode(audio).decode("utf-8")

	audio_data: dict = {
		"nchannels": nchannels,
		"sampwidth": sampwidth,
		"framerate": framerate,
		"nframes": nframes,
		"comp_type": comp_type,
		"comp_name": comp_name,
		"duration": duration,
		"audio": audio_base64
	}

	return audio_data
