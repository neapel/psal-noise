#ifndef __gen_hh__
#define __gen_hh__


#include <algorithm>
#include <bitset>
#include <array>
#include <set>
#include <random>

// Generate a random rule in which `lambda` bits are 1.
// The LSB is always 0.
template<size_t rules, typename random>
std::bitset<rules> rule_from_lambda(random &gen, size_t lambda) {
	using namespace std;
	array<bool, rules> r;
	r.fill(false);
	for(size_t i = 1 ; i <= lambda && i < rules ; i++) r[i] = true;
	random_shuffle(r.begin() + 1, r.end(), [&gen](ptrdiff_t x){
		return uniform_int_distribution<ptrdiff_t>(0, x - 1)(gen);
	});
	bitset<rules> b;
	for(size_t i = 0 ; i < rules ; i++) b[i] = r[i];
	return b;
}

// Rules are sortable.
namespace std {
	template<size_t N>
	bool operator<(const bitset<N> &a, const bitset<N> &b) {
		return a.to_ulong() < b.to_ulong();
	}
}

// Generate an initial population of unique rules.
template<size_t rules, size_t count, typename random>
std::array<std::bitset<rules>, count> initial_population(random &gen) {
	using namespace std;
	set<bitset<rules>> pop;
	uniform_int_distribution<size_t> lambda(1, rules/2);
	while(pop.size() < count)
		pop.insert(rule_from_lambda<rules>(gen, lambda(gen)));
	array<bitset<rules>, count> out;
	copy(pop.begin(), pop.end(), out.begin());
	return out;
}

// Uniform crossover. Swaps bits between two genomes with some probability.
template<size_t N, typename random>
std::pair<std::bitset<N>, std::bitset<N>> uniform_crossover(random &gen, const std::bitset<N> &a, const std::bitset<N> &b, double prob = 0.6) {
	using namespace std;
	auto x = a, y = b;
	bernoulli_distribution bit(1 - prob);
	for(size_t i = 0 ; i < N ; i++)
		if(bit(gen)) {
			const bool temp = x[i];
			x[i] = y[i];
			y[i] = temp;
		}
	return make_pair(x, y);
}

// Flip bits with some probability.
template<size_t N, typename random>
std::bitset<N> mutate(random &gen, const std::bitset<N> &x, double prob = 0.05) {
	std::bernoulli_distribution bit(prob);
	auto y = x;
	for(size_t i = 1 ; i < N ; i++)
		if(bit(gen)) y[i] = !y[i];
	return y;
}

// Create the next generation from the scored generation
// Assuming the input is already sorted.
template<size_t elite, size_t rules, size_t count, typename random>
std::array<std::bitset<rules>, count> next_generation(random &gen, const std::array<std::pair<std::bitset<rules>, double>, count> &pop) {
	using namespace std;
	set<bitset<rules>> next;
	// copy the best rules
	for(size_t i = 0 ; i < elite ; i++)
		next.insert(pop[i].first);
	// set up the roulette wheel
	array<double, count> scores;
	for(size_t i = 0 ; i < count ; i++) scores[i] = pop[i].second;
	discrete_distribution<size_t> wheel(scores.begin(), scores.end());
	// create the rest by roulette crossover
	while(next.size() < count) {
		const auto c = uniform_crossover(gen, pop[wheel(gen)].first, pop[wheel(gen)].first);
		next.insert(mutate(gen, c.first));
		next.insert(mutate(gen, c.second));
	}
	// got enough, maybe 1 too many.
	array<bitset<rules>, count> out;
	copy_n(next.begin(), count, out.begin());
	return out;
}

#endif
