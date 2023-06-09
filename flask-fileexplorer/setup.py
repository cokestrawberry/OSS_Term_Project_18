from flask import Flask, render_template, request, send_file, redirect, session, jsonify
from werkzeug.utils import secure_filename
from hurry.filesize import size
from datetime import datetime
from flask_fontawesome import FontAwesome
from flask_qrcode import QRcode
from pathlib import Path
import os
import mimetypes
import sys
import re
import json
import zipfile
import filetype

# ====================================
# OSS Code
import git
repo_str = ""
# ====================================

from urllib.parse import unquote
import socket
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
print("Your Computer Name is: " + hostname)
print("Your Computer IP Address is: " + IPAddr)
maxNameLength = 15


app = Flask(__name__)
#app.config["SERVER_NAME"] = "wifile.com"
app.secret_key = 'my_secret_key'

# FoNT AWESOME
fa = FontAwesome(app)
# QRcode
qrcode = QRcode(app)
# Config file
config = os.path.abspath(os.path.join(os.path.dirname(__file__), "config.json"))
with open(config) as json_data_file:
    data = json.load(json_data_file)
hiddenList = data["Hidden"]
favList = data["Favorites"]
password = data["Password"]

currentDirectory = data["rootDir"]
osWindows = False  # Not Windows
default_view = 0
tp_dict = {'image': [['png', "jpg", 'svg'], 'image-icon.png'],
           'audio': [['mp3', 'wav'], 'audio-icon.png'], 
           'video': [['mp4', 'flv'], 'video-icon.png'],
           "pdf": [['pdf'], 'pdf-icon.png'],
           "word": [['docx', 'doc'], 'doc-icon.png'],
           "txt": [['txt'], 'txt-icon.png'],
           "compressed":[["zip", "rar"], 'copressed-icon.png'],
           "code": [['css', 'scss', 'html', 'py', 'js', 'cpp'], 'code-icon.png']
           }
supported_formats = video_types = ['mp4', "webm", "opgg",'mp3', 'pdf', 'txt', 'html', 'css', 'svg', 'js', 'png', 'jpg']

if 'win32' in sys.platform or 'win64' in sys.platform:
    # import win32api
    osWindows = True
    # WINDOWS FEATURE
    # drives = win32api.GetLogicalDriveStrings()
    # drives=drives.replace('\\','')
    # drives = drives.split('\000')[:-1]
    # drives.extend(favList)
    # favList=drives

if(len(favList) > 3):
    favList = favList[0:3]
# print(favList)
# if(len(favList)>0):
#     for i in range(0,len(favList)):

#         favList[i]=favList[i].replace('\\','>') #CHANGE FOR MAC

# WINDOWS FEATURE
# drives = win32api.GetLogicalDriveStrings()
# drives=drives.replace('\\','')
# drives = drives.split('\000')[:-1]
# drives.extend(favList)
# favList=drives

def make_zipfile(output_filename, source_dir):
    relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(source_dir):
            # add directory (needed for empty dirs)
            zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename):  # regular files only
                    arcname = os.path.join(
                        os.path.relpath(root, relroot), file)
                    zip.write(filename, arcname)


@app.route('/login/')
@app.route('/login/<path:var>')
def loginMethod(var=""):
    global password
    # print("LOGGING IN")
    # print(var)
    if(password == ''):
        session['login'] = True
    if('login' in session):
        return redirect('/'+var)
    else:
        return render_template('login.html')


@app.route('/login/', methods=['POST'])
@app.route('/login/<path:var>', methods=['POST'])
def loginPost(var=""):
    global password
    text = request.form['text']
    if(text == password):
        session['login'] = True
        return redirect('/'+var)
    else:
        return redirect('/login/'+var)


@app.route('/logout/')
def logoutMethod():
    if('login' in session):
        session.pop('login', None)
    return redirect('/login/')

# @app.route('/exit/')
# def exitMethod():
#    exit()


def hidden(path):
    for i in hiddenList:
        if i != '' and i in path:
            return True
    return False


def changeDirectory(path):
    global currentDirectory, osWindows
    pathC = path.split('/')
    # print(path)
    if(osWindows):
        myPath = '//'.join(pathC)+'//'
    else:
        myPath = '/'+'/'.join(pathC)
    # print(myPath)
    myPath = unquote(myPath)
    # print("HELLO")
    # print(myPath)
    try:
        os.chdir(myPath)
        ans = True
        if (osWindows):
            if(currentDirectory.replace('/', '\\') not in os.getcwd()):
                ans = False
        else:
            if(currentDirectory not in os.getcwd()):
                ans = False
    except:
        ans = False
    return ans

# def getDirList():
#     dList= list(filter(lambda x: os.path.isdir(x), os.listdir('.')))
#     finalList = []
#     curDir=os.getcwd()

#     for i in dList:
#         if(hidden(curDir+'/'+i)==False):
#             finalList.append(i)

#     return(finalList)

@app.route('/changeView')
def changeView():
    global default_view
    # print('view received')
    v = int(request.args.get('view', 0))
    if v in [0, 1]:
        default_view = v
    else:
        default_view = 0

    return jsonify({
        "txt": default_view,
    })


def getDirList():
    # print(default_view)
    global maxNameLength, tp_dict, hostname
    dList = list(os.listdir('.'))
    dList = list(filter(lambda x: os.path.isdir(x), os.listdir('.')))
    dir_list_dict = {}
    fList = list(filter(lambda x: not os.path.isdir(x), os.listdir('.')))
    file_list_dict = {}
    curDir = os.getcwd()
    # print(os.stat(os.getcwd()))
    for i in dList:
        if(hidden(curDir+'/'+i) == False):
            # ===============================
            # orgin
            # image = 'folder5.png'
            # OSS code
            image = 'folder5.png'
            try:
                if '.git' in list(os.listdir(curDir+'/'+i)):
                    image = 'folder5_g.png'
            except:
                print()
            # ===============================
            if len(i) > maxNameLength:
                dots = "..."
            else:
                dots = ""
            dir_stats = os.stat(i)
            dir_list_dict[i] = {}
            dir_list_dict[i]['f'] = i[0:maxNameLength]+dots
            dir_list_dict[i]['f_url'] = re.sub("#", "|HASHTAG|", i)
            dir_list_dict[i]['currentDir'] = curDir
            dir_list_dict[i]['f_complete'] = i
            dir_list_dict[i]['image'] = image
            dir_list_dict[i]['dtc'] = datetime.utcfromtimestamp(dir_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            dir_list_dict[i]['dtm'] = datetime.utcfromtimestamp(dir_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            dir_list_dict[i]['size'] = "---"

    from utils import get_file_extension
    for i in fList:
        if(hidden(curDir+'/'+i) == False):
            image = None
            try:
                tp = get_file_extension(i)
                for file_type in tp_dict.values():
                    if tp in file_type[0]:
                        # ====================================
                        # origin
                        ## image = "files_icon/"+file_type[1]
                        # OSS Code
                        if isGitRepo():
                            if getFileStatus(i)!="committed":
                                image = "files_icon/" + file_type[1][:-4] + "-" + getFileStatus(i) + ".png"
                            else:
                                image = "files_icon/" + file_type[1]
                        else:
                            image = "files_icon/"+file_type[1]                        
                        # ====================================
                        break
                tp = "" if not tp else tp
            except:
                pass
            if not image:
                image = 'files_icon/unknown-icon.png'
            if len(i) > maxNameLength:
                dots = "..."
            else:
                dots = ""
            file_list_dict[i] = {}
            file_list_dict[i]['f'] = i[0:maxNameLength]+dots
            file_list_dict[i]['f_url'] = re.sub("#", "|HASHTAG|", i)
            file_list_dict[i]['currentDir'] = curDir
            file_list_dict[i]['f_complete'] = i
            file_list_dict[i]['image'] = image
            file_list_dict[i]['supported'] = True if tp.lower() in supported_formats else False
            try:
                dir_stats = os.stat(i)
                file_list_dict[i]['dtc'] = datetime.utcfromtimestamp(dir_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                file_list_dict[i]['dtm'] = datetime.utcfromtimestamp(dir_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                file_list_dict[i]['size'] = size(dir_stats.st_size)
                file_list_dict[i]['size_b'] = dir_stats.st_size
            except:
                file_list_dict[i]['dtc'] = "---"
                file_list_dict[i]['dtm'] = "---"
                file_list_dict[i]['size'] = "---"
            # ====================================
            # OSS Code
            if isGitRepo():
                file_list_dict[i]['state'] = getFileStatus(i)
            else:
                file_list_dict[i]['state'] = None
            # ====================================
    return dir_list_dict, file_list_dict


def getFileList():
    dList = list(filter(lambda x: os.path.isfile(x), os.listdir('.')))
    finalList = []
    curDir = os.getcwd()
    for i in dList:
        if(hidden(curDir+'/'+i) == False):
            finalList.append(i)
    return(finalList)


@app.route('/files/', methods=['GET'])
@app.route('/files/<path:var>', methods=['GET'])
def filePage(var=""):
    global default_view
    # ====================================
    # OSS Code
    global repo_str
    repo_str = var
    
    isgit = False
    # ====================================
    if('login' not in session):
        return redirect('/login/files/'+var)
    # print(var)
    if(changeDirectory(var) == False):
        # Invalid Directory
        print("Directory Doesn't Exist")
        return render_template('404.html', errorCode=300, errorText='Invalid Directory Path', favList=favList)

    try:
        dir_dict, file_dict = getDirList()
        if default_view == 0:
            var1, var2 = "DISABLED", ""
            default_view_css_1, default_view_css_2 = '', 'style=display:none'
        else:
            var1, var2 = "", "DISABLED"
            default_view_css_1, default_view_css_2 = 'style=display:none', ''
    except:
        return render_template('404.html', errorCode=200, errorText='Permission Denied', favList=favList)
    if osWindows:
        cList = var.split('/')
        var_path = '<a style = "color:black;"href = "/files/' + \
            cList[0]+'">'+unquote(cList[0])+'</a>'
        for c in range(1, len(cList)):
            var_path += ' / <a style = "color:black;"href = "/files/' + \
                '/'.join(cList[0:c+1])+'">'+unquote(cList[c])+'</a>'
    else:
        cList = var.split('/')
        var_path = '<a href = "/files/"><img src = "/static/root.png" style = "height:25px;width: 25px;">&nbsp;</a>'
        for c in range(0, len(cList)):
            var_path += ' / <a style = "color:black;"href = "/files/' + \
                '/'.join(cList[0:c+1])+'">'+unquote(cList[c])+'</a>'
            
    # ====================================
    # origin
    ## return render_template('home.html', currentDir=var, favList=favList, default_view_css_1=default_view_css_1, default_view_css_2=default_view_css_2, view0_button=var1, view1_button=var2, currentDir_path=var_path, dir_dict=dir_dict, file_dict=file_dict)
    # OSS Code
    # 현재 디렉토리가 git repo인지 판단
    isgit = isGitRepo()

    if isgit:
        parsed_status = gitStatus_parsing()
        branch_list = getBranchNameList()
        repo = git.Repo(var)
        changed_list = getChangedList()
        tracked_list = getTrackedList()
        untracked_list = getUntrackedList()
        branch_commit = getBranchCommits()

        try:
            cur_branch = repo.active_branch.name
        except:
            if(repo.head.is_detached):
                cur_branch = 'DETACHED_HEAD'
            else:
                cur_branch = ''
        return render_template('home.html', currentDir=var, favList=favList, default_view_css_1=default_view_css_1, default_view_css_2=default_view_css_2, view0_button=var1, view1_button=var2, currentDir_path=var_path, dir_dict=dir_dict, file_dict=file_dict, isgit=isgit, parsed_status=parsed_status, currentBranch_name = cur_branch, branch_list=branch_list, changed_list=changed_list, tracked_list=tracked_list, untracked_list=untracked_list, branch_commit=branch_commit)
    
    return render_template('home.html', currentDir=var, favList=favList, default_view_css_1=default_view_css_1, default_view_css_2=default_view_css_2, view0_button=var1, view1_button=var2, currentDir_path=var_path, dir_dict=dir_dict, file_dict=file_dict, isgit=isgit, parsed_status=None)
    # ====================================

@app.route('/', methods=['GET'])
def homePage():
    global currentDirectory, osWindows
    if('login' not in session):
        return redirect('/login/')
    if osWindows:
        if(currentDirectory == ""):
            return redirect('/files/C:')
        else:
            # cura = currentDirectory
            cura = '>'.join(currentDirectory.split('\\'))
            return redirect('/files/'+cura)
    else:
        return redirect('/files/'+currentDirectory)
        # REDIRECT TO UNTITLED OR C DRIVE FOR WINDOWS OR / FOR MAC


@app.route('/browse/<path:var>', defaults={"browse":True})
@app.route('/download/<path:var>', defaults={"browse":False})
def browseFile(var, browse):
    var = var.replace("|HASHTAG|", "#")
    if('login' not in session):
        return redirect('/login/download/'+var)
    # os.chdir(currentDirectory)
    pathC = unquote(var).split('/')
    #print(var)
    if(pathC[0] == ''):
        pathC.remove(pathC[0])
    # if osWindows:
    #     fPath = currentDirectory+'//'.join(pathC)
    # else:
    #     fPath = '/'+currentDirectory+'//'.join(pathC)
    if osWindows:
        fPath = '//'.join(pathC)
    else:
        fPath = '/'+'//'.join(pathC)
    # print("HELLO")
    # print('//'.join(fPath.split("//")[0:-1]))
    # print(hidden('//'.join(fPath.split("//")[0:-1])))
    f_path_hidden = '//'.join(fPath.split("//")[0:-1])
    if(hidden(f_path_hidden) == True or changeDirectory(f_path_hidden) == False):
        # FILE HIDDEN
        return render_template('404.html', errorCode=100, errorText='File Hidden', favList=favList)
    fName = pathC[len(pathC)-1]
    #print(fPath)
    if browse:
        from utils import is_media
        is_media_file = is_media(fPath)
        if is_media_file:
            from utils import get_file
            return get_file(fPath, is_media_file)
    return send_file(fPath)
    try:
        return send_file(fPath, download_name=fName)
    except:
        return render_template('404.html', errorCode=200, errorText='Permission Denied', favList=favList)


@app.route('/downloadFolder/<path:var>')
def downloadFolder(var):
    if('login' not in session):
        return redirect('/login/downloadFolder/'+var)
    pathC = var.split('/')
    if(pathC[0] == ''):
        pathC.remove(pathC[0])
    if osWindows:
        fPath = '//'.join(pathC)
    else:
        fPath = '/'+'//'.join(pathC)
    f_path_hidden = '//'.join(fPath.split("//")[0:-1])
    if(hidden(f_path_hidden) == True or changeDirectory(f_path_hidden) == False):
        # FILE HIDDEN
        return render_template('404.html', errorCode=100, errorText='File Hidden', favList=favList)
    fName = pathC[len(pathC)-1]+'.zip'
    downloads_folder = str(Path.home() / "Downloads\\temp")
    if not os.path.exists(downloads_folder):
        os.mkdir(downloads_folder)
    try:
        make_zipfile(downloads_folder+'\\abc.zip', os.getcwd())
        return send_file(downloads_folder+'\\abc.zip', attachment_filename=fName)
    except Exception as e:
        print(e)
        return render_template('404.html', errorCode=200, errorText='Permission Denied', favList=favList)


@app.errorhandler(404)
def page_not_found(e):
    if('login' not in session):
        return redirect('/login/')
    # note that we set the 404 status explicitly
    return render_template('404.html', errorCode=404, errorText='Page Not Found', favList=favList), 404


@app.route('/upload/', methods=['GET', 'POST'])
@app.route('/upload/<path:var>', methods=['GET', 'POST'])
def uploadFile(var=""):
    if('login' not in session):
        return render_template('login.html')
    text = ""
    if request.method == 'POST':
        pathC = var.split('/')
        if(pathC[0] == ''):
            pathC.remove(pathC[0])
        # if osWindows:
        #     fPath = currentDirectory+'//'.join(pathC)
        # else:
        #     fPath = '/'+currentDirectory+'//'.join(pathC)
        if osWindows:
            fPath = '//'.join(pathC)
        else:
            fPath = '/'+'//'.join(pathC)
        f_path_hidden = fPath
        # print(f_path_hidden)
        # print(hidden(f_path_hidden))
        if(hidden(f_path_hidden) == True or changeDirectory(f_path_hidden) == False):
            # FILE HIDDEN
            return render_template('404.html', errorCode=100, errorText='File Hidden', favList=favList)
        files = request.files.getlist('files[]')
        fileNo = 0
        for file in files:
            fupload = os.path.join(fPath, file.filename)
            if secure_filename(file.filename) and not os.path.exists(fupload):
                try:
                    file.save(fupload)
                    print(file.filename + ' Uploaded')
                    text = text + file.filename + ' Uploaded<br>'

                    fileNo = fileNo + 1
                except Exception as e:
                    print(file.filename + ' Failed with Exception '+str(e))
                    text = text + file.filename + \
                        ' Failed with Exception '+str(e) + '<br>'
                    continue
            else:
                print(file.filename +
                      ' Failed because File Already Exists or File Type Issue')
                text = text + file.filename + \
                    ' Failed because File Already Exists or File Type not secure <br>'
    fileNo2 = len(files)-fileNo
    return render_template('uploadsuccess.html', text=text, fileNo=fileNo, fileNo2=fileNo2, favList=favList)


@app.route('/qr/<path:var>')
def qrFile(var):
    global hostname
    if('login' not in session):
        return redirect('/login/qr/'+var)
    # os.chdir(currentDirectory)
    pathC = unquote(var).split('/')
    if(pathC[0] == ''):
        pathC.remove(pathC[0])
    if osWindows:
        fPath = '//'.join(pathC)
    else:
        fPath = '/'+'//'.join(pathC)
    f_path_hidden = '//'.join(fPath.split("//")[0:-1])
    if(hidden(f_path_hidden) == True or changeDirectory(f_path_hidden) == False):
        # FILE HIDDEN
        return render_template('404.html', errorCode=100, errorText='File Hidden', favList=favList)
    fName = pathC[len(pathC)-1]
    qr_text = 'http://'+hostname+"//download//"+fPath
    return send_file(qrcode(qr_text, mode="raw"), mimetype="image/png")
    return send_file(fPath, attachment_filename=fName)

# ====================================
# OSS Code

# getFileStatus:
#   파일 이름을 받아서 untracked / modified / staging / committed 를 판단
#   순서대로 ["untracked", "modified", "staged", ""]으로 return
def getFileStatus(filename=""):
    state = ["untracked", "modified", "staged", "committed"]
    ret = 0

    ## git status parsing
    status_l = gitStatus_parsing()

    untracked = status_l['untracked']
    modified = status_l['modified']
    staging = status_l['staged']
    
    for i in untracked:
        if filename in untracked:
            return state[0]
    for i in modified:
        if filename in i:
            return state[1]
    for i in staging:
        if filename in i:
            return state[2]
    return state[3] 

# isGitRepo:
#   현재 디렉토리 내에 .git repo가 있는지 판단
#       존재하는 경우 -> return True
#       존재하지 않는 경우 -> return False
def isGitRepo():
    dList = list(filter(lambda x: os.path.isdir(x), os.listdir('.')))

    if ".git" in dList:
        return True
    else:
        return False

# gitInit:
#   ./laouy.html 에 선언된 git_init 버튼이 눌릴 경우 작동하는 함수
#   현재 directory에 git init 실행

@app.route('/git_init/', methods=['POST'])
@app.route('/git_init/<path:var>', methods=['POST'])

def gitInit(var=""):
    global repo_str

    curDir = var

    repo = git.Repo.init(curDir)
    repo_str = curDir

    # print("git init done")
    return filePage(var)


# gitAdd:
#   ./laouy.html 에 선언된 git_add 버튼이 눌릴 경우 작동하는 함수
#   현재 directory에 git add 실행

@app.route('/git_add/', methods=['POST'])
@app.route('/git_add/<path:var>', methods=['POST'])
def gitAdd(var=""):
    f = var.split('/')[-1]
    var = '/'.join(var.split('/')[:-1])
    
    cmd = 'git add ' + f
    print(cmd)
    os.system(cmd)

    # print("git add " + f + " done")
    return filePage(var)


# gitRestore:
#   ./laouy.html 에 선언된 git_restore 버튼이 눌릴 경우 작동하는 함수
#   현재 directory에 git restore ~~ 실행

@app.route('/git_restore/', methods=['POST'])
@app.route('/git_restore/<path:var>', methods=['POST'])
def gitRestore(var=""):
    fn = var.split('/')[-2]
    fs = var.split('/')[-1]
    var = '/'.join(var.split('/')[:-2])

    repo = git.Repo(var)

    cmd = "git restore "
    if fs=="modified":
        cmd = cmd + fn
        os.system(cmd)
        print("git restore " + fn + " done")
    elif fs=="staged":
        cmd = cmd + "--staged " + fn
        print(cmd)
        os.system(cmd)
        print("git restore --staged " + fn + " done")

    return filePage(var)

# gitRm_untracking:
#   ./laouy.html 에 선언된 git_rm_u 버튼이 눌릴 경우 작동하는 함수
#   현재 directory에 git rm --cached 실행
@app.route('/git_rm_u/', methods=['POST'])
@app.route('/git_rm_u/<path:var>', methods=['POST'])
def gitRm_u(var=""):
    fn = var.split('/')[-2]
    fs = var.split('/')[-1]
    var = '/'.join(var.split('/')[:-2])

    cmd = 'git rm --cached ' + fn
    os.system(cmd)
    print(cmd + " done")

    return filePage(var)

# gitRm_deleting:
#   ./laouy.html 에 선언된 git_rm_d 버튼이 눌릴 경우 작동하는 함수
#   현재 directory에 git rm 실행
@app.route('/git_rm_d/', methods=['POST'])
@app.route('/git_rm_d/<path:var>', methods=['POST'])
def gitRm_d(var=""):
    fn = var.split('/')[-2]
    fs = var.split('/')[-1]
    var = '/'.join(var.split('/')[:-2])

    cmd = 'git rm ' + fn
    os.system(cmd)
    print(cmd + " done")

    return filePage(var)

# gitMv:
#   ./laouy.html 에 선언된 git_mv 버튼이 눌릴 경우 작동하는 함수
#   현재 directory에 git mv ~~ 실행
@app.route('/git_mv/', methods=['POST'])
@app.route('/git_mv/<path:var>', methods=['POST'])
def gitMv(var=""):
    fn = var.split('/')[-1]
    var = '/'.join(var.split('/')[:-1])

    rename = request.form['mv_name']
    cmd = 'git mv ' + fn + ' ' + rename
    os.system(cmd)

    print(cmd + " done")

    return filePage(var)


# gitCommit:
#   ./laouy.html 에 선언된 git_commit 버튼이 눌릴 경우 작동하는 함수
#   현재 directory에 git commit 실행
@app.route('/git_commit/', methods=['POST'])
@app.route('/git_commit/<path:var>', methods=['POST'])
def gitCommit(var=""):
    repo = git.Repo(var)

    com_msg = request.form['commit_msg']
    if com_msg=='':
        com_msg = "blank msg"
    
    repo.index.commit(com_msg)

    return filePage(var)

# gitStatus_parsing:
#   현재 git status를 parsing
#   staged / modified / untracked 세 개의 리스트를 하나의 dict로 return
def gitStatus_parsing():
    status_l = {}

    global repo_str
    repo = git.Repo(repo_str)
    status = repo.git.status().split('\n')

    try:
        p_staged = status.index('Changes to be committed:')
    except:
        p_staged = -1
    try:
        p_modified = status.index('Changes not staged for commit:')
    except:
        p_modified = -1
    try:
        p_untracked = status.index('Untracked files:')
    except:
        p_untracked = -1

    untracked = repo.untracked_files
    if p_modified==-1:
        modified = []
    else:
        modified = [i for i in status[p_modified:p_untracked] if '\t' in i]
    if p_staged==-1:
        staged = []
    else:
        if p_modified==-1:
            staged = [i for i in status[p_staged:p_untracked] if '\t' in i]
        else:
            staged = [i for i in status[p_staged:p_modified] if '\t' in i]

    status_l['staged'] = staged
    status_l['modified'] = modified
    status_l['untracked'] = untracked

    return status_l
# ====================================
# Feature 1 : Branch Management

# 커밋 히스토리 유무를 판단
def isNoneCommit():
    global repo_str
    repo = git.Repo(repo_str)
    return repo.heads==[]

# GET_BRANCH_LIST
# 현재 디렉토리에 저장된 브랜치명을 리스트로 반환
def getBranchNameList():
    global repo_str
    repo = git.Repo(repo_str)
    branch_name = []
    for branch in repo.heads:
        branch_name.append(branch.name)
    if isNoneCommit():
        branch_name.append(repo.active_branch.name)
    return branch_name

# Get UntrackedList
# 현재 저장소의 untracked 파일명을 리스트로 반환
def getUntrackedList():
    global repo_str
    status = gitStatus_parsing()
    return status['untracked']

# Get ChangedList
# 현재 브랜치의 modified와 staged 파일명을 합쳐 하나의 리스트로 반환
def getChangedList():
    global repo_str
    status = gitStatus_parsing()
    str_list = status['modified'] + status['staged']
    changed_list = []
    for str in str_list:
        changed_element = str.split(':')[1].strip()
        changed_list.append(changed_element)
    return changed_list

# Get TrackedList
# 해당 저장소 내 모든 브랜치에 대한 tracked 파일명을
# {브랜치1,2, .. : 파일1,2, ..}의 dict로 반환
def getTrackedList():
    global repo_str 
    repo = git.Repo(repo_str)
    trackedDict = {}
    heads = repo.heads
    for branch in heads:
        name = branch.name
        trackedDict.setdefault(name, [])
        tree = branch.commit.tree.traverse()
        trackedDict[name] = list([blob.name for blob in tree])
    return trackedDict

# 브랜치 삭제 가능 여부를 판단하기 위해
# 현재 디렉토리 전체 브랜치의 커밋 로그를 dict로 반환
# home에서 사용자 입력에 대하여 삭제 여부 확인
def getBranchCommits():
    global repo_str 
    repo = git.Repo(repo_str)
    commitDict = {}
    heads = repo.heads
    for branch in heads:
        name = branch.name
        commitDict.setdefault(name, [])
        commits = repo.iter_commits(branch)
        commitDict[name] = list([commit.hexsha for commit in commits])
                
    return commitDict

# Create Branch
# 사용자가 submit한 branch_name의 값을 branch_list에 저장
# repo.heads==[]이면 원칙적으로 다른 branch 생성 불가.
# git checkout -b 옵션 추가 시 .git/HEAD의 값 변경.
# 이후 add-commit 하면 master의 이름이 변경되는 효과를 가짐.
# 이후 git branch master로 다시 master 생성하면 동일 커밋을 가리킴.
@app.route('/create_branch/<path:var>', methods=['POST'])
def createBranch(var=""):
    repo = git.Repo(var)
    branch_name_list = getBranchNameList()
    new_branch = request.form['create_text']

    if isNoneCommit():
        repo.git.checkout(b=new_branch)
    elif new_branch not in branch_name_list:
        repo.create_head(new_branch)        
    return redirect('/files/' + var)

# Checkout Branch
# 커밋되지 않은 변경사항이 있으면 error 발생
# git checkout -f 옵션 붙이면 변경사항 삭제하고 강제로 이동함.
@app.route('/checkout_branch/<path:var>', methods=['POST'])
def checkoutBranch(var="", force=0):
    repo = git.Repo(var)
    branch = request.form['checkout_text']

    if repo.is_dirty():
        repo.git.checkout(branch, force=True)
    elif isNoneCommit():
        repo.git.checkout(b=branch)
    else:
        repo.git.checkout(branch)
    return redirect('/files/' + var)

# Delete Branch
@app.route('/delete_branch/<path:var>', methods=['POST'])
def deleteBranch(var=""):
    repo = git.Repo(var)
    branch = request.form['delete_text']
    repo.delete_head(branch)
    return redirect('/files/' + var)

# 이름 중복 - front 에서 처리
@app.route('/rename_branch/<path:var>', methods=['POST'])
def renameBranch(var=""):
    repo = git.Repo(var)
    branch = request.form['rename_select']
    name = request.form['new_name'].strip()
    if isNoneCommit():
        repo.git.checkout(b=name)
    else:
        repo.heads[branch].rename(name)
    return redirect('/files/' + var)

# ====================================
if __name__ == '__main__':
    local = "127.0.0.1"
    public = '0.0.0.0'
    app.run(host=public, debug=True, port=80)