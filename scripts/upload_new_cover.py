#!/usr/bin/env python3
"""Upload cover to WeChat and return media_id."""

import json
import os
import urllib.request

WECHAT_APPID = "wx2003a12d1b3d867f"
WECHAT_SECRET = "32dbd01b12d99e18ed4a997e9145f922"
COVER_PATH = r"C:\Users\jt\WorkBuddy\Claw\_cover_day172.png"

def get_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WECHAT_APPID}&secret={WECHAT_SECRET}"
    return json.loads(urllib.request.urlopen(url).read()).get("access_token")

def upload_cover(token, path):
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    with open(path, 'rb') as f:
        image_data = f.read()
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="media"; filename="cover.png"\r\n'
        f'Content-Type: image/png\r\n\r\n'
    ).encode('utf-8') + image_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')
    
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
    req = urllib.request.Request(url, data=body)
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    resp = json.loads(urllib.request.urlopen(req).read())
    return resp

def delete_old_draft(token, media_id):
    """Delete old draft if possible."""
    url = f"https://api.weixin.qq.com/cgi-bin/draft/delete?access_token={token}"
    payload = json.dumps({"media_id": media_id}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())

# Old draft media_id
OLD_MEDIA_ID = "CPphwVaTdyJY6D79IuCazR3Feo95yM2mi-xXDC3t9fHbnnWrtFOX4Hve8q9smEUO"

token = get_token()
print(f"TOKEN: {'OK' if token else 'FAIL'}")

# Delete old draft
result = delete_old_draft(token, OLD_MEDIA_ID)
print(f"Delete old draft: {result}")

# Upload new cover
result = upload_cover(token, COVER_PATH)
print(f"New cover upload: {result}")
if "media_id" in result:
    print(f"MEDIA_ID={result['media_id']}")
