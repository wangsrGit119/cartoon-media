
# -*- coding: utf-8 -*-
import os,io,base64,sys,platform
import cv2
import numpy as np
import uuid
from fastapi import FastAPI,File, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import numpy as np


import skvideo.io


logger.add('log/face.log', rotation="5MB")
logger.add("log/face.log", rotation="2h")

from cartoonize import WB_Cartoonize

model_path = './saved_models'
gpu = len(sys.argv) < 2 or sys.argv[1] != '--cpu'
wb_cartoonizer = WB_Cartoonize(model_path, gpu)


app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/front", StaticFiles(directory="dist",html=True), name="static")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

UPLOAD_FOLDER_VIDEOS = './uploader'




def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.post("/image-upload/")
async def image_upload(file: UploadFile = File(...)):
    if file and allowed_file(file.filename):
        logger.info("文件信息 " +file.filename)
        return {"status":200,"base64": await actiontarnsfer(file)}
    else:
        return {"status":400,"error": "非法文件"}
    

class Item(BaseModel):
    name: str
    description: Optional[str] = None


@app.post("/commit-record/")
async def create_item(item: Item):
    logger.info("提价数据打印 %s",item)
    return item



async def img2cv2Img(img):
    data = await img.read()
    try:
        return cv2.imdecode(np.fromstring(data, np.uint8),cv2.IMREAD_UNCHANGED)
    except Exception as e:
        logger.info("CV图片转换异常 " +str(e))
        raise e

def cv2_base64(image):
    base64_str = cv2.imencode('.jpg',image)[1].tostring()
    base64_str = base64.b64encode(base64_str)
    return base64_str 

async def actiontarnsfer(image_file):
    image = await img2cv2Img(image_file)
    try:
        cartoon_image = wb_cartoonizer.infer(image)
        return cv2_base64(cartoon_image)
    except Exception as e:
        logger.info("卡通化异常 " +str(e))
        raise e
    



def videoactiontransfer(original_video_path):
    ## Fetch Metadata and set frame rate
    file_metadata = skvideo.io.ffprobe(original_video_path)
    original_frame_rate = None
    if 'video' in file_metadata:
        if '@r_frame_rate' in file_metadata['video']:
            original_frame_rate = file_metadata['video']['@r_frame_rate']
    filename = str(uuid.uuid4()) + ".mp4"
    output_frame_rate = '24/1'    
    modified_video_path = os.path.join(UPLOAD_FOLDER_VIDEOS, filename.split(".")[0] + "_modified.mp4")

    output_frame_rate_number = int(output_frame_rate.split('/')[0])

    #change the size if you want higher resolution :
    ############################
    # Recommnded width_resize  #
    ############################
    #width_resize = 1920 for 1080p: 1920x1080.
    #width_resize = 1280 for 720p: 1280x720.
    #width_resize = 854 for 480p: 854x480.
    #width_resize = 640 for 360p: 640x360.
    #width_resize = 426 for 240p: 426x240.
    width_resize=720
    # 是否截断视频 false 则转换整个视频
    trim_video = False
    # 设置true表示不想变更原有视频的尺寸
    original_resolution = True
    ## 下面命令遇到报错 非法参数 去掉文件夹两边单引号
    print("开始转换",output_frame_rate_number)

    # Slice, Resize and Convert Video as per settings
    if trim_video:
        #限制转换长度 秒
        time_limit = 14 
        if original_resolution:
            os.system("ffmpeg -hide_banner -loglevel warning -ss 0 -i {} -t {} -filter:v scale=-1:-2 -r {} -c:a copy {}".format(os.path.abspath(original_video_path), time_limit, output_frame_rate_number, os.path.abspath(modified_video_path)))
        else:
            os.system("ffmpeg -hide_banner -loglevel warning -ss 0 -i {} -t {} -filter:v scale={}:-2 -r {} -c:a copy {}".format(os.path.abspath(original_video_path), time_limit, width_resize, output_frame_rate_number, os.path.abspath(modified_video_path)))
    else:
        if original_resolution:
            os.system("ffmpeg -hide_banner -loglevel warning -ss 0 -i {} -filter:v scale=-1:-2 -r {} -c:a copy {}".format(os.path.abspath(original_video_path), output_frame_rate_number, os.path.abspath(modified_video_path)))
        else:
            os.system("ffmpeg -hide_banner -loglevel warning -ss 0 -i {} -filter:v scale={}:-2 -r {} -c:a copy {}".format(os.path.abspath(original_video_path), width_resize, output_frame_rate_number, os.path.abspath(modified_video_path)))

    audio_file_path = os.path.join(UPLOAD_FOLDER_VIDEOS, filename.split(".")[0] + "_audio_modified.mp4")
    os.system("ffmpeg -hide_banner -loglevel warning -i {} -map 0:1 -vn -acodec copy -strict -2  {}".format(os.path.abspath(modified_video_path), os.path.abspath(audio_file_path)))

    cartoon_video_path = wb_cartoonizer.process_video(modified_video_path, output_frame_rate)
    
    ## Add audio to the cartoonized video
    final_cartoon_video_path = os.path.join(UPLOAD_FOLDER_VIDEOS, filename.split(".")[0] + "_cartoon_audio.mp4")
    print("音频路径  ",audio_file_path)
    cmd = "ffmpeg -hide_banner -loglevel warning -i {} -i {} -codec copy -shortest {}".format(os.path.abspath(cartoon_video_path), os.path.abspath(audio_file_path), os.path.abspath(final_cartoon_video_path))
    print("添加音频",cmd)
    os.system(cmd)

    # Delete the videos from local disk
    sysstr = platform.system()
    if(sysstr =="Windows"):
        os.system("del {} {} {} {}".format(original_video_path, modified_video_path, audio_file_path, cartoon_video_path))
    else:
        os.system("rm {} {} {} {}".format(original_video_path, modified_video_path, audio_file_path, cartoon_video_path))



if __name__ == '__main__':
    gpu = len(sys.argv) < 2 or sys.argv[1] != '--cpu'

    # file_path = './videos/WeChat_20221204104403.mp4'
    im = cv2.imread('./images/10001.jpg')
    im2 = cv2.imread('./images/alarm.png')
    print(im.shape)
    print(im2.shape)

    # video transfer
    # videoactiontransfer(file_path)
    # print("开始转换，转换结果文件见：uploader")


    
    # import uvicorn
    # uvicorn.run(app='main:app',host='0.0.0.0',port=18080,reload=True)
    # 启动失败则单独安装 pip install tensorflow==2.1.0 -i https://pypi.douban.com/simple
    # uvicorn main:app --reload --port 18080 # fastAPI 启动
    

    