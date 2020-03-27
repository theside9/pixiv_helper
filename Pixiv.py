from pixivpy3 import AppPixivAPI,PixivError
from pynput.keyboard import Listener,Key
import os,time,_thread

#重写了代理，使用本地代理访问pixiv
class Pixiv(AppPixivAPI):

    proxies=None
    thread_count=None
    speed_all=[]
    stop=False

    def __init__(self, **requests_kwargs):
        super().__init__(**requests_kwargs)

    def set_thread_count(self,count):
        self.thread_count=count
        self.speed_all=[0]*self.thread_count

    def download(self, url, prefix='', path=os.path.curdir, name=None, replace=False, fname=None, referer='https://app-api.pixiv.net/',tid=None):
        """Download image to file (use 6.0 app-api)"""
        _thread.start_new_thread(self.keyboard_listen,())#开始监听键盘，esc终止
        if fname is None and name is None:
            name = os.path.basename(url)
        elif isinstance(fname, basestring):
            name = fname

        if name:
            name = prefix + name
            img_path = os.path.join(path, name)
            if (os.path.exists(img_path) and os.path.getsize(img_path)>10) or (os.path.exists(img_path[:-3]+'jpg') and os.path.getsize(img_path[:-3]+'jpg')>10) and not replace:
                raise EXISTS_ERROR("该文件已存在！%s"%img_path)

        response = self.requests_call('GET', url, headers={'Referer': referer}, stream=True)
        if response.status_code != 200:
            raise HTTP_REQUESTS_STATUS_ERROR('图片地址错误：%s，状态码：%d'%(url,response.status_code))
#下线显示速度
        if name:
            f= open(img_path, 'wb')
        else:
            f=fname
        count = 0
        count_tmp = 0
        time1 = time.time()
        for chunk in response.iter_content(chunk_size = 128):
            if self.stop:
                f.close()
                os.remove(img_path)
                raise USER_EXIT("esc press!")
            if chunk:
                f.write(chunk)
                count += len(chunk)
                if time.time() - time1 > 0.5:
                    speed = (count - count_tmp) / 1024 / 1024 / 0.5
                    self.update_speed(speed,tid)
                    count_tmp = count
                    time1 = time.time()
        f.close()
        return True

    def update_speed(self,speed,tid):
        self.speed_all[tid]=speed#第tid进程的下载速度


    def formatFloat(self,num):
        return '{:.2f}'.format(num)
    
    def keyboard_on_release(self,key):
        try:
            if key.char=="e" or self.stop:
                # 停止监听
                self.stop=True
                return False
        except AttributeError:
            pass

    def keyboard_listen(self):
        with Listener(on_release=self.keyboard_on_release) as listener:
            listener.join()

class USER_EXIT(Exception):
    def __init__(self,value):
        self.value=value
    def __str__(self):
        return repr(self.value)


class HTTP_REQUESTS_STATUS_ERROR(Exception):
    def __init__(self,value):
        self.value=value
    def __str__(self):
        return repr(self.value)

class EXISTS_ERROR(Exception):
    def __init__(self,value):
        self.value=value
    def __str__(self):
        return repr(self.value)