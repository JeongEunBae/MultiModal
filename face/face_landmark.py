import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import Tuple, Union
import math
import cv2
import numpy as np
import sys
import argparse

MARGIN = 10  # 픽셀 단위의 여백
ROW_SIZE = 10  # 픽셀 단위의 행 크기
FONT_SIZE = 1 # 폰트 크기
FONT_THICKNESS = 1 # 폰트 두께
TEXT_COLOR = (255, 0, 0)  # red

# 얼굴 랜드마크 좌표를 저장할 리스트 초기화 (6개점)
# 최대 두 사람까지 데이터 저장 가능 (multi) -> 다만 현재는 1명 기준으로 코드화 되어있음. (2명일 경우 코드 수정 필요)
landmark_save = [[], []] 

# 정규화된 좌표를 픽셀 좌표로 변환하는 함수
def _normalized_to_pixel_coordinates(normalized_x: float, normalized_y: float, image_width: int, image_height: int) -> Union[None, Tuple[int, int]]:
  """Converts normalized value pair to pixel coordinates."""

  # Checks if the float value is between 0 and 1.
  def is_valid_normalized_value(value: float) -> bool:
    return (value > 0 or math.isclose(0, value)) and (value < 1 or
                                                      math.isclose(1, value))

  if not (is_valid_normalized_value(normalized_x) and
          is_valid_normalized_value(normalized_y)):
    # TODO: Draw coordinates even if it's outside of the image bounds.
    return None
  x_px = min(math.floor(normalized_x * image_width), image_width - 1)
  y_px = min(math.floor(normalized_y * image_height), image_height - 1)
  return x_px, y_px

# 입력 이미지에 bounding box와 key-point(landmark)를 그리는 함수
def visualize(image, detection_result) -> np.ndarray:
  """Draws bounding boxes and keypoints on the input image and return it.
  Args:
    image: The input RGB image.
    detection_result: The list of all "Detection" entities to be visualize.
  Returns:
    Image with bounding boxes.
  """
  annotated_image = image.copy()
  height, width, _ = image.shape

  pose_landmarker_list = detection_result.detections
  for idx in range(len(pose_landmarker_list)):
    # Draw bounding_box
    bbox = pose_landmarker_list[idx].bounding_box
    start_point = bbox.origin_x, bbox.origin_y
    end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
    cv2.rectangle(annotated_image, start_point, end_point, TEXT_COLOR, 3)

    pose_landmarkers = pose_landmarker_list[idx]
    pose = np.zeros(6 * 2)
    # Draw keypoints
    for i, keypoint in enumerate(pose_landmarkers.keypoints):
      keypoint_px = _normalized_to_pixel_coordinates(keypoint.x, keypoint.y,
                                                     width, height)
      pose[i * 2 + 0] = keypoint.x
      pose[i * 2 + 1] = keypoint.y

      color, thickness, radius = (0, 255, 0), 2, 2
      cv2.circle(annotated_image, keypoint_px, thickness, color, radius)
    landmark_save[0].append(pose)
    # Draw label and score

    category = pose_landmarkers.categories[0]
    category_name = category.category_name
    category_name = '' if category_name is None else category_name
    probability = round(category.score, 2)
    result_text = category_name + ' (' + str(probability) + ')'
    text_location = (MARGIN + bbox.origin_x,
                     MARGIN + ROW_SIZE + bbox.origin_y)
    cv2.putText(annotated_image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

  return annotated_image

# STEP 1: Import the necessary modules.
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 얼굴 탐지 모델을 설정하고 초기화
# STEP 2: Create an FaceDetector object.
VisionRunningMode = mp.tasks.vision.RunningMode
base_options = python.BaseOptions(model_asset_path='detector.tflite')
options = vision.FaceDetectorOptions(base_options=base_options, running_mode=VisionRunningMode.VIDEO)
detector = vision.FaceDetector.create_from_options(options)

# 비디오 처리를 위한 설정
# 커맨드 라인 인자로 부터 clip_name을 받습니다.
parser = argparse.ArgumentParser()
parser.add_argument('-clip_name', help=' : Please set the clip name')
args = parser.parse_args()

clip_name = args.clip_name[:-4]

cap = cv2.VideoCapture(clip_name + ".mp4")
fps = cap.get(cv2.CAP_PROP_FPS)
timestamp = 0
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
out = cv2.VideoWriter(clip_name + '_face.mp4', fourcc, fps, (640, 320))

# 비디오 프레임 별 얼굴 Detection를 수행하는 반복문
timestamp = 0
while cap.isOpened():
  success, image = cap.read()
  timestamp += 1

  if not success:
    print("Video processing completed or error occurred")
    break  # 비디오가 끝나거나 읽기에 실패하면 반복문 종료 
            
  # STEP 3: Load the input image.
  resize_frame = cv2.resize(image, (640, 320), interpolation=cv2.INTER_CUBIC)
  mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=resize_frame)

  # STEP 4: Detect faces in the input image.
  detection_result = detector.detect_for_video(mp_image,timestamp)

  # STEP 5: Process the detection result. In this case, visualize it.
  annotated_image = visualize(resize_frame, detection_result)
  cv2.imshow("image", annotated_image)
  out.write(annotated_image)

  if cv2.waitKey(5) & 0xFF == 27:
    break  # 사용자가 ESC 키를 누르면 루프를 종료

arr = np.array(landmark_save[0])

import pandas as pd
face = pd.read_csv("face_point_name.csv",header=None).iloc[:,0].to_list()

output_path = "../results/face/"
if not os.path.exists(output_path):
    os.makedirs(output_path)
os.chdir(output_path)
    
# 탐지된 특징점 데이터를 엑셀 파일로 저장
df = pd.DataFrame(arr, columns=face)
df.to_excel(clip_name.split('\\')[-1] + ".xlsx")

# 비디오 캡처와 출력 객체를 해제
cap.release()
out.release()

