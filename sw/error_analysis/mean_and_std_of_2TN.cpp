#include <iostream>
#include <cstdint>
#include <cmath>
#include <limits>

extern "C" uint64_t add16se_2TN(uint64_t B, uint64_t A);

int main() {

    // =========================================
    // FULL SEARCH: Compute gamma mean & std
    // =========================================
    const uint64_t MAX = 1ULL << 16;
    const long double N = (long double)MAX * (long double)MAX;

    long double sum  = 0.0L;
    long double sum2 = 0.0L;

    for (uint64_t a = 0; a < MAX; a++) {
        for (uint64_t b = 0; b < MAX; b++) {

            uint64_t exact  = (a + b) & 0xFFFF;
            uint64_t approx = add16se_2TN(b, a) & 0xFFFF;

            int32_t gamma = (int32_t)approx - (int32_t)exact;

            sum  += gamma;
            sum2 += (long double)gamma * gamma;
        }
    }

    long double mean = sum / N;
    long double var  = sum2 / N - mean * mean;
    long double std  = std::sqrt(var);

    std::cout << "=== Approximate Adder (2TN) Statistics ===\n";
    std::cout << "Mean(gamma) = " << (double)mean << "\n";
    std::cout << "Std(gamma)  = " << (double)std  << "\n";

    return 0;
}
