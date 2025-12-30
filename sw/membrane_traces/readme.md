# HOMIN Neuron Simulation

This repository simulates membrane potential traces of the HOMIN neuron model using
fixed-point arithmetic (Q4.4 and Q6.9 format), including four standard neuron behaviors:
Regular Spiking, Intrinsically Bursting, Chattering, and Low-Threshold Spiking.

Two implementations are provided:
- HOMIN_exact_fixed_point.py: exact fixed-point arithmetic
- HOMIN_CORDIC_approx.py: CORDIC-based approximate arithmetic
