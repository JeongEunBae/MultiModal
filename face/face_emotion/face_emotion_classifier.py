import csv
import os
import shutil
import sys
import cv2
import tensorflow as tf
import argparse
from keras.models import load_model
import pandas as pd
import numpy as np
from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from tensorflow.keras.utils import load_img
from utils.preprocessor import preprocess_input

def most_frequent(List):
    return max(set(List), key=List.count)

def get_most_frequent_emotion(dict_):
    emotions = []
    for frame_nmr in dict_.keys():
        for face_nmr in dict_[frame_nmr].keys():
            emotions.append(dict_[frame_nmr][face_nmr]['emotion'])

    return most_frequent(emotions)

def process():
    # parameters for loading data and images

    # 비디오 처리를 위한 설정
    # 커맨드 라인 인자로 부터 clip_name을 받습니다.
    parser = argparse.ArgumentParser()
    parser.add_argument('-clip_name', help=' : Please set the clip name')
    args = parser.parse_args()

    image_path = args.clip_name
    clip_name = args.clip_name[:-4]
    detection_model_path = './trained_models/detection_models/haarcascade_frontalface_default.xml'
    emotion_model_path = './trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
    emotion_labels = get_labels('fer2013')
    font = cv2.FONT_HERSHEY_SIMPLEX

    # 각 프레임별 감정 예측값을 저장하는 딕셔너리를 초기화
    emotions_per_frame = []

    # hyper-parameters for bounding boxes shape
    emotion_offsets = (0, 0)

    # loading models
    face_detection = load_detection_model(detection_model_path)
    emotion_classifier = load_model(emotion_model_path, compile=False)

    # getting input model shapes for inference
    emotion_target_size = emotion_classifier.input_shape[1:3]

    frames_dir = './.tmp'
    if image_path[-3:] in ['jpg', 'png']:
        images_list = [image_path]
    else:
        if os.path.exists(frames_dir):
            shutil.rmtree(frames_dir)
        os.mkdir(frames_dir)
        os.system('ffmpeg -i {} {}/$frame_%010d.jpg'.format(image_path, frames_dir))
        images_list = [os.path.join(frames_dir, f) for f in sorted(os.listdir(frames_dir))]

    output = {}
    timestamp = 0
    for image_path_, image_path in enumerate(images_list):
        # loading images
        gray_image = load_img(image_path, color_mode="grayscale")
        gray_image = np.squeeze(gray_image)
        gray_image = gray_image.astype('uint8')

        faces = detect_faces(face_detection, gray_image)

        tmp = {}
        for face_coordinates_, face_coordinates in enumerate(faces):

            x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
            gray_face = gray_image[y1:y2, x1:x2]

            try:
                gray_face = cv2.resize(gray_face, (emotion_target_size))
            except:
                continue

            gray_face = preprocess_input(gray_face, True)
            gray_face = np.expand_dims(gray_face, 0)
            gray_face = np.expand_dims(gray_face, -1)
            np.set_printoptions(precision=8, suppress = True)
            emotion_prediction = emotion_classifier.predict(gray_face)

            emotions_per_frame.append([timestamp] + list(emotion_prediction.flatten()))

            timestamp += 1
        output[image_path_] = tmp

    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)

    return emotions_per_frame, emotion_labels, clip_name

import os
if __name__ == "__main__":
    emotions_per_frame, emotion_labels, clip_name = process()

    output_path = f"D:/MultiModal/multi_modal/results/face/face_emotion/{clip_name.split('/')[5]}"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    output_file = output_path + clip_name.split('/')[-1] + "_emotion_predictions.csv"
    file = open(output_file, 'w', encoding="utf-8", newline='')
    writer = csv.writer(file)

    title = [emotion_labels[idx] for idx in range(len(emotion_labels))]
    writer.writerow(["Timestamp"] + title)

    for line in emotions_per_frame:
        writer.writerow(line)
