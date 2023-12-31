import json
import os.path
import shutil
from datetime import datetime
import requests
from selenium import webdriver
import pandas as pd
from MyWindow import *

def init_folder():
    try:
        if os.path.exists("./output"):
            shutil.rmtree("./output")
        os.makedirs("./output")
    except:
        print("文件夹删除失败，检查是否存在占用？")

def set_cookie(api_server):
    try:
        driver = webdriver.Chrome()
        driver.get(api_server)
        cookies = driver.get_cookies()
        driver.quit()
        return {cookie['name']: cookie['value'] for cookie in cookies}
    except:
        print("网络出错，Cookie不能获取")
        sys.exit(0)

def get_timestamp(date = "0000-00-00 00:00:00"):
    if date == "0000-00-00 00:00:00":
        now = datetime.now()
        return int(round(datetime.timestamp(now) * 1000, 0))
    else:
        date_format = "%Y-%m-%d %H:%M:%S"
        dt_obj = datetime.strptime(date, date_format)
        return int(round(datetime.timestamp(dt_obj) * 1000, 2))

def to_excel(data, timestamp):
    df = pd.DataFrame(data)
    df.to_excel("./output/{}.xlsx".format(timestamp))
    return df

if __name__ == "__main__":
    api_server = "https://www.chinamoney.com.cn"
    api = "https://www.chinamoney.com.cn/r/cms/www/chinamoney/data/fx/ccpr.json"
    init_folder()
    cookies = set_cookie(api_server)
    timestamp = get_timestamp()

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    headers = {
        "User-Agent": user_agent
    }

    formdata = json.dumps({
        "t": timestamp
    })

    try:
        data = requests.post(url=api, headers=headers, cookies=cookies, data=formdata).json()['records']
        to_excel(data, timestamp)
    except:
        print("网络出错，api请求失败")
        sys.exit(0)
    window = MyWindow(data, api_server, headers, cookies)
    window.init_ui()

