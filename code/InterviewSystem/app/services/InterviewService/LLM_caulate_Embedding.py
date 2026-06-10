import requests
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json
import numpy as np

#鉴权信息
APPID = "f53357ff"
APIKEY = "4c3b3f50f26078081ac259ed196346d3"
APISECRET = "NTU3ODljZTg1ODdlNjg2ODgyOWNjM2Iz"
HOST = 'https://emb-cn-huabei-1.xf-yun.com/'


#鉴权辅助
class Url:
    def __init__(self, host, path, schema):
        self.host = host
        self.path = path
        self.schema = schema


def parse_url(request_url):
    stidx = request_url.index("://")
    host = request_url[stidx + 3:]
    schema = request_url[:stidx + 3]
    edidx = host.index("/")
    path = host[edidx:]
    host = host[:edidx]
    return Url(host, path, schema)


def assemble_ws_auth_url(request_url, method="POST", api_key="", api_secret=""):
    u = parse_url(request_url)
    host = u.host
    path = u.path
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    signature_origin = f"host: {host}\ndate: {date}\n{method} {path} HTTP/1.1"
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'), digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(signature_sha).decode()
    authorization_origin = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    authorization = base64.b64encode(authorization_origin.encode()).decode()
    params = {
        "host": host,
        "date": date,
        "authorization": authorization
    }
    return request_url + "?" + urlencode(params),date


#构造请求体
def build_body(appid, text, domain):
    data = {
        "messages": [{"content": text, "role": "user"}]
    }
    body = {
        "header": {
            "app_id": appid,
            "uid": "user001",
            "status": 3
        },
        "parameter": {
            "emb": {
                "domain": domain,
                "feature": {
                    "encoding": "utf8"
                }
            }
        },
        "payload": {
            "messages": {
                "text": base64.b64encode(json.dumps(data, ensure_ascii=False).encode('utf-8')).decode()
            }
        }
    }
    return body


#解析响应
def parse_response(response_text):
    data = json.loads(response_text)
    if data['header']['code'] != 0:
        raise Exception(f"请求错误: {data['header']['code']}, {data['header']['message']}")
    text_base = data["payload"]["feature"]["text"]
    text_bytes = base64.b64decode(text_base)
    dt = np.dtype(np.float32).newbyteorder("<")
    return np.frombuffer(text_bytes, dtype=dt).tolist()


#主函数封装
def get_embedding(text: str, domain: str = "query") -> list:
    url,date = assemble_ws_auth_url(HOST, method="POST", api_key=APIKEY, api_secret=APISECRET)
    body = build_body(APPID, text, domain)
    headers = {
        "Content-Type": "application/json",
        "Date": date
    }
    response = requests.post(url, json=body, headers=headers)
    if response.status_code != 200:
        raise Exception(f"HTTP错误: {response.status_code}, {response.text}")
    return parse_response(response.text)
