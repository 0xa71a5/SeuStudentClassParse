#*-* coding:utf-8 *-*
# author: 0xa71a5
# date:   2017/02/19
'''
用法：
在同一目录下
import parseClass
html=....#html中存放读到的课表页面文本
parseClass.handleOnePage(html)#这一句会直接去解析html然后执行插入到数据库中的操作
#另外第48行你要自己加数据库对象
#就酱，快给加班费！(￢_￢)
'''
from bs4 import BeautifulSoup 
import sys
import re
reload(sys)
sys.setdefaultencoding('utf8')
def parseHtmlToClass(content):#从html文本中第一步解析
    soup = BeautifulSoup(content,"html5lib")
    tmp=soup.findAll('table')[2].findAll('table')[1].findAll("td")
    cardNumber=tmp[3].string.split(":")[1]#获取学生一卡通号
    stuName=tmp[4].string.split(":")[1]#获取学生姓名
    classTimeTable=soup.findAll('table')[2].findAll('table')[2].findAll('table')[1]#这个table里面存着所有课
    rows=classTimeTable.findAll('tr')#不同的行表示不同的时间段，分别是上午，下午，晚上，周六，周日
    morningClass=rows[1];afternoonClass=rows[6];eveningClass=rows[11];saturdayClass=rows[13];sundayClass=rows[15]
    morningClass=morningClass.findAll("td")[1:]#上午从周一到周五所有的课，下标1表示周一，下标2表示周二
    afternoonClass=afternoonClass.findAll("td")[1:]#下午从周一到周五所有的课
    eveningClass=eveningClass.findAll("td")[1:]
    return (morningClass,afternoonClass,eveningClass,stuName,cardNumber)#返回的是一个tuple，注意顺序
def parseToSql(cont):#这个函数第二步解析，把上午或者下午，一个时间段内多个课程进行分解
    try:
        if(len(cont)==1):return []
        cont=cont.split(",")[:-1]#去看html文档，每一个课程的几个信息之间都是用<br>分割的，但是我前面已经将<br>替换成了,所以现在以,分割
        divNum=len(cont)/3#因为一个时间段可能有好几门课，而一门课有3个时间因子，所以将总的时间因子除以3得到的就是当前时间段需要迭代的课程数
        retList=[]
        for x in range(0,divNum):
            className=cont[3*x+0]
            tmp=re.findall(r"\d+",cont[3*x+1])
            startWeek=tmp[0];endWeek=tmp[1];startPeriod=tmp[2];endPeriod=tmp[3]
            retList.append([className,startWeek,endWeek,startPeriod,endPeriod])
        return retList
    except Exception as e:print e;return []
def insertIntoDatabase(result,weekday,stuName,cardNumber):
    command=""
    for items in result:
        command="insert into StudentClass (stuName,cardNumber,className,weekday,startWeek,endWeek,startPeriod,endPeriod) values('{}','{}','{}',{},{},{},{},{})".format(stuName,str(cardNumber),items[0],weekday,items[1],items[2],items[3],items[4])
        print command#这是插入数据库的命令
        #cur.execute(command)这里是你要自己加的插入数据库的语言
def handleOnePage(html):
    content=html
    content=content.replace("<br>",",")#<br>会在解析的bs4解析的时候出现bug
    tmp=parseHtmlToClass(content)#从html文本中第一步解析，请去看这个函数的实现过程
    morningClass=tmp[0]
    afternoonClass=tmp[1]
    stuName=tmp[3]
    cardNumber=tmp[4]
    for weekday in range(1,6):#周一到周五依次插入到数据库中
        result=parseToSql(morningClass[weekday].string)
        insertIntoDatabase(result,weekday,stuName,cardNumber)
        result=parseToSql(afternoonClass[weekday].string)
        insertIntoDatabase(result,weekday,stuName,cardNumber)
if __name__=="__main__":
    content=open("web.html","r").read()
    handleOnePage(content)




