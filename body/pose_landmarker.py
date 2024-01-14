import sys
import os.path
import cv2
import argparse
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# landmarks 저장 리스트 초기화
landmark_save = []

# RGB 이미지 위에 포즈 랜드마크를 그리는 함수
def draw_landmarks_on_image(rgb_image, detection_result):
    pose_landmarks_list = detection_result.pose_landmarks
    annotated_image = np.copy(rgb_image)

    # 탐지된 포즈를 시각화함
    # Loop through the detected poses to visualize.
    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]
        pose = np.zeros((33 * 3))
        for i, landmark in enumerate(pose_landmarks):
            # 각 랜드마크의 x, y, z 좌표를 저장
            pose[i * 3 + 0] = landmark.x
            pose[i * 3 + 1] = landmark.y
            pose[i * 3 + 2] = landmark.z

        # 각 프레임의 포즈 데이터를 저장
        landmark_save[idx].append(pose)

        # Draw the pose landmarks.
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        pose_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
        ])
        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            pose_landmarks_proto,
            solutions.pose.POSE_CONNECTIONS,
            solutions.drawing_styles.get_default_pose_landmarks_style())
    return annotated_image

# STEP 1: Import the necessary modules.
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 커맨드 라인 인자를 파싱
if len(sys.argv) < 1:
    print("Usage: pose_landmarker.py <clip_name> <num_poses> <min_pose_detection_confidence> <min_pose_presence_confidence> <min_tracking_confidence>")
    sys.exit(1)

# 인자 값 설정 (없으면 기본 값 설정)
parser = argparse.ArgumentParser()
parser.add_argument('-clip_name', help=' : Please set the clip name')
parser.add_argument('-num_poses', default = 1)
parser.add_argument('-min_pose_detection_confidence', default = 0.4)
parser.add_argument('-min_pose_presence_confidence', default = 0.2)
parser.add_argument('-min_tracking_confidence', default = 0.2)
args = parser.parse_args()

clip_name = args.clip_name[:-4]
num_poses = int(args.num_poses)
min_pose_detection_confidence = float(args.min_pose_detection_confidence)
min_pose_presence_confidence = float(args.min_pose_presence_confidence)
min_tracking_confidence = float(args.min_tracking_confidence)

landmark_save = [[] for i in range(num_poses)] # landmarks 저장 리스트 초기화

# STEP 2: Create an PoseLandmarker object.
# 포즈 랜드마커 객체를 생성
VisionRunningMode = mp.tasks.vision.RunningMode
base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    num_poses=num_poses,
    min_pose_detection_confidence=min_pose_detection_confidence,
    min_pose_presence_confidence=min_pose_presence_confidence,
    min_tracking_confidence=min_tracking_confidence,
    running_mode=VisionRunningMode.VIDEO,
    output_segmentation_masks=True)
detector = vision.PoseLandmarker.create_from_options(options)

cap = cv2.VideoCapture(clip_name + ".mp4") # 비디오 캡처 객체 생성
fps = cap.get(cv2.CAP_PROP_FPS) # 비디오의 FPS
timestamp = 0
fourcc = cv2.VideoWriter_fourcc(*'DIVX') # 비디오 코덱 설정

outvideo_path = clip_name.split('/')
output_path = '\\'.join(outvideo_path[:3] + ["Data_Results"] + outvideo_path[4:-1])
if not os.path.exists(output_path):
    os.makedirs(output_path)

out = cv2.VideoWriter('\\'.join(outvideo_path[:3] + ["Data_Results"] + outvideo_path[4:]) + '_pose.mp4', fourcc, fps, (640, 720)) # 박스 크기 조절 필요 (resize 후)
 
timestamp = 0
while cap.isOpened():
  success, image = cap.read()
  timestamp += 1

  if not success:
      print("Video processing completed or error occurred")
      break  # 비디오가 끝나거나 읽기에 실패하면 반복문 종료 

  resize_frame = cv2.resize(image, (640, 720), interpolation=cv2.INTER_CUBIC) # 박스 크기 조절 필요 (resize 후)
  mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=resize_frame)

  # STEP 4: Detect pose landmarks from the input image.
  detection_result = detector.detect_for_video(mp_image,timestamp)

  # STEP 5: Process the detection result. In this case, visualize it.
  annotated_image = draw_landmarks_on_image(resize_frame, detection_result)

  cv2.imshow("image",annotated_image)
  out.write(annotated_image)

  if cv2.waitKey(5) & 0xFF == 27:
    break  # 사용자가 ESC 키를 누르면 루프를 종료

cap.release()
out.release()

# joint name 파일 읽기
import pandas as pd
joints = pd.read_csv("joint_name.csv",header=None).iloc[:,0].to_list()

output_path = "../results/body/"
if not os.path.exists(output_path):
    os.makedirs(output_path)
os.chdir(output_path)

for idx in range(num_poses):
    arr = np.array(landmark_save[idx])
    arr = arr.reshape(-1, 99)

    #엑셀 저장
    df = pd.DataFrame(arr, columns=joints)
    df.to_excel(clip_name.split('/')[-1] + "-" + str(idx + 1) + ".xlsx")