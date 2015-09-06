__author__ = 'solid'
import os
import urllib2
import zipfile
import re
import requests
import threading
from Queue import Queue


GIT_RESOURCE_URL= "http://github-windows.s3.amazonaws.com"
GIT_CFG_FILE = "GitHub.application"
GIT_VERSION_DIR = "" #Application Files\GitHub_3_0_4_0
GIT_MANIFEST_FILE = "GitHub.exe.manifest"#GitHub.exe.manifest
DOWNLOAD_DIR = "./download"


def zip_dir(dirname, zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else :
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))

    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]
        #print arcname
        zf.write(tar,arcname)
    zf.close()


def listFile(fileList):
    URL = "http://github-windows.s3.amazonaws.com/%s/"%GIT_VERSION_DIR
    for fileInfo in fileList:
        name = fileInfo[0]
        if "\\" in name:
            name = name.replace("\\", "/")

        file_url = URL + name + ".deploy"
        print file_url.replace("\\", "/")


def readManifestFile():
    manifestFile = os.path.join(DOWNLOAD_DIR, GIT_VERSION_DIR, GIT_MANIFEST_FILE)
    fd = open(manifestFile, "r")
    fileList = []
    for line in fd:
        #print line
        tag = "codebase=\""
        index =  line.find(tag)
        if index > 0:
        #if "codebase=\"" in line:
            line = line[index::]
            info =  line.split("\"")

            name = info[1].replace("\\", "/")
            size = info[3]

            fileList.append([name, size])
            #print name, size
            pass

        tag = "file name="

        index =  line.find(tag)
        if index > 0:
        #if "codebase=\"" in line:
            line = line[index::]
            info =  line.split("\"")
            name = info[1].replace("\\", "/")
            size = info[3]

            #print info
            #print name, size
            fileList.append([name, size])
            pass


    # print fileList
    # listFile(fileList)
    return fileList

        #dependentAssembly dependencyType="install" allowDelayedBinding="true" codebase="Akavache.dll" size="73216">



def downloadFile(file_url):
    print "download: ", file_url

    send_headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection':'keep-alive'
    }
    r = requests.get(file_url, verify=True, headers=send_headers)
    if r.status_code == 200:
        data = r.content
        return data
    else:
        print r.status_code
        return None



def needDownLoadFile(fileDir, size):

    filePath = os.path.join(DOWNLOAD_DIR, GIT_VERSION_DIR, fileDir)
    filePath += ".deploy"
   # print "check file: ", filePath

    if os.path.exists(filePath):
        fsize = os.path.getsize(filePath)
        #print filePath, "size:", fsize, "need:", size,
        if size == fsize:
            #print "not need to download"
            return False
        else:
            # print "  !!!!!!!!!!need to download"
            pass

    return True



def saveFile(fileDir, data):
    filePath = os.path.join(DOWNLOAD_DIR, fileDir)
    if not os.path.exists(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)

    path = os.path.split(filePath)[0]
    #print "path:", path
    if not os.path.exists(path):
        os.makedirs(path)

    f = open(filePath, "wb")
    f.write(data)
    f.close()



def getConfigureFile():
    file_url = "%s/%s"%(GIT_RESOURCE_URL, GIT_CFG_FILE)

    data = downloadFile(file_url)
    print "configure file done"
    saveFile(GIT_CFG_FILE, data)

def parseConfigureFile():

    cfg_fd = open(os.path.join(DOWNLOAD_DIR, GIT_CFG_FILE))
    for line in cfg_fd:
        if "codebase" in line:
            p = re.compile(r"(.*)codebase=\"(.*)\\(.*)\" size")
            match = p.match(line)
            global GIT_VERSION_DIR
            global GIT_MANIFEST_FILE
            GIT_VERSION_DIR = match.group(2)
            GIT_MANIFEST_FILE = match.group(3)
            # codeBase = match.groups()


def getManifestFile():
    #  codebase="Application Files\GitHub_3_0_4_0\GitHub.exe.manifest"
    file_url = os.path.join(GIT_RESOURCE_URL, GIT_VERSION_DIR, GIT_MANIFEST_FILE)
    file_url = file_url.replace("\\", "/")
    print file_url

    data = downloadFile(file_url)
    manifestDir = "%s\%s"%(GIT_VERSION_DIR, GIT_MANIFEST_FILE)
    saveFile(manifestDir, data)



def collecter(work_queue):
    while True:
        work = work_queue.get()
        name, data_size = work
        #print name, data_size
        if needDownLoadFile(name, int(data_size)):
            fileUrl = "%s/%s/%s.deploy"%(GIT_RESOURCE_URL, GIT_VERSION_DIR, name)

            while True:
                data = downloadFile(fileUrl)
                if data and len(data) == int(data_size):
                    savePath = os.path.join(GIT_VERSION_DIR, name+".deploy")
                    saveFile(savePath, data)
                    work_queue.task_done()
                    break


if __name__ == "__main__":
    getConfigureFile()
    parseConfigureFile()
    getManifestFile()

    fileList = readManifestFile()

    work_queue = Queue()

    print "need download:"
    sizeLeft = 0
    for fileInfo in fileList:
        name, data_size = fileInfo
        if needDownLoadFile(name, int(data_size)):
            # print name, float(data_size)/1024/102
            fileUrl = "%s/%s/%s.deploy"%(GIT_RESOURCE_URL, GIT_VERSION_DIR, name)
            print fileUrl.replace("\\", "/")
            sizeLeft += float(data_size)
            work_queue.put(fileInfo)

    print "total size:", sizeLeft/1024/1024


    for i in range(20):
        tsk = threading.Thread(target=collecter, args=(work_queue, ))
        tsk.start()


    work_queue.join()
    print "done xxxxxxxxxxxxxxxxxxxxxxxxxxx"


    #
    # zip_dir("./Application Files/GitHub_2_5_2_2", "tesss.zip")