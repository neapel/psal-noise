#ifndef __ca_hh__
#define __ca_hh__

#include <cstdlib>
#include <bitset>
#include <array>
#include <complex>
#include <random>
#include <chrono>
#include <fcntl.h>
#include <fftw3.h>

// Calculate x for: y = 1 << x.
constexpr size_t log2(size_t x) {
	return __builtin_ffsll(x) - 1;
}

template<size_t length>
struct rule_traits {
	enum {
		neighbors = log2(length),
		delta = (neighbors - 1) / 2
	};
};

// Specialisations for older GCC.
template<>
struct rule_traits<32> { enum { neighbors = 5, delta = 2 }; };

template<>
struct rule_traits<8> { enum { neighbors = 3, delta = 1 }; };




// Create an initial configuration: Random uniform distribution of 0 and 1.
template<size_t width, typename random>
void initial(random &gen, std::array<bool, width> &d) {
	std::bernoulli_distribution bit;
	for(size_t x = 0 ; x < width ; x++)
		d[x] = bit(gen);
}

// Evaluate the rule, return output array.
template<size_t width, size_t height, size_t rules>
void eval(const std::bitset<rules> &r, std::array<std::array<bool, width>, height> &d) {
	using namespace std;
	const size_t neighbors = rule_traits<rules>::neighbors;
	const size_t delta = rule_traits<rules>::delta;
	// Evaluate each line.
	for(size_t i = 1 ; i < height ; i++)
		for(size_t j = 0 ; j < width ; j++) {
			size_t index = 0;
			for(size_t k = 0 ; k < neighbors ; k++)
				index |= d[i - 1][(width + j + k - delta) % width] << k;
			d[i][j] = r[index];
		}
}


template<typename T> T *fftwf_new(size_t n) {
	return reinterpret_cast<T *>(fftwf_malloc(n * sizeof(T)));
}

struct plan_t {
	typedef std::complex<float> C;
	float *in;
	C *out;
	fftwf_plan plan;

	plan_t(size_t N) {
		in = fftwf_new<float>(N);
		out = fftwf_new<C>(N/2+1);
		FILE *fi = fopen("fftwf.wisdom", "r");
		if(fi) { fftwf_import_wisdom_from_file(fi); fclose(fi); }
		plan = fftwf_plan_dft_r2c_1d(N, in, reinterpret_cast<fftwf_complex *>(out), FFTW_EXHAUSTIVE);
		FILE *fo = fopen("fftwf.wisdom", "w");
		if(fo) { fftwf_export_wisdom_to_file(fo); fclose(fo); }
	}

	void operator()() {
		fftwf_execute(plan);
	}
};


// Calculate the frequency spectrum of this array.
template<size_t N, size_t width, size_t height>
void spectrum(plan_t &plan, const std::array<std::array<bool, width>, height> &data, std::array<float, N> &sum) {
	using namespace std;
	sum.fill(0.0);
	for(size_t j = 0 ; j < width ; j++) {
		// One column
		for(size_t i = 0 ; i < height ; i++) plan.in[i] = data[i][j];
		// Run forward fourier for column
		plan();
		// Sum up spectrum
		for(size_t i = 0 ; i < N ; i++)
			sum[i] += norm(plan.out[i + 1] / float(height));
	}
}




#endif
