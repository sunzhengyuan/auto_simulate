import pickle
import os
#
module_inst_prot = '''
$MODULE_NAME$ 
$PARAM_INST$
$MODULE_NAME$_inst(
$PORT_INST$
);
'''

#
#tb_prot='''
#`timescale 1ns/1ns
#module $TB_NAME$();
#// PARAMETER DECLARATION
#$PARAMETER_DECLARATIONS$
#// LOGIC DECLARATION
#$LOGIC_DECLARATIONS$
#// SYSTEM RESET DECLARATION
#task system_reset;
#    begin
#        $CLK_SIG$             = 0 ;
#        $RST_SIG$             = 0 ;
#        $DATA_SIG$            = 0 ;
#        $VALID_SIG$           = 0 ;
#        $LAST_SIG$            = 0 ;
#        //$RESET_LIST$
#        @ ( posedge $CLK_SIG$ )   ;
#        $RST_SIG$             = 1 ;
#    end
#endtask
#// GENERATE COLCK SIGNAL
#initial forever #10 $CLK_SIG$=~$CLK_SIG$;
#// AUTOGEN $TASK$
#task delay;
#    input int cnt ;
#    repeat ( cnt ) @ ( posedge $CLK_SIG$ );
#endtask
#// SIMULATION PROCESS
#initial
#    begin
#        system_reset        ;
#        @ ( posedge $CLK_SIG$ )   ;
#        // USER CODE BEGIN $USER_CODE$
#        // USER CODE END
#        repeat(100)@( posedge $CLK_SIG$ ) ;
#        $stop;
#    end
#// DUT 
#$MODULE_INST$
#endmodule
#'''
tb_prot='''
`timescale 1ns/1ns
module $TB_NAME$();
// PARAMETER DECLARATION
$PARAMETER_DECLARATIONS$
// LOGIC DECLARATION
$LOGIC_DECLARATIONS$
// SYSTEM RESET DECLARATION
task system_reset;
    begin
        //$RESET_LIST$
        <CLK_SPEC>@ ( posedge $CLK_SIG$ )   ;</CLK_SPEC>
        <RST_SPEC>$RST_SIG$             = 1 ;</RST_SPEC>
    end
endtask

<CLK_SPEC>
// GENERATE COLCK SIGNAL
initial forever #10 $CLK_SIG$=~$CLK_SIG$;
</CLK_SPEC>

// AUTOGEN $TASK$
<CLK_SPEC>
task delay;
    input int cnt ;
    repeat ( cnt ) @ ( posedge $CLK_SIG$ );
endtask
</CLK_SPEC>

// SIMULATION PROCESS
initial
    begin
        system_reset        ;
        <CLK_SPEC>@ ( posedge $CLK_SIG$ )   ;</CLK_SPEC>
        // USER CODE BEGIN $USER_CODE$
        // USER CODE END
        <CLK_SPEC>repeat(100)@( posedge $CLK_SIG$ ) ;</CLK_SPEC>
        $stop;
    end
// DUT 
$MODULE_INST$
endmodule
'''

gen_frame_prot='''
// Generate Frame Task 
task gen_frame;
    input int len ;
    begin
        for ( int j = 0 ; j < len ; j++ )
            begin
                $DATA_SIG$    = j ;
                $VALID_SIG$   = 1 ;
                <LAST_SPEC>s_axis_tlast    = ( j == len - 1 )? 1'b1 : 1'b0 ;</LAST_SPEC>
                <BLOCK_SPEC>do @ ( posedge $CLK_SIG$ ); while (!$READY_SIG$) ;</BLOCK_SPEC><NONBLOCK_SPEC>@ ( posedge $CLK_SIG$ ); </NONBLOCK_SPEC>
            end
            $DATA_SIG$ = 0 ;
            $VALID_SIG$= 0 ;
            <LAST_SPEC>s_axis_tlast = 0 ;</LAST_SPEC>
    end
endtask   
'''

prot_dict={'module_inst_prot':module_inst_prot,'tb_prot':tb_prot,'gen_frame_prot':gen_frame_prot}
dir_name=os.path.dirname(os.path.abspath(__file__))
prot_dict_fid = open(dir_name+'./prot_dict.dat','wb')
pickle.dump(prot_dict,prot_dict_fid);
prot_dict_fid.close()
print(os.path.abspath(__file__))
