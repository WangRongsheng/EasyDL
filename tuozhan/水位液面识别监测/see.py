import cv2
import sys
import requests
import base64
import json
import time
import datetime



##############################################################
#  利用EasyDL进行视觉识别，通过树莓派实现液体液位高度测量。
#  不仅仅可以测量单一液体，也可以轻松实现油水混合等，多种分层液体的分辨测量，异常报警等
#
#  第一步 在EasyDL (https://ai.baidu.com/easydl/) 中创建一个数据集，进行标注，训练选公有云部署，发布
#  第二步 在服务详情里点立即使用，创建新应用，得到API Key和Secret Key
#  第三步 在电脑上建立一个py文件，复制以下代码，并将API Key、Secret Key和EasyDL的云服务URL地址填写在程序里。运行后按空格识别
#  第四步 在树莓派上建立一个py文件，复制以下代码，运行后GPIO18拉低识别
#  第五步 可选，在EasyDL中，训练选软硬一体部署。并将模型安装在Jetson或者EdgeBoard上，使用EasyDLObjectDetectEdge通过边缘计算板识别
#
#  
##############################################################
API_Key = "【替换为你自己的API Key】"
Secret_Key = "【替换为你自己的Secret Key】"
EasyDL_Service_URL = "【替换为你自己的EasyDL的云服务URL】"




#图像转base64码
def cv2_to_base64(image):
    data = cv2.imencode('.jpg', image,[cv2.IMWRITE_JPEG_QUALITY,40])[1]
    return base64.b64encode(data.tobytes()).decode('utf8')

def getCouldToken(client_id,client_secret):
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + client_id + '&client_secret=' + client_secret
    response = requests.get(host)
    if response:
        dict = response.json()
        if  ("access_token" in dict) :
            token = dict.get('access_token')
            print("Got Token:" + token)
            return token 
        else:
            print("Token is Nothing")
            return ""
    else:
        print("Token Error")
    return ""


def EasyDLObjectDetect(token,image,URL,threshold=0.5):
    request_url = URL + "?access_token=" + token
    image_base64 = cv2_to_base64(image) #将numpy图像转换成base64字符串
    params = {"image": image_base64,"threshold":threshold}
    headers = {'content-type': 'application/json'}

    response = requests.post(url=request_url, data=json.dumps(params), headers=headers)

    if response:
        print(response.text)
        jsonData = response.json()

        results = jsonData.get('results')
        print("Find %d Objects" % (len(results)))
        if len(results) > 0:
            return results
        elif ("error_msg" in jsonData):
            print("ERROR:%s" % jsonData.get('error_msg'))
    return []

def EasyDLObjectDetectEdge(self,image,URL,threshold=0.5):
    imgdata = cv2.imencode('.jpg', image)[1]
    response = requests.post(URL,params={'threshold': threshold}, data=imgdata.tobytes()).json()
    if response:
        print(response.text)
        jsonData = response.json()

        results = jsonData.get('results')
        print("Find %d Objects" % (len(results)))
        if len(results) > 0:
            return results
        elif ("error_msg" in jsonData):
            print("ERROR:%s" % jsonData.get('error_msg'))
    return []

success = False
GPIO = None
if sys.platform == "linux": #Linux下获取摄像头
    import RPi.GPIO as GPIO #树莓派
    #初始化IO口
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(20, GPIO.OUT)
    GPIO.output(20, GPIO.HIGH)

    GPIO.setup(21, GPIO.OUT)
    GPIO.output(21, GPIO.HIGH)

    GPIO.setup(26, GPIO.OUT)
    GPIO.output(26, GPIO.HIGH)

    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP) #输入触发

    cap = cv2.VideoCapture('/dev/video0') #0代表第一个，如果有多个摄像头，可以改成1或其他
    success,camera_frame = cap.read() 

elif sys.platform == "win32": 
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)    #0代表第一个，如果有多个摄像头，可以改成1或其他
    success,camera_frame = cap.read() 


elif sys.platform == "darwin": #Mac下获取摄像头
    cap = cv2.VideoCapture(0) #0代表第一个，如果有多个摄像头，可以改成1或其他
    success,camera_frame = cap.read() 


if success : #如果成功获取图像
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) #设定拍摄图像宽度
                #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) #设定拍摄图像高度
    success,camera_frame = cap.read() 
    print(camera_frame.shape)  #输出拍到图片的高、宽、颜色字节数
    image_height = camera_frame.shape[0] #得到图像的高度

    Token = getCouldToken(API_Key,Secret_Key)  #先要获取Token，才能访问云服务


    detection_time = time.time() - 10
    liquid_surface = 0
    objects = []

    if sys.platform != "linux":
        cv2.namedWindow("Camera",0)
        cv2.resizeWindow("Camera", 800, 600)  #设置opencv窗口尺寸,需与拍摄图像长宽比例一致，避免显示变形
    autoDetection = False #自动持续识别

    while success:
        success,camera_frame = cap.read()       # 读摄像头

        if sys.platform == "linux": #在树莓派ZERO上直接识别不进行图像显示，无键盘交互
            if GPIO.input(18) == GPIO.LOW :  #拉低IO18，进行识别
                objects = EasyDLObjectDetect(Token,camera_frame,EasyDL_Service_URL,threshold =0.6) #threshold是置信度的阈值，可以在0-1之间调节
                detection_time = time.time()
                liquid_surface = -1
                GPIO.output(20, GPIO.HIGH)
                GPIO.output(21, GPIO.HIGH)
                GPIO.output(26, GPIO.HIGH)

                for Obj in objects: 
                    if (Obj['name'] == "liquid_surface"):
                        centerY = Obj['location']['top'] + Obj['location']['height'] / 2
                        liquid_surface =1- centerY / image_height
                        print("\033[0;33;1m%.0f%%\033[0m" % (liquid_surface* 100))
                        if liquid_surface > 0.66:  #根据液面高度不同，点亮不同的灯
                            GPIO.output(21, GPIO.LOW)
                        elif liquid_surface > 0.33:
                            GPIO.output(20, GPIO.LOW)
                        else:
                            GPIO.output(26, GPIO.LOW)
                        break
            if time.time() - detection_time > 3:
                #距离上次识别超过3秒自动关闭继电器
                GPIO.output(20, GPIO.HIGH)
                GPIO.output(21, GPIO.HIGH)
                GPIO.output(26, GPIO.HIGH)
            time.sleep(10)  #识别间隔时间，可以设定一分钟或者十分钟监控识别一次
        else:
            pressedkey = cv2.waitKey(1)
            if pressedkey == ord('q') or pressedkey == 27:  # 按q或ESC退出
                break

            elif pressedkey == ord('s'):  #按s保存图片
                timeStr = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                cv2.imwrite(timeStr + '.jpg', camera_frame) #保存图片
                print("Image Saved")
            elif pressedkey == ord('t'):  #按t,开启或关闭自动识别模式
                autoDetection = not autoDetection

            elif pressedkey == ord(' ') or autoDetection  :  #按空格识别
                if Token != "":
                    #可以进阶自己将这里改成多线程的，就不会在识别的时候画面停顿了
                    objects = EasyDLObjectDetect(Token,camera_frame,EasyDL_Service_URL,threshold =0.5) #threshold是置信度的阈值，可以在0-1之间调节
                    detection_time = time.time()
                    liquid_surface = -1

                    for Obj in objects:  
                        if (Obj['name'] == "liquid_surface"):
                            centerY = Obj['location']['top'] + Obj['location']['height'] / 2
                            liquid_surface =1- centerY / image_height
                            break
                else:
                    print('未获取到Token')

            if time.time() - detection_time < 3: #距离上一次识别在3秒以内
                for Obj in objects:
                    #绘制识别框
                    if (Obj['name'] == "liquid_surface"):
                        cv2.rectangle(camera_frame,(Obj['location']['left'],Obj['location']['top']),(Obj['location']['left'] + Obj['location']['width'],Obj['location']['top'] + Obj['location']['height']), (0,255,0), 2, 1)

                    #绘制识别名称和置信度
                    cv2.putText(camera_frame, ("%.0f%%" % (Obj['score'] * 100)) , (Obj['location']['left'],Obj['location']['top']),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 20, 0), 1)
                #绘制液面高度百分比
                if liquid_surface > -1:
                    cv2.putText(camera_frame, "%.0f%%" % (liquid_surface* 100) , (30,100),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 8)


            #显示图像到窗口
            cv2.imshow("Camera", camera_frame)
    #关闭opencv窗口
    cv2.destroyAllWindows()
    

    #释放相机
    cap.release()  
else:
    print('未打开相机')