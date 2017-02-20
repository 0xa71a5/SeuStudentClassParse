#*-* coding:utf-8 *-*
# author: 0xa71a5
# date:   2017/02/20
from bs4 import BeautifulSoup 
import sys
import urllib
import urllib2
import re
import MySQLdb
import thread
import threadpool
import time
import SendMail
reload(sys)
sys.setdefaultencoding('utf8')

counter=0
def parseHtmlToClass(content):#从html文本中第一步解析
    soup = BeautifulSoup(content,"lxml")
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
            classRoom=cont[3*x+2].replace("九龙湖教","J").replace("一","1").replace("二","2").replace("三","3").replace("四","4").replace("五","5").replace("六","6").replace("七","7").replace("八","8")
            tmp=re.findall(r"\d+",cont[3*x+1])
            startWeek=tmp[0];endWeek=tmp[1];startPeriod=tmp[2];endPeriod=tmp[3]
            retList.append([className,startWeek,endWeek,startPeriod,endPeriod,classRoom])
        return retList
    except Exception as e:print e;return []
def insertIntoDatabase(result,weekday,stuName,cardNumber,cur):
    #global cur
    #global sql
    command=""
    for items in result:
        command="insert into StudentClass (stuName,cardNumber,className,weekday,startWeek,endWeek,startPeriod,endPeriod,classRoom) values('{}','{}','{}',{},{},{},{},{},'{}')".format(stuName,str(cardNumber),items[0],weekday,items[1],items[2],items[3],items[4],items[5])
        #print command#这是插入数据库的命令
        try:
            cur.execute(command)#这里是你要自己加的插入数据库的语言
        except Exception as e:
            print e


def handleOnePage(html,sql,cur):
    #global sql
    content=html
    content=content.replace("<br>",",")#<br>会在解析的bs4解析的时候出现bug
    if(len(content)<300):print(content);return
    tmp=parseHtmlToClass(content)#从html文本中第一步解析，请去看这个函数的实现过程
    morningClass=tmp[0]
    afternoonClass=tmp[1]
    eveningClass=tmp[2]
    stuName=tmp[3]
    cardNumber=tmp[4]
    for weekday in range(1,6):#周一到周五依次插入到数据库中
        result=parseToSql(morningClass[weekday].string)
        insertIntoDatabase(result,weekday,stuName,cardNumber,cur)
        result=parseToSql(afternoonClass[weekday].string)
        insertIntoDatabase(result,weekday,stuName,cardNumber,cur)
        result=parseToSql(eveningClass[weekday].string)
        insertIntoDatabase(result,weekday,stuName,cardNumber,cur)
        sql.commit()
    

def getPage(cardNumber,academicYear):
    try:
        data={"returnStr":"","queryStudentId":str(cardNumber),"queryAcademicYear":str(academicYear)}
        url="http://xk.urp.seu.edu.cn/jw_service/service/stuCurriculum.action"
        postData=urllib.urlencode(data)
        request = urllib2.Request(url=url,data=postData)
        response = urllib2.urlopen(request)
        content=response.read()
    except Exception as e:
        content="ERROR"
        print e
    return content

def task(start,end):
    global counter
    sql=MySQLdb.connect("localhost","root","neverorforever","www",charset="utf8")
    cur=sql.cursor()
    #end=start+50
    for x in range(start,end):
        try:
            print counter
            handleOnePage(getPage(str(x),"16-17-3"),sql,cur)
            counter=counter+1
        except Exception as e:
            print e
    SendMail.SendMail("497425817@qq.com","Inform",str(start)+"-"+str(end)+" Finished!")
    cur.close()
    sql.close()
def Timer():
    global counter
    while  True:
        print counter
        time.sleep(3)
#大一213160001-213163967
#大二213150001-213153986
#大三213140001-213143947
#大四213130001-213134219
thread.start_new_thread(task,(213160001,213161500))
time.sleep(0.7)
thread.start_new_thread(task,(213161500,213163000))
time.sleep(0.7)
thread.start_new_thread(task,(213163000,213163968))
time.sleep(0.7)
thread.start_new_thread(task,(213150001,213151500))
time.sleep(0.7)
thread.start_new_thread(task,(213151500,213153000))
time.sleep(0.7)
thread.start_new_thread(task,(213153000,213153986))
time.sleep(0.7)
thread.start_new_thread(task,(213140001,213141500))
time.sleep(0.7)
thread.start_new_thread(task,(213141500,213143000))
time.sleep(0.7)
thread.start_new_thread(task,(213143000,213143968))
while True:
   time.sleep(10)
   print "Sys beep"


'''
taskParamters=[x for x in range(213160001,213163967,50)]+[x for x in range(213150001,213153986,50)]+[x for x in range(213140001,213143947,50)]+[x for x in range(213130001,213134219,50)]
pool = threadpool.ThreadPool(8) 
requests = threadpool.makeRequests(task, taskParamters) 
[pool.putRequest(req) for req in requests] 
pool.wait() 
print "Done!"
'''






