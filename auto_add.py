
import json
from random import random
import time
import re

import jieba
import requests
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import jieba.posseg as psg
# jieba.set_dictionary("./dict.txt")
jieba.initialize()
his_txt='history_cord.txt'

def get_dict0():
    f=r'parm_total.txt'
    dic={}
    with open(f,encoding='utf-8') as file:
        for s in file.readlines():
            if s=='\n':
                continue
            l=s.split()
            if(len(l)!=2):
                continue
            chinese, en=l[0],l[1]
            dic[chinese]=en

    return dic
DIC=get_dict0()
def get_dict():
    return DIC
def cro_fanyi(res,x):#爬取翻译
    ans=''
    try:

        str_json = res.content.decode("utf-8")
        myjson = json.loads(str_json)
        total = myjson['data'][0]['v']
        print('cro_fy2')
        r = x
        ok=True
        if total.find(";") != -1:
            r = total.split(';')[0]
            ok=False
        if total.find(",") != -1 and ok:
            r = total.split(',')[0]
        r=re.sub('(\[.*?\])','',r)
        ans = re.sub('[^a-z\s]', '', r).lstrip()
        res.close()
        return ans
    except:
        raise Exception()
        return ''
    return ans
def search_transform(x):#核心后端，主要是翻译中文和创建格式
    #写的很拉，主要是先看标签库里有没有直接的标签，没有就分词然后翻译再组合，
    # 如果爬虫翻译也出问题就在标签库里模糊查找关键词（不太准），
    # 因为用到了爬虫和jieba，导致效率很低，但是勉强能完成功能
    if len(x)==0 or bool(re.search('[a-z]', x)):
        return ''
    dic=get_dict()

    if x in dic:
        return dic[x]
    else:#爬虫翻译

        word_list = psg.cut(x)
        try:

            url = "https://fanyi.baidu.com/sug"
            # 定义请求的参
            res1=[]
            dic2={
                1: [],
                2: []
            }
            for x,v in word_list:#分词翻译
                if v[0] == 'a'or v[0]=='d' or v[0]=='t' or  v[0]=='z':
                    dic2[1].append(x)
                elif v[0] == 'n' or v[0] == 'v':
                    dic2[2].append(x)
            print(dic2)
            for x in dic2[1]:
                data = {'kw': x}
                # 创建请求， 发送请求， 爬取信息
                res = requests.post(url, data=data)
                if not(x in dic):
                    ans=cro_fanyi(res,x)

                else:
                    ans=dic[x]
                if len(ans)==0:
                    raise Exception
                temp=ans
                if x!='' and temp!='':
                    res1.append(temp)

            for x in dic2[2]:
                data = {'kw': x}
                # 创建请求， 发送请求， 爬取信息
                res = requests.post(url, data=data)
                # 解析结果
                if not (x in dic):
                    ans = cro_fanyi(res, x)
                else:
                    ans = dic[x]
                if len(ans)==0:
                    raise Exception
                temp = ans
                if x!='' and temp!='':
                    res1.append(temp)
            print('res1',res1)
            res2=[]
            for xx in res1:
                t1=xx.split()
                for x3 in t1:
                    res2.append(x3)
            ans='_'.join(res2)
            ans=ans.lstrip()
            ans=ans.rstrip()
            print(ans,114)
            if len(ans)==0:
                raise Exception
            print(ans)
            # dic[x]=ans
            # if not (x in dic):
            #     with open('parm_total.txt', mode='a', encoding='utf-8') as f:
            #         f.write('\n'+x+f' {ans}')
            return ans
        except:#爬虫出错，只能在数据库里找出最接近的标签
            print('fy_except')
            key=list(dic.keys())
            n_list=[]
            x_cut = psg.cut(x)
            for word, ch in x_cut:
                n_list.append(word)
            print(n_list)
            for k in key:
                for n_ in n_list:
                    if k.find(n_)!=-1:
                        return dic[k]

            for k in key:
                for n_ in n_list:
                    for x_ in n_:
                        print((x_))
                        if k.find(x_) != -1:
                            return dic[k]
            return ''


class MyWin(QWidget):
    #组相当于是小窗口，可以接受应该布局器，所以可以添加子组件进布局器然后加到组窗口中，
    # 最后把组加入主窗口的布局器。然后主窗口设置主布局器
    #布局器同时也能直接接受子布局器
    pic=r'app.jpg'
    p1 = '强调参数'
    p2 = '负面参数'
    p3 = '正常参数'
    Well_Pre='<font color="blue" size = "5">{masterpiece},{perfect face},{best quality},{extremely detailed cg},{girl},</font>'
    Well_Pre_Neg='<font color="blue" size = "5">lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry</font>'
    text_list={
        p1:[''],
        p2:[''],
        p3:['']
    }
    history_text={}
    history_err=[]
    MAX_SAVE=200#历史记录的最大存储
    W=800
    H=800
    label_data=''
    con_dic={}
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_data()
    def init_data(self):
        self.con_dic=get_dict()
        with open(his_txt,encoding='utf-8') as f:
            try:
                self.label_data=f.readlines()
                for x in f.readlines():
                    if len(x)==1:
                        continue
                    t,pram=x.split('_')
                    self.history_text[t]=pram
            except:
                pass
        pass
    def init_ui(self):
        #预设部分
        self.resize(self.W,self.H)
        self.setWindowIcon(QIcon(self.pic))
        self.setWindowTitle('川川的参数生成器')
        self.parm_out = QTextEdit()
        self.his_text_out=QTextEdit()
        # self.parm_out.setTextInteractionFlags(Qt.TextSelectableByMouse)
        ##最外层的总体布局
        container = QVBoxLayout()
    #创建一个组1------组可以看作小窗口
        g1=QGroupBox('输入')

        #创建组件和子布局器
        vlayout=QVBoxLayout()
        h1=QHBoxLayout()
        lb1 = QLabel(self.p1+":", g1)
        bt1=QLineEdit()
        bt1.setPlaceholderText('"{}" 以空格或逗号隔开每个参数，输入完请点击确定上传')
        b1=QPushButton('确定')
        h1.addWidget(lb1)
        h1.addWidget(bt1)
        h1.addWidget(b1)
        b1.clicked.connect(lambda: self.get_text(self.p1,bt1.text()))


        h2 = QHBoxLayout()
        lb2 = QLabel(self.p2+':', g1)
        bt2 = QLineEdit()
        bt2.setPlaceholderText('"[]" 以空格或逗号隔开每个参数，输入完请点击确定上传')
        b2 = QPushButton('确定')
        b2.clicked.connect(lambda: self.get_text(self.p2,bt2.text()))
        h2.addWidget(lb2)
        h2.addWidget(bt2)
        h2.addWidget(b2)

        h3 = QHBoxLayout()
        lb3 = QLabel(self.p3+':', g1)
        bt3 = QLineEdit()
        bt3.setPlaceholderText('"_" 以空格或逗号隔开每个参数，输入完请点击确定上传')
        b3 = QPushButton('确定')
        b3.clicked.connect(lambda: self.get_text(self.p3,bt3.text()))
        h3.addWidget(lb3)
        h3.addWidget(bt3)
        h3.addWidget(b3)
        #给子布局器添加组件
        vlayout.addLayout(h1)
        vlayout.addLayout(h2)
        vlayout.addLayout(h3)
        #给组1添加布局器
        g1.setLayout(vlayout)
    #创建组2-------
        g2=QGroupBox('输出')
        # g2.setStretch(1)
        #创建改组的组件和子布局器
        vlayout2=QVBoxLayout()
        vlayout2.addWidget(self.parm_out)
        #按钮
        ans=QPushButton('生成参数')
        vlayout2.addWidget(ans)
        ans.clicked.connect(self.creat_clicked)
        #给组2添加布局器
        g2.setLayout(vlayout2)

        #其他功能的水平布局
        h_layout3=QHBoxLayout()
        # 优化预设
        hh_layout3=QHBoxLayout()
        gb1 = QGroupBox()#预设组
        self.well_pre = QRadioButton('添加优化预设(默认)')
        self.well_pre.setChecked(True)
        self.not_pre = QRadioButton('取消预设')
        hh_layout3.addWidget(self.well_pre)
        hh_layout3.addWidget(self.not_pre)
        gb1.setLayout(hh_layout3)
        h_layout3.addWidget(gb1)
        # 把组的组件加入总体布局器
        # 历史记录组设置
        g3 = QGroupBox('其他功能')
        check1 = QPushButton('查看历史记录')
        h_layout3.addWidget(check1)

        check1.clicked.connect(self.check_his_text)

        ran_bt=QPushButton('简要说明(没事就点我)')
        ran_bt.clicked.connect(self.ran_bt_clicked)

        add_label=QPushButton('添加自定义标签(用法见说明)')
        add_label.clicked.connect(self.add_label_clicked)
        h_layout3.addWidget(add_label)
        h_layout3.addWidget(ran_bt)
        g3.setLayout(h_layout3)
        container.addWidget(g1)
        # container.addStretch(10)
        container.addWidget(g3)
        container.addWidget(g2)
        # container.addStretch(8)
        #给总窗口设置布局器
        self.setLayout(container)
    def deal_text(self,text):
        def is_all_chinese(strs):
            for _char in strs:
                if not '\u4e00' <= _char <= '\u9fa5':
                    return False
            return True
        def is_all_en(strs):
            strs=strs.lower()
            for x in strs:
                if not (ord(x)>=ord('a') and ord(x)<=ord('z')) and x!=' ' and x!='_':
                    return False
                else:
                    return True
        res=text
        try:
            ch=re.findall('[\u4e00-\u9fa5]+',res)
            print('ch',ch)
            en=re.findall("[a-zA-Z].*[a-zA-Z]",res)

            if len(ch)==0 or len(en)==0:
                return ''
            en[0] = en[0].replace(' ', '_')
            res=ch[0]+' '+en[0]
            x1=res
            print(x1, ' text')

            l=x1.split()
            if len(l)!=2:
                return ''
            if is_all_chinese(l[0]) and is_all_en(l[1]):
                return l[0]+' '+l[1]
            return ''
        except:
            return ''

        pass
    def add_label_clicked(self):
        data=self.parm_out.toPlainText()
        total = data
        useage='<font color="blue" size = "4">【格式：<br>{中文1 英文1 <br> 中文2 英文2}<br> 支持在输出框内一串多行由{}框起的文本】</font><br>'
        data=data
        # self.parm_out.setHtml(useage)
        res=re.sub('【.*】','',data)
        res = re.sub('[\n]', '_', data)
        res=re.findall('\{(.*?)\}',res)
        r=''
        if len(res)!=0:
            r=res[0]

        r=r.split('_')
        cnt=0
        with open("parm_total.txt", mode='a+', encoding='utf-8') as f:
            print(2)
            for x in r:
                print(3,x)
                if len(x)==1 or len(x)==0:
                    continue
                print(4,x)
                s1=self.deal_text(x)
                if s1!='':
                    print('写入 ',s1)
                    f.write('\n'+s1)
                else:
                    cnt+=1
                    continue
        l=0
        for x in r:
            if x!='':
                l+=1
        warnings=f'<font color="red" size = "4">【添加结束<br>写入{l}条语句，最后添加了{l-cnt}条<br>有{cnt}书写有误。对该功能有疑问请查看说明】</font>'
        total=warnings+'\n'

        self.parm_out.setHtml(total)

        pass
    def ran_bt_clicked(self):
        t2 = time.localtime()  # 获得时间结构体
        res=''
        th=int(t2.tm_hour)
        print(th)
        lword='早上好！ 中午好！ 下午好！ 晚上好！ 这么晚还不睡啊？'.split()
        deg=2
        col='"blue"'
        if 11>=th>=5:
            res+=f'< h{deg} align = "center" color={col}> {lword[0]} 现在的时间是{time.strftime("%H:%M",t2)} </h{deg} >'

        if 14>=th>11:
            res+=f'< h{deg} align = "center" color={col}> {lword[1]} 现在的时间是{time.strftime("%H:%M",t2)} </h{deg} >'
        if th>14 and th<=16:
            res+=f'< h{deg} align = "center" font-color={col} {lword[2]}  现在的时间是 {time.strftime("%H:%M",t2)} </h{deg}>'
        if 24>=th>=17:
            res+=f'< h{deg} align = "center" font-color={col}> {lword[3]}  现在已经{time.strftime("%H:%M",t2)}了 </h{deg} >'
        if 0<=th<5:
            res+=f'< h{deg} align = "center" color={col}> {lword[4]} 现在已经{time.strftime("%H:%M",t2)}了 </h{deg} >'
        #简要说明
        res+=''' <font color="green" size = "4">1.在对应输入框输入中文用空格和逗号隔开即可，然后点击生成参数，稍等1秒左右得到处理完的参数。须注意：翻译过程有一部分采用了爬虫爬取百度翻译，需要链接网络，而且不一定准确。描写细致的情况还是自己查阅。
        重要的是，输入支持 tag1*2,tag*3... 的格式生成{{tag1}},{{{tag2}}}的参数。注：每个括号使相关性变成原来的1.05
        <br>2.同一目录下的[parm_total.txt]文件下存储着一些标签，你可以查阅和合理修改（如果格式改变可能导致程序读取出错）也可以使用[添加自定义标签]的功能。其用法见【3】 <br><br>
        3.自定义添加标签功能。格式：<br>{中文1 英文1 <br> 中文2 英文2_英文} <br> 支持在输出框内一串多行由{}框起的文本,也就是在输出框内用{}框起来内容然后点击[添加标签功能],软件会对内容检索，添加可行的标签。
        <br>4.历史记录功能会存储最近一段时间的tag记录。
        <br><br>5.可能会用到的网站：<br>
        检测图片参数占比：http://danbooru.iqdb.org/
        <br>http://dev.kanotype.net:8003/deepdanbooru/

        <br><br>              QQ:2669459326
            <br>              by:断川 2022/10/11
            </font>'''
        self.parm_out.setHtml(res)
        pass
    def ran_get_tag(self):
        p=random.randint(1,4)
        pos=random.randint(0,250)
        return (p,pos)
        pass
    def check_his_text(self):# 查看历史记录
        tem=''
        for t,parm in reversed(self.history_text.items()):
            tem += f'<font color="green" size = "5">{t}<br>{parm} </font> <br><br>'
        self.parm_out.setHtml(tem)

    def show_label(self,res):
        tem=' '
        if self.well_pre.isChecked():
            tem=f'<br> <font color="green" size = "5">Negative Prompt: </font> </br><br>{self.Well_Pre_Neg}'

        self.parm_out.setHtml(f'<font color="red" size = "5"><br> <font color="green" size = "5">Prompt: </font> </br><br>{res}<br>{tem}</font>')

        self.save_his_text()
    def save_his_text(self):
        tem = ''
        for t, pram in reversed(self.history_text.items()):
            tem += t+'_'+pram+'\n'
        with open(his_txt, "r+") as f:
            old = f.read()
            f.seek(0)
            f.write(tem+'\n')



            # f.write(old)
    def creat_clicked(self):
        self.parm_out.setHtml(f'<font color="red" size = "5"><br>            正在生成，稍等...</font>')
        self.out_pram()
    def out_pram(self):#处理选择的参数列表
        def is_all_chinese(strs):
            for _char in strs:
                if '\u4e00' <= _char <= '\u9fa5':
                    return True
            return False
        l1,l2,l3=self.text_list[self.p1],self.text_list[self.p2],self.text_list[self.p3]
        in_=[l1[-1],l2[-1],l3[-1]]#得到最新的数据
        res=[]
        print(in_)
        for i,context in enumerate(in_):
            con=[context]
            if context.find(' ')!=-1:
                con=context.split()
            if context.find(',')!=-1:
                con = context.split(',')
            if context.find('，')!=-1:
                con=context.split('，')
            sign_={
                0:['{','}'],
                1:['[',']'],
                2:['','']
            }
            for j,x in enumerate(con):
                tem=x
                cnt0 = re.findall('\*([0-9]+)',tem)
                cnt=0
                if len(cnt0)!=0:
                    cnt=int(cnt0[0])
                tem=re.sub('[\[\]{}\*]','',tem)
                if is_all_chinese(tem):
                    tem=re.findall('[\u4e00-\u9fa5]+',tem)[0]
                    tem=search_transform(tem)
                else:
                    tem=tem.lower()
                res.append(sign_[i][0]*(max(1,cnt))+tem+sign_[i][1]*(max(1,cnt)))
        if self.well_pre.isChecked():
            res=self.Well_Pre+','.join(res)
        else:
            res =  ','.join(res)
        t2 = time.localtime()  # 获得时间结构体
        self.history_text[time.strftime('%Y-%m-%d %H:%M:%S',t2)]=res
        self.show_label(res)

        pass
    def get_text(self,from_,msg):

        if msg==None:
            self.text_list[from_].append('')
        else:
            self.text_list[from_].append(msg)
        pass
if __name__ == '__main__':
    app=QApplication(sys.argv)
    w=MyWin()
    w.show()
    app.exec_()