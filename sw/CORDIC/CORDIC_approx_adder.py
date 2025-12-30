import evoapproxlib as eal

def u2s17(v):
    if v & (1 << 16):
        return v - (1 << 17)
    return v

def cordic_multiply_scaled(x, z, iterations=8, fpx=4, fpz=4):
    # scale inputs
    x = x * (1 << fpx)
    z = z * (1 << fpz)

    # normalize z
    scale = 0
    temp_z = abs(z)
    while temp_z > 1:
        temp_z /= 2
        scale += 1

    z_scaled = z / (2 ** scale)
    y = 0.0

    for i in range(iterations):
        d = 1.0 if z_scaled >= 0 else -1.0
        shift = x * (2 ** -i) * (2 ** scale)

        # approximate addition
        y = eal.add16se_2TN.calc(y, d * shift)

        # emulate signed 17-bit overflow
        y = u2s17(int(round(y)))

        z_scaled -= d * (2 ** -i)

    return y / (1 << (fpx + fpz))
x = 1.25
z = 1.25

y_approx = cordic_multiply_scaled(x, z)
y_exact = x * z

print("CORDIC approx :", y_approx)
print("Exact         :", y_exact)
