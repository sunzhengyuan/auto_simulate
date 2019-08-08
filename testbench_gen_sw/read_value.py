def read_value(info,typ=str,filter=[],title_len=30):
    ''' Read A Variable With type in Block Mode  
        参数说明：
            info   : 显示于commandline的提示信息
            typ    : 要读取输入类型如int,float,str,tupple等
            filter : 滤器列表，用户有效输入的预定义集合如定义为[3,5,8]
                     则只有在用户输入3、5、7时才会被程序接收，否则继续读取
    ''' 
    # 读取状态标志量
    ReadStatus = False
    # 对输入info进行长度对齐
    while not ReadStatus :
        try:
            # 输入滤器非空
            FilterNotEmpty = len(filter)!=0
            # 输入字符串缓冲
            ReadTemp       = input(info+[' : ',' ({}) : '.format('\\'.join([str(item) for item in filter]))][FilterNotEmpty])
            # 输入映射，如果要读取函数为str类型，仍然映射为str，否则使用python解释器解释为对应类型
            ValueMapped    = ReadTemp if typ == str else eval(ReadTemp)
            # 类型错误，如果映射后的类型与需求类型不同则触发后端处理
            TypeError      = type(ValueMapped) != typ
            # 数值错误，当滤器列表不空且映射后结果不在滤器列表内则出现数值错误
            ValError       = FilterNotEmpty and ValueMapped not in filter
        except:
            print('Invalid Input,if you want to enter a string ,please use \'\',\"\" ')
        else :
            if TypeError :
                print('Type Error, expect type {} while input type {}'.format(str(typ),type(ValueMapped))) 
            elif ValError :
                print('Value Error, expect value in the set {}'.format(filter))
            else:
                #若输入类型与数值满足要求将读取标志量置True，跳出循环返回映射后的数值
                ReadStatus = True
    return typ(ValueMapped)
    
    
#i=read_value('Please Enter Int : ',int,[3,5,7])
#print(i)
#b=read_value('Please Enter Bool',bool,[True,False])
#print(b)
#b=read_value('Please Enter Bool',str,['v','sv'])
#print(b)

