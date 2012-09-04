#include <cstdlib>
#include <cstddef>
#include <cmath>
#include <complex>

#include <bitset>
#include <array>
#include <set>
#include <tuple>

#include <algorithm>

#include <iostream>
#include <iomanip>
#include <fstream>

#include <stdexcept>
#include <chrono>
#include <random>

#define BOOST_DISABLE_ASSERTS 1

#include <boost/program_options.hpp>
#include <boost/filesystem.hpp>
#include <boost/format.hpp>
#include <boost/lexical_cast.hpp>

#include <fcntl.h>
#include <fftw3.h>
#include <omp.h>


using namespace std;
using namespace std::chrono;
using namespace boost;
using namespace boost::program_options;
using namespace boost::filesystem;


//## Cellular Automaton.

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


struct spectrum_t {
	private:
	size_t width, height;
	bool *lines;
	float *in;
	complex<float> *out;
	fftwf_plan plan;

	template<typename T> static T *fftwf_new(size_t n) {
		return reinterpret_cast<T *>(fftwf_malloc(n * sizeof(T)));
	}

	public:
	spectrum_t(size_t width, size_t height)
	: width(width), height(height),
	  lines(fftwf_new<bool>(width * height)),
	  in(fftwf_new<float>(width * height)),
	  out(fftwf_new<complex<float>>(width * (height/2+1))) {
		auto path = str(format("fftwm-w%d-h%d.wisdom") % width % height);
		FILE *fi = fopen(path.c_str(), "r");
		if(fi) { fftwf_import_wisdom_from_file(fi); fclose(fi); }

		int N[] = {static_cast<int>(height)};
		fftwf_set_timelimit(60); // max 1 minute
		plan = fftwf_plan_many_dft_r2c(
			/*rank*/1, /*n*/N, /*howmany*/width, in,
			/*inembed*/nullptr, /*istride*/width, /*idist*/1,
			reinterpret_cast<fftwf_complex *>(out),
			/*onembed*/nullptr, /*ostride*/width, /*odist*/1,
			FFTW_EXHAUSTIVE);
		FILE *fo = fopen(path.c_str(), "w");
		if(fo) { fftwf_export_wisdom_to_file(fo); fclose(fo); }
	}


	// Initialize the first line.
	template<class Iterator>
	void init(Iterator i) {
		for(size_t x = 0 ; x < width ; x++)
			lines[x] = *i++;
	}


	// Evaluate the rule.
	template<size_t rules>
	void eval(const bitset<rules> &r) {
		const size_t neighbors = rule_traits<rules>::neighbors;
		const size_t delta = rule_traits<rules>::delta;
		const auto rule = r.to_ulong();
#if 0
		// Evaluate naively.
		for(size_t y = 1 ; y < height ; y++) {
			const auto curr = lines + (y * width), prev = curr - width;
			for(size_t x = 0 ; x < width ; x++) {
				size_t index = 0;
				for(size_t k = 0 ; k < neighbors ; k++)
					index |= prev[(width + x + k - delta) % width] << k;
				curr[x] = (rule >> index) & 1;
			}
		}
#else
		// Evaluate each line.
		for(size_t y = 1 ; y < height ; y++) {
			const auto start = lines + (y * width), end = start + width;
			auto curr = start, prev = start - width;
			// fill index, evaluate first cell.
			size_t index = 0;
			for(size_t k = 0 ; k < neighbors ; k++)
				index |= prev[(width + k - delta) % width] << k;
			*curr++ = (rule >> index) & 1;
			prev += neighbors - delta;
			// evaluate next cells
			while(prev != start) {
				// update index
				index >>= 1;
				index |= *prev++ << (neighbors - 1);
				*curr++ = (rule >> index) & 1;
			}
			prev -= width;
			// evaluate wrapping cells
			while(curr != end) {
				index >>= 1;
				index |= *prev++ << (neighbors - 1);
				*curr++ = (rule >> index) & 1;
			}
		}
#endif
	}


	// Calculate the frequency spectrum of this array.
	template<class Iterator>
	void freq(Iterator begin, Iterator end) {
		// convert input to float.
		copy(lines, lines + width * height, in);
		// transform columns.
		fftwf_execute(plan);
		// sum columns.
		assert(end <= begin + height/2 + 1);
		auto row = out + width; // skip first row.
		const auto scale = 1 / pow(height, 2);
		for(auto I = begin ; I != end ; I++, row += width) {
			float sum = 0;
			for(size_t x = 0 ; x < width ; x++)
				sum += norm(row[x]);
			*I = sum * scale;
		}
	}


	// Dump lines
	void dump(ostream &o) const {
		for(size_t y = 0 ; y < height ; y++) {
			for(size_t x = 0 ; x < width ; x++)
				o << (lines[y * width + x] ? '1' : '0') << ' ';
			o << '\n';
		}
	}
};

ostream &operator <<(ostream &o, const spectrum_t &s) {
	s.dump(o);
	return o;
}



//## Fitness calculation.

// Return average of array values.
template<class Iterator>
double average(Iterator begin, Iterator end) {
	double sum = 0;
	size_t n = 0;
	for(auto I = begin ; I != end ; I++, n++) sum += *I;
	return sum / n;
}


// Fit a series of 2D points with `alpha + beta x`.
template<typename I, typename J>
pair<double, double> regress(I x_begin, I x_end, J y_begin, J y_end) {
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
	return make_pair(alpha, beta);
}


// Calculate the fitness of this spectrum
template<class Iterator>
tuple<double, double, double> fitness(Iterator begin, Iterator end, size_t fit) {
	const size_t resid = end - begin;
	assert(fit <= resid);
	// linear regression in log-log-space
	double xs[resid];
	for(size_t i = 0 ; i < resid ; i++) xs[i] = log(i + 1);
	double ys[resid];
	transform(begin, end, ys, [](double x){return log(x);});
	double alpha, beta;
	tie(alpha, beta) = regress(xs, xs + fit, ys, ys + fit);
	// calculate fitness
	double f = 0;
	if(beta < 0) {
		// residuals
		double res = 0;
		for(size_t i = 0 ; i < resid ; i++)
			res += pow(ys[i] - alpha - beta * xs[i], 2);
		res /= resid;
		// fitness value
		f = abs(beta) / (res + 1.0e-6);
	}
	return make_tuple(f, alpha, beta);
}


//## Scoring

// a scored rule.
template<class Rule>
struct scored {
	Rule the_rule;
	vector<double> scores;
	double avg_score;

	scored() : the_rule(), scores(), avg_score(-1) {}
	scored(Rule r) : the_rule(r), scores(), avg_score(-1) {}

	bool operator<(const scored &other) const {
		return avg_score > other.avg_score;
	}
};

template<class Rule>
ostream &operator<<(ostream &o, const scored<Rule> &s) {
	o << s.the_rule.to_string();
	if(s.avg_score >= 0) {
		o << ' ' << s.avg_score << '\t';
		for(auto x : s.scores) o << x << ' ';
	}
	return o;
}


// scores and sorts the given rules.
struct population_scorer {
	vector<spectrum_t> spectrum;
	size_t width, initials, resid, fit;
	float initials_density;

	population_scorer(size_t w, size_t h, size_t in, size_t r, size_t f, float id) : width(w), initials(in), resid(r), fit(f), initials_density(id) {
		for(int i = 0 ; i < omp_get_max_threads() ; i++)
			spectrum.push_back(spectrum_t(w, h));
	}

	template<class Random, class Iterator>
	void operator()(Random &gen, Iterator begin, Iterator end) {
		// reserve places for scores
		for(auto I = begin ; I != end ; I++) {
			I->scores.clear();
			fill_n(back_inserter(I->scores), initials, -1);
		}

		// create initial lines
		bool *start = new bool[initials * width];
		bernoulli_distribution bit(initials_density);
		generate(start, start + initials * width, [&]{return bit(gen);});

		#pragma omp parallel for schedule(dynamic)
		for(size_t i = 0 ; i < initials ; i++) {
			// initialize this thread's automaton
			const size_t thread = omp_get_thread_num();
			auto spect = spectrum.at(thread);
			spect.init(start + i * width);
			float spec[resid];

			// score each rule.
			for(auto I = begin ; I != end ; I++) {
				spect.eval(I->the_rule);
				spect.freq(spec, spec + resid);
				auto f = get<0>(fitness(spec, spec + resid, fit));
				I->scores[i] = f;
			}
		}

		delete[] start;

		// sort by average score.
		for(auto I = begin ; I != end ; I++)
			I->avg_score = average(I->scores.begin(), I->scores.end());
		sort(begin, end);
	}
};

template<class Rule>
ostream &operator<<(ostream &o, const vector<scored<Rule>> &pop) {
	for(auto p : pop) o << p << '\n';
	return o;
}


//## Genetic algorithm.

// Rules are sortable.
namespace std {
	template<size_t N>
	bool operator<(const bitset<N> &a, const bitset<N> &b) {
		return a.to_ulong() < b.to_ulong();
	}
}

template<size_t N, class Random>
struct genetic_algorithm {
	// Probability for one bit to be swapped
	double mutation_prob;
	// Probability for crossover to happen at all
	double crossover_prob;

	size_t elite;

	Random &gen;

	genetic_algorithm(double mp, double cp, size_t e, Random &g) : mutation_prob(mp), crossover_prob(cp), elite(e), gen(g) {}


	// Generate a random rule in which `lambda` bits are 1.
	// The LSB is always 0.
	bitset<N> rule_from_lambda(size_t lambda) {
		std::array<bool, N> r;
		r.fill(false);
		for(size_t i = 1 ; i <= lambda && i < N ; i++) r[i] = true;
		random_shuffle(r.begin() + 1, r.end(), [&](ptrdiff_t x){
			return uniform_int_distribution<ptrdiff_t>(0, x - 1)(gen);
		});
		bitset<N> b;
		for(size_t i = 0 ; i < N ; i++) b[i] = r[i];
		return b;
	}


	// Generate an initial population of unique rules.
	template<class OutputIterator>
	void initial_population(OutputIterator out, size_t count) {
		set<bitset<N>> pop;
		uniform_int_distribution<size_t> lambda(1, N/2);
		while(pop.size() < count)
			pop.insert(rule_from_lambda(lambda(gen)));
		copy(pop.begin(), pop.end(), out);
	}


	// Uniform crossover. Swaps bits randomly.
	pair<bitset<N>, bitset<N>> uniform_crossover(const bitset<N> &a, const bitset<N> &b) {
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
	bitset<N> mutate(const bitset<N> &x) {
		bernoulli_distribution bit(mutation_prob);
		auto y = x;
		for(size_t i = 1 ; i < N ; i++)
			if(bit(gen)) y[i] = !y[i];
		return y;
	}


	// Create the next generation from the scored generation
	// Assuming the input is already sorted.
	template<class Iterator>
	void next_generation(Iterator begin, Iterator end, ostream &genealogy) {
		size_t count = end - begin;
		set<bitset<N>> next;
		// copy the best rules
		auto best = begin;
		for(size_t i = 0 ; i < elite ; i++, best++) {
			next.insert(best->the_rule);
			genealogy << "elite " << best->the_rule.to_string() << '\n';
		}

		bernoulli_distribution do_crossover(crossover_prob);
		
		// set up the roulette wheel
		double scores[count];
		for(size_t i = 0 ; i < count ; i++)
			scores[i] = (begin + i)->avg_score;
		discrete_distribution<size_t> wheel(scores, scores + count);

		// create the rest by roulette crossover
		while(next.size() < count) {
			const auto p1 = (begin + wheel(gen))->the_rule,
			           p2 = (begin + wheel(gen))->the_rule;
			if(do_crossover(gen)) {
				const auto c = uniform_crossover(p1, p2);
				const auto c1 = mutate(c.first), c2 = mutate(c.second);
				next.insert(c1);
				next.insert(c2);
				genealogy << "mate " << p1 << ' ' << p2 << " children " << c1 << ' ' << c2 << '\n';
			} else {
				// no crossover, just mutate
				const auto c1 = mutate(p1), c2 = mutate(p2);
				next.insert(c1);
				next.insert(c2);
				genealogy << "mutate " << p1 << ' ' << c1 << '\n';
				genealogy << "mutate " << p2 << ' ' << c2 << '\n';
			}
		}
		genealogy << endl;
		// got enough, maybe 1 too many.
		copy_n(next.begin(), count, begin);
	}
};


//## Main part.

// Run the rule once, diagnostic output.
template<class Random, class Rule>
void run_once(Random &gen, const Rule &r, size_t width, size_t height, bool do_spectrum, bool dump, size_t residN, size_t fitN, float initials_density) {
	// run once
	spectrum_t spectrum(width, height);
	bernoulli_distribution bit(initials_density);
	bool init[width];
	generate(init, init + width, [&]{return bit(gen);});	
	spectrum.init(init);
	spectrum.eval(r);

	if(do_spectrum) {
		// calculate spectrum
		float spec[height/2 + 1];
		spectrum.freq(spec, spec + (height/2 + 1));

		double fit, alpha, beta;
		tie(fit, alpha, beta) = fitness(spec, spec + residN, fitN);

		cout.precision(10);
		cout << scientific;
		cout << fit << '\t' << alpha << '\t' << beta << "\n\n\n";
		for(size_t i = 0 ; i != height/2 + 1 ; i++)
			cout << spec[i] << '\n';
	}

	if(dump) {
		// print lines
		cout << spectrum;
	}
}



int main(int argc, char **argv) {
	// Parameters.
	typedef mt19937 Random;
	unsigned int seed;
	size_t generations, width, height, population, elite, initials, resid, fit;
	string directory, rule_info;
	double mutation_prob, crossover_prob, initials_density;
	typedef bitset<32> rule_t;

	// Parse options.
	options_description desc("Usage: " + string(argv[0]) + " [options]\nOptions");
	desc.add_options()
		("help",
		 "Show this message.")
		("info", value(&rule_info),
		 "Calculate the frequency profile/score of one rule for one initial configuration.")
		("run", value(&rule_info),
		 "Run one rule for one initial configuration.")
		("name", value(&directory),
		 "Batch input/output folder name.")
		("initials", value(&initials)->default_value(10),
		 "Number of initial configurations used to evaluate fitness.")
		("density", value(&initials_density)->default_value(0.5),
		 "Density of 1s in initials, 0=all 0s, 1=all 1s.")
		("resid", value(&resid)->default_value(100),
		 "Number of residual values used to calculate fitness.")
		("fit", value(&fit)->default_value(10),
		 "Number of values used in regression.")
		("width", value(&width)->default_value(700),
		 "Evaluation width/columns.")
		("height", value(&height)->default_value(3000),
		 "Evaluation height/time steps.")
		("generations", value(&generations)->default_value(200),
		 "Batch run for this many generations.")
		("population", value(&population)->default_value(160),
		 "Size of the rule-population.")
		("elite", value(&elite)->default_value(20),
		 "Number of rules to copy without mutation.")
		("mutation", value(&mutation_prob)->default_value(0.05),
		 "Probability of mutating=flipping one child bit.")
		("crossover", value(&crossover_prob)->default_value(0.6),
		 "Uniform crossover proportion.")
		("seed", value(&seed)->default_value(0),
		 "Explicit seed value.");
	positional_options_description pos;
	pos.add("name", 1);
	
	variables_map vm;
	store(command_line_parser(argc, argv).options(desc).positional(pos).run(), vm);
	if(vm.count("help")) {
		cerr << desc;
		return EXIT_SUCCESS;
	}
	try {
		notify(vm);
	} catch(required_option e) {
		cerr << e.what() << endl << desc;
		return EXIT_FAILURE;
	}

	// create and seed RNG
	if(seed == 0) {
		random_device dev;
		seed = dev();
	}
	Random random(seed);

	if(vm.count("info")) { // show info
		switch(rule_info.size()) {
			case 32:
				run_once(random, bitset<32>(rule_info), width, height, true, false, resid, fit, initials_density);
				break;
			case 8:
				run_once(random, bitset<8>(rule_info), width, height, true, false, resid, fit, initials_density);
				break;
		}
	} else if(vm.count("run")) { // run once
		switch(rule_info.size()) {
			case 32:
				run_once(random, bitset<32>(rule_info), width, height, false, true, resid, fit, initials_density);
				break;
			case 8:
				run_once(random, bitset<8>(rule_info), width, height, false, true, resid, fit, initials_density);
				break;
		}

	} else if(vm.count("name")) { // batch run

		// parallel scorer
		population_scorer scorer(width, height, initials, resid, fit, initials_density);
		// genetic algorithm
		genetic_algorithm<32, Random> ga(mutation_prob, crossover_prob, elite, random);

		format pop_fmt("%s/%05d.pop");
		format gen_fmt("%s/%05d.gen");

		// load or create initial population
		vector<scored<rule_t>> pop;

		size_t start_gen = 0;
		if(exists(directory)) {
			// load the last generation as the next initial generation.
			vector<path> files;
			copy(directory_iterator(directory), directory_iterator(), back_inserter(files));
			if(files.size() > 0) {
				auto last = *max_element(files.begin(), files.end());
				start_gen = lexical_cast<size_t>(last.stem());
				ifstream in(last.string());
				in.exceptions(ifstream::failbit | ifstream::eofbit | ifstream::badbit);
				for(size_t i = 0 ; i < population ; i++) {
					string line;
					getline(in, line);
					pop.push_back(scored<rule_t>(rule_t(line)));
				}
			}
		} else {
			create_directory(directory);
		}

		if(pop.size() == 0)
			ga.initial_population(back_inserter(pop), population);

		// dump parameters
		{
			ofstream params(directory + "/parameters");
			params
				<< " --name" << directory
				<< " --width " << width
				<< " --height " << height
				<< " --initials " << initials
				<< " --resid " << resid
				<< " --fit " << fit
				<< " --mutation " << mutation_prob
				<< " --crossover " << crossover_prob
				<< " --seed " << seed << endl;
		}

		// run
		for(size_t g = 0 ; g < generations ; g++) {
			const size_t this_gen = g + start_gen;

			// score current population
			cout << "# generation " << setw(5) << this_gen << flush;
			const auto t_start = high_resolution_clock::now();
			scorer(random, pop.begin(), pop.end());
			const duration<double> dur = high_resolution_clock::now() - t_start;
			cout << " total " << dur.count() << "s" << endl;

			// save score
			ofstream pop_out(str(pop_fmt % directory % this_gen));
			pop_out << pop << endl;

			// create next population, save parentage/elitism
			ofstream gen_out(str(gen_fmt % directory % (this_gen + 1)));
			ga.next_generation(pop.begin(), pop.end(), gen_out);

			// save next population, overwrite with score in next step.
			ofstream next_pop_out(str(pop_fmt % directory % (this_gen + 1)));
			next_pop_out << pop << endl;
		}

	} else {
		cerr << desc;
		return EXIT_FAILURE;
	}

	return EXIT_SUCCESS;
}
