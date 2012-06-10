#ifndef __ca_hh__
#define __ca_hh__

#include <cstdlib>
#include <bitset>
#include <array>
#include <complex>
#include <fftw3.h>
#include <random>
#include <chrono>

// Calculate x for: y = 1 << x.
constexpr size_t log2(size_t x) {
	return __builtin_ffsll(x) - 1;
}

// Create an initial configuration: Random uniform distribution of 0 and 1.
template<size_t width, typename random>
std::bitset<width> initial(random &gen) {
	std::bitset<width> x;
	std::bernoulli_distribution bit;
	for(size_t j = 0 ; j < width ; j++)
		x[j] = bit(gen);
	return x;
}

// Evaluate the rule, return output array.
template<size_t width, size_t height, size_t rules>
std::array<std::bitset<width>, height> eval(const std::bitset<rules> &r, const std::bitset<width> &initial) {
	using namespace std;
	const size_t neighbors = log2(rules);
	const size_t delta = (neighbors - 1) / 2;
	array<bitset<width>, height> d;
	d[0] = initial;
	// Evaluate each line.
	for(size_t i = 1 ; i < height ; i++)
		for(size_t j = 0 ; j < width ; j++) {
			bitset<neighbors> index;
			for(size_t k = 0 ; k < neighbors ; k++)
				index[k] = d[i - 1][(width + j + k - delta) % width];
			d[i][j] = r[index.to_ulong()];
		}
	return d;
}


template<size_t N, typename T> struct plan_t;

template<size_t N>
struct plan_t<N, float> {
	float *in;
	std::complex<float> *out;
	fftwf_plan plan;

	plan_t() {
		in = fftwf_alloc_real(N);
		auto out_ = fftwf_alloc_complex(N/2+1);
		out = reinterpret_cast<std::complex<float>*>(out_);
		fftwf_import_wisdom_from_filename("fftwf.wisdom");
		plan = fftwf_plan_dft_r2c_1d(N, in, out_, FFTW_EXHAUSTIVE);
		fftwf_export_wisdom_to_filename("fftwf.wisdom");
	}

	void operator()() {
		fftwf_execute(plan);
	}
};

template<size_t N>
struct plan_t<N, double> {
	double *in;
	std::complex<double> *out;
	fftw_plan plan;

	plan_t() {
		in = fftw_alloc_real(N);
		auto out_ = fftw_alloc_complex(N/2+1);
		out = reinterpret_cast<std::complex<double>*>(out_);
		fftw_import_wisdom_from_filename("fftw.wisdom");
		plan = fftw_plan_dft_r2c_1d(N, in, out_, FFTW_EXHAUSTIVE);
		fftw_export_wisdom_to_filename("fftw.wisdom");
	}

	void operator()() {
		fftw_execute(plan);
	}
};



// Calculate the frequency spectrum of this array.
template<size_t N, size_t width, size_t height, typename real>
std::array<real, N> spectrum(plan_t<height, real> &plan, const std::array<std::bitset<width>, height> &data) {
	using namespace std;
	array<real, N> sum;
	sum.fill(0.0);
	for(size_t j = 0 ; j < width ; j++) {
		// One column
		for(size_t i = 0 ; i < height ; i++) plan.in[i] = data[i][j];
		// Run forward fourier for column
		plan();
		// Sum up spectrum
		for(size_t i = 0 ; i < N ; i++)
			sum[i] += pow(abs(plan.out[i + 1] / real(height)), 2);
	}
	return sum;
}




#endif
