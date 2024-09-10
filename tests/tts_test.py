import torch
from TTS.api import TTS
from TTS.utils.manage import ModelManager


def show_all_models() -> None:
	# Crear una instancia del gestor de modelos
	manager = ModelManager()

	# Listar los modelos disponibles
	available_models = manager.list_models()

	# Imprimir los modelos disponibles
	for model in available_models:
		print(model)


def get_device() -> str:
	return "cuda" if torch.cuda.is_available() else "cpu"


def test_tts(model: str, device: str) -> None:
	tts = TTS(model_name=model, progress_bar=False).to(device)
	tts.tts_to_file(
		text="El sol se alzaba lentamente en el horizonte, pintando el cielo con tonos cálidos de naranja y rosa.",
		speaker_wav="my/cloning/audio.wav",
		file_path="output.wav"
	)


if __name__ == "__main__":
	# show_all_models()
	device = get_device()
	test_tts(model="tts_models/es/css10/vits", device=device)
