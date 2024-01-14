# Multi Modal(Face, Body) Data Extract Model

**피험자의 `Body(body pose)`, `Face(face landmarker, rotation, emotion)`의 Feature 값을 추출하는 프로그램**
> **GitHub 폴더 이름**: MultiModal_Model 👉🏻 [Downloads](https://github.com/JeongEunBae/MultiModal) </br>
> **Local 폴더 이름** : MultiModal_Model 👉🏻 [Downloads](https://drive.google.com/file/d/1tJFk0t0dzGoA-30rauG4GkaGWCaSa7AH/view?usp=sharing)

#### 가상 환경 구축 
> Tensorflow 버전은 CUDA 버전과 모두 맞추었다고 가정한다.
> Torch환경도 CUDA 버전과 모두 맞추었다고 가정한다.
> MultiModal 폴더를 만들었다고 가정한다.

1. **전체 환경 구축**
   - **`requirement.txt`** 파일이 있는 디렉토리 내에서 아래와 같은 명령어로 **패키지를 설치한다.**
   
   ```bash
   ~\MultiModal\MultiModal_Model> pip install -r requirement.txt
   ```

2. **추가 환경 구축**
   - 딥러닝 기반 Face Rotation 값을 추출하는 모델을 사용하기 위해 추가로 환경을 구축한다. (기존 모델 👉🏻 [References](https://github.com/thohemp/6drepnet)) 
   - **`requirement.txt`** 파일이 있는 디렉토리 내에서 아래와 같은 명령어로 **패키지를 설치한다.** 
   
   ```bash
   ~\MultiModal\MultiModal_Model> cd face/face_rotation
   ~\MultiModal\MultiModal_Model\face\face_rotation> pip install -r requirement.txt
   ~\MultiModal\MultiModal_Model\face\face_rotation> pip3 install sixdrepnet # 모델 다운로드
   ```
---

#### 데이터 추출 
**[데이터셋 위치]** : **MultiModal/Data/Data_Preprocessing** 폴더

**[결과파일 위치]** : 
- `좌표 데이터 파일(excel)` : **MultiModal/MultiModal_Model/results** 폴더 내 
- `landmark된 영상 파일(video)` : **MultiModal/Data/Data_Results** 폴더 내

#### 📌 실행 순서
1. **`setting.py`** 파일이 존재하는 디렉토리로 이동
   
   ```bash
   ~\MultiModal> cd MultiModal_Model
   ```

2. **`setting.py`** 실행 
  - **옵션**에 맞게 실행하면 된다. 
    
  ```bash
  ~\MultiModal\MultiModal_Model> python setting.py -group_name <group_name> -option <option>
  ```

**[Option 설명]**

- `-group_name` :  그룹명 입력 (ex - `-group_name A`) **⭐필수 입력⭐**

- `-option` : 추출할 Feature 선택 (ex - `-option face_emotion`) **⭐필수 입력⭐**
  > option은 `body|face_landmark|face_emotion|face_rotation` 중에 입력

</br>

#### 💡 [참고] Body Pose Parameter
**[Parameter 설명]**

- `-clip_name` :  비디오 파일 이름 (ex - `-clip_name ..\dataset\body\body_test.mp4`) **⭐필수 입력⭐**

- `-num_poses` : 최대 인식할 Pose 수 (ex - `-num_poses 1`) 
  
  > **default 값 : 1**

- `-min_pose_detection_confidence` : 포즈 감지의 성공을 간주하기 위한 최소 신뢰도 점수 (ex - `-min_pose_detection_confidence 0.4`)
  
  > **default 값 : 0.4**

- `-min_pose_presence_confidence` : 포즈 랜드마크 감지에서 포즈 존재 점수의 최소 신뢰도 점수 (ex - `-min_pose_presence_confidence 0.4`)
  
  > **default 값 : 0.2**

- `-min_tracking_confidence` : 성공적인 포즈 추적을 간주하기 위한 최소 신뢰도 점수 (ex - `-min_tracking_confidence 0.4`)
  
  > **default 값 : 0.2**

**변경하고 싶으면 `setting.py`에서 위에 옵션에 따라 명령어를 수정하면 된다.**
