# 参考代码（Python3版）


替换访问凭证后，可直接运行:

```python
import hashlib
import time
import requests
import json

# 访问凭证和地址
api_key = "xxxxxxxx"
api_secret = "xxxxxxxxxxxxxxxxxx"
base_url = "https://app.ai-galaxy.cn/openapi/v2"

def get_base_url():
    return base_url

def get_service_url(path):
    if path.startswith("http"):
        return path
    if path.startswith("/"):
        return get_base_url() + path
    return get_base_url() + "/" + path

def md5_v(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def random_str():
    return str(int(time.time() * 1e9))

def gen_md5_sign(params: dict, secret: str):
    # 排序
    keys = sorted(params.keys())
    kvpairs = []
    for k in keys:
        if k == "sign" or k == "secret":
            continue
        v = params[k]
        if v is None or v == "":
            continue
        kvpairs.append(f"{k}={v}")
    if secret:
        kvpairs.append(f"secret={secret}")
    sign_string = "&".join(kvpairs)
    return md5_v(sign_string)

def post_request(url, data: dict, timeout=30):
    try:
        response = requests.post(url, data=data, timeout=timeout)
        response.raise_for_status()
        return response.text, None
    except Exception as e:
        print("Post error:", e)
        return None, e

def get_instance_list(api_key, api_secret, page, page_size, status_type):
    service_url = get_service_url("instance/get_instance_list")
    params = {
        "apikey": api_key,
        "timestamp": str(int(time.time())),
        "nonce": random_str(),
        "page": str(page),
        "page_size": str(page_size),
        "status_type": status_type,
    }
    sign = gen_md5_sign(params, api_secret)
    params["sign"] = sign
    body, err = post_request(service_url, params, 30)
    if err:
        return None, f"PostRequest err: {err}"
    try:
        resp_json = json.loads(body)
    except Exception:
        return None, "响应格式错误"
    if "code" not in resp_json:
        return None, "响应格式错误"
    if str(resp_json["code"]) != "2000":
        return None, resp_json.get("message", "未知错误")
    data = resp_json.get("data")
    if data is None:
        return None, "响应格式错误"
    return data, None

def get_instance_detail(api_key, api_secret, instance_name):
    service_url = get_service_url("instance/get_instance_detail")
    params = {
        "apikey": api_key,
        "timestamp": str(int(time.time())),
        "nonce": random_str(),
        "instance_name": instance_name,
    }
    sign = gen_md5_sign(params, api_secret)
    params["sign"] = sign
    body, err = post_request(service_url, params, 30)
    if err:
        return None, f"PostRequest err: {err}"
    try:
        resp_json = json.loads(body)
    except Exception:
        return None, "响应格式错误"
    if "code" not in resp_json:
        return None, "响应格式错误"
    if str(resp_json["code"]) != "2000":
        return None, resp_json.get("message", "未知错误")
    data = resp_json.get("data")
    if data is None:
        return None, "响应格式错误"
    return data, None

if __name__ == "__main__":
    # 获取实例列表
    instance_list, err = get_instance_list(api_key, api_secret, 1, 10, "statusAll")
    if err:
        print("获取实例列表失败", err)
    else:
        print("实例列表", json.dumps(instance_list, ensure_ascii=False, indent=2))

    # 获取实例信息
    instance_name = "18621629564_lyg115_c0366bb0fcca448da3588a20c900170a_u1"
    detail, err = get_instance_detail(api_key, api_secret, instance_name)
    if err:
        print("获取实例信息失败", err)
    else:
        print("实例信息", json.dumps(detail, ensure_ascii=False, indent=2))
```

如果需要其他编程语言版本，请参考上述逻辑自行编写。
