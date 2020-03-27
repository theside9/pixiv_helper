from os import path,system,mkdir
import re,_thread,time,Pixiv,getpass

thread_count=15
t=thread_count
now=All=thistime=tid=0
savepath=path.expanduser('~')+r"\Pictures\p站收藏同步"
if not path.exists(savepath):
    mkdir(savepath)
token_save_path=path.expanduser('~')
def login(api,i=1):
    system("cls")
    self_print("\r开始登录")
    if path.exists(token_save_path + r"\pixiv_token_save"):
        f=open(token_save_path + r"\pixiv_token_save",'r')
        api.refresh_token=f.read()
        f.close()

    if api.refresh_token is not None and api.refresh_token != "":
        api.auth()
    else:#说明token不存在
        try:
            self_print("账号：")
            username=input()
            self_print("密码：")
            passwd=getpass.getpass("")
            api.login(username, passwd)
        except:
            if i<=3:
                i+=1
                self_print("\r登录失败,正在准备第%d次尝试"%(i))
                time.sleep(3)
                login(api,i+1)
            else:
                self_print("\r网络异常，请检查代理和网络连接后重试。")
                return
        f=open(token_save_path + r"\pixiv_token_save",'w')
        f.write(api.refresh_token)
        f.close()

def auto_Synch(api,json_result='',all_pic_url=[]):
    if json_result == '' : 
        json_result = api.user_bookmarks_illust(user_id=api.user_id)
    else:
        next_page=api.parse_qs(json_result.next_url)
        json_result = api.user_bookmarks_illust(**next_page)

    for i in range(0,len(json_result.illusts)):
        illust = json_result.illusts[i]
        all_pic_url.append(illust.image_urls['large'])
    if json_result.next_url != None:
        auto_Synch(api,json_result,all_pic_url)
    else:
        print("\r提示：同步过程中，按e可随时中断。\n---------")
        download_all(api,parse_url(all_pic_url))

def download_all(api,all_url):
 
    global t,All,thistime

    thread_list=[True]*thread_count
    All=len(all_url)
    _thread.start_new_thread(bar,(api,))
    for url in all_url:
        while t==0:
            pass
        if not api.stop:
            t-=1
            start_thread(api,url,thread_list)
    while t<thread_count:#等待进程全部结束
        pass
    time.sleep(1)
    print("\n-----------\n本次同步了%d个图片"%thistime)

def bar(api):
    global now,All
    while now!=All and not api.stop:
        print("\r当前进度：{}%".format(int((now/All)*100)),"■"*int(((now/All)*30)),end="")#方块后的数值为控制进度条长度
        speed=0
        for i in api.speed_all:
            speed+=i
        print("     %0.2f M/S"%speed,end="")
        #time.sleep(0.1)
    print("\r当前进度：{}%".format(int((now/All)*100)),"■"*int(((now/All)*30)),end="")

def start_thread(api,url,thread_list):
    global t,All
    try:
        for tid in range(0,thread_count):
            if thread_list[tid]:
                thread_list[tid]=False
                _thread.start_new_thread(pic_download,(api,url,thread_list,tid))
                break     
            if tid==thread_count:
                raise Exception("线程异常")
    except Pixiv.PixivError as e:
        log(e)
        start_thread(api,url,tid)
    except Pixiv.HTTP_REQUESTS_STATUS_ERROR as e:
        print("该图片无法下载%s"%e.value)
        t+=1

def log(e):
    f=open("log.txt","a")
    f.write(str(e))
    f.write("\n--------------------------\n")
    f.close()

def pic_download(api,url,thread_list,tid):
    global t,now,All,thistime
    try:
        api.download(url,path=savepath,tid=tid)
        thistime+=1
    except Pixiv.HTTP_REQUESTS_STATUS_ERROR:
        try:
            api.download(url[:-3]+"jpg",path=savepath,tid=tid)
            thistime+=1
        except Pixiv.EXISTS_ERROR:
            now+=1;t+=1
        except Pixiv.PixivError as e:
            log(e);start_thread(api,url,thread_list)
        except Pixiv.USER_EXIT:
            t+=1
    except Pixiv.EXISTS_ERROR:
            now+=1;t+=1
    except Pixiv.PixivError as e:
        log(e);start_thread(api,url,thread_list)
    except Pixiv.USER_EXIT:
        t+=1
    t+=1;now+=1;thread_list[tid]=True


def parse_url(all_pic_url):
    new_pic_url=[]
    for i in all_pic_url:
        find=re.compile("https://i.pximg.net/.*?/img/(.*?_p0)_.*?\.jpg")
        picinfo=find.findall(i)
        if len(picinfo) >0 :new_pic_url.append("https://i.pximg.net/img-original/img/"+picinfo[0]+".png")
    return new_pic_url

def self_print(str0):
    print("\r"," "*50,"\r",end="")
    print(str0,end="")

if __name__ == "__main__":
    while 1:
        select=input("按回车开始同步所有收藏")
        t=thread_count;now=All=thistime=0
        self_print("正在初始化设置..")
        proxies={
        "http":"http://127.0.0.1:1080",
        "https":"http://127.0.0.1:1080"
        }
        api= Pixiv.Pixiv(proxies=proxies)
        api.set_thread_count(thread_count)
        login(api)
        auto_Synch(api)
