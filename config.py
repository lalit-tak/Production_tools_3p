import base64
import json
from os import urandom
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import hashlib


class Config:
    def __init__(self):
        self.ITERATIONS = 390000
        self.PASSWORD = b"PUT_ENC_PASSWORD"
        self.CHECKSUMPASS = "PUT_CHECKSUM_PASSWORD"

    def decrypt_json(self, encrypted_json): 
        try:   
            with open(encrypted_json, "rb") as f:
                salt = f.read(16)
                encrypted_data = f.read()
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=390000,)
            
            key = base64.urlsafe_b64encode(kdf.derive(self.PASSWORD))
            cipher = Fernet(key)
            decrypted = cipher.decrypt(encrypted_data)
            config = json.loads(decrypted.decode("utf-8"))
            return config
        except Exception as e:
            print("error : ", str(e))

    def load_config_json(self, filename):
        data = {}
        with open(filename, 'r') as file:
            data = json.load(file)
        if len(data) > 0:
            return data, True
        else:
            return {}, False
    
    # ---------- CHECKSUM ----------
    def generate_checksum(self, data):
        json_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_string.encode()).hexdigest()

    # ---------- KEY FROM PASSWORD ----------
    def get_key_from_password(self, password):
        try:
            key = hashlib.sha256(password.encode()).digest()
            return base64.urlsafe_b64encode(key)
        except Exception as e:
            print("Error: ", str(e))
            return False

    def decrypt_data(self, encrypted_data, password):
        try:
            key = self.get_key_from_password(password)
            cipher = Fernet(key)
            decrypted = cipher.decrypt(encrypted_data.encode())
            return json.loads(decrypted.decode())
        except Exception as e:
            if str(type(e).__name__) == "InvalidToken":
                print("Error Wrong fixed_config file is used", type(e).__name__)
            return {}

    def check_encrypted_json(self, filename):
        try:
            config_dict = {}
            config_dict = self.decrypt_json(filename)
            if isinstance(config_dict, dict):
                if "encrypted_data" in config_dict and "checksum" in config_dict:
                    encrypted_data = config_dict["encrypted_data"]
                    old_checksum = config_dict["checksum"]
                    try:
                        data = self.decrypt_data(encrypted_data, self.CHECKSUMPASS)
                        if len(data)>0:
                            new_checksum = self.generate_checksum(data)
                            if old_checksum == new_checksum:
                                if "pct" in data.get("TOOL_TYPE", "img_pct").lower():
                                    return data, True
                                else:
                                    print("Wrong Encrypted Serial Config file Selected")
                                    return {}, False
                            else:
                                return {}, False
                        else:
                            return {}, False
                        
                    except Exception as e:
                        print("Error: ",str(e))
                        return {}, False
                else:
                    return {}, False
            else:
                return {}, False
        except Exception as e:
            print("Error: ", str(e))
            return {}, False

