"""модуль HTTP запросов"""
import requests

class ApiDriver:
    """Класс, обеспечивающий работу с внешним API AlertSight"""
    def __init__(self, _url):
        """Инициализация
        :param _url: Адрес API
        """
        self.url = _url

    def upload(self, filename, category="undefined", source_id="undefined"):
        """Загрузка данных
        :param filename: Адрес API
        :param category: Путь к изображению
        :param source_id: Источник фото
        """
        data = {
            "type": category,
            "source_id": source_id,
        }

        # Файл для отправки
        with open(filename, "rb") as img:
            files = {
                "image": img
            }
            # Отправляем POST-запрос
            response = requests.post(f"{self.url}/upload", data=data, files=files)
            # Проверяем ответ
            if response.status_code == 200:
                print("Upload successful!")
                print("Response:", response.json())  # Выводим JSON-ответ
            else:
                print("Upload failed!")
