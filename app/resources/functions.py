import wave
import json
from re import sub
from os import getenv
from TTS.api import TTS
from os.path import join
from pyaudio import paInt16
from base64 import b64encode
from dotenv import load_dotenv
from num2words import num2words
from geopy.distance import geodesic
from cryptography.fernet import Fernet
from vosk import Model, KaldiRecognizer

from app.resources.config import *
from app.resources.llm import AgenteConversacional


load_dotenv(DOTENV_ABSPATH)
agente = AgenteConversacional()


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

		results: list = []
		while True:
			data: bytes = file.readframes(FRAMES_FLOW)
			if len(data) == 0:
				break
			if recognizer.AcceptWaveform(data):
				result = recognizer.Result()
				results.append(json.loads(result))

		final_result = recognizer.FinalResult()
		results.append(json.loads(final_result))

		return f"{' '.join([res['text'] for res in results])}."


def format_text(text: str) -> str:
	for symbol, word in TEXT_REPLACEMENTS.items():
		text = text.replace(symbol, word)

	# Replace the symbol $ followed by a number, like "$50" or "$25", with "fifty pesos"
	text = sub(r"\$(\d+)", lambda x: f"{num2words(int(x.group(1)), lang='es')} pesos", text)

	# Replace numbers with words for other cases (without the $ symbol in front)
	# This also converts numbers with decimals correctly
	text = sub(r"\b\d+(\.\d+)?\b", lambda x: num2words(float(x.group()), lang="es").replace('.', " punto "), text)

	text = text.replace("hrs.", "horas")

	# Remove "http://", "https://", and "www." and replace "." with "punto" on URLs
	text = sub(r"https?://(www\.)?([^/]+)", lambda x: x.group(2).replace('.', " punto "), text)
	text = sub(r"\b([\w\-]+ punto [\w\-]+(?: punto [\w\-]+)?)(/.*)?\b(/)?", r"\1", text)

	# Replace more special characters
	text = text.replace(':', " dos puntos ") \
		.replace('*', "") \
		.replace(';', "") \
		.replace('=', "") \
		.replace('(', "").replace(')', "") \
		.replace('[', "").replace(']', "") \
		.replace('{', "").replace('}', "") \

	return text


def tts_func(text: str) -> dict:
	text = format_text(text)

	tts: TTS = TTS(model_name=TTS_MODEL_NAME, progress_bar=False).to(DEVICE)
	tts.tts_to_file(
		text=text,
		speaker_wav="my/cloning/audio.wav",
		file_path=join("/tmp", TEMP_FILE_NAME)
	)

	with wave.open(join("/tmp", TEMP_FILE_NAME), "rb") as file:
		nchannels: int = file.getnchannels()
		sampwidth: int = file.getsampwidth()
		framerate: int = file.getframerate()
		nframes: int = file.getnframes()
		comp_type: str = file.getcomptype()
		comp_name: str = file.getcompname()
		duration: float = nframes / float(framerate)

		audio: bytes = file.readframes(nframes)
		audio_base64: str = b64encode(audio).decode("utf-8")

	return {
		"nchannels": nchannels,
		"sampwidth": sampwidth,
		"framerate": framerate,
		"nframes": nframes,
		"comp_type": comp_type,
		"comp_name": comp_name,
		"duration": duration,
		"audio": audio_base64
	}


def consultar_agente(pregunta: str) -> dict:
	respuesta: str = agente.consultar_agente(pregunta)

	return {
		"text": respuesta,
		"audio_data": tts_func(respuesta)
	}
