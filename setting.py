import argparse
import os

def option_setting_script(option): # 폴더 위치 이동
    if option == "body": # body일 경우
        os.chdir("./body")
        return

    # face일 경우
    os.chdir(f"./face/{option}")

def run_body_script(script_name, data_path_folder, file_list): #body script 실행
    for file in file_list:
        command = f"python {script_name} -clip_name {data_path_folder + file}"
        os.system(command)

def run_face_script(script_name, data_path_folder, file_list):
    for file in file_list:
        command = f"python {script_name} -clip_name {data_path_folder + file}"
        os.system(command)


if __name__ == "__main__":
    # 커맨드 라인으로 인자 받기
    parser = argparse.ArgumentParser()
    parser.add_argument('-group_name', help=' : Please set the group name')
    parser.add_argument('-option', help=' : Please set the option(body, face_emotion, face_landmark, face_rotation)')
    args = parser.parse_args()

    # 기본 변수 (그룹, 옵션)
    group = args.group_name
    option = args.option

    #옵션에 따른 폴더 이동
    option_setting_script(option)
    print(os.getcwd())

    # 데이터 폴더 설정 및 파일 읽어오기
    data_path_folder = "D:/MultiModal/Data/Data_PreProcessing/Body_Cutting/" + group + "/" if option == "body" else "D:/MultiModal/Data/Data_PreProcessing/Face/" + group + "/"
    file_list = os.listdir(data_path_folder)
    print(file_list)

    # 옵션에 따른 스크립트 설정 후 실행
    script_name = "pose_landmarker.py" if option == "body" else ("face_emotion_classifier.py" if option == "face_emotion" else ("face_landmark.py" if option == "face_landmark" else "face_rotation.py"))

    if option == "body":
        run_body_script(script_name, data_path_folder, file_list) # 해당 파일 내 있는 만큼 돌리기
    else:
        run_face_script(script_name, data_path_folder, file_list) # 해당 파일 내 있는 만큼 돌리기
