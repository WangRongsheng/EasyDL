import cv2
import os
#from tqdm import tqdm
import requests
import base64
import json
from PIL import Image, ImageDraw, ImageFont
ft = ImageFont.truetype("./font/arialuni.ttf",26)
import datetime
import os
import shutil
from datetime import timedelta
from PIL import Image
import time

video_path = r'./test.mp4'  # 分割测试的视频路径
timeF = 2  # 视频帧计数间隔频率
save_path = r'results.mp4'

'''
视频分割
'''
print('开始分帧...')
vc = cv2.VideoCapture(video_path)
n = 1

if vc.isOpened():  # 判断是否正常打开
    rval, frame = vc.read()
else:
    rval = False

i = 0
while rval:  # 循环读取视频帧
    rval, frame = vc.read()
    if (n % timeF == 0):  # 每隔timeF帧进行存储操作
        i += 1
        print('已分帧：{}张'.format(i))
        if os.path.exists('./images') == False:
            os.makedirs('./images')
        #if os.path.exists('./images') == True:
            #os.remove('./images')
        cv2.imwrite(r'./images/{}.jpg'.format(i), frame)  # 存储为图像
    n = n + 1
    cv2.waitKey(1)
vc.release()
print('分帧结束...')

'''
目标检测
'''
print('开始预测...')
ii = 0
for filename in os.listdir(r'./images/'):
    #print(filename)
    a = filename
    ii += 1
    fileName = './images/'+filename
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=Mif41kCWgp8w85RcUkOcz8Df&client_secret=usSif6fATfeyxSi6GNjWRN0fIz0aGpqU'
    response = requests.get(host)
    content = response.json()
    access_token = content["access_token"]
    imgpath = fileName
    image = open(r'{}'.format(imgpath), 'rb').read()
    data = {'image': base64.b64encode(image).decode(),'threshold': 0.2}
    request_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/detection/person-wrs" + "?access_token=" + access_token
    response = requests.post(request_url, data=json.dumps(data))
    content = response.json()
    print(content)
    info = {}
    im=Image.open(imgpath)
    draw = ImageDraw.Draw(im)
    for i in range(len(content['results'])):
        c = []
        x1 = content['results'][i]['location']['left']
        y1 = content['results'][i]['location']['top']
        y2 = content['results'][i]['location']['top']+content['results'][i]['location']['height']
        x2 = content['results'][i]['location']['left']+content['results'][i]['location']['width']
        draw.line([(x1, y1),(x2,y1),(x2,y2),(x1,y2),(x1, y1)],width=8,fill='green')
        draw.text((x1,y1),content['results'][i]['name']+'-'+str(i),font = ft,fill = "red")
        draw.text((x1,y1+20),str(round(content['results'][i]['score'], 3)),font = ft,fill = "red")
        c.append(int(content['results'][i]['location']['height']*int(content['results'][i]['location']['width'])))
        c.append(round(content['results'][i]['score'], 3))
        print(c)
        info[str(content['results'][i]['name']+'-'+str(i))]=c
    if os.path.exists('./results') == False:
        os.makedirs('./results')
    #if os.path.exists('./results') == True:
            #os.remove('./results')
    im.save('./results/'+a)
    print('已预测：{}张'.format(ii))
    time.sleep(5) 
print('预测结束...')

'''
图片大小
'''
im = Image.open('./images/1.jpg')#返回一个Image对象
#print('宽：%d,高：%d'%(im.size[0],im.size[1]))

'''
视频合成
'''
print('视频合成...')
def generate_video(path,size):
    fps = 24                  #帧率
    #size = (640, 480)
    videowriter = cv2.VideoWriter(save_path,cv2.VideoWriter_fourcc('U', '2', '6', '3'), fps, size)
    for i in os.listdir(path):
        img = cv2.imread(path + i)
        videowriter.write(img)
    videowriter.release()

generate_video('./results/',(im.size[0], im.size[1]))  
print('合成结束...')
