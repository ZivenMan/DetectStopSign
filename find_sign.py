#-*- coding: utf-8 -*-

import json

import os

import numpy as np

from darkflow.net.build import TFNet
import cv2

import  my_configparser

options = {"model": "cfg/coco-yolo-lite-trial6_653550.cfg", "load": "weights/coco-yolo-lite-trial6_653550.weights", "threshold": 0.3}

print ("Start to Load Detect Algorithm Models.........")

tfnet = TFNet(options)


#要检测的目标目录
target_dir = ''

#视频文件格式
video_formats = ['.avi', '.mp4']

#每隔多少ms检测一次
time_gap = 1000.0

show_video_frame = False


def  read_settings_file():
    global video_formats, target_dir, time_gap, show_video_frame
    settings_file = os.path.join(os.path.dirname(__file__), 'settings.ini')

    if not  os.path.exists(settings_file):
        print ("Not Exist settings.ini File! Program Exits.")
        exit(1)

    cfg = my_configparser.MyConfigParser()
    cfg.read(settings_file)
    print ("Detect Stop Sign Settings:")
    for section in cfg.sections():
        print (section, ":\n", cfg.items(section))

    target_dir = cfg.get('detect_scope', 'target_dir')

    video_extensions = cfg.get('detect_scope', 'target_video_ext')
    extensions = video_extensions.split(',')
    for i in range(len(extensions)):
        format = '.'+extensions[i]
        if format not in video_formats:
            video_formats.append(format)

    gap = cfg.get('detect_params', 'time_gap')
    time_gap = float(gap) * 1000.0

    show = cfg.getint('detect_params', 'show_video_frame')
    show_video_frame = False if 0 == show else True





#获取指定目录下（包括子目录）所有文件的绝对路径和文件名(不包括扩展名)
def  get_file_names(dir):
    full_file_paths = []
    file_path_shot_names = [] # full_file_paths 去掉扩展名
    '''
    获得目录(包括子目录)下所有文件的绝对路径
    root_dir_path: 当前根路径(字符串)
    subdir_names: 当前根路径下的所有子目录名(列表)
    file_names: 当前根路径下的所有非目录文件名(列表)
    注意，在外层for循环中，这3个值都是变化的
    '''
    for root_dir_path, subdir_names, file_names in os.walk(dir):
        for file_name in file_names:
            full_path = os.path.join(root_dir_path, file_name)


            ############################################################################
            #方式一
            shot_name, extension = os.path.splitext(file_name)

            # 方式二 （演示 os.path.split()的用法）
            # file_path, full_name = os.path.split(full_path)
            # shot_name, extension = os.path.splitext(full_name)
            ############################################################################

            if  extension in video_formats:
                full_file_paths.append(full_path)
                file_path_shot_names.append(os.path.join(root_dir_path, shot_name))


    return full_file_paths, file_path_shot_names

def  detect_sign_camera():
    camNo = 0
    cap = cv2.VideoCapture(camNo)
    if False == cap.isOpened():
        print ("Fail to Open Camera: ", camNo)
        exit(3)

    run_flag = True
    while(run_flag):
        ret, frame = cap.read()
        if False == ret:
            print("Fail to Get Frame.")
            continue

        result = tfnet.return_predict(frame)

        for i in range(len(result)):
            result_json = result[i]

            print("type: ", type(result_json))

            label = result_json['label']
            confidence = result_json['confidence']
            topleft_x = result_json['topleft']['x']
            topleft_y = result_json['topleft']['y']
            bottomright_x = result_json['bottomright']['x']
            bottomright_y = result_json['bottomright']['y']
            print(label)
            print(confidence)
            print("tl_x: ", topleft_x, ", tl_y: ", topleft_y)
            print("br_x: ", bottomright_x, ", br_y: ", bottomright_y)

            if 'stop sign' == label:

                #画检测结果框
                cv2.rectangle(frame, (topleft_x, topleft_y), (bottomright_x, bottomright_y), (0, 255, 0), 2)

                # 检测信息背景框
                topleft_y_background = max(0, topleft_y - 30)
                cv2.rectangle(frame, (topleft_x, topleft_y_background), (bottomright_x, topleft_y), (0, 255, 0), -1)

                text_info = label + ", " + str(confidence)
                topleft_y_background = max(0, topleft_y - 5)
                cv2.putText(frame, text_info, (topleft_x, topleft_y_background), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 1)


        cv2.imshow("Frame", frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            run_flag = False
            print("Main Loop Break.")


#从单张图里检测stop sign，有的话返回True，否则返回False
def  detect_sign_image(image):
    result = tfnet.return_predict(frame)

    for i in range(len(result)):
        result_json = result[i]
        label = result_json['label']
        if 'stop sign' == label:
            return True

    return False



if  __name__ == '__main__':


    read_settings_file()

    full_file_paths, file_path_shot_names = get_file_names(target_dir)

    msg = "\nReady to Process %d File(s)." % (len(full_file_paths))
    print (msg)

    file_num = len(full_file_paths)
    for i in range(file_num):
        cap = None
        try:
            cap = cv2.VideoCapture(full_file_paths[i])
        except  Exception as e:
            msg = 'Fail to Open Video File: %s. Error Msg: %s.' % (full_file_paths[i], str(e))
            print(msg)
            continue

        if not cap.isOpened():
            continue

        print("\nStart to Process Video File: ", full_file_paths[i], ".")

        record_txt_file = file_path_shot_names[i] + '.txt'
        if  os.path.exists(record_txt_file):#避免覆盖老的txt记录文件，改为 xxx(1).txt
            record_txt_file = file_path_shot_names[i] + '(1).txt'

        frame_num = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        if frame_num <= 1.0:#图片文件跳过
            continue

        check_point = 1 #要检查的时间点： check_point * time_gap
        time_stamps = []

        frame_time = 1000.0 / cap.get(cv2.CAP_PROP_FPS) #一帧的时间，单位ms

        frame_count = 0
        while (1):
            if frame_count >= int(frame_num):
                break

            if frame_count * frame_time < check_point * time_gap:
                frame_count += 1
            else:
                check_point += 1

                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)#只读指定帧号的视频帧，以节省时间
                ret, frame = cap.read()
                processed_percent = frame_count / frame_num * 100
                # "%04.1f"，4表示总共4个输出宽度（包括整数位小数点和小数位），不够4位用0填充
                msg = "%05.2f%% of %d th File Processed. Have %d / %d File(s) Done." % (processed_percent, i+1, i, file_num)
                print(msg)
                if ret:
                    cur_time_stamp = cap.get(cv2.CAP_PROP_POS_MSEC)
                    if detect_sign_image(frame):
                        m, s = divmod(cur_time_stamp / 1000.0, 60)
                        h, m = divmod(m, 60)
                        msg = "\nFind Stop Sign at: %d:%02d:%06.3f in %d th File.\n" % (h, m, s, i)#h, m, s对应时:分:秒
                        print(msg)
                        stamp = "%d:%02d:%06.3f" % (h, m, s)#时:分:秒
                        time_stamps.append(stamp)

                    if  show_video_frame:
                        cv2.imshow("DetectedFrame", frame)
                        cv2.waitKey(1)

        cap.release()
        cv2.destroyAllWindows()

        file = open(record_txt_file, 'w+')
        file.writelines('\n'.join(time_stamps))#按行并换行存储list
        file.close()

        msg = "\nFinish to Process File: %s. Have %d / %d File(s) Done.\n" % (full_file_paths[i], i+1, file_num)
        print (msg)




