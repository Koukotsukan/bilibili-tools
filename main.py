import random
import asyncio
import requests
import time
import json
import hashlib
import rsa
import base64
import re
import datetime
from urllib import parse
from login import BiliLogin

def CurrentTime():
    currenttime = str(int(time.mktime(datetime.datetime.now().timetuple())))
    return currenttime


class login():
    global serverchan
    cookies = ""
    username = "#你的账号填在引号内"
    password = "#你的密码填在引号内"
    serverchan = "#你的serverchan的SCKEY" #ServerChan网站:http://sc.ftqq.com/3.version
    headers = {
        "Host": "api.bilibili.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cookie": cookies
    }
    csrf = ""
    uid = ""
    access_key = ""

    async def calc_sign(self, str):
        str = str + "560c52ccd288fed045859ed18bffd973"
        hash = hashlib.md5()
        hash.update(str.encode('utf-8'))
        sign = hash.hexdigest()
        return sign

    async def get_pwd(self, username, password):
        url = 'https://passport.bilibili.com/api/oauth2/getKey'
        temp_params = 'appkey=1d8b6e7d45233436'
        sign = await self.calc_sign(temp_params)
        params = {'appkey': '1d8b6e7d45233436', 'sign': sign}
        response = requests.post(url, data=params)
        value = response.json()['data']
        key = value['key']
        Hash = str(value['hash'])
        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(key.encode())
        password = base64.b64encode(rsa.encrypt(
            (Hash + password).encode('utf-8'), pubkey))
        password = parse.quote_plus(password)
        username = parse.quote_plus(username)
        return username, password

    def login(self):
        name, login.cookies, login.access_key = BiliLogin().login(login.username, login.password)

        s1 = re.findall(r'bili_jct=(\S+)', login.cookies, re.M)
        s2 = re.findall(r'DedeUserID=(\S+)', login.cookies, re.M)
        login.headers = {
            "Host": "api.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cookie": login.cookies
        }
        login.csrf = (s1[0]).split(";")[0]
        login.uid = (s2[0].split(";")[0])


class judge(login):

    def randomint(self):
        return ''.join(str(random.choice(range(10))) for _ in range(17))

    def CurrentTime(self):
        millis = int((time.time() * 1000))
        return str(millis)

    async def query_reward(self):
        url = "https://account.bilibili.com/home/reward"
        url2 = "https://api.bilibili.com/x/web-interface/nav"
        headers = {
            "Referer": "https://account.bilibili.com/account/home",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
            "Cookie": login.cookies
        }
        response = requests.get(url, headers=headers)
        level_response = requests.get(url2, headers=headers)
        iflogin = response.json()['data']['login']
        ifwatch_av = response.json()['data']['watch_av']
        ifshare_av = response.json()['data']['share_av']
        ifgive_coin = response.json()['data']['coins_av']
        current_exp = response.json()['data']["level_info"]['current_exp']
        next_exp = response.json()['data']["level_info"]['next_exp']
        current_money = level_response.json()['data']['money']
        current_level = response.json()['data']["level_info"]['current_level']
        return [iflogin, ifwatch_av, ifshare_av, int(ifgive_coin), current_exp, next_exp, current_money,current_level]

    async def get_attention(self):
        top50_attention_list = []
        url = "https://api.bilibili.com/x/relation/followings?vmid=" + \
              str(login.uid) + "&ps=50&order=desc"
        headers = {
            "Host": "api.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cookie": login.cookies
        }
        response = requests.get(url, headers=headers)
        checklen = len(response.json()['data']['list'])
        for i in range(0, checklen):
            uids = (response.json()['data']['list'][i]['mid'])
            top50_attention_list.append(uids)
        return top50_attention_list

    async def getsubmit_video(self):
        top50_attention_list = await self.get_attention()
        video_list = []
        for mid in top50_attention_list:
            url = "https://space.bilibili.com/ajax/member/getSubmitVideos?mid=" + \
                  str(mid) + "&pagesize=100&tid=0"
            response = requests.get(url)
            datalen = len(response.json()['data']['vlist'])
            for i in range(0, datalen):
                aid = response.json()['data']['vlist'][i]['aid']
                video_list.append(aid)
        return video_list

    async def givecoin(self):
        video_list = await self.getsubmit_video()
        url = "https://api.bilibili.com/x/web-interface/coin/add"
        aid = video_list[random.randint(0, len(video_list))]
        data = {
            "aid": aid,
            "multiply": "1",
            "cross_domain": "true",
            "csrf": login.csrf
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
            "Referer": "https://www.bilibili.com/video/av" + str(aid),
            "Origin": "https://www.bilibili.com",
            "Host": "api.bilibili.com",
            "Cookie": login.cookies
        }
        response = requests.post(url, data=data, headers=headers)
        global coinresponse
        coinresponse = response.json()['code']
        print("coin_task:", response.text)

        if response.json()['code'] != 0 and response.json()['code'] != -104:
            await self.givecoin()
        await asyncio.sleep(10)

    async def get_cid(self, aid):
        url = "https://www.bilibili.com/widget/getPageList?aid=" + str(aid)
        response = requests.get(url)
        cid = response.json()[0]['cid']
        return cid

    async def share(self):
        video_list = await self.getsubmit_video()
        aid = video_list[random.randint(0, len(video_list))]
        url1 = "https://app.bilibili.com/x/v2/view/share/add"
        headers = {
            "User-Agent": "Mozilla/5.0 BiliDroid/5.26.3 (bbcallen@gmail.com)",
            "Host": "app.bilibili.com",
            "Cookie": "sid=8wfvu7i7"
        }
        ts = CurrentTime()
        temp_params = "access_key=" + login.access_key + "&aid=" + \
                      str(
                          aid) + "&appkey=1d8b6e7d45233436&build=5260003&from=7&mobi_app=android&platform=android&ts=" + str(
            ts)
        sign = await self.calc_sign(temp_params)
        data = {
            "access_key": login.access_key,
            "aid": aid,
            "appkey": "1d8b6e7d45233436",
            "build": "5260003",
            "from": "7",
            "mobi_app": "android",
            "platform": "android",
            "ts": ts,
            "sign": sign
        }
        response = requests.post(url1, headers=headers, data=data)
        print("分享视频:", response.json())

    async def watch_av(self, aid, cid):
        url = "https://api.bilibili.com/x/report/web/heartbeat"
        headers = {
            "Host": "api.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
            "Referer": "https://www.bilibili.com/video/av" + str(aid),
            "Cookie": login.cookies
        }
        data = {
            "aid": aid,
            "cid": cid,
            "mid": login.uid,
            "csrf": login.csrf,
            "played_time": "0",
            "realtime": "0",
            "start_ts": self.CurrentTime(),
            "type": "3",
            "dt": "2",
            "play_type": "1"
        }

        response = requests.post(url, headers=headers, data=data)

        print("watch_Av_state:", response.text)

    async def coin_run(self):
        global coinnum
        coinnum = 0
        global coinlog
        coinlog = " "

        while  coinnum < 5:
            try:
                i = await self.query_reward()
                global coin_exp
                coin_exp = i[3]
                if coin_exp == 50:
                    coinnum = 5
                
                while coin_exp < 50:
                    await self.givecoin()
                    if coinresponse == -104:
                        raise DTError                   
                    coinnum = coinnum + 1
                    coin_exp = coin_exp + 10
                    print ("第",coinnum,"次投币Success")
                    coinlog = coinlog + "\n\n" + "第" + str(coinnum) + "次投币Success"
            except:
                coinnum = coinnum + 1
                print("第",coinnum,"次投币Error")
                coinlog = coinlog + "\n\n" + "第" + str(coinnum) +"次投币Error"
        if coinnum == 5:
            print("投币任务完成")
            coinlog = "<font color=\"red\">投币任务完成</font>" + "\n\n" + coinlog




    async def share_run(self):
        global sharenum
        sharenum = 0
        global sharelog
        sharelog = " "
        while sharenum < 5:
            try:
                await self.share()
                sharenum = sharenum + 1
                print("第",sharenum,"次分享Success")
                sharelog = sharelog + "\n\n第" + str(sharenum) + "次分享Success"
                await asyncio.sleep(2)
            except:
                sharenum = sharenum + 1
                print("第",sharenum,"次分享Error")
                sharelog = sharelog + "\n\n第" + str(sharenum) + "次分享Error"
        if sharenum == 5:
            print("分享任务完成")
            sharelog ="<font color=\"red\">分享任务完成</font>" + "\n\n" + sharelog


    async def watch_run(self):
        global watchnum
        watchnum = 0
        global watchlog
        watchlog = " "
        while watchnum < 5:
            try:
                video_list = await self.getsubmit_video()
                aid = video_list[random.randint(0, len(video_list))]
                cid = await self.get_cid(aid)
                await self.watch_av(aid, cid)
                await asyncio.sleep(3)
                watchnum = watchnum + 1
                print ("第",watchnum,"次视频Success")
                watchlog = watchlog + "\n\n第" + str(watchnum) + "次视频Success"
            except:
                watchnum = watchnum + 1
                print("第",watchnum,"次视频Error")
                watchlog = watchlog + "\n\n第" + str(watchnum) + "次视频Error"
        if watchnum == 5:
            print("视频任务完成")
            watchlog = "<font color=\"red\">视频任务完成</font>" + "\n\n" + watchlog
            time.sleep (3)

    async def daily_report(self):
        global day_log
        day_log = " "
        value = await self.query_reward()
        current_money = int(value[6])
        next_exp = int(value[5])
        current_exp = int(value[4])
        coin_exp = int(value[3])
        current_level = int(value[7]) + 1
        remain_exp = next_exp - current_exp
        today_exp = coin_exp + 15
        remain_coin_days = current_money / 4
        remain_coin_exp = remain_coin_days * 50
        remain_15_days = (remain_exp - remain_coin_exp - remain_coin_days * 15) / 25
        remain_days = remain_coin_days + remain_15_days
        day_log = "**今日经验: " + str(int(today_exp)) + " Exp**\n\n**硬币投完天数: " + str(round(remain_coin_days)) + "天**\n\n**升级至Lv" + str(int(current_level)) + "天数: " + str(round(remain_days)) + "天**\n\n\n\n"


def main_handler():
    judge().login()
    loop = asyncio.get_event_loop()
    tasks2 = [
        judge().coin_run(),
        judge().share_run(),
        judge().watch_run(),
        judge().daily_report(),
    ]
    loop.run_until_complete(asyncio.wait(tasks2))
    loop.close()
    log = day_log +"**投币情况**" + "\n\n" + coinlog + "\n\n" + "**分享情况**" + "\n\n" + sharelog + "\n\n" + "**视频情况**" + "\n\n" + watchlog
    requests.get("https://sc.ftqq.com/" + serverchan +  ".send?text=哔哩哔哩签到结束&desp=" + log)
    print (log)


main_handler()
