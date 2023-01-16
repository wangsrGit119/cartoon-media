FROM python:3.7-slim
MAINTAINER suke119

ENV TZ=Asia/Shanghai
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY ./server /app
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg
RUN /usr/local/bin/python -m pip install --upgrade pip -i https://pypi.douban.com/simple
RUN pip uninstall -y protobuf
RUN pip install protobuf==3.19.0 -i https://pypi.douban.com/simple      
RUN pip install -r requirements.txt -i https://pypi.douban.com/simple 
CMD uvicorn main:app --reload --port 18080 --host 0.0.0.0


