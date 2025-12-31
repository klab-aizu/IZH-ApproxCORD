module cordic_multiplier_approx_2U6(
    input clk,
    input rst_n,
    input start,
    input signed [7:0] x,
    input signed [7:0] z,
    output [15:0] y,
    output done
);
    // Parameters
    parameter MAX_ITERATIONS = 16;
    parameter SCALE = 128;
    parameter FRAC_BITS = 8;
    
    // Internal registers
    reg [4:0] iter_cnt;
    reg signed [15:0] z_scaled_reg;
    reg signed [15:0] y_reg;
    
    // Next-state values
    reg signed [15:0] z_scaled_next;
    reg signed [15:0] y_next;
    reg [4:0] iter_cnt_next;
    
    // Approximate adder signals for y updates
    wire signed [15:0] y_add_operand;
    wire signed [15:0] y_sub_operand;
    wire [16:0] y_add_result;
    wire [16:0] y_sub_result;
    
    // Instantiate approximate adders for y calculation
    // For addition: y + shift
    assign y_add_operand = (x <<< FRAC_BITS) >>> iter_cnt;
    add16se_2U6 y_adder (
        .A(y_reg),
        .B(y_add_operand),
        .O(y_add_result)
    );
    
    // For subtraction: y - shift (implement as y + (-shift))
    assign y_sub_operand = -((x <<< FRAC_BITS) >>> iter_cnt);
    add16se_2U6 y_subtractor (
        .A(y_reg),
        .B(y_sub_operand),
        .O(y_sub_result)
    );
    
    // Sequential logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            iter_cnt <= 5'b0;
            z_scaled_reg <= 16'b0;
            y_reg <= 16'b0;
        end else begin
            iter_cnt <= iter_cnt_next;
            z_scaled_reg <= z_scaled_next;
            y_reg <= y_next;
        end
    end
    
    // Combinational logic
    always @(*) begin
        // Default values
        iter_cnt_next = iter_cnt;
        z_scaled_next = z_scaled_reg;
        y_next = y_reg;
        
        if (start) begin
            if (iter_cnt == 0) begin
                // Initialize
                iter_cnt_next = 5'b1;
                z_scaled_next = (z <<< FRAC_BITS)/SCALE;
                y_next = 16'b0;
            end else if (iter_cnt < MAX_ITERATIONS) begin
                // CORDIC iterations with approximate adders
                iter_cnt_next = iter_cnt + 1;
                
                if (z_scaled_reg >= 0) begin  // d = 1
                    // Use approximate adder for y += shift
                    y_next = y_add_result[15:0];  // Take lower 16 bits
                    z_scaled_next = z_scaled_reg - (16'h0100 >>> iter_cnt);
                end else begin  // d = 0
                    // Use approximate subtractor for y -= shift
                    y_next = y_sub_result[15:0];  // Take lower 16 bits
                    z_scaled_next = z_scaled_reg + (16'h0100 >>> iter_cnt);
                end
            end
        end else begin
            // Reset when start is low
            iter_cnt_next = 5'b0;
            z_scaled_next = 16'b0;
            y_next = 16'b0;
        end
    end
    
    // Outputs
    assign done = (iter_cnt == MAX_ITERATIONS);
    assign y = (y_reg * SCALE) >>> FRAC_BITS;
    
endmodule
