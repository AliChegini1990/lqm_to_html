import os
import glob
import subprocess
import shutil
import pdb
import sys
from bs4 import  BeautifulSoup
import re
import json
import datetime
# Simple lqm extension check
def is_lqm(input_file_name):
    (root,extension) = os.path.splitext(input_file_name) 
    return extension == '.lqm'
        #raise RuntimeError('this is not correct lqm file')

# back up, rename 
def lqm_to_zip(input_file_name):
    new_name = ''
    back_up_name = input_file_name + ".bak"
    try:
        shutil.copy(input_file_name, back_up_name)
    except OSError as why:
        print(str(why))
        raise

    try:
        (root,ext) = os.path.splitext(input_file_name)
        new_name = root + ".zip"
        os.rename(input_file_name,new_name)
    except OSError as why:
        print("can not rename {0} to {1}".format(input_file_name,new_name))
        print(str(why))
        raise
    return new_name

# unzip file
def unzip_file(input_file_name, output_path):
    z = shutil.which('7z')
    if z==None:
        raise RuntimeError('could not find 7z')
    #(root,ext) = os.path.splitext(input_file_name)
    #unzip_path =  root + "_ex"
    os.mkdir(output_path)
    subprocess.run([z,'x','-o'+output_path, input_file_name])


def convert_lqm_files_to_htmls(extracted_lqm_path):
    file_jlqm = glob.glob(os.path.join(extracted_lqm_path,'*.jlqm'))
    for f in file_jlqm:
        with open(f,'r') as input_file:
            print("work on {0}".format(f))
            text = input_file.read()
            data = json.loads(text)
            html = convert_lqm_to_html(data)
            
            last_file_name = os.path.dirname(f)
            pattern = re.compile('(QuickMemo+[^.]+)')
            if not pattern.search(last_file_name):
                print("Error can not find correct file name {0}".format(last_file_name))
                continue
            match = pattern.search(last_file_name)
            
            new_file_name = os.path.join(last_file_name,match.group()+'.html')
            with open(new_file_name,'w') as output_file:
                output_file.write(str(html));

# just convert text content
def convert_lqm_to_html(lqm_dictionary):
    try:
        if not lqm_dictionary['Memo']['Desc']:
            raise RuntimeError("can not extract memo text")
        data = lqm_dictionary['Memo']['Desc']
        text = convert_unicode_to_html(data)
        return text
    
    except Exception as why:
        print(str(why))
        print("try more ...") 
    
    try:
        data=''
        if not lqm_dictionary['MemoObjectList']:
            raise RuntimeError("failed text extraction")
        for item in lqm_dictionary['MemoObjectList']:
            if type(item)==type([]):
                for item2 in item:
                    if  item2.get('Desc'):
                        data += item2.get('Desc')                   
                        data +='\n'
            else:
                if item.get('Desc'):
                    data += item.get('Desc')
                    data +='\n'
        
        text = convert_unicode_to_html(data)
        return text
    except Exception as why:
            print(str(why))
   
def convert_unicode_to_html(text):
    text = BeautifulSoup(text,'lxml')
    return text


def get_time():
    x=datetime.datetime.now()
    return x.strftime("%d-%m-%y-%H%M%S")


if __name__ == "__main__":
    # find all lqm in the folder
            
    # first argument must be a folder path that contains lqm files
    if (len(sys.argv) < 2 ):
        print("Usage: \n \t python convert_qm_to_html.py <FolderPath>\nPut all .lqm files in the <FolderPath>")
        exit()

    folder = sys.argv[1]
    lqms = glob.glob(os.path.join(folder,'*.lqm'))
    out_put_directory=[]
    zip_file_name=''
    count=0
    for lqm in lqms:
        print("found {0}".format(lqm))
        if is_lqm(lqm):
            count +=1
            try:
                zip_file_name = lqm_to_zip(lqm);        
            except Exception as ex:
                print("can not convert lqm to zip")
                print(str(ex))
                exit()
           
            out_path=''
            
            try:
                if not zip_file_name:
                    print("Error: Zip file name is empty")
                    print("       Base name {0}".format(lqm))
                    continue
                out_path = lqm + get_time()
                out_put_directory.append(out_path)
                unzip_file(zip_file_name, out_path)
            except Exception as ex:
                print("can not unzip file: {0}".format(lqm))
                print(str(ex))
                exit()
            convert_lqm_files_to_htmls(out_path)
    # print some information
    print("Number of file found {0}".format(count))
    print("Number of output directory {0}".format(len(out_put_directory)))
    print("List of output directory :")
    for item in out_put_directory:
        print("{0}".format(item))






