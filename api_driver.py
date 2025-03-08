import requests

class API_Driver:
    def __init__(self, _url):
        self.url = _url

    def upload(self, filename, type="undefined", source_id="undefined"):

        data = {
            "type": type,
            "source_id": source_id,
        }

        # Файл для отправки
        files = {
            "image": open(filename, "rb")
        }

        # Отправляем POST-запрос
        response = requests.post(f"{self.url}/upload", data=data, files=files)

        # Проверяем ответ
        if response.status_code == 200:
            print("Upload successful!")
            print("Response:", response.json())  # Выводим JSON-ответ
        else:
            print("Upload failed!")
            # print("Status code:", response.status_code)
            # print("Response:", response.text)  # Выводим текст ответа