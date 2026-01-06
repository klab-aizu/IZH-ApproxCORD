# MRE

The MRE(Mean Relative Error) quantitatively measures the deviation in spike timing between the tested neuron model and the standard HOMIN model, and is defined as:

$$
\mathrm{MRE} =
\frac{1}{h}
\sum_{i=1}^{h}
\frac{l_{model,i} - l_{HOMIN,i}}
     {l_{HOMIN,i}}
\times 100
$$

where  $l_{\text{model},i}$ are the spike times of the tested variant (CORDIC-based or CORDIC with approximate adder HOMIN model), $l_{\text{HOMIN},i}$ are the spike times of the standard HOMIN neuron, and $h$ is the total number of spikes considered.

# MRE analysis for HOMIN_cordic throughout 4 to 16 iterations

The code employs Mean Relative Error (MRE) to quantitatively compare the spike timing of HOMIN_cordic_approx models with the standard HOMIN reference model.
The evaluation is conducted for CORDIC iteration counts ranging from 4 to 16 across four HOMIN neuron behaviors: Regular Spiking, Initial Bursting, Chattering, and Low-Threshold Spiking, enabling an analysis of how iterative CORDIC approximation affects spike timing accuracy.
