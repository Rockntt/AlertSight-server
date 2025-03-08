# pylint: disable=missing-module-docstring
# pylint: disable=no-member
# pylint: disable=dangerous-default-value
# pylint: disable=import-error

import random

import cv2  # Обратно видео и изображений
import numpy as np  # Математические операции с векторами
from ultralytics import YOLO  # Нейросеть OD
from ultralytics.utils.plotting import Annotator


# модуль логирования
import logger
from apidriver import ApiDriver

# инициализация логгера
api = ApiDriver('http://127.0.0.1:5000')
logs = logger.Logger()
logs.init_log_file()
logs.log("[AlertSight] Logger initialized")



def average_video(video_path, n_seconds, fps, output_path):
    """
    Создает видео из средних кадров за последние n секунд исходного видео.

    Args:
      video_path: Путь к исходному видеофайлу.
      n_seconds: Количество секунд, для которых нужно вычислить средний кадр.
      fps: Частота кадров исходного видео.
      output_path: Путь к выходному видеофайлу.
    """


    # Загружаем исходное видео
    cap = cv2.VideoCapture(video_path)

    # Определяем количество кадров для усреднения
    n_frames = int(n_seconds * fps)

    # Создаем список для хранения последних кадров
    frames = []

    # Создаем видеокодек для записи выходного видео
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Используйте подходящий кодек для вашего видео
    out = cv2.VideoWriter(output_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))
    first_iter = True

    # Проходим по исходному видео кадр за кадром
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if first_iter:
            avg = np.float32(frame)
            first_iter = False
        else:
            frames.append(frame)

        # Если длина списка достигла количества кадров для усреднения,
        # вычисляем средний кадр и записываем его в выходное видео
        if len(frames) == n_frames:
            for i in range(1, n_frames):
                cv2.accumulateWeighted(frames[i], avg, 0.01)
            average_frame = cv2.convertScaleAbs(avg)

            for i in range(5):
                out.write(average_frame)

            # Удаляем первые 2 кадра из списка, чтобы поддерживать его длину
            frames.pop(0)
            frames.pop(0)

    # Закрываем видео потоки
    cap.release()
    out.release()

    cap = cv2.VideoCapture(output_path)

    # Показываем пользователю результат в окне программы
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def inference(video_path, model_path='yolov8n.pt', threshold=0.0, classes=[0]):
    """
      Распознает все указанные объекты на видео с помощью YOLOv8

      Args:
        video_path: Путь к исходному видеофайлу.
        model_path: Путь к весам нейросети.
        threshold: Порог точности.
        classes: Классы к обнаружению.
      """

    saved_objects = {}

    # Загрузка модели
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_path)

    # Работа с файлом покадрово
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model.track(frame, verbose=False,
                              classes=classes, conf=threshold,
                              tracker='bytetrack.yaml', persist=True)

        for result in results:
            annotator = Annotator(frame)
            for box in result.boxes:

                # Аннотация кадра
                annotator.box_label(box.xyxy[0], model.names[int(box.cls)],
                                    color=(255, 255, 255),
                                    txt_color=(0, 0, 0))

                # Получение ID объекта
                track_id = int(box.id) if box.id is not None else None

                if track_id is not None:
                    if track_id not in saved_objects:

                        filename = f'objects/{track_id}_{random.randint(1, 10**5)}.jpg'

                        # Сохранение кадра с происшествием
                        cv2.imwrite(filename, frame)

                        # Обращаемся к AlertSight-API, загружаем в БД происшествие
                        api.upload(filename, model.names[int(box.cls)], 'kmv-junior')

                        logs.log(
                            f"{model.names[int(box.cls)]} | {str(box.conf)[8:14]}",
                            "red")

                        # Отметка, что объект сохранен
                        saved_objects[track_id] = True

        cv2.imshow("Inference", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


N_SECONDS = 5  # Количество секунд для усреднения
FPS = 30  # Частота кадров видео потока


if __name__ == "__main__":
    inference("samples/crash0avg.avi", model_path="weights/yolov8n_c.pt",
              threshold=0.5, classes=[2])
    inference("samples/drone0.mp4", model_path="weights/drones.pt",
              threshold=0.5)
    inference("samples/drone1.mp4", model_path="weights/drones.pt",
              threshold=0.5)

    logs.log("Program finished", "INFO")
    logs.log("Closing log file. Bye!", "INFO")
    logs.close()
