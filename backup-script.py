
# -*- coding:UTF-8 -*- ＃
'''
Created on 2011-12-18

@author: Ahan
'''
import re
import sys
import os
import time
import socket
import locale
import datetime
import codecs
from urllib import urlopen

reload(sys)
sys.setdefaultencoding("utf-8")

#正则表达式定义
#匹配博文目录链接
pattern1=u"""<a  href="(http:.*?)">博文目录</a>"""
prog1 = re.compile(pattern1)
#匹配博文标题链接
pattern2=u"""<a title="(.*?)" target="_blank" href="(.*?)">.*?</a>"""
prog2=re.compile(pattern2)
#匹配下一页链接
pattern3=u"""<a href="([^"]+)" title="[^"]+">下一页"""
prog3=re.compile(pattern3)
#匹配正文部分
pattern4=u"""<!--博文正文 begin -->[\\s\\S]*?<!-- 正文结束 -->"""
prog4=re.compile(pattern4)
#匹配正文图片链接
pattern5=u"""(src="[^"]+"( real_src ="([^"]+)"))"""
prog5=re.compile(pattern5)

def read_date_from_url(url):
    """以Unicode形式返回从url上读取的所有数据
    """
    try:
        data = ""
        request = urlopen(url)
        while True:
            s = request.read(1024)
            if not s:
                break
            data += s
        return unicode(data)
    except:
        #print '读取数据时出错'
        print 'Error in reading data'
        print "Unexpected error:", sys.exc_info()[0],sys.exc_info()[1]
        return None
    finally:
        if request:
            request.close()
        
def save_to_file(url,filename,blog_address):
    """url为博文地址，filename为要保存的文件名，默认后缀为html
    """
    #如果文件夹不存在则创建文件夹
    if os.path.exists(blog_address)==False:
        os.makedirs(blog_address)
    #去掉文件名中的非法字符
    filename=ReplaceBadCharOfFileName(filename)
    file_no=0
    while os.path.isfile(blog_address+'/'+filename+'.html')==True:
        filename=filename+'('+file_no.__str__()+')'
        file_no+=1
    text = read_date_from_url(url)
    text=_filter(text)
    #将图片保存到本地
    result=prog5.findall(text)
    i=1
    for pic in result:
        folder=blog_address+'/'+filename+'/'
        pic_name='image'+i.__str__()+'.gif' 
        if os.path.exists(folder)==False:
            os.makedirs(folder)
        try:
            url_file = urlopen(pic[2])
            pic_file = codecs.open(folder+pic_name,'wb')
            while True:
                s = url_file.read(1024)
                if not s:
                    break
                pic_file.write(s)
            pic_file.close()
            url_file.close()
        except:
            #print '噢，保存图片的时候出现问题了，跳过此张图片...'
            print 'Error in saving photo, skipping this one...'
            print "Unexpected error:", sys.exc_info()[0],sys.exc_info()[1]
        else:
            #print '保存图片成功...'
            print 'successfully saved this photo...'
            #替换正文中的图片地址
            text=text.replace(pic[0],unicode("src=\"" + filename + "/" + pic_name + "\"" + pic[1]),1)
            i=i+1
    blog_file = codecs.open(blog_address+'/'+filename+'.html','wb')
    blog_file.write(text)
    blog_file.close()
    
#提取文本中的正文部分
def _filter(t):
    # """提取文本中的正文部分，返回Unicode形式的字符串
    # """
    result=prog4.search(t)
    if result is not None:
        return u'<html><head></head><body>' + unicode(result.group()) + u'</dody></html>'
    else:
        #raise Exception('噢，提取正文出错了……')
        raise Exception('Error in extracting content from blog...')

#去掉文件名的不合法字符 
def ReplaceBadCharOfFileName(filename):
    filename=filename.replace("&nbsp;","")
    filename=filename.replace("\\", "")
    filename=filename.replace("/", "")
    filename=filename.replace(":", "")
    filename=filename.replace("*", "")
    filename=filename.replace("?", "")
    filename=filename.replace("<", "")
    filename=filename.replace(">", "")
    filename=filename.replace("|", "")
    filename=filename.replace("&","")
    filename=filename.replace(";","")
    return filename
    
#主函数

if __name__ == '__main__':
    #准备阶段
    blog_no=1#博文编号
    begin=1#起始博文
    end=0#结束博文
    page=0#页码
    saved=0#成功保存的篇数
    timeout = 60*5#超时设为5分钟
    socket.setdefaulttimeout(timeout)#这里对整个socket层设置超时时间。后续文件中如果再使用到socket，不必再设置
    #blog_address=raw_input("请输入您的博客地址（输入最后部分即可，比如您的博客地址是http://blog.sina.com.cn/jiangafu，只要输入jiangafu）：")
    blog_address=raw_input("Please enter your blog user handler(e.g. if your blog url is http://blog.sina.com.cn/jiangafu, just enter jiangafu as the handler):")
    blog_address=blog_address.replace('\r','')
    #begin=raw_input('从第几篇开始：')   
    begin=raw_input('From Article No.:')   
    begin=locale.atoi(begin)
    while begin<=0:
        #begin=raw_input('请输入大于0的数：')
        begin=raw_input('Please enter a number bigger than 0:')
        begin=locale.atoi(begin)
    #end=raw_input('到第几篇结束（到最后请输入0）：')
    end=raw_input('Until Article No. (to the end please enter 0):')
    end=locale.atoi(end)
    while end<0:
        #end=raw_input('请输入大于等于0的数：')
        end=raw_input('Please enter a number that is >=0: ')
        end=locale.atoi(end)
    if end==0:
        #print '您的博客地址是：http://blog.sina.com.cn/'+blog_address+'，保存第'+begin.__str__()+'篇到最后一篇博文'
        print 'The url of your blog is: http://blog.sina.com.cn/'+blog_address+', saving the '+begin.__str__()+'th to the last blog post'
    else:
        # print '您的博客地址是：http://blog.sina.com.cn/'+blog_address+'，保存第'+begin.__str__()+'篇到第'\
        #       +end.__str__()+'篇的博文'
        print 'The url of your blog is: http://blog.sina.com.cn/'+blog_address+', saving the '+begin.__str__()+'th to the '\
              +end.__str__()+'th blog post'      
    starttime = datetime.datetime.now()
    text=read_date_from_url('http://blog.sina.com.cn/'+blog_address)
    
    time.sleep(0.5)
    #提取“博文目录”的url
    result = prog1.search(text)
    if result is not None:
        #print '博文目录地址：' , result.group(1)
        print 'URL of blog post listing: ' , result.group(1)
        text=read_date_from_url(result.group(1))
        time.sleep(0.4)
    else:
        #print '提取博文目录地址失败'
        print 'Failed to extract the blog post listing'
        #终止程序运行
        sys.exit()
    #查找每一页的全部博文，分析、提取、保存 
    while True:
        page+=1
        #print '开始备份第' , page , '页'
        print 'Start backing up the ' , page , 'th page'
        #匹配该页的所有博文地址
        result=prog2.findall(text)
        #循环下载本页每篇博文
        for blog in result: 
            if blog_no < begin:
                blog_no += 1
            elif end != 0 and blog_no > end:
                break
            else:
                try:
                    print blog
                    save_to_file(blog[1],unicode(blog[0]),blog_address)
                except:
                    #print '噢，保存第',blog_no,'篇博文',blog[0],'的时候出现问题了，跳过...'
                    print 'Error in saving the ',blog_no,'th blog post',blog[0],'Skipping this one'
                    blog_no += 1
                    print "Unexpected error:", sys.exc_info()[0],sys.exc_info()[1]
                else:
                    #print '成功保存了第', blog_no, '篇博文:', blog[0]
                    print 'successfully saved the ', blog_no, 'th blog post:', blog[0]
                    blog_no += 1
                    saved += 1
                    time.sleep(0.4)
        #判断是否有下一页
        result = prog3.search(text)
        if result is not None:
            text = read_date_from_url(result.group(1))
        else:
            #print '这是最后一页'
            print 'This is the last page'
            break
    #print '博客备份完成一共备份',saved,'篇博文'
    print 'Backed up',saved,'blog posts in total.'
    #print '共用时:',datetime.datetime.now() - starttime
    print 'Time taken:',datetime.datetime.now() - starttime
    #raw_input('按回车键退出...')
    raw_input('Press ENTER to exit...')
