
tcl_prot = '''
vlib work
vmap work work
vlog ../verilog/*.sv
vlog ../verilog/*.v
vsim $LIB$ $OPT$ work.$TB_NAME$ $GLBL$
'''

lib_prot = '''-L D:/xilinx_lib/unisims_ver -L D:/xilinx_lib/simprims_ver -L D:/xilinx_lib/unimacro_ver -L D:/xilinx_lib/xilinxcorelib_ver'''

def tcl_gen(tb_name,dir='./script/',opt=False,xilinx_sim=True):
    ''' 用于产生仿真所需要的脚本文件 
        tcl_gen(dir,gui_mode = True,opt=False,xilinx_sim=True)
        dir : do文件生成路径
        opt : 是否开启优化为False时将使用-novopt选项
        xilinx_sim : 是否进行xilinx库仿真，如果True将自动添加连接库并添加glbl文件
    '''
    tcl_fname =  'vsim.do'
    tcl_fid = open(dir+tcl_fname,'w');
    tcl_cont=tcl_prot.replace('$TB_NAME$',tb_name)
    tcl_cont=tcl_cont.replace('$LIB$',lib_prot if xilinx_sim else '' )
    tcl_cont=tcl_cont.replace('$GLBL$','work.glbl' if xilinx_sim else '' )
    tcl_cont=tcl_cont.replace('$OPT$','' if opt else '-novopt' )
    tcl_fid.write(tcl_cont);
    #print('Create Modelsim Do Script Done!')