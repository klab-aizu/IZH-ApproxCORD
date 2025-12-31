module cordic_multiplier_approx_2TN (
    input clk,
    input rst_n,
    input start,
    input signed [7:0] x,
    input signed [7:0] z,
    output reg [15:0] y,
    output reg done
);
    // Parameters
    parameter ITERATIONS = 9;
    parameter SCALE = 128;
    parameter FRAC_BITS = 8;
    
    // Internal signals for each iteration
    wire signed [15:0] z_scaled_init;
    wire signed [15:0] z_iter [0:ITERATIONS];
    wire signed [15:0] y_iter [0:ITERATIONS];
    
    // Pre-computed signals for all iterations
    wire signed [15:0] x_shift [0:ITERATIONS-1];
    wire signed [15:0] y_add_operand [0:ITERATIONS-1];
    wire signed [15:0] y_sub_operand [0:ITERATIONS-1];
    wire [16:0] y_add_result [0:ITERATIONS-1];
    wire [16:0] y_sub_result [0:ITERATIONS-1];
    wire signed [15:0] z_update [0:ITERATIONS-1];
    
    // Initialize scaled z and y
    assign z_scaled_init = (z <<< FRAC_BITS) / SCALE;
    assign z_iter[0] = z_scaled_init;
    assign y_iter[0] = 16'b0;
    
    // Pre-compute all signals for each iteration
    genvar j;
    generate
        for (j = 0; j < ITERATIONS; j = j + 1) begin : signal_gen
            assign x_shift[j] = (x <<< FRAC_BITS) >>> (j + 1);
            assign y_add_operand[j] = x_shift[j];
            assign y_sub_operand[j] = -x_shift[j];
            assign z_update[j] = 16'h0100 >>> (j + 1);
        end
    endgenerate
    
    // Generate all 9 CORDIC iterations combinationally
    genvar i;
    generate
        for (i = 0; i < ITERATIONS; i = i + 1) begin : cordic_iter
            // Instantiate approximate 2TN adders for this iteration
            add16se_2TN y_adder (
                .A(y_iter[i]),
                .B(y_add_operand[i]),
                .O(y_add_result[i])
            );
            
            add16se_2TN y_subtractor (
                .A(y_iter[i]),
                .B(y_sub_operand[i]),
                .O(y_sub_result[i])
            );
            
            // Determine rotation direction and update coordinates
            assign y_iter[i+1] = (z_iter[i] >= 0) ? y_add_result[i][15:0] : y_sub_result[i][15:0];
            assign z_iter[i+1] = (z_iter[i] >= 0) ? (z_iter[i] - z_update[i]) : (z_iter[i] + z_update[i]);
        end
    endgenerate
    
    // Final result with scaling
    wire signed [15:0] y_final;
    assign y_final = (y_iter[ITERATIONS] * SCALE) >>> FRAC_BITS;
    
    // Sequential logic for output registers
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            y <= 16'b0;
            done <= 1'b0;
        end else begin
            if (start) begin
                y <= y_final;
                done <= 1'b1;
            end else begin
                y <= 16'b0;
                done <= 1'b0;
            end
        end
    end

endmodule
