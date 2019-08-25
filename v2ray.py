#coding=utf-8
"""Simple HTTP Server.

This module builds on BaseHTTPServer by implementing the standard GET
and HEAD requests in a fairly straightforward manner.

"""


__version__ = "0.6"

__all__ = ["SimpleHTTPRequestHandler"]

import os
import posixpath
import BaseHTTPServer
import urllib
import urlparse
import cgi
import sys
import shutil
import mimetypes
import json
import base64
import requests 
import commands
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class SimpleHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    """Simple HTTP request handler with GET and HEAD commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method.

    The GET and HEAD requests are identical except that the HEAD
    request omits the actual contents of the file.

    """

    server_version = "SimpleHTTP/" + __version__

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def do_POST(self):
        path = self.translate_path(self.path)
        if self.path.endswith('/save_config'):
            datasets = cgi.FieldStorage(fp = self.rfile,headers = self.headers,environ = {'REQUEST_METHOD': 'POST'})
            jsonmsg = datasets.getvalue('jsonmsg')
            #print(str(jsonmsg))
            jsoninput=json.loads(urllib.unquote(base64.b64decode(str(jsonmsg))))
            fw =open('config.json','w')
            json.dump(jsoninput,fw,ensure_ascii=False,indent=4)
            (status, output)=commands.getstatusoutput('service v2ray restart')
            print status, output
            restr='ok'
            if status !=0:
                restr=output
            print restr
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(restr.decode('gbk').encode('utf-8'))
            fw.close()
            
            
            return None
        if self.path.endswith('/query_subs'):
            #print(os.getcwd()+'\ss_subs.json')
            st={}
            #print(os.getcwd()+'\\ss_subs.json')
            if os.path.isfile(os.getcwd()+'/ss_subs.json'):
                fw =open('ss_subs.json','r')
                ss=json.loads(fw.read().decode('utf-8'))
                ss=ss['servers']
                st['ss']=ss
                #ss=json.dumps(ss,indent=4).decode('unicode_escape').encode('utf-8')
            if os.path.isfile(os.getcwd()+'/v2ray_subs.json'):
                fw =open('v2ray_subs.json','r')
                v2=json.loads(fw.read().decode('utf-8'))
                st['v2']=v2
                #v2=json.dumps(v2,indent=4).decode('unicode_escape').encode('utf-8')
                
                #print(str(v2).decode('unicode_escape'))
           # print(os.getcwd()+'\\v2ray_subs.json')

            st=json.dumps(st,indent=4).decode('unicode_escape').encode('utf-8')
            #print(st)
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(st)
            fw.close()
            return None

        if self.path.endswith('/query_confList'):
            #print(os.getcwd()+'\ss_subs.json')
            st={}
            #print(os.getcwd()+'\\ss_subs.json')
            if os.path.isfile(os.getcwd()+'/confList.json'):
                fw =open('confList.json','r')
                conflist=json.loads(fw.read().decode('utf-8'))
                st['conflist']=conflist
                #v2=json.dumps(v2,indent=4).decode('unicode_escape').encode('utf-8')
                
                #print(str(v2).decode('unicode_escape'))
           # print(os.getcwd()+'\\v2ray_subs.json')

            st=json.dumps(st,indent=4).decode('unicode_escape').encode('utf-8')
            #print(st)
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(st)
            fw.close()
            return None
            
        #根据节点列表更新配置文件并重启服务
        if self.path.endswith('/save_config_subs'):
            datasets = cgi.FieldStorage(fp = self.rfile,headers = self.headers,environ = {'REQUEST_METHOD': 'POST'})
            protocol = datasets.getvalue('protocol')
            idstr = datasets.getvalue('idstr')
            print(protocol)
            print(idstr)
            if protocol=="ss":
                self.conf_ss(idstr)
            if protocol=="vmess":
                self.conf_v2ray(idstr)
            (status, output)=commands.getstatusoutput('service v2ray restart')
            print status, type(output)
            restr='ok'
            if status !=0:
                restr=output
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(restr.decode('gbk').encode('utf-8'))
            return None
        #增加订阅地址
        if self.path.endswith('/addsubsurl'):
            datasets = cgi.FieldStorage(fp = self.rfile,headers = self.headers,environ = {'REQUEST_METHOD': 'POST'})
            urldata = datasets.getvalue('urldata')
            urldata=urllib.unquote(base64.b64decode(str(urldata)))
            if os.path.isfile(os.getcwd()+'/subsList.json')==False:
                f=open('subsList.json','w')
                f.close()
            f=open('subsList.json','rb+')
            subsList=f.read()
            isjson=True
            try:
                json.loads(subsList)
            except ValueError:
                isjson = False
            print(isjson,subsList)
            if isjson:
                subsList=json.loads(subsList)
                isexists=False
                for i in subsList:
                    if i['url']==urldata:
                        isexists=True
                        break;
                if isexists==False:
                    subsList.append(dict([('url'.decode('utf-8'),urldata.decode('utf-8'))])) #追加jsonarray
                    fw=open('subsList.json','wb')
                    json.dump(subsList,fw,ensure_ascii=False,indent=4)
                    fw.close()
            else:
                subsList=[1]
                subsList[0]=dict([('url',urldata)])
                fw=open('subsList.json','wb')
                json.dump(subsList,fw,ensure_ascii=False,indent=4)
            f.close()
            #print(subsList)
            subsList=json.dumps(subsList,indent=4).decode('unicode_escape').encode('utf-8')
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(subsList)
            return None
            
        #增加自定义配置
        if self.path.endswith('/save_conflist'):
            datasets = cgi.FieldStorage(fp = self.rfile,headers = self.headers,environ = {'REQUEST_METHOD': 'POST'})
            conf = datasets.getvalue('conf')
            #conf=urllib.unquote(base64.b64decode(str(conf)))
            name = datasets.getvalue('name')
            name=urllib.unquote(base64.b64decode(str(name)))
            if os.path.isfile(os.getcwd()+'/confList.json')==False:
                f=open('confList.json','w')
                f.close()
            f=open('confList.json','rb+')
            confList=f.read()
            isjson=True
            try:
                json.loads(confList)
            except ValueError:
                isjson = False
            #print(isjson,confList)
            if isjson:
                confList=json.loads(confList)
                confList1=[1]
                confList1[0]=dict([('name',name),('conf',conf)])
                for i in confList:
                    if i['name'].encode('utf-8')==name:
                        continue
                    confList1.append(dict([('name',i['name'].encode('utf-8')),('conf',i['conf'].encode('utf-8'))])) #追加jsonarray
                fw=open('confList.json','wb')
                #print(confList1)
                json.dump(confList1,fw,ensure_ascii=False,indent=4)
                fw.close()
                confList=confList1
            else:
                confList=[1]
                confList[0]=dict([('name',name),('conf',conf)])
                fw=open('confList.json','wb')
                #print(confList)
                json.dump(confList,fw,ensure_ascii=False,indent=4)
                fw.close()
            f.close()
            #print(subsList)
            confList=json.dumps(confList,indent=4).decode('unicode_escape').encode('utf-8')
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(confList)
            return None

        #删除自定义配置
        if self.path.endswith('/delconf'):
            datasets = cgi.FieldStorage(fp = self.rfile,headers = self.headers,environ = {'REQUEST_METHOD': 'POST'})
            name = datasets.getvalue('name')
            name=urllib.unquote(base64.b64decode(str(name)))

            if os.path.isfile(os.getcwd()+'/confList.json')==False:
                f=open('confList.json','w')
                f.close()
            f=open('confList.json','rb+')
            confList=f.read()
            isjson=True
            try:
                json.loads(confList)
            except ValueError:
                isjson = False
            #print(isjson,confList)
            if isjson:
                confList=json.loads(confList)
                confList1=[]
                #confList1[0]=dict([('name',name),('conf',conf)])
                for i in confList:
                    if i['name'].encode('utf-8')==name:
                        continue
                    confList1.append(dict([('name',i['name'].encode('utf-8')),('conf',i['conf'].encode('utf-8'))])) #追加jsonarray
                fw=open('confList.json','wb')
                #print(confList1)
                json.dump(confList1,fw,ensure_ascii=False,indent=4)
                fw.close()
                confList=confList1


            f.close()
            #print(subsList)
            confList=json.dumps(confList,indent=4).decode('unicode_escape').encode('utf-8')
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(confList)
            return None
            
        #查询订阅地址
        if self.path.endswith('/querysubsurl'):
            f=open('subsList.json','r')
            subsList=f.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(subsList)
            return None

        #更新订阅地址
        if self.path.endswith('/update_subs'):
            datasets = cgi.FieldStorage(fp = self.rfile,headers = self.headers,environ = {'REQUEST_METHOD': 'POST'})
            urldata = datasets.getvalue('subsurl')
            urldata=urllib.unquote(base64.b64decode(str(urldata)))
            print(urldata)
            self.subscribe(urldata)
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("ok")
            return None
        #删除订阅地址
        if self.path.endswith('/delsubs'):
            datasets = cgi.FieldStorage(fp = self.rfile,headers = self.headers,environ = {'REQUEST_METHOD': 'POST'})
            urldata = datasets.getvalue('subsurl')
            urldata=urllib.unquote(base64.b64decode(str(urldata)))
            print(urldata)
            if os.path.isfile(os.getcwd()+'/subsList.json')==False:
                f=open('subsList.json','w')
                f.close()
            f=open('subsList.json','rb+')
            subsList=f.read()
            isjson=True
            try:
                json.loads(subsList)
            except ValueError:
                isjson = False
            print(isjson,subsList)
            if isjson:
                subsList=json.loads(subsList)
                isexists=False
                ii=0
                for i in subsList:
                    if i['url']==urldata:
                        del subsList[ii]
                        print(subsList)
                    ii=ii+1
                if isexists==False:
                    fw=open('subsList.json','wb')
                    json.dump(subsList,fw,ensure_ascii=False,indent=4)
                    fw.close()
            f.close()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("ok")
            return None
        #查询默认配置
        if self.path.endswith('/querydefult'):
            #print(123)
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            fv=open("demon.json","r")
            res=fv.read()
            self.wfile.write(json.dumps(json.loads(res),ensure_ascii=False,indent=4))
            fv.close()
            return None

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        print(path)
        if self.path.endswith('/v2ray_config'):
            #print(123)
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            fv=open("config.json","r")
            res=fv.read()
            self.wfile.write(json.dumps(json.loads(res),ensure_ascii=False,indent=4))
            fv.close()
            return None
        if os.path.isdir(path):
            parts = urlparse.urlsplit(self.path)
            if not parts.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                new_parts = (parts[0], parts[1], parts[2] + '/',
                             parts[3], parts[4])
                new_url = urlparse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        try:
            self.send_response(200)
            self.send_header("Content-type", ctype)
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            return f
        except:
            f.close()
            raise

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>Directory listing for %s</title>\n" % displaypath)
        f.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
        f.write("<hr>\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write('<li><a href="%s">%s</a>\n'
                    % (urllib.quote(linkname), cgi.escape(displayname)))
        f.write("</ul>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })

    #base64补足=号
    def fill_padding(self,base64str):
        b=len(base64str)%4!=0
        if b :
            m=4-b
            base64str+='='*m
        return base64str
 
        #更新订阅
    def subscribe(self,url):
        r = requests.get(url) 
        #将订阅内容放到变量中
        dystr=r.content 
        #如果是ss订阅
        if dystr.startswith("ssd://"): 
            dystr=dystr[6:]
            with open("ss_subs.json","wb") as code: 
                #对订阅内容解码
                dystr=base64.urlsafe_b64decode(self.fill_padding(dystr))
                #print(dystr)
                #dystr=json.loads(str(dystr).encode('utf-8'))
                dystr=dystr.decode('unicode_escape') #如果字符串中文/u开头用 decode('unicode_escape')解码
                dystr=dystr.encode('utf-8') #写入时编码成需要的编码形式
                #print(type(dystr))
                code.write(dystr)
        else:
            dystr=base64.urlsafe_b64decode(self.fill_padding(dystr))
            if dystr.startswith('vmess'):
                vmessstr='['
                dystr=dystr.split('vmess://')
                print len(dystr)
                for i in dystr:
                    if len(i)>10:
                        vmessstr+= base64.urlsafe_b64decode(self.fill_padding(i)).decode('utf-8')+','
                vmessstr=vmessstr[0:len(vmessstr)-1]+']'
                #print (vmessstr)
                with open("v2ray_subs.json","wb") as code:
                    vmessstr=json.loads(vmessstr)
                    vmessstr=json.dumps(vmessstr, indent=4)
                    code.write(vmessstr.decode('unicode_escape').encode('utf-8'))

#根据传入参数查找订阅信息并更新配置文件
    def conf_v2ray(self,addr):
        f=open('demon.json','r')
        fs=open('v2ray_subs.json','r')
        subs=json.loads(fs.read())
        for j in subs:
            if j['add']==addr:
                subs=j
        print j
        s=f.read()
        ss=json.loads(s)
        jsonstr=ss['outbounds']
        for i in jsonstr:
            if i['protocol']=='vmess' :
                jsonstr=i
        for i in jsonstr['settings']['vnext']:
            i['address']=subs['add']
            i['port']=int(subs['port'])
            i['users'][0]['id']=subs['id']
            i['users'][0]['alterId']=int(subs['aid'])
        if subs['type']=='none':
            jsonstr['streamSettings']['tcpSettings']=None
        print ss
        with open('config.json','w') as code:
            json.dump(ss,code,ensure_ascii=False,indent=4)
       
        
#根据传入参数查找订阅信息并更新配置文件
    def conf_ss(self,idnum):
        f=open('demon.json','r')
        fs=open('ss_subs.json','r')
        subs=json.loads(fs.read())
        for j in subs['servers']:
            if j['id']==int(idnum):
                serverstr=j
                print serverstr
        s=f.read()
        ss=json.loads(s)
        jsonstr=ss['outbounds']
        for i in jsonstr:
            if i['protocol']=='vmess' :
                jsonstr=i
                i['protocol']='shadowsocks'
                del i['mux']
        del jsonstr['settings']['vnext']
        print type(jsonstr)
        jsonstr['settings']['servers']=[1]
        #jsonstr['settings']['servers'][0]=dict([('address',serverstr['server']),('method',subs['encryption']),('ota',True),('password',subs['password']),('port',int(subs['port']))]) 
        jsonstr['settings']['servers'][0]=dict([('address',serverstr['server']),('method',subs['encryption']),('password',subs['password']),('port',int(subs['port']))])
    
        del jsonstr['streamSettings']['tcpSettings']
        del jsonstr['streamSettings']['network']
        print ss
        with open('config.json','w') as code:
            json.dump(ss,code,ensure_ascii=False,indent=4)
        

def test(HandlerClass = SimpleHTTPRequestHandler,
         ServerClass = BaseHTTPServer.HTTPServer):
    BaseHTTPServer.test(HandlerClass, ServerClass)


if __name__ == '__main__':
    test()
