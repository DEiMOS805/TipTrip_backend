import os
import wave
import json
from TTS.api import TTS
from pyaudio import paInt16
from base64 import b64encode
from vosk import Model, KaldiRecognizer

from app.resources.config import *


def speech_recognition() -> str:
	with wave.open(os.path.join("/tmp", TEMP_FILE_NAME), "rb") as file:
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
