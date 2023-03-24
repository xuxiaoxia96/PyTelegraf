from flask import Flask,request,render_template,jsonify
from flask_uploads import UploadSet, configure_uploads, IMAGES
import requests, os
import subprocess
# from werkzeug.utils import secure_filename


app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB
 
@app.route('/')
def index():
    return 'file server'
 
 # 下载文件
@app.route('/fileinfo',methods=['GET', 'POST'])
def test():
    path = request.values.get('path')
    print(path)
    
    # with open(path, 'r', newline='') as f:
    #     content = f.read()
    #     print(content)
    
    data = {'file': open(path, 'rb')}
    r = requests.post('http://9.135.93.3:1234/recv_log', files=data)        
    return r.text

# 执行脚本
@app.route('/exe_script', methods=['GET', 'POST'])
def exe():
    cmd = request.values.get('cmd')
    print(cmd)
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        print(output)
        result = "success"
    except:
        result = "fail"
            
    # TODO: 执行命令    
    return jsonify({"err_code": result})


UPLOAD_FOLDER = '/data/home/user00/tables/'
ALLOWED_EXTENSIONS = ['lua']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# 上传文件
@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = request.form.get('filename')

        print(filename)
        print(allowed_file(file.filename))
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            filename = file.filename
            print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify({"err_code": "upload success"})

        else:
            return jsonify({"err_code": "fail"})
 
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5678,debug=True)