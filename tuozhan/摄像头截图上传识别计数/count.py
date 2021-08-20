import cv2
import sys
import requests
import base64
import json
import time
import datetime


##############################################################
#  这个AI计数应用可以用于各种物体的计数，自己训练什么模型，就数什么
#  也可以增加不同种类物体，分别计数
#
#  第一步 在EasyDL (https://ai.baidu.com/easydl/) 中创建一个图像的“物体检测”数据集，进行标注，训练选公有云部署，发布
#  第二步 在服务详情里点立即使用，创建新应用，得到API Key和Secret Key
#  第三步 将API Key、Secret Key和EasyDL的云服务URL地址填写在程序里
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


success = False
if sys.platform == "win32": #Windows下获取摄像头
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)    #0代表第一个，如果有多个摄像头，可以改成1或其他
    success,camera_frame = cap.read() 

elif sys.platform == "linux": #Linux下获取摄像头
    cap = cv2.VideoCapture('/dev/video0') #0代表第一个，如果有多个摄像头，可以改成1或其他
    success,camera_frame = cap.read() 

elif sys.platform == "darwin": #Mac下获取摄像头
    cap = cv2.VideoCapture(0) #0代表第一个，如果有多个摄像头，可以改成1或其他
    success,camera_frame = cap.read() 

if success : #如果成功获取图像
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  #设定拍摄图像宽度
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  #设定拍摄图像高度
    #success,camera_frame = cap.read() 
    print(camera_frame.shape)  #输出拍到图片的高、宽、颜色字节数


    
    Token = getCouldToken(API_Key,Secret_Key)  #先要获取Token，才能访问云服务

    if Token != "":
        detection_time=time.time() - 10
        objects = []
        cv2.namedWindow("Camera",0);
        cv2.resizeWindow("Camera", 1280, 960);  #设置opencv窗口尺寸,需与拍摄图像长宽比例一致，避免显示变形
        while success:
            success,camera_frame = cap.read()       # 读摄像头
            
            pressedkey = cv2.waitKey(1)
            if pressedkey == ord('q')or pressedkey == 27:  # 按q或ESC退出
                break
            elif pressedkey == ord(' ')  :  #按空格识别


                #可以进阶自己将这里改成多线程的，就不会在识别的时候画面停顿了
                objects=EasyDLObjectDetect(Token,camera_frame,EasyDL_Service_URL,0.3)  #threshold是置信度的阈值，可以在0-1之间调节
                detection_time=time.time()
                timeStr = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                cv2.imwrite(timeStr + '.jpg', camera_frame) #保存图片


            if time.time() - detection_time < 10: #距离上一次识别在10秒以内
                Names_dict=dict()
                for Obj in objects:
                    #为每一种识别到的物体分别进行计数统计
                    if Obj['name'] in Names_dict:
                        Names_dict[Obj['name']] +=1
                    else:
                        Names_dict[Obj['name']]=1

                    #绘制识别框
                    cv2.rectangle(camera_frame,(Obj['location']['left'],Obj['location']['top']),(Obj['location']['left']+Obj['location']['width'],Obj['location']['top']+Obj['location']['height']), (255,127,0), 2, 1)
                    #绘制识别名称和置信度
                    cv2.putText(camera_frame, ("%s %.0f%%" % (Obj['name'],Obj['score']*100)) , (Obj['location']['left'],Obj['location']['top']),cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 200, 0), 1)
                #绘制总数
                cv2.putText(camera_frame, str(len(objects)) , (30,100),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 8)

                #绘制分类统计数量
                S=""
                for Name in Names_dict:
                    S+= Name +":" +str(Names_dict[Name]) + '     '
                cv2.putText(camera_frame, S , (10,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 127, 127), 2)
            #显示图像到窗口
            cv2.imshow("Camera", camera_frame)
        #关闭opencv窗口
        cv2.destroyAllWindows()
    #释放相机
    cap.release()      