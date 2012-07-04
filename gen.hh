#ifndef __gen_hh__
#define __gen_hh__


#include <algorithm>
#include <bitset>
#include <array>
#include <set>
#include <random>
#include <iostream>

// Probability for one bit to be swapped
double mutation_prob = 0.05;
// Probability for crossover to happen at all
double crossover_prob = 0.6;

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

// Uniform crossover. Swaps bits randomly.
template<size_t N, typename random>
std::pair<std::bitset<N>, std::bitset<N>> uniform_crossover(random &gen, const std::bitset<N> &a, const std::bitset<N> &b) {
	using namespace std;
	auto x = a, y = b;
	// Swap bits with P_s = 0.5.
	bernoulli_distribution bit;
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
std::bitset<N> mutate(random &gen, const std::bitset<N> &x) {
	std::bernoulli_distribution bit(mutation_prob);
	auto y = x;
	for(size_t i = 1 ; i < N ; i++)
		if(bit(gen)) y[i] = !y[i];
	return y;
}

// Create the next generation from the scored generation
// Assuming the input is already sorted.
template<size_t elite, size_t rules, size_t count, typename random, template<size_t> class scored>
std::array<std::bitset<rules>, count> next_generation(random &gen, const std::array<scored<rules>, count> &pop, std::ostream &genealogy) {
	using namespace std;
	set<bitset<rules>> next;
	// copy the best rules
	for(size_t i = 0 ; i < elite ; i++) {
		next.insert(pop[i].the_rule);
		genealogy << "elite " << pop[i].the_rule.to_string() << '\n';
	}
	bernoulli_distribution do_crossover(crossover_prob);
	// set up the roulette wheel
	array<double, count> scores;
	for(size_t i = 0 ; i < count ; i++) scores[i] = pop[i].avg_score;
	discrete_distribution<size_t> wheel(scores.begin(), scores.end());
	// create the rest by roulette crossover
	while(next.size() < count) {
		const auto p1 = pop[wheel(gen)].the_rule, p2 = pop[wheel(gen)].the_rule;
		if(do_crossover(gen)) {
			const auto c = uniform_crossover(gen, p1, p2);
			const auto c1 = mutate(gen, c.first), c2 = mutate(gen, c.second);
			next.insert(c1);
			next.insert(c2);
			genealogy << "mate " << p1 << ' ' << p2 << " children " << c1 << ' ' << c2 << '\n';
		} else {
			// no crossover, just mutate
			const auto c1 = mutate(gen, p1), c2 = mutate(gen, p2);
			next.insert(c1);
			next.insert(c2);
			genealogy << "mutate " << p1 << ' ' << c1 << '\n';
			genealogy << "mutate " << p2 << ' ' << c2 << '\n';
		}
	}
	genealogy << endl;
	// got enough, maybe 1 too many.
	array<bitset<rules>, count> out;
	copy_n(next.begin(), count, out.begin());
	return out;
}

#endif
