# cartoon-media

> image or video to cartoon

[example](example.png)

> base repo [cartoonize](https://github.com/experience-ml/cartoonize)

## get starter with docker 

> build image

```sh
docker build -t cartoon-media:1.0 .
```

> start container

```sh
docker run -d --name cartoon-1.0 -p 18080:18080 cartoon-media:1.0
```

> visit: http://localhost:18080/front/

## get start with local

```cmd
cd server
pip uninstall -y protobuf
pip install protobuf==3.19.0 -i https://pypi.douban.com/simple      
pip install -r requirements.txt -i https://pypi.douban.com/simple 
uvicorn main:app --reload --port 18080 --host 0.0.0.0

```
> visit: http://localhost:18080/front/




