module grey2bin
#(
    parameter DATA_WIDTH = 8
)
(
    grey,
    bin
);
/*
    LOCALPARAM DECLARATION
*/
   localparam DW = DATA_WIDTH ;

/*
    PORT DECLARATION
*/
    input       [DW-1:0] grey ; 
    output      [DW-1:0] bin  ;
    integer              i    ;
    
    reg [DW-1:0]bin ;
    
    always @ ( * )
        begin
            bin[DW-1] = grey[DW-1] ;
            for ( i = DW-1 ; i >= 0 ; i = i - 1 )
                bin[i-1] = grey[i-1] ^ bin[i];
        end

endmodule
/*
    function [DW-1:0] grey2bin(input [DW-1:0] grey );
        integer i ;
        begin
            grey2bin[DW-1] = grey[DW-1];
            for ( i = DW-1 ; i > 0 ; i = i - 1 )
                begin
                    grey2bin[i-1] = grey2bin[i] ^ grey[i-1] ;
                end
        end
    endfunction
    
    
*/