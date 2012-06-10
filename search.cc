#include "linear_fit.hh"
#include "ca.hh"
#include "gen.hh"

#include <iostream>
#include <iomanip>
#include <bitset>
#include <chrono>
#include <random>
#include <omp.h>
#include <stdexcept>
#include <fstream>

template<size_t height, size_t width, size_t N, typename rule, typename plan_t>
double score_rule(plan_t &plan, const rule &r, const std::array<std::bitset<width>, N> &initials) {
	using namespace std;
	const size_t fit_w = 10, resid_w = 100;
	double avg_fit = 0;
	for(auto I = initials.begin() ; I != initials.end() ; I++) {
		const auto lines = eval<width, height>(r, *I);
		const auto spec = spectrum<resid_w>(plan, lines);
		avg_fit += get<0>(fitness<fit_w, resid_w>(spec));
	}
	return avg_fit / N;
}

typedef std::bitset<32> rule;



template<size_t width, size_t height, typename real>
struct population_scorer {
	typedef plan_t<height, real> _plan_t;
	std::vector<_plan_t> plan;
	typedef std::pair<rule, double> scored;

	population_scorer() {
		for(int i = 0 ; i < omp_get_max_threads() ; i++)
			plan.push_back(_plan_t());
	}

	template<typename random, size_t population>
	std::array<scored, population> operator()(random &gen, const std::array<rule, population> &rules) {
		using namespace std;
		// first lines
		array<bitset<width>, 10> initial_lines;
		for(auto I = initial_lines.begin() ; I != initial_lines.end() ; I++) *I = initial<width>(gen);
		// score the rules
		array<scored, population> scores;
		#pragma omp parallel for default(shared) schedule(static,40)
		for(size_t i = 0 ; i < population ; i++) {
			const size_t thread = omp_get_thread_num();
			scores[i] = scored(rules[i], score_rule<height>(plan[thread], rules[i], initial_lines));
			cerr << '|' << flush;
		}
		// sort by score
		sort(scores.begin(), scores.end(),
			[](const scored &a, const scored &b) { return a.second > b.second; });
		return scores;
	}

};


template<size_t N>
std::ostream &operator<<(std::ostream &o, const std::array<std::pair<rule, double>, N> &pop) {
	for(auto I = pop.begin() ; I != pop.end() ; I++)
		o << I->first.to_string() << '\t' << I->second << '\n';
	return o;
}

template<size_t N>
std::ostream &operator<<(std::ostream &o, const std::array<rule, N> &pop) {
	for(auto I = pop.begin() ; I != pop.end() ; I++)
		o << I->to_string() <<'\n';
	return o;
}


using namespace std;
using namespace std::chrono;



int main(int argc, char **argv) {
	if(argc != 2) {
		cerr << "Usage: " << argv[0] << " output-file" << endl;
		return 1;
	}

	const size_t width = 700, height = 3000;
	const size_t generations = 200;
	const size_t population = 160, elite = 20;

	// create and seed RNG
	random_device dev;
	mt19937 random(dev());

	// parallel scorer
	population_scorer<width, height, float> scorer;

	ofstream pop_out(argv[1]);

	auto pop = initial_population<32, population>(random);
	for(size_t g = 0 ; g < generations ; g++) {
		cout << "# generation " << setw(4) << g << flush;
		const auto t_start = high_resolution_clock::now();
		const auto pop_scored = scorer(random, pop);
		const duration<double> dur = high_resolution_clock::now() - t_start;
		cout << " total " << dur.count() << "s" << endl;

		pop_out << pop_scored << endl;
		pop = next_generation<elite>(random, pop_scored);
	}

	return 0;
}
