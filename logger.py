# pylint: disable=unspecified-encoding
"""
Модуль для логирования событий
"""

import datetime
import os
from colorama import Fore
from colorama import Style

class Logger:
    """
    Класс логгера с необходимыми методами
    """
    def __init__(self):
        self.log_file = ''
        self.log_file_dir = ''

    def init_log_file(self):
        """
        Создание файла для логирования
        """
        now = datetime.datetime.now()
        formatted_date = now.strftime("%Y-%m-%d_%H-%M-%S")
        try:
            os.mkdir("logs")
        except FileExistsError:
            pass
        with open(f"logs/log-{formatted_date}.txt", "w") as file:
            self.log_file_dir = f"logs/log-{formatted_date}.txt"
            self.log_file = file


    def log(self, message='n/a', level='n/a'):
        """
        Запись события в файл
        :param message: Сообщение (событие)
        :param level: Класс события (ИНФО, ПРЕД, ОШИБКА, ОК)
        """
        with open(self.log_file_dir, 'a', encoding='utf-8') as f:
            now = datetime.datetime.now()
            formatted_time = now.strftime("%H:%M:%S")
            f.write(f"[{formatted_time}] {level}: {message}\n")
            if level.upper() == 'ERROR' or level.upper() == 'RED':
                status_color = Fore.LIGHTRED_EX
            elif level.upper() == 'WARNING' or level.upper() == 'YELLOW':
                status_color = Fore.LIGHTYELLOW_EX
            elif level.upper() == "SUCCESS" or level.upper() == 'GREEN':
                status_color = Fore.LIGHTGREEN_EX
            else:
                status_color = Fore.LIGHTWHITE_EX
            print(status_color + f"[{formatted_time}] : {message}" + Style.RESET_ALL)
        f.close()

    def close(self):
        """
        Безопасное закрытие файла
        """
        self.log_file.close()
