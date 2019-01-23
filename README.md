## 功能说明

本工程代码的功能：

指定某个目录和指定视频文件格式，搜索该目录下所有的视频文件，对视频文件按指定时间间隔检测六边形红色交通标志STOP(见imgs/stop.jpeg):
![image](https://github.com/ZivenMan/DetectStopSign/blob/master/imgs/stop.jpeg)
并将检测到STOP标志的时间戳(时分秒格式，形如0:12:34.341)存在同级目录下同名的txt文档里。使用python3开发，在64位Ubuntu和64位win10上测试。

STOP标志越大，颜色越鲜艳，标志之外的背景越白，视频对比度越高，亮度适中，则检测效果越好。

如果视频文件xyz.avi已经有对应的检测记录文件xyz.txt，则会生成xyz(1).txt重新记录，以防原来的老记录被覆盖。

如果有多个目录要检测，复制本工程代码，再修改配置文件，再运行一份即可。

## 准备工作
用下述命令安装依赖包：
```
pip3 install -r requirements   (python2和python3共存时)  或   pip3 install -r requirements  (仅有python3时)
```
若提示权限问题，则加参数`--user`。然后，下载本工程代码，cd到工程根目录，则执行下述命令安装darkflow：
```
python3 setup.py build_ext --inplace   (python2和python3共存时)  或  python3 setup.py build_ext --inplace  (仅有python3时)
```

## 修改配置文件
将文件settings-win.ini(Ubuntu为settings-ubuntu.ini)重命名为setting.ini，重新指定相应的搜索目录、相应的要检测的视频文件格式，以及检测间隔时间等参数。

## 运行程序
执行命令运行检测任务：
```
python3 find_sign.py   (python2和python3共存时)  或  python find_sign.py  (仅有python3时)
```

## 备注
本代码基于[darkflow](https://github.com/thtrieu/darkflow)(commit: b2aee00, Mar 25, 2018)
和[YOLO-LITE](https://github.com/reu2018DL/YOLO-LITE)(commit: 5a96f4f, Dec 2, 2018)，并遵循GNU协议。
