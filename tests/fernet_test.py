from cryptography.fernet import Fernet


def generate_key() -> str:
	key = Fernet.generate_key()
	return key


def encrypt_message(message: str, key: str) -> bytes:
	encoded_message = message.encode()
	f = Fernet(key)
	return f.encrypt(encoded_message)


def decrypt_message(encrypted_message: str, key: str) -> str:
	f = Fernet(key)
	decrypted_message = f.decrypt(encrypted_message)
	decrypted_message = decrypted_message.decode()
	return decrypted_message


if __name__ == "__main__":
	key = generate_key()

	encrypted_message = encrypt_message("encrypt this message", key)
	print(encrypted_message)
	print(type(encrypted_message))

	decrypted_message = decrypt_message(encrypted_message, key)
	print(decrypted_message)
	print(type(decrypted_message))
