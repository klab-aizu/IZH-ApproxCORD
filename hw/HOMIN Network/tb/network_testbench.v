`timescale 1ns/1ps

module network_testbench;
    parameter N = 1000;
    parameter T_MS = 1000;
    parameter DT = 0.03125;
    parameter CLK_PERIOD = 10;
    parameter STEPS = 32000;

    parameter SCALE = 512;
    parameter I_EXT_Q69 = 16'sd7680;
    parameter I_EXT_START_STEP = 3200;
    parameter I_EXT_END_STEP = 32000;

    reg clk;
    reg rst_n;

    reg signed [15:0] W [0:N*N-1];

    wire signed [15:0] v [0:N-1];
    wire spike [0:N-1];
    wire ready [0:N-1];
    reg signed [15:0] input_current [0:N-1];
    reg signed [7:0] q4_4_in [0:N-1];

    reg spike_prev [0:N-1];

    integer step_count;
    integer i, j;
    reg simulation_done;

    integer spike_file;
    integer file;
    integer scan_result;
    integer row, col;
    integer value;

    initial begin
        clk = 0;
        forever #(CLK_PERIOD/2) clk = ~clk;
    end

    initial begin
        file = $fopen("../W_matrix.csv", "r");

        if (file == 0) begin
            $display("ERROR: Could not open W_matrix.csv");
            $finish;
        end

        for (row = 0; row < N; row = row + 1) begin
            for (col = 0; col < N; col = col + 1) begin
                scan_result = $fscanf(file, "%d", value);
                if (scan_result != 1) begin
                    $display("ERROR: Failed to read W[%0d][%0d]", row, col);
                    $finish;
                end
                W[row*N + col] = value;

                if (col < N-1) begin
                    scan_result = $fgetc(file);
                end
            end
        end

        $fclose(file);
    end

    genvar n;
    generate
        for (n = 0; n < N; n = n + 1) begin : neuron_array
            homin_cordic_2TN neuron_inst (
                .clk(clk),
                .rst_n(rst_n),
                .input_current(input_current[n]),
                .q4_4_in(q4_4_in[n]),
                .v(v[n]),
                .spike(spike[n]),
                .ready(ready[n])
            );
        end
    endgenerate

    initial begin
        rst_n = 0;
        step_count = 0;
        simulation_done = 0;

        for (i = 0; i < N; i = i + 1) begin
            input_current[i] = 0;
            spike_prev[i] = 0;
            q4_4_in[i] = -8'sd104;
        end

        spike_file = $fopen("spikes_verilog.txt", "w");
        if (spike_file == 0) begin
            $display("ERROR: Could not open spike output file");
            $finish;
        end

        #(CLK_PERIOD * 10);
        rst_n = 1;
        #(CLK_PERIOD * 10);

        wait_for_ready();

        for (step_count = 0; step_count < STEPS; step_count = step_count + 1) begin
            compute_input_currents();

            for (i = 0; i < N; i = i + 1) begin
                q4_4_in[i] = v[i] >>> 5;
            end

            @(posedge clk);

            wait_for_ready();

            record_spikes();

            for (i = 0; i < N; i = i + 1) begin
                spike_prev[i] = spike[i];
            end

            if (step_count % 1000 == 0) begin
                $display("Step %0d / %0d (%.1f%%)", step_count, STEPS,
                         (step_count * 100.0) / STEPS);
            end
        end

        $fclose(spike_file);
        simulation_done = 1;
        #(CLK_PERIOD * 100);
        $finish;
    end

    task wait_for_ready;
        integer all_ready;
        integer timeout;
        begin
            all_ready = 0;
            timeout = 0;

            while (!all_ready && timeout < 1000) begin
                all_ready = 1;
                for (i = 0; i < N; i = i + 1) begin
                    if (!ready[i]) begin
                        all_ready = 0;
                    end
                end

                if (!all_ready) begin
                    @(posedge clk);
                    timeout = timeout + 1;
                end
            end

            if (timeout >= 1000) begin
                $display("ERROR: Timeout waiting for neurons to be ready at step %0d", step_count);
                $finish;
            end
        end
    endtask

    task compute_input_currents;
        reg signed [31:0] I_syn;
        reg signed [15:0] I_ext;
        begin
            if (step_count >= I_EXT_START_STEP && step_count < I_EXT_END_STEP) begin
                I_ext = I_EXT_Q69;
            end else begin
                I_ext = 0;
            end

            for (i = 0; i < N; i = i + 1) begin
                I_syn = 0;

                for (j = 0; j < N; j = j + 1) begin
                    if (spike_prev[j]) begin
                        I_syn = I_syn + W[i*N + j];
                    end
                end

                input_current[i] = I_syn[15:0] + I_ext;
            end
        end
    endtask

    task record_spikes;
        begin
            $fwrite(spike_file, "%0d", step_count);
            for (i = 0; i < N; i = i + 1) begin
                $fwrite(spike_file, ",%0d", spike[i]);
            end
            $fwrite(spike_file, "\n");
        end
    endtask

    initial begin
        #(CLK_PERIOD * STEPS * 100);
        if (!simulation_done) begin
            $display("ERROR: Simulation timeout!");
            $finish;
        end
    end

endmodule
