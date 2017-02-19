#*-* coding:utf-8 *-*
import socket
socket.setdefaulttimeout(10.0)
import urllib
import urllib2
import sys
reload(sys)
sys.setdefaultencoding('utf8')
def getPage(cardNumber):
    try:
        data={"returnStr":"","queryStudentId":str(cardNumber),"queryAcademicYear":"16-17-2"}
        url="http://xk.urp.seu.edu.cn/jw_service/service/stuCurriculum.action"
        postData=urllib.urlencode(data)
        request = urllib2.Request(url=url,data=postData)
        response = urllib2.urlopen(request)
        content=response.read()
    except:
        content="ERROR"
    return content
def parseData(cont,mark1):
    try:
        index1=cont.find(mark1)
        index2=cont.find("</td>",index1)
        output=cont[index1:index2]
    except:
        output="ERROR"
    return output
if __name__=="__main__":
    cont=getPage(213151267)
    open("web.html","w").write(cont)
    print "Done!"