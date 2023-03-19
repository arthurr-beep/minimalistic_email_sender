import base64

def file_to_base64(file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()
        return base64.b64encode(file_data).decode("utf-8")
