import json
import os
import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

APP_ID = os.environ.get("LARK_APP_ID", "")
APP_SECRET = os.environ.get("LARK_APP_SECRET", "")
APP_TOKEN = os.environ.get("LARK_APP_TOKEN", "")
TABLE_ID = "tblUPJE583VJqB1b"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method='POST')
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))['tenant_access_token']

def get_record(token, record_id):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/{record_id}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))

token = get_token()

# Check first 3 records
record_ids = ["recTHgeYJP", "recKvePHmT", "recQToi0JC"]

for rid in record_ids:
    result = get_record(token, rid)
    if result.get('code') == 0:
        fields = result['data']['record']['fields']
        name = fields.get('产品名称', 'N/A')[:30]
        plan = fields.get('拍摄计划', '')
        think = fields.get('思考过程', '')
        output = fields.get('输出结果', '')
        print(f"记录: {rid}")
        print(f"  产品: {name}")
        print(f"  拍摄计划: {'✓ 有内容' if plan else '✗ 空'} ({len(plan)}字)")
        print(f"  思考过程: {'✓ 有内容' if think else '✗ 空'} ({len(think)}字)")
        print(f"  输出结果: {'✓ 有内容' if output else '✗ 空'} ({len(output)}字)")
        print()
    else:
        print(f"查询失败 {rid}: {result}")
