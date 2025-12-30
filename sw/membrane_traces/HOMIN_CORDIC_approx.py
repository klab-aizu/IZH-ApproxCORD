import numpy as np
import matplotlib.pyplot as plt
import evoapproxlib as eal

# =================================
# Fixed-point config (Q6.9)
# =================================
FRAC_BITS = 9
SCALE = 1 << FRAC_BITS

def float_to_fixed(x):
    return int(round(x * SCALE))

def fixed_to_float(x):
    return x / SCALE

# =================================
# Q-format helpers
# =================================
def q6_9_to_q4_4(v):
    return v >> (FRAC_BITS - 4)

def u2s17(v):
    if v & (1 << 16):
        return v - (1 << 17)
    return v

# =================================
# CORDIC multiply
# =================================
def cordic_mul_2tn(x, z, iterations=12, fpx=4, fpz=4):
    x = x * (1 << fpx)
    z = z * (1 << fpz)

    scale = 0
    tmp = abs(z)
    while tmp > 1:
        tmp /= 2
        scale += 1

    z_scaled = z / (2 ** scale)
    y = 0.0

    for i in range(iterations):
        d = 1 if z_scaled >= 0 else -1
        shift = x * (2 ** -i) * (2 ** scale)
        y = eal.add16se_2TN.calc(y, d * shift)
        y = u2s17(int(round(y)))
        z_scaled -= d * (2 ** -i)

    return y / (1 << (fpx + fpz))

# =================================
# HOMIN neuron (CORDIC)
# =================================
def simulate_homin_neuron(d_float, iterations=12, t_max=1000, dt=0.03125):
    steps = int(t_max / dt)

    v = float_to_fixed(-6.5)
    b = float_to_fixed(0.25)
    u = (v * b) >> FRAC_BITS
    d = float_to_fixed(d_float)
    threshold = float_to_fixed(3.0)

    V, spikes = [], []
    times = np.arange(steps) * dt

    for t in range(steps):
        I = float_to_fixed(15 if 100 < t * dt < 1000 else 0)

        # v^2 via CORDIC
        v_q44 = q6_9_to_q4_4(v)
        v_f = v_q44 / (1 << 4)
        v_sq_f = cordic_mul_2tn(v_f, v_f, iterations)
        v_sq = float_to_fixed(v_sq_f)

        # dv/dt
        dv  = (v_sq >> 2)
        dv += (v << 2)
        dv += v
        dv += float_to_fixed(14)
        dv -= u
        dv += I

        # du/dt
        du = ((v >> 2) - u) >> 6

        # update
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

# =================================
# Plotting
# =================================
def plot_4_homin_behaviors():
    configs = [
        (8.0, "Regular Spiking"),
        (5.0, "Initial Bursting"),
        (1.125, "Chattering"),
        (0.375, "Low-Threshold Spiking")
    ]

    plt.figure(figsize=(14, 12))

    for i, (d_val, name) in enumerate(configs):
        times, V, spikes = simulate_homin_neuron(d_val)

        plt.subplot(4, 2, 2*i + 1)
        plt.plot(times, V, color="blue", linewidth=0.8,
                 label=f"{name} (d={d_val})")
        plt.axhline(3.0, linestyle="--", color="gray", linewidth=0.5)
        plt.ylabel("Membrane Potential")
        plt.title(name)
        plt.grid(True)
        plt.legend()

        plt.subplot(4, 2, 2*i + 2)
        spike_times = [t for t, s in zip(times, spikes) if s]
        plt.stem(spike_times, [1]*len(spike_times),
                 linefmt='r-', markerfmt='ro', basefmt='k-')
        plt.ylim(-0.1, 1.5)
        plt.ylabel("Spike Output")
        plt.xlabel("Time (ms)")
        plt.title("Spike Train")
        plt.grid(True)

    plt.tight_layout()
    plt.show()

# =================================
# Run
# =================================
plot_4_homin_behaviors()
