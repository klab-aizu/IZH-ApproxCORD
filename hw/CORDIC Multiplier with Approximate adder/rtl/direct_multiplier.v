module direct_multiplier (
    input clk,
    input rst_n,
    input start,
    input signed [7:0] x,
    input signed [7:0] z,
    output reg [15:0] y,
    output reg done
);
    
    // Behavioral multiplication - single cycle operation
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            y <= 16'b0;
            done <= 1'b0;
        end else begin
            if (start) begin
                // Direct multiplication using behavioral modeling
                y <= x * z;
                done <= 1'b1;
            end else begin
                y <= 16'b0;
                done <= 1'b0;
            end
        end
    end
    
endmodule