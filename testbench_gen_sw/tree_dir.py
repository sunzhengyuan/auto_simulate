#coding:utf-8
import os

def export_file(context):
    dir_list.write(context + '\n')

def dfs_showdir(path, depth):
    if depth == 0:
        print("root:[" + path + "]")
        export_file("root:[" + path + "]")

    for item in os.listdir(path):
        if '.git' not in item:
            line = "|   " * depth + "|-- " + item
            print(line)
            export_file(line)

            newitem = path +'/'+ item
            if os.path.isdir(newitem):
                dfs_showdir(newitem, depth +1)

if __name__ == '__main__':
    dir_list = open('list.txt','w')
    dfs_showdir('C:/Users/SunZhengYuan/Desktop',0)
    dir_list.close()

