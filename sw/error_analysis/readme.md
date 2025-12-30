# Purpose

The objective of this workflow is to quantify the impact of the **2TN approximate 16-bit adder** when used within the HOMIN neuron model.  
Specifically, the study analyzes how the intrinsic arithmetic error introduced by the 2TN adder propagates through **CORDIC-based computations**, which are employed for multiplication inside the model, and how this accumulated error may affect higher-level neural dynamics.

To achieve this, the adder error is first statistically characterized at the arithmetic level, and then its effect is evaluated at the algorithmic level through CORDIC error accumulation analysis.

# How to run

## mean_and_std_of_2TN.cpp
This file run first.
It performs an exhaustive evaluation of the 2TN approximate adder over the full 16-bit input space.
The program computes the mean and standard deviation of the adder error, where the error is defined as the difference between the approximate addition result and the exact addition result.
The computed statistical parameters are exported to a CSV file, which serves as the input for subsequent analysis.

## error_analysis_2TN.py
This script run after adder_stats.cpp.
It reads the CSV file generated in the previous step and uses the extracted adder error statistics to perform a Monte-Carlo simulation of accumulated error in CORDIC-based computations.
The simulation is carried out for CORDIC iteration counts ranging from 4 to 16, enabling the evaluation of how errors introduced by the 2TN approximate adder propagate and accumulate across multiple CORDIC iterations.
