# coding:utf-8
 
from flask import Flask, render_template, request, redirect, url_for, make_response,jsonify
from werkzeug.utils import secure_filename
import os
import cv2
import time
import sys
import os
import json
import requests
import base64
import cv2
 
from datetime import timedelta
 
#设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
 
app = Flask(__name__)
# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds=1)
 
 
# @app.route('/upload', methods=['POST', 'GET'])
@app.route('/upload', methods=['POST', 'GET'])  # 添加路由
def upload():
    if request.method == 'POST':
        f = request.files['file']
 
        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001, "msg": "请检查上传的图片类型，仅限于png、PNG、jpg、JPG、bmp"})
 
        user_input = request.form.get("name")
 
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
 
        upload_path = os.path.join(basepath, 'static/images', secure_filename(f.filename))  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
        # upload_path = os.path.join(basepath, 'static/images','test.jpg')  #注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)
 
        # 使用Opencv转换一下图片格式和名称
        img = cv2.imread(upload_path)
        cv2.imwrite(os.path.join(basepath, 'static/images', 'test.jpg'), img)
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=AK&client_secret=SK'
        response = requests.get(host)
        content = response.json()
        access_token = content["access_token"]
        imgpath = upload_path
        image = open(r'{}'.format(imgpath), 'rb').read()
        data = {'image': base64.b64encode(image).decode()}
        request_url = "https://aip.baidubce.com/rpc/2.0/ai_custom_pro/v1/classification/rmb-wrs" + "?access_token=" + access_token
        response = requests.post(request_url, data=json.dumps(data))
        content = response.json()
        content_result = content['results']
        best_content_result = content['results'][0]['name']
        user_input=content_result
        #return content_result
        return render_template('upload_ok.html',userinput=user_input,bestuserinput=best_content_result,val1=time.time())
 
    return render_template('upload.html')
 
 
if __name__ == '__main__':
    # app.debug = True
    app.run(host='127.0.0.1', port=8987, debug=True)
    #app.run()