# Import SixDRepNet
import argparse
from sixdrepnet import SixDRepNet
import cv2
import os
import numpy as np

# Create model
# Weights are automatically downloaded
model = SixDRepNet()

# 얼굴 랜드마크 좌표를 저장할 리스트 초기화 (6개점)
# 최대 두 사람까지 데이터 저장 가능 (multi) -> 다만 현재는 1명 기준으로 코드화 되어있음. (2명일 경우 코드 수정 필요)
landmark_save = [[], []]

# Open a video file
# 비디오 처리를 위한 설정
# 커맨드 라인 인자로 부터 clip_name을 받습니다.
parser = argparse.ArgumentParser()
parser.add_argument('-clip_name', help=' : Please set the clip name')
args = parser.parse_args()

clip_name = args.clip_name[:-4]

cap = cv2.VideoCapture(clip_name + ".mp4")
fps = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*'DIVX')

outvideo_path = clip_name.split('/')
output_path = '\\'.join(outvideo_path[:3] + ["Data_Results"] + [outvideo_path[4]] + ["Face_Rotation"] + outvideo_path[5:-1])
if not os.path.exists(output_path):
    os.makedirs(output_path)

out = cv2.VideoWriter('\\'.join(outvideo_path[:3] + ["Data_Results"] + [outvideo_path[4]] + ["Face_Rotation"] + outvideo_path[5:]) + '_rotation.mp4', fourcc, fps, (640, 360))

while cap.isOpened():
    # Read a frame from the video
    ret, frame = cap.read()
    
    # Break the loop if the video has ended
    if not ret:
        break

    # Predict orientation
    pitch, yaw, roll = model.predict(frame)
    landmark_save[0].append([yaw[0], pitch[0], roll[0]])

    # Display the frame
    model.draw_axis(frame, yaw, pitch, roll)
    cv2.imshow("Video Frame", frame)

    # Break the loop if 'esc' key is pressed
    if cv2.waitKey(1) & 0xFF == 27:
        break

arr = np.array(landmark_save[0])
import pandas as pd

face_rotation = ["Yaw", "Pitch", "Roll"]

output_path = f"../../results/face/face_rotation/{outvideo_path[5]}"
if not os.path.exists(output_path):
    os.makedirs(output_path)
os.chdir(output_path)

# rotation 데이터를 엑셀 파일로 저장
df = pd.DataFrame(arr, columns=face_rotation)
df.to_excel(clip_name.split('/')[-1] + ".xlsx")

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()
