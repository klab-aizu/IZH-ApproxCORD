// Comprehensive testbench for all x,z combinations
module cordic_multiplier_exact_tb;
reg clk, rst_n, start;
reg signed [7:0] x, z;
wire [15:0] y;
wire done;

// Test control variables
integer x_val, z_val;
integer error_count = 0;
integer test_count = 0;
real max_error = 0.0;
real avg_error = 0.0;
real total_error = 0.0;

// Instantiate the module
cordic_multiplier_exact uut (
    .clk(clk),
    .rst_n(rst_n),
    .start(start),
    .x(x),
    .z(z),
    .y(y),
    .done(done)
);

// Clock generation
always #5 clk = ~clk;

// Main test sequence
initial begin
    // Initialize
    clk = 0;
    rst_n = 0;
    start = 0;
    x = 0;
    z = 0;
    
    // Reset
    #10 rst_n = 1;
    #10;
    
    $display("Starting comprehensive CORDIC multiplier test...");
    $display("Testing all combinations: x=[-128:127], z=[-128:127]");
    $display("Format: x, z, cordic_result, expected, error");
    
    // Test all combinations
    for (x_val = -128; x_val <= 127; x_val = x_val + 1) begin
        for (z_val = -128; z_val <= 127; z_val = z_val + 1) begin
            test_single_case(x_val, z_val);
        end
        
        // Progress indicator every 32 x values
        if (x_val % 32 == 0) begin
            $display("Progress: x=%d, completed %d tests", x_val, test_count);
        end
    end
    // test_single_case(127,127);    
    // Final statistics
    avg_error = total_error / test_count;
    $display("\n=== CORDIC MULTIPLIER TEST RESULTS ===");
    $display("Total tests: %d", test_count);
    $display("Errors (>5%% difference): %d", error_count);
    $display("Error rate: %0.2f%%", (real'(error_count) / real'(test_count)) * 100.0);
    $display("Maximum error: %0.2f%%", max_error);
    $display("Average error: %0.2f%%", avg_error);
    
    $finish;
end

// Task to test a single x,z combination
task test_single_case;
    input integer x_in, z_in;
    integer expected, cordic_result;
    integer error_abs;
    real error_percent;
    begin
        x = x_in;
        z = z_in;
        expected = x_in * z_in;
        
        // Start computation
        start = 1;
        #10;
        
        // Wait for completion
        wait(done);
        cordic_result = $signed(y);
        
        // Calculate absolute error manually
        error_abs = (cordic_result > expected) ? (cordic_result - expected) : (expected - cordic_result);
        
        // Calculate error percentage
        if (expected != 0) begin
            if (expected < 0) begin
                error_percent = real'(error_abs) / real'(-expected) * 100.0;
            end else begin
                error_percent = real'(error_abs) / real'(expected) * 100.0;
            end
        end else begin
            error_percent = real'(error_abs);
        end
        
        // Track statistics
        test_count = test_count + 1;
        total_error = total_error + error_percent;
        if (error_percent > max_error) max_error = error_percent;
        
        // Flag significant errors (>5%)
        if (error_percent > 5.0) begin
            error_count = error_count + 1;
            $display("ERROR: x=%d, z=%d, cordic=%d, expected=%d, error=%0.2f%%", 
                     x_in, z_in, cordic_result, expected, error_percent);
        end
        
        // Show some sample results
        if ((x_in % 37 == 0) && (z_in % 41 == 0)) begin
            $display("Sample: x=%d, z=%d, cordic=%d, expected=%d, error=%0.2f%%", 
                     x_in, z_in, cordic_result, expected, error_percent);
        end
        
        start = 0;
        #20;  // Wait between tests
    end
endtask

endmodule
