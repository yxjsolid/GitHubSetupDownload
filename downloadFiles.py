__author__ = 'solid'
import os
import urllib2
import zipfile

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
    URL = "http://github-windows.s3.amazonaws.com/Application%20Files/GitHub_2_5_2_2/"
    for fileInfo in fileList:
        name = fileInfo[0]
        if "\\" in name:
            name = name.replace("\\", "/")


        file_url = URL + name + ".deploy"
        print file_url


def readConfigure():
    cfgFile = "GitHub.exe.manifest"

    fd = open(cfgFile, "r")

    #lines =  fd.readlines()

    fileList = []

    for line in fd:
        #print line

        tag = "codebase=\""

        index =  line.find(tag)
        if index > 0:
        #if "codebase=\"" in line:
            line = line[index::]
            info =  line.split("\"")

            name = info[1]
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
            name = info[1]
            size = info[3]

            #print info
            #print name, size
            fileList.append([name, size])
            pass


    print fileList


    listFile(fileList)


    return fileList

        #dependentAssembly dependencyType="install" allowDelayedBinding="true" codebase="Akavache.dll" size="73216">



def downloadFile(file_name):

    URL = "http://github-windows.s3.amazonaws.com/Application%20Files/GitHub_2_5_2_2/"
    if "\\" in file_name:
        file_name = file_name.replace("\\", "/")



    file_url = URL + file_name + ".deploy"

    print file_url

    request = urllib2.Request(file_url)

    f = urllib2.urlopen(request)
    #data = urllib2.urlopen(request).read()
    data = f.read()
    print "size ", len(data)

    fileName = file_name +".deploy"

    saveFile(fileName, data)


def needDownLoadFile(fileDir, size):
    root = ".\\Application Files\\GitHub_2_5_2_2"
    filePath = os.path.join(root, fileDir)
    filePath += ".deploy"


    print filePath

    if os.path.exists(filePath):
        fsize = os.path.getsize(filePath)
        print filePath, "size:", fsize, "need:", size,



        if size == fsize:
            #print "not need to download"
            return False
        else:
            print "  !!!!!!!!!!need to download"

    return True



def saveFile(fileDir, data):
    root = "./Application Files/GitHub_2_5_2_2"
    filePath = os.path.join(root, fileDir)

    path = os.path.split(filePath)[0]

    if not os.path.exists(path):
        os.mkdir(path)

    f = open(filePath, "wb")
    f.write(data)
    f.close()



if __name__ == "__main__":
    print "aaa"

    #fileList = readConfigure()
    #
    #for fileInfo in fileList:
    #    name, size = fileInfo
    #
    #    if needDownLoadFile(name, int(size)):
    #        downloadFile(name)
    #
    #
    #print "done"

    for aaa in  os.walk("./Application Files/GitHub_2_5_2_2"):
        print aaa


    zip_dir("./Application Files/GitHub_2_5_2_2", "tesss.zip")