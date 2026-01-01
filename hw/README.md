# Hardware (hw) Directory Documentation

This directory contains Verilog/SystemVerilog hardware designs for the Izhikevich neuron model using Approximate CORDIC. 

## Directory Structure

```
hw/
├── README.md
├── W_matrix.csv                              # Synaptic weight matrix for neuron network
├── CORDIC Multiplier with Approximate adder/ # CORDIC multiplier module with approximate adders
│   ├── rtl/                                  # RTL source code
│   └── tb/                                   # Testbench
└── HOMIN Network/                            # HOMIN neuron network design
    ├── rtl/                                  # RTL source code
    └── tb/                                   # Testbench
```

---

## CORDIC Multiplier with Approximate Adder

### Description

Module multiplier based on the CORDIC (COordinate Rotation DIgital Computer) algorithm combined with approximate adders to optimize area and power consumption. 

### RTL Directory (`rtl/`)

#### 1. Approximate Adders

| File | Description |
|------|-------------|
| `add16se_exact.v` | Exact 16-bit adder (reference) |
| `add16se_2TN.v` | Approximate adder variant 2TN |
| `add16se_2U6.v` | Approximate adder variant 2U6 |
| `add16se_2UB.v` | Approximate adder variant 2UB |
| `add16se_2UY.v` | Approximate adder variant 2UY |
| `add16se_2YM.v` | Approximate adder variant 2YM |
| `add16se_32T.v` | Approximate adder variant 32T |
| `add16se_349.v` | Approximate adder variant 349 |
| `add16se_36D.v` | Approximate adder variant 36D |
| `add16se_3BD.v` | Approximate adder variant 3BD |

#### 2. CORDIC Multiplier Modules

| File | Description |
|------|-------------|
| `cordic_multiplier_exact. v` | Exact CORDIC multiplier |
| `cordic_multiplier_exact_fully_unrolled.v` | Exact CORDIC multiplier (fully unrolled) |
| `cordic_multiplier_approx_2TN.v` | CORDIC multiplier with approximate adder 2TN |
| `cordic_multiplier_approx_2TN_full_unrolled.v` | CORDIC multiplier 2TN (fully unrolled) |
| `cordic_multiplier_approx_2U6.v` | CORDIC multiplier with approximate adder 2U6 |
| `cordic_multiplier_approx_2UB.v` | CORDIC multiplier with approximate adder 2UB |
| `cordic_multiplier_approx_2UY.v` | CORDIC multiplier with approximate adder 2UY |
| `cordic_multiplier_approx_2YM.v` | CORDIC multiplier with approximate adder 2YM |
| `cordic_multiplier_approx_32T.v` | CORDIC multiplier with approximate adder 32T |
| `cordic_multiplier_approx_349.v` | CORDIC multiplier with approximate adder 349 |
| `cordic_multiplier_approx_36D. v` | CORDIC multiplier with approximate adder 36D |
| `cordic_multiplier_approx_3BD.v` | CORDIC multiplier with approximate adder 3BD |
| `direct_multiplier.v` | Direct multiplier (for comparison) |

### CORDIC Multiplier Module Interface

```verilog
module cordic_multiplier_approx_XXX (
    input         clk,        // Clock signal
    input         rst_n,      // Active-low reset
    input         start,      // Start multiplication
    input  signed [7:0] x,    // Multiplicand (Q4.4 format)
    input  signed [7:0] z,    // Multiplier (Q4.4 format)
    output [15:0] y,          // Product (Q6.9 format)
    output        done        // Done signal
);
```

### Parameters

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| `MAX_ITERATIONS` | 16 | Maximum number of CORDIC iterations |
| `SCALE` | 128 | Scale factor |
| `FRAC_BITS` | 8 | Number of fractional bits |

### Testbench Directory (`tb/`)

Contains SystemVerilog testbenches for each variant: 

- `cordic_multiplier_exact_tb.sv`
- `cordic_multiplier_approx_2TN_tb. sv`
- `cordic_multiplier_approx_2U6_tb.sv`
- ... and other variants

---

## HOMIN Network

### Description

HOMIN (Hardware-Optimized Modified Izhikevich Neuron) network design using approximate CORDIC for v² multiplication. 

### RTL Directory (`rtl/`)

#### `homin_cordic_2TN.v`

Main module implementing the HOMIN neuron model with approximate CORDIC. 

**Interface:**

```verilog
module homin_cordic_2TN (
    input         clk,                    // Clock signal
    input         rst_n,                  // Active-low reset
    input  signed [15:0] input_current,   // Input current (Q6.9 format)
    input  signed [7:0]  q4_4_in,         // Membrane voltage input (Q4.4 format)
    output reg signed [15:0] v,           // Membrane voltage (Q6.9 format)
    output reg    spike,                  // Spike signal
    output reg    ready                   // Ready signal
);
```

**Neuron Parameters:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| `c` | -3328 (Q6.9) | Reset voltage after spike (~-6.5mV) |
| `d` | 1024 (Q6.9) | Recovery coefficient after spike |
| `v_threshold` | 1536 (Q6.9) | Spike threshold (~3mV) |

**HOMIN Equations:**

```
dv/dt = v²/4 + 5v + 14 - u + I
du/dt = (v/4 - u) / 64

if v >= v_threshold: 
    v = c
    u = u + d
```

### Testbench Directory (`tb/`)

#### `network_testbench.v`

Testbench for simulating a network of 1000 neurons. 

**Simulation Parameters:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| `N` | 1000 | Number of neurons in the network |
| `T_MS` | 1000 | Simulation time (ms) |
| `DT` | 0.03125 | Time step |
| `CLK_PERIOD` | 10ns | Clock period |
| `STEPS` | 32000 | Number of simulation steps |

**Inputs:**

- Weight matrix `W_matrix.csv` (1000x1000)
- External current `I_EXT_Q69 = 7680` (Q6.9 format, ~15µA)

**Outputs:**

- File `spikes_verilog.txt`: Records all spikes from the network

---

## W_matrix.csv File

Synaptic weight matrix connecting neurons in the network, CSV format with dimensions 1000x1000. Each element `W[i][j]` represents the connection weight from neuron `j` to neuron `i`.

This matrix is generated from Python code, and the `W_matrix.csv` file serves as a sample file for running the hardware simulation. 

---

## Fixed-Point Formats

This project uses two fixed-point formats:

### Q4.4 Format (8-bit)

- 1 sign bit + 3 integer bits + 4 fractional bits
- Range: [-8, 7.9375]
- Resolution: 0.0625

### Q6.9 Format (16-bit)

- 1 sign bit + 6 integer bits + 9 fractional bits
- Range: [-64, 63.998]
- Resolution: 0.001953125

**Conversion:**

```verilog
// Q6.9 to Q4.4
q4_4 = (q6_9 + 16) >>> 5;

// Q4.4 to Q6.9
q6_9 = q4_4 <<< 5;
```

---

## Supported Neuron Behavior Types

| Type | Parameter d (float) | Parameter d (Q6.9) | Description |
|------|---------------------|--------------------| ------------|
| Regular Spiking (RS) | 8.0 | 4096 | Regular spiking pattern |
| Initial Bursting (IB) | 5.0 | 2560 | Initial burst followed by regular spiking |
| Chattering (CH) | 1.125 | 576 | Fast oscillations/chattering |
| Low-Threshold Spiking (LTS) | 0.375 | 192 | Low threshold spiking |

---

## References

- [Izhikevich Neuron Model](https://www.izhikevich.org/publications/spikes.htm)
- [EvoApproxLib](http://www.fit.vutbr.cz/research/groups/ehw/approxlib/) - Approximate adder library