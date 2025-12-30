#include <iostream>
#include <cstdint>
#include <cmath>
#include <limits>
#include <random>
#include <fstream>

extern "C" uint64_t add16se_2TN(uint64_t B, uint64_t A);

int main() {

    // ======================================================
    // PART 1: FULL-SEARCH — COMPUTE gamma statistics
    // ======================================================
    const uint64_t MAX = 1ULL << 16;
    const uint64_t N   = MAX * MAX;

    long double sum = 0.0L;
    long double sum2 = 0.0L;
    int32_t gmin = INT32_MAX;
    int32_t gmax = INT32_MIN;

    for (uint64_t a = 0; a < MAX; a++) {
        for (uint64_t b = 0; b < MAX; b++) {

            uint64_t exact  = (a + b) & 0xFFFF;
            uint64_t approx = add16se_2TN(b, a) & 0xFFFF;

            int32_t gamma = (int32_t)approx - (int32_t)exact;

            sum  += gamma;
            sum2 += (long double)gamma * gamma;

            if (gamma < gmin) gmin = gamma;
            if (gamma > gmax) gmax = gamma;
        }
    }

    long double mean = sum / N;
    long double var  = sum2 / N - mean * mean;
    long double std  = std::sqrt(var);

    std::cout << "=== Approximate Adder Statistics ===\n";
    std::cout << "Mean γ = " << (double)mean << "\n";
    std::cout << "Std  γ = " << (double)std  << "\n";
    std::cout << "Min γ  = " << gmin << "\n";
    std::cout << "Max γ  = " << gmax << "\n\n";


    // ======================================================
    // PART 2: CORDIC accumulated error simulation (K = 4..16)
    // ======================================================
    const int MC = 200000;    // Monte-Carlo trials

    double mu    = (double)mean;
    double sigma = (double)std;

    std::mt19937_64 rng(123456);
    std::normal_distribution<double> dist(mu, sigma);
    std::uniform_int_distribution<int> sign_dist(0, 1);

    // ===== CSV OUTPUT =====
    std::ofstream fout("cordic_results.csv");
    fout << "K,MeanE,StdE,Emin,Emax\n";

    // ===== Loop through K = 4..16 =====
    for (int K = 4; K <= 16; K++) {

        double alphas[32];
        for (int i = 0; i < K; i++)
            alphas[i] = std::pow(2.0, -i);

        double sumE = 0.0, sumE2 = 0.0;
        double Emin = 1e300, Emax = -1e300;

        for (int t = 0; t < MC; t++) {
            double E = 0.0;

            for (int i = 0; i < K; i++) {
                double gamma_i = dist(rng);
                int sgn        = (sign_dist(rng) == 0 ? -1 : 1);

                E += alphas[i] * (sgn * gamma_i);
            }

            sumE  += E;
            sumE2 += E * E;

            if (E < Emin) Emin = E;
            if (E > Emax) Emax = E;
        }

        double meanE = sumE / MC;
        double varE  = sumE2 / MC - meanE * meanE;
        double stdE  = std::sqrt(varE);

        std::cout <<
            "K=" << K <<
            "  Mean(E)=" << meanE <<
            "  Std(E)="  << stdE <<
            "  Range=["  << Emin << "," << Emax << "]\n";

        fout << K << "," << meanE << "," << stdE << "," << Emin << "," << Emax << "\n";
    }

    fout.close();
    std::cout << "\nSaved results to cordic_results.csv\n";

    return 0;
}
