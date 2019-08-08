''' 2018/11/29 1.添加 frame_gen 逻辑用于方便的生成流输入 
               2.测试中存在丢失端口检测的情况     
               3.复位极性，时钟，复位信号无法自动检测
               4.信号没有再系统初始化的时候自动添加复位（reg型）
               
               添加 function blog2
                   function integer blog2(input integer num);
                        for ( blog2 = 0 ; num > 0 ; blog2 = blog2+1 )
                        num = num >> 1 ;
                    endfunction
    
    2018/12/3
                1.修复形如 input_cnt 等变量错误被识别为输入接口的BUG
                2.在gen_stream任务中添加tlast选项
                3.修复了初始化时数据与使能信号的清0
                4.添加复位逻辑将待测模块中属性为input端口全部置0
    
    2018/12/4
                1.添加工程文件夹模式，指定工程文件夹目录，目录中所有的
                文件都会被添加到测试空间的Verilog文件夹中
    2018/12/5
                1.将测试文档的生成编写成为一个函数，未后期的类化做准备
                2.对部分逻辑复杂代码进行优化
    
    2018/12/11  1.添加了读取用户输入的逻辑
                2.定位并解决了函数化后路径上的错误
                3.下一步预定添加信号绑定功能，用户可以通过命令行选择哪些
                信号作为总线中的时钟信号、复位信号、数据信号等
    
    2018/12/21  1.添加了类似于output reg signed [3:0] data;的支持，支持
                在端口声明reg类型
                2.添加将端口解析出来的多维列表转化为字典的函数，为后续功能优化
                提供基础
                3.修正了搜索参数定义的正则表达式，防止搜索到的参数值包含换行符
                4.将程序中原有通过正则表达式搜索的多维列表全部改为字典，并修改
                了程序中的其他接口
    2019/1/31   1.发现了不能正确识别 output reg[DW*WL-1:0]   m_axis_tdata 类型
                信号，因为reg与后端[符号并未添加多余空格，问题待解决
    '''
    
''' This Program is Used to Create TestBench For a Verilog File '''
import os 
import shutil
import time
import re
import pickle
from glbl_gen import glbl_gen
from tcl_gen  import tcl_gen
from print_table import *
from read_value import read_value

CMDLINE_ENABLE = True # 命令行使能控制，True时所有控制参数通过命令行读取

if CMDLINE_ENABLE :
    ## User Input Configuration
    TOP_NAME  = read_value('Enter top file name',str)
    TOP_TYPE  = read_value('Enter top file type',str,['v','sv'])
    PROJ_DIR_NAME = read_value('Enter project director name',str)
    FRAME_GEN_SPEC = read_value('Enable Frame Generater',bool) # 是添加帧生成任务
    #FRAME_GEN_SPEC = False
    if FRAME_GEN_SPEC :
        FRAME_GEN_LEN  = read_value('Enable Frame Generate Length',int)   # 帧生成长度
        FRAME_GEN_BLOCK= read_value('Is Frame Generator Block',bool)# 是否阻塞生成
        FRAME_GEN_TLAST= read_value('dose Frame Generator have Tlast Signal',bool)
else :
    ## Parameter Configuration
    TOP_NAME  = 'matrix_trans'
    TOP_TYPE  = 'v'
    PROJ_DIR_NAME = 'matrix_trans_new'
    FRAME_GEN_SPEC = True # 是添加帧生成任务
    FRAME_GEN_LEN  = 64   # 帧生成长度
    FRAME_GEN_BLOCK= False# 是否阻塞生成
    FRAME_GEN_TLAST= True

    
WORK_DIR  = os.path.dirname(os.path.abspath(__file__))
TOP_FNAME = TOP_NAME+'.'+TOP_TYPE
TB_NAME   = TOP_NAME+'_tb'
TB_FNAME   = TOP_NAME+'_tb.sv'
PROJ_NAME = 'MODELSIM_AUTO_'+TOP_NAME.upper()

## Change Dir to Work Place
os.chdir(WORK_DIR)

## Create Folder
PROJ_NAME in os.listdir() and shutil.rmtree(PROJ_NAME)
os.mkdir(PROJ_NAME)
os.chdir('./'+PROJ_NAME)
# 创建多个文件夹
mkmdir=lambda lst: [ os.mkdir(dir) for dir in lst ] 
mkmdir(['proj','script','verilog','data'])
print_info('Create Folder Done !',time_info=True)

## Load Prototype
prot_fid = open(WORK_DIR+'/prot_dict.dat','rb')
prot_dict = pickle.load(prot_fid)
module_inst_prot = prot_dict['module_inst_prot']
tb_prot = prot_dict['tb_prot']
gen_frame_prot = prot_dict['gen_frame_prot']

## Create Bat File
bat_prog='''del proj\*.* /f /s /y
cd proj
modelsim -do ../script/vsim.do '''
bat_fname ='modelsim_auto.bat'
bat_fid = open(bat_fname,'w');
bat_fid.write(bat_prog);
bat_fid.close()
print_info('Create Bat File Done!')

## Create Modelsim Tcl Script
tcl_gen(TB_NAME,dir='./script/',opt=False,xilinx_sim=True) # 关闭优化，开启xilinx选项
print_info('Create Modelsim Do Script Done!')


## Copy File to Destination Path
file_filter = lambda file_lst,format_lst : [ item for item in file_lst if item.partition('.')[2] in format_lst ]
src_lst=[shutil.copy('../'+PROJ_DIR_NAME+'/'+item,'verilog/') for item in file_filter(os.listdir('../'+PROJ_DIR_NAME),['sv','v'])]
#src_lst=[shutil.copy('../'+PROJ_DIR_NAME+'/'+item,'verilog/') for item in file_filter(os.listdir('../'+PROJ_DIR_NAME),['v'])]
print_table(['Module Name'],src_lst)

## Create glbg
glbl_gen('./verilog/')

## Regex Function Get & Delete
format_get = lambda format,string : re.compile(format).findall(string)
format_delete = lambda format,string : re.compile(format).sub('',string)

## This Function Convert List to Dictionary
list2dict=lambda keys,vals : [ dict(zip(keys,item)) for item in vals]

def select_delete(src_str,spec_str,status):
    if status :
        return format_delete('<'+spec_str+'>'+'(\n|.)*?'+'</'+spec_str+'>',src_str);
    else :
        return format_delete('</?'+spec_str+'>',src_str);

def string_dict_replace(string,dict):
    for key in dict :
        string = string.replace(key,dict[key])
    return string

inst_format = '\t.$INST_NAME$($INST_NAME$)\t'
port_decl_format = 'logic $SIGNED$ [$MSB$:$LSB$] $NAME$ ;'
param_decl_format = '$TYPE$ $NAME$ = $VAL$ ;'

def module_inst_gen(module_name,port_dict,param_dict):
    ''' 根据传入的参数信息与端口信息生成例化 '''
    param_dict  =   [item for item in param_dict if item['Type']!='localparam']
    module_inst =   string_dict_replace(module_inst_prot,{'$PARAM_INST$':['#(\n$PARAM_INST$\n)',''][len(param_dict)==0],'$MODULE_NAME$':module_name})
    # 产生参数与接口列表
    param_list  =   [ inst_format.replace('$INST_NAME$',item['Name']) for item in param_dict if item['Type']!='localparam' ]
    port_list   =   [ inst_format.replace('$INST_NAME$',item['Name']) for item in port_dict  ]
    # 生成字符串
    param_str   =   ',\n'.join(param_list)
    port_str    =   ',\n'.join(port_list)
    # 进行列表替换
    module_inst =   string_dict_replace(module_inst,{'$PARAM_INST$':param_str,'$PORT_INST$':port_str})
    return module_inst

def port_decl_gen(port_dict):
    ''' 根据输入的端口信息生成端口的声明列表 '''
    port_decl_list = [ string_dict_replace(port_decl_format,{'$TYPE$':item['IO Type'],'$SIGNED$':item['SIGNED'],'$MSB$':[item['MSB'],'0'][item['MSB']==''],'$LSB$':[item['LSB'],'0'][item['LSB']==''],'$NAME$':item['Name']}) for item in port_dict ] ;
    port_decl_str    = '\n'.join(port_decl_list)
    return port_decl_str 

def param_decl_gen(param_dict):
    ''' 根据输入的端口信息生成端口的声明列表 '''
    #param_info      = [ item for item in param_info if item[0]!='localparam']
    param_dict      = [ item for item in param_dict ]
    param_decl_list = [ param_decl_format.replace('$TYPE$',item['Type']).replace('$NAME$',item['Name']).replace('$VAL$',item['Value']) for item in param_dict] ;
    param_decl_str    = '\n'.join(param_decl_list)
    return param_decl_str 

    

    
def testbench_analyze(dut_fid):
    ''' 分析Verilog代码并产生对应的测试文本 '''
    ''' 未考虑到函数里的端口定义，与线网 signed情况 '''
    print_info('Start Verilog File Analyze!')
    file=dut_fid.read()
    
    # 去除所有注释部分 
    file=format_delete('(/{2,}.*?\n)|(?:/\*(\n|.)*?\*/)',file)

    # 模块名位于'module'后，若有参数列表则位于'#'前，否则则位于'('前
    module_name=format_get('module\s*(\S*)\s*[#|\(]',file)[0]
    print('Module Name Table : \n')
    print_table(['Name'],module_name)
    
    # 提取参数列表中的参数 提取逻辑可以表示如下 位于#右侧的第一个括号内以,分割
    param_info=format_get('((?:parameter)|(?:localparam))\s*(\w*)\s*=\s*(\w*)(?:\n|.)*?[;,)]',file)
    print('Parameter Information Table  :')
    print_table(['Type','Name','Value'],param_info)
    param_dict=list2dict(['Type','Name','Value'],param_info)
    
    # 提取端口具体信息
    file=format_delete('(?:function)(?:.|\n)*(?:endfunction)',file)# 提前删除function->endfunction防止function中有端口声明
    port_info = format_get('((?:input)|(?:output)|(?:inout))(?:\s+(?:(?:reg)|(?:wire)))?\s+((?:signed)|(?:unsigned))?\s*(?:\[\s*(\S*)\s*:\s*(\S*)\s*\])?\s*(\w*)(?:\n|.)*?[;,)]',file)
    print('Port Information Table  :')
    print_table(['IO Type','SIGNED','MSB','LSB','Name'],port_info)
    port_dict=list2dict(['IO Type','SIGNED','MSB','LSB','Name'],port_info)
    
    # 生成例化原型
    return ( module_name , param_dict , port_dict)
    
    

## Create Testbench file
s_axis_bus_dict ={'clk_sig':'s_axis_aclk','rst_sig':'s_axis_aresetn','data_sig':'s_axis_tdata','valid_sig':'s_axis_tvalid','ready_sig':'s_axis_tready'};
def gen_frame_task(bus_dict,block=False,last=False):
    ''' 用于生成具有数据流生成格式的信号传入数据为存储有总线信号名称的字典'''
    prog = string_dict_replace(gen_frame_prot,{'$CLK_SIG$':bus_dict['clk_sig'],'$DATA_SIG$':bus_dict['data_sig'],'$VALID_SIG$':bus_dict['valid_sig'],'$READY_SIG$':bus_dict['ready_sig']})
    prog = select_delete(prog,'BLOCK_SPEC',not block)
    prog = select_delete(prog,'NONBLOCK_SPEC',block)
    prog = select_delete(prog,'LAST_SPEC',not last)
    
    return format_delete('\$.*?\$',prog)
    

def signal_bind(port_dict):
    ''' 该函数用于让用户在提供的信号内选择绑定的信号用作时钟或复位 '''
    print('Valid Input Signal:')
    print_table(['Name'],[i['Name'] for i in port_dict if i['IO Type']=='input' ])
    clk_sig = read_value('Plese Select the Clock Signal',str,[i['Name'] for i in port_dict if i['IO Type']=='input' ]+['none'])
    print('You have select {} as input clock resource .'.format(clk_sig))
    rst_sig = read_value('Plese Select the Reset Signal',str,[i['Name'] for i in port_dict if i['IO Type']=='input' ]+['none'])
    print('You have select {} as input reset resource .'.format(rst_sig))
    return {'clk_sig':clk_sig,'rst_sig':rst_sig,'data_sig':'s_axis_tdata','valid_sig':'s_axis_tvalid','ready_sig':'s_axis_tready'} ;
    
def testbench_file_generate(tb_prot):
    ''' 产生testbench文件 '''
    ## Analyze the Top Module And Gernerate the Test Bench
    dut_fid     = open('./verilog/'+TOP_FNAME,'r')
    module_name , param_dict , port_dict=testbench_analyze(dut_fid)
    module_inst = module_inst_gen(module_name,port_dict,param_dict)
    bus_dict    = signal_bind(port_dict)
    print_info(module_inst,title='Module Instance',centered=False)
    port_decl   = port_decl_gen(port_dict)
    param_decl  = param_decl_gen(param_dict) 
    tb_fid      = open('./verilog/'+TB_FNAME,'w')
    # 是否添加帧生成
    if FRAME_GEN_SPEC :
        tb_prot=tb_prot.replace('$TASK$',gen_frame_task(bus_dict,FRAME_GEN_BLOCK,FRAME_GEN_TLAST)).replace('$USER_CODE$','$USER_CODE$\n\t\tgen_frame({});'.format(FRAME_GEN_LEN))
    # 替换时钟信号与复位信号
    tb_prot=string_dict_replace(tb_prot,{'$TB_NAME$':TB_NAME,'$PARAMETER_DECLARATIONS$':param_decl,'$LOGIC_DECLARATIONS$':port_decl,'$MODULE_INST$':module_inst,'$RESET_LIST$':'\n'+'\n'.join([ '\t\t{} = 0 ;'.format(item['Name']) for item in port_dict if item['IO Type']=='input' ])})
    tb_prot=string_dict_replace(tb_prot,{'$CLK_SIG$':bus_dict['clk_sig'],'$RST_SIG$':bus_dict['rst_sig']});
    tb_prot=select_delete(tb_prot,'CLK_SPEC',bus_dict['clk_sig']=='none')
    tb_prot=select_delete(tb_prot,'RST_SPEC',bus_dict['rst_sig']=='none')
    # 写入tb文件
    tb_fid.write(tb_prot)
    tb_fid.close()

## 生成测试文本
testbench_file_generate(tb_prot)