#ifndef __linear_fit_hh__
#define __linear_fit_hh__

#include <array>
#include <cstddef>
#include <cmath>
#include <tuple>

// Return average of array values.
template<typename I>
double average(I begin, I end) {
	double sum = 0;
	size_t n = 0;
	for(I i = begin ; i != end ; i++, n++) sum += *i;
	return sum / n;
}

// Fit a series of 2D points with `alpha + beta x`.
template<typename I, typename J>
std::pair<double, double> regress(I x_begin, I x_end, J y_begin, J y_end) {
	const auto x_avg = average(x_begin, x_end);
	const auto y_avg = average(y_begin, y_end);

	double v1 = 0, v2 = 0;
	auto x = x_begin;
	auto y = y_begin;
	for(; x != x_end && y != y_end ; x++, y++) {
		v1 += (*x - x_avg) * (*y - y_avg);
		v2 += pow(*x - x_avg, 2);
	}
	const auto beta = v1 / v2;
	const auto alpha = y_avg - beta * x_avg;
	return std::make_pair(alpha, beta);
}

// Calculate the fitness of this spectrum
template<size_t N_fit, size_t N_resid, size_t N, typename real>
std::tuple<double, double, double> fitness(const std::array<real, N> &spectrum) {
	using namespace std;
	static_assert(N_fit <= N_resid, "must fit over fewer values");
	// linear regression in log-log-space
	array<double, N_resid> xs, ys;
	for(size_t i = 0 ; i < N_resid ; i++) {
		xs[i] = log(i + 1);
		ys[i] = log(spectrum[i]);
	}
	const auto param = regress(xs.begin(), xs.begin() + N_fit, ys.begin(), ys.begin() + N_fit);
	const auto alpha = param.first, beta = param.second;
	double fit = 0;
	if(beta < 0) {
		// residuals
		double res = 0;
		for(size_t i = 0 ; i < N_resid ; i++)
			res += pow(ys[i] - alpha - beta * xs[i], 2);
		res /= N_resid;
		// fitness value
		fit = abs(beta) / (res + 1.0e-6);
	}
	return make_tuple(fit, alpha, beta);
}

#endif
