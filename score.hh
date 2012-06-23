#ifndef __score_hh__
#define __score_hh__

#include "ca.hh"
#include "linear_fit.hh"
#include <cstddef>
#include <array>
#include <bitset>
#include <iostream>
#include <omp.h>


template<size_t height, size_t width, size_t N, typename rule, typename plan_t>
std::array<double, N> score_rule(plan_t &plan, const rule &r, const std::array<std::bitset<width>, N> &initials) {
	using namespace std;
	const size_t fit_w = 10, resid_w = 100;
	array<double, N> fit;
	for(size_t i = 0 ; i < N ; i++) {
		const auto lines = eval<width, height>(r, initials[i]);
		const auto spec = spectrum<resid_w>(plan, lines);
		fit[i] = get<0>(fitness<fit_w, resid_w>(spec));
	}
	return fit;
}


const size_t initial_N = 10;


template<size_t rules>
struct scored {
	std::bitset<rules> the_rule;
	std::array<double, initial_N> scores;
	double avg_score;

	scored() : the_rule(), scores(), avg_score(-1) {}

	scored(std::bitset<rules> r, std::array<double, initial_N> s) : the_rule(r), scores(s), avg_score(0) {
		for(size_t i = 0 ; i < initial_N ; i++)
			avg_score += s[i];
		avg_score /= initial_N;
	}

	bool operator<(const scored &other) const {
		return avg_score > other.avg_score;
	}
};

template<size_t rules>
std::ostream &operator<<(std::ostream &o, const scored<rules> &s) {
	o << s.the_rule.to_string() << ' ' << s.avg_score << "\t";
	for(auto I = s.scores.begin() ; I != s.scores.end() ; I++)
		o << *I << ' ';
	return o;
}



template<size_t width, size_t height, typename real>
struct population_scorer {
	typedef plan_t<height, real> _plan_t;
	std::vector<_plan_t> plan;

	population_scorer() {
		for(int i = 0 ; i < omp_get_max_threads() ; i++)
			plan.push_back(_plan_t());
	}

	template<typename random, size_t population, size_t rules>
	std::array<scored<rules>, population> operator()(random &gen, const std::array<std::bitset<rules>, population> &pop) {
		using namespace std;
		// first lines
		array<bitset<width>, initial_N> initial_lines;
		for(auto I = initial_lines.begin() ; I != initial_lines.end() ; I++) *I = initial<width>(gen);
		// score the rules
		array<scored<rules>, population> scores;
		#pragma omp parallel for default(shared) schedule(static,40)
		for(size_t i = 0 ; i < population ; i++) {
			const size_t thread = omp_get_thread_num();
			scores[i] = scored<rules>(pop[i], score_rule<height>(plan[thread], pop[i], initial_lines));
			cerr << '|' << flush;
		}
		// sort by score
		sort(scores.begin(), scores.end());
		return scores;
	}

};


template<size_t N, size_t rules>
std::ostream &operator<<(std::ostream &o, const std::array<scored<rules>, N> &pop) {
	for(size_t i = 0 ; i < N ; i++)
		o << pop[i] << '\n';
	return o;
}


#endif
