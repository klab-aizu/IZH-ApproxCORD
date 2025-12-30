import numpy as np
import matplotlib.pyplot as plt

# === Fixed-point config (Q6.9) ===
FRAC_BITS = 9
SCALE = 1 << FRAC_BITS
MAX_VAL = (1 << 15) - 1
MIN_VAL = -(1 << 15)

# === Fixed-point conversion ===
def float_to_fixed(val):
    return int(round(val * SCALE))

def fixed_to_float(val):
    return val / SCALE

def saturate16(x):
    return max(MIN_VAL, min(MAX_VAL, x))

# === Chuyển đổi Q6.9 <-> Q4.4 ===
def q6_9_to_q4_4(v_q69):
    return v_q69 >> (FRAC_BITS - 4)

def q4_4_to_q6_9(v_q44):
    return v_q44 << (FRAC_BITS - 4)

def fixed_square_v(v_q69):
    # Q6.9 -> Q4.4 (8-bit)
    v_q44 = q6_9_to_q4_4(v_q69)
    v_q44 = saturate16(v_q44)

    # Q4.4 × Q4.4 = Q8.8 (16-bit)
    prod_q88 = v_q44 * v_q44
    prod_q88 = saturate16(prod_q88)

    # Scale 2^-2: Q8.8 -> Q8.6
    prod_q86 = prod_q88 >> 2

    # Q8.6 -> Q6.9
    prod_q69 = prod_q86 << 3
    prod_q69 = saturate16(prod_q69)

    return prod_q69

# === HOMIN neuron simulation ===
def simulate_homin_neuron_fixed(d_float, t_max=1000, dt=0.03125):
    steps = int(t_max / dt)
    v = float_to_fixed(-6.5)   # Q6.9
    b = float_to_fixed(0.25)
    u = (v * b) >> FRAC_BITS
    d = float_to_fixed(d_float)
    threshold = float_to_fixed(3.0)

    V, spikes = [], []
    times = np.arange(0, steps) * dt

    for t in range(steps):
        I = float_to_fixed(15 if 100 < t * dt < 1000 else 0)

        v_sq = fixed_square_v(v)

        # dv/dt = (2^-2)v² + (2^2)v + v + 14 - u + I
        dv = (v_sq >> 2)        # (2^-2)v²
        dv += (v << 2)          # (2^2)v
        dv += v                 # v
        dv += float_to_fixed(14)
        dv -= u
        dv += I

        # du/dt = (2^-6)[(2^-2)v - u]
        temp = (v >> 2) - u
        du = temp >> 6

        # Update v, u
        v = saturate16(v + ((dv * float_to_fixed(dt)) >> FRAC_BITS))
        u = saturate16(u + ((du * float_to_fixed(dt)) >> FRAC_BITS))

        # Clamp v
        v = max(v, float_to_fixed(-8))

        if v >= threshold:
            V.append(fixed_to_float(threshold))
            spikes.append(1)
            v = float_to_fixed(-6.5)
            u = saturate16(u + d)
        else:
            V.append(fixed_to_float(v))
            spikes.append(0)

    return times, V, spikes

# === Plotting ===
def plot_4_homin_behaviors_fixed():
    configs = [
        (8.0, "Regular Spiking"),
        (5.0, "Initial Bursting"),
        (1.125, "Chattering"),
        (0.375, "Low-Threshold Spiking")
    ]

    plt.figure(figsize=(14, 12))

    for i, (d_val, name) in enumerate(configs):
        times, V, spikes = simulate_homin_neuron_fixed(d_val)

        plt.subplot(4, 2, 2 * i + 1)
        plt.plot(times, V, label=f"{name} (d={d_val})", color="blue", linewidth=0.8)
        plt.axhline(3.0, linestyle="--", color="gray", linewidth=0.5)
        plt.ylabel("Membrane Potential")
        plt.title(name)
        plt.grid(True)
        plt.legend()

        plt.subplot(4, 2, 2 * i + 2)
        spike_times = [t for t, s in zip(times, spikes) if s == 1]
        plt.stem(spike_times, [1]*len(spike_times),
                 linefmt='r-', markerfmt='ro', basefmt='k-')
        plt.ylim(-0.1, 1.5)
        plt.ylabel("Spike Output")
        plt.xlabel("Time (ms)")
        plt.title("Spike Train")
        plt.grid(True)

    plt.tight_layout()
    plt.show()

# === Run simulation ===
plot_4_homin_behaviors_fixed()
