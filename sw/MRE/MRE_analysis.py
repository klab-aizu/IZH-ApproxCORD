import numpy as np
import evoapproxlib as eal
import pandas as pd

# =====================================================
# Fixed-point configuration (Q6.9 format)
# =====================================================
FRAC_BITS = 9
SCALE = 1 << FRAC_BITS

def float_to_fixed(val):
    return int(round(val * SCALE))

def fixed_to_float(val):
    return val / SCALE

# =====================================================
# Q6.9 <-> Q4.4
# =====================================================
def q6_9_to_q4_4(v_q69):
    return v_q69 >> (FRAC_BITS - 4)

def q4_4_to_q6_9(v_q44):
    return v_q44 << (FRAC_BITS - 4)

# =====================================================
# Approximate adders from EvoApproxLib
# =====================================================
APPROX_ADDERS = {
    "2TN": eal.add16se_2TN,
    "36D": eal.add16se_36D,
    "2UY": eal.add16se_2UY,
    "2UB": eal.add16se_2UB,
    "2U6": eal.add16se_2U6,
}

# =====================================================
# Convert unsigned 17-bit
# =====================================================
def u2s17(v):
    if v & (1 << 16):
        return v - (1 << 17)
    return v

# =====================================================
# Exact CORDIC-based multiplication (no approximation)
# =====================================================
def cordic_multiply_scaled_no_approx(x, z, iterations=12, fpx=4, fpz=4):
    x = x * (1 << fpx)
    z = z * (1 << fpz)
    scale = 0
    temp_z = abs(z)
    while temp_z > 1:
        temp_z /= 2
        scale += 1

    z_scaled = z / (2 ** scale)
    y = 0.0
    for i in range(iterations):
        d = 1 if z_scaled >= 0 else -1
        shift = x * (2 ** -i) * (2 ** scale)
        y += d * shift
        z_scaled -= d * (2 ** -i)
    return y / (1 << (fpx + fpz))

# =====================================================
# Approximate CORDIC-based multiplication
# Uses selected approximate adder
# =====================================================
def cordic_multiply_scaled_approx(x, z, iterations=12, fpx=4, fpz=4, adder_name="2TN"):
    adder = APPROX_ADDERS[adder_name]
    x = x * (1 << fpx)
    z = z * (1 << fpz)
    scale = 0
    temp_z = abs(z)
    while temp_z > 1:
        temp_z /= 2
        scale += 1
    z_scaled = z / (2 ** scale)
    y = 0.0
    for i in range(iterations):
        d = 1 if z_scaled >= 0 else -1
        shift = x * (2 ** -i) * (2 ** scale)
        y = adder.calc(y, d * shift)
        y_scaled = u2s17(int(round(y)))
        z_scaled -= d * (2 ** -i)
    return y_scaled / (1 << (fpx + fpz))

# =====================================================
# Baseline HOMIN neuron (exact multiplication)
# =====================================================
def simulate_homin_neuron(d_float, t_max=1000, dt=0.03125):
    steps = int(t_max / dt)
    v = float_to_fixed(-6.5)
    b = float_to_fixed(0.25)
    u = (v * b) >> FRAC_BITS
    d = float_to_fixed(d_float)
    threshold = float_to_fixed(3.0)

    V, spikes = [], []
    times = np.arange(0, steps) * dt

    for t in range(steps):
        I = float_to_fixed(15 if 100 < t * dt < 1000 else 0)

        v_sq = (v * v) >> FRAC_BITS

        # dv/dt equation
        dv = (v_sq >> 2) + (v << 2) + v + float_to_fixed(14) - u + I

        # du/dt equation
        temp = (v >> 2) - u
        du = temp >> 6

        v += (dv * float_to_fixed(dt)) >> FRAC_BITS
        u += (du * float_to_fixed(dt)) >> FRAC_BITS

        v = max(v, float_to_fixed(-8))

        if v >= threshold:
            V.append(fixed_to_float(threshold))
            spikes.append(1)
            v = float_to_fixed(-6.5)
            u += d
        else:
            V.append(fixed_to_float(v))
            spikes.append(0)

    return times, V, spikes

# =====================================================
# HOMIN neuron using exact CORDIC multiplication
# =====================================================
def simulate_homin_neuron_cordic_no_approx(d_float, iterations, t_max=1000, dt=0.03125):
    steps = int(t_max / dt)
    v = float_to_fixed(-6.5)
    b = float_to_fixed(0.25)
    u = (v * b) >> FRAC_BITS
    d = float_to_fixed(d_float)
    threshold = float_to_fixed(3.0)

    V, spikes = [], []
    times = np.arange(0, steps) * dt

    for t in range(steps):
        I = float_to_fixed(15 if 100 < t * dt < 1000 else 0)

        v_q44 = q6_9_to_q4_4(v)
        v_f = v_q44 / (1 << 4)

        v_sq_f = cordic_multiply_scaled_no_approx(
            v_f, v_f, iterations=iterations, fpx=4, fpz=4
        )
        v_sq = float_to_fixed(v_sq_f)

        dv = (v_sq >> 2) + (v << 2) + v + float_to_fixed(14) - u + I

        temp = (v >> 2) - u
        du = temp >> 6

        v += (dv * float_to_fixed(dt)) >> FRAC_BITS
        u += (du * float_to_fixed(dt)) >> FRAC_BITS

        v = max(v, float_to_fixed(-8))

        if v >= threshold:
            V.append(fixed_to_float(threshold))
            spikes.append(1)
            v = float_to_fixed(-6.5)
            u += d
        else:
            V.append(fixed_to_float(v))
            spikes.append(0)

    return times, V, spikes

# =====================================================
# HOMIN neuron using approximate CORDIC (selectable adder)
# =====================================================
def simulate_homin_neuron_cordic_approx(d_float, iterations, t_max=1000, dt=0.03125, adder_name="2TN"):
    steps = int(t_max / dt)
    v = float_to_fixed(-6.5)
    b = float_to_fixed(0.25)
    u = (v * b) >> FRAC_BITS
    d = float_to_fixed(d_float)
    threshold = float_to_fixed(3.0)

    V, spikes = [], []
    times = np.arange(0, steps) * dt

    for t in range(steps):
        I = float_to_fixed(15 if 100 < t * dt < 1000 else 0)

        v_q44 = q6_9_to_q4_4(v)
        v_f = v_q44 / (1 << 4)

        v_sq_f = cordic_multiply_scaled_approx(
            v_f, v_f, iterations=iterations, fpx=4, fpz=4, adder_name=adder_name
        )
        v_sq = float_to_fixed(v_sq_f)

        dv = (v_sq >> 2) + (v << 2) + v + float_to_fixed(14) - u + I

        temp = (v >> 2) - u
        du = temp >> 6

        v += (dv * float_to_fixed(dt)) >> FRAC_BITS
        u += (du * float_to_fixed(dt)) >> FRAC_BITS

        v = max(v, float_to_fixed(-8))

        if v >= threshold:
            V.append(fixed_to_float(threshold))
            spikes.append(1)
            v = float_to_fixed(-6.5)
            u += d
        else:
            V.append(fixed_to_float(v))
            spikes.append(0)

    return times, V, spikes

# =====================================================
# Mean Relative Error (MRE) computation (%)
# =====================================================
def compute_mre_percent(t_cordic, t_ref):
    n = min(len(t_ref), len(t_cordic))
    if n == 0:
        return float('inf')
    total_error = 0.0
    for i in range(n):
        if t_ref[i] != 0:
            total_error += abs((t_cordic[i] - t_ref[i]) / t_ref[i])

    return (total_error / n) * 100

# =====================================================
# Run experiments and export MRE results to CSV
# =====================================================
def export_mre_results_to_csv(filename="mre_results.csv"):
    """
    Evaluate MRE for four HOMIN neuron types across
    different CORDIC iteration counts and adders.
    """
    neuron_configs = [
        ("RS", 8.0, "Regular Spiking"),
        ("IB", 5.0, "Intrinsically Bursting"),
        ("CH", 1.125, "Chattering"),
        ("LTS", 0.375, "Low-Threshold Spiking"),
    ]

    iteration_list = list(range(4, 17))
    results = []

    for abbr, d_val, label in neuron_configs:
        times_ref, _, spikes_ref = simulate_homin_neuron(d_val)
        spike_times_ref = [t for t, s in zip(times_ref, spikes_ref) if s == 1]

        for iter_count in iteration_list:
            # Exact CORDIC
            times_no, _, spikes_no = simulate_homin_neuron_cordic_no_approx(
                d_val, iterations=iter_count
            )
            spike_times_no = [t for t, s in zip(times_no, spikes_no) if s == 1]
            mre_no = compute_mre_percent(spike_times_no, spike_times_ref)
            results.append([abbr, iter_count, "No-Approx", mre_no])

            # Approximate adders
            for adder_name in APPROX_ADDERS.keys():
                times_ap, _, spikes_ap = simulate_homin_neuron_cordic_approx(
                    d_val, iterations=iter_count, adder_name=adder_name
                )
                spike_times_ap = [t for t, s in zip(times_ap, spikes_ap) if s == 1]
                mre_ap = compute_mre_percent(spike_times_ap, spike_times_ref)
                results.append([abbr, iter_count, adder_name.upper(), mre_ap])

    df = pd.DataFrame(results, columns=["Neuron", "Iteration", "Adder", "MRE"])
    df.to_csv(filename, index=False)

# =====================================================
# Run experiment
# =====================================================
export_mre_results_to_csv("mre_results.csv")
