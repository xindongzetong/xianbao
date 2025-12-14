import requests
import time
from pywebio import *
from models import SqlAct
from fake_useragent import UserAgent
import threading
from collections import deque

MAX_PUSHED = 5000

pushed_set = set()
pushed_queue = deque(maxlen=MAX_PUSHED)


def add_pushed(user_id, news_id):
    key = (user_id, news_id)
    if key in pushed_set:
        return False
    if len(pushed_queue) == pushed_queue.maxlen:
        old_key = pushed_queue[0]
        pushed_set.remove(old_key)

    pushed_queue.append(key)
    pushed_set.add(key)
    return True


def push_task():
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random
    }
    url = "https://new.xianbao.fun/plus/json/push.json"
    try:
        while True:
            time.sleep(6)
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                continue
            news_list = r.json()
            users = SqlAct().fetch_sql("SELECT * FROM users", True)
            SqlAct().close_con()

            for user in users:
                if user[2] != '是':
                    continue
                user_id = user[1]
                wx_uid = user[3]
                keys = [k.strip() for k in user[4].split('\n') if k.strip()]
                if not keys:
                    continue
                for news in news_list:
                    news_id = news['id']
                    title = news.get('title', '')
                    content = news.get('content', '')
                    if any(k in title or k in content for k in keys):
                        if not add_pushed(user_id, news_id):
                            continue
                        msg = {
                            "appToken": "AT_5lFOdQx9ffbKQtaqdaqpOvzSpeQmQqnb",
                            "content": f"{content}\n原文链接：http://new.xianbao.fun{news['url']}",
                            "summary": title,
                            "contentType": 3,
                            "uids": [wx_uid],
                            "verifyPay": False
                        }
                        requests.post(
                            url='https://wxpusher.zjiecode.com/api/send/message',
                            json=msg,
                            timeout=10
                        )
    except Exception as e:
        print(e)


def index():
    username = input.input(label='用户名', type=input.TEXT, required=True)
    data = SqlAct().fetch_sql("SELECT * FROM users WHERE username='{}'".format(username), False)
    SqlAct().close_con()
    if not data:
        SqlAct().insert_update_table("INSERT INTO users(username, task, token, keyword) VALUES('{}', '{}', '{}', '{}')"
                                     .format(username, '否', '', ''))
        data = SqlAct().fetch_sql("SELECT * FROM users WHERE username='{}'".format(username), False)
        SqlAct().close_con()
    output.put_link(name='点击链接关注，获取UID', url='https://wxpusher.zjiecode.com/wxuser/?type=1&id=64961#/follow',
                    new_window=True)
    info = input.input_group("信息", [
        input.radio(label='是否启用推送', name='task', inline=True, options=['是', '否'], required=True,
                    value=data[2]),
        input.input(label="token", name="token", type=input.TEXT, required=True, value=data[3]),
        input.textarea(label="关键字(回车分隔)", name="keyword", type=input.TEXT, required=True, value=data[4])
    ])
    SqlAct().insert_update_table("UPDATE users SET task='{}', token='{}', keyword='{}' WHERE id={}"
                                 .format(info['task'], info['token'], info['keyword'], data[0]))
    SqlAct().close_con()
    output.toast('设置完成', position='center', color='#2188ff', duration=1)
    time.sleep(1)
    session.go_app('index', new_window=False)


def admin():
    password = input.input(label="管理密码", type=input.TEXT)
    if password == "Sh172737.....":
        names = SqlAct().fetch_sql("SELECT * FROM users", True)
        SqlAct().close_con()
        name_list = []
        for i in names:
            name_list.append(i[1])
        name = input.select("选择要删除的用户", options=name_list, required=True)
        SqlAct().delete_table("DELETE FROM users WHERE username='{}'".format(name))
        SqlAct().close_con()
        session.go_app('admin', new_window=False)



def pretreatment():
    creat_tb = '''
        CREATE TABLE IF NOT EXISTS users(
            id integer PRIMARY KEY autoincrement,
            username TEXT NOT NULL,
            task TEXT NOT NULL,
            token TEXT NOT NULL,
            keyword TEXT NOT NULL
        );
    '''
    SqlAct().create_tabel(creat_tb)
    SqlAct().close_con()
    threading.Thread(target=push_task).start()


if __name__ == '__main__':
    pretreatment()
    config(title='线报推送', theme='yeti')
    start_server([index, admin], port=8080)