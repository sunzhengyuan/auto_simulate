import time
def print_info(str,title='',time_info = True,centered=True):
    space       =   50 #每个表格项宽度
    bound_list  =   '='*space
    split_list  =   '-'*space
    print(bound_list)
    print('{} Information '.format(title).center(space))
    time_info and print(time.asctime().center(space))
    print(split_list)
    str_lst= str.strip('\n').split('\n')
    for line in str_lst :
        print(line.center(space)) if centered else print(line)
    print(bound_list+'\n')
    
def print_table(str_lst,lst):
    simple_table=   type(lst)==str # 输入数据只有一项，正常传入的应为列表类型
    space       =   20 #每个表格项宽度
    title_num   =   [len(str_lst),1][type(str_lst)==str]
    item_num    =   [len(lst),1][simple_table]  
    space_list  =   [' '*space]*(title_num+1)
    str_list    =   [' '*space]+[ item.center(space) for item in str_lst]
    splt_list   =   ['-'*space]*(title_num+1)
    print('+'.join(splt_list))
    print('|'.join(str_list))
    print('+'.join(splt_list))
    for cnt in range(item_num):
        # 若表格中只有一个项目传入的为字符串，不能使用索引
        item_lst = [str(cnt+1).center(space)]+([[[ str(item).center(space) for item in lst[cnt] ],[ str(lst[cnt]).center(space)]][title_num==1],[str(lst).center(space)]][simple_table])
        print('|'.join(item_lst))
        print('+'.join(splt_list))

    
