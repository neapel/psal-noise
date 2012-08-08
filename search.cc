#include "gen.hh"
#include "score.hh"

#include <iostream>
#include <iomanip>
#include <bitset>
#include <chrono>
#include <random>
#include <stdexcept>
#include <fstream>
#include <boost/program_options.hpp>
#define BOOST_FILESYSTEM_VERSION 2
#include <boost/filesystem.hpp>
#include <boost/format.hpp>
#include <boost/lexical_cast.hpp>


using namespace std;
using namespace std::chrono;
using namespace boost;
using namespace boost::program_options;
using namespace boost::filesystem;


template<size_t width, size_t height, size_t length, typename Random>
void show_info(bitset<length> rule, Random random) {
	// run once
	array<array<bool, width>, height> lines;
	initial(random, lines[0]);
	eval(rule, lines);

	// calculate spectrum
	plan_t plan(height);
	array<float, height/2+1> spec;
	spectrum(plan, lines, spec);

	double fit, alpha, beta;
	tie(fit, alpha, beta) = fitness<fit_w, resid_w>(spec);

	// dump
	cout.precision(10);
	cout << scientific;
	cout << fit << '\t' << alpha << '\t' << beta << "\n\n\n";
	for(size_t i = 0 ; i != spec.size() ; i++)
		cout << spec[i] << '\n';
}


template<size_t width, size_t height, size_t length, typename Random>
void run_once(bitset<length> rule, Random random) {
	// run once
#if 0
	bitset<width> init;
	init[width/2] = true;
	const auto lines = eval<width, height>(rule, init);
#else
	array<array<bool,width>, height> lines;
	initial(random, lines[0]);
	eval(rule, lines);
#endif

	// print lines
	for(size_t y = 0 ; y < height ; y++) {
		for(size_t x = 0 ; x < width ; x++)
			cout << (lines[y][x] ? '1' : '0') << ' ';
		cout << '\n';
	}
}



int main(int argc, char **argv) {
	unsigned int seed = 0;
	size_t generations;
	string directory, rule_info;
	options_description desc("Usage: " + string(argv[0]) + " [options]\nOptions");
	desc.add_options()
		("help", "Show this message.")
		("info", value<string>(&rule_info), "Calculate the frequency profile/score of one rule for one initial configuration.")
		("run", value<string>(&rule_info), "Run one rule for one initial configuration.")
		("name", value<string>(&directory), "Batch input/output folder name.")
		("generations", value<size_t>(&generations)->default_value(200), "Batch run for this many generations.")
		("mutation", value<double>(&mutation_prob)->default_value(0.05), "Probability of mutating=flipping one child bit.")
		("crossover", value<double>(&crossover_prob)->default_value(0.6), "Uniform crossover proportion.")
		("seed", value<unsigned int>(&seed)->default_value(0), "Explicit seed value.")
		;
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

	// basic options
	const size_t width = 700, height = 3000;
	const size_t population = 160, elite = 20;
	typedef bitset<32> rule_t;

	// create and seed RNG
	if(seed == 0) {
		random_device dev;
		seed = dev();
	}
	mt19937 random(seed);

	if(vm.count("info")) { // show info
		switch(rule_info.size()) {
			case 32:
				show_info<width, height>(bitset<32>(rule_info), random);
				break;
			case 8:
				show_info<width, height>(bitset<8>(rule_info), random);
				break;
		}
	} else if(vm.count("run")) { // run once
		const size_t width = 1024/4, height = 640/4;
		switch(rule_info.size()) {
			case 32:
				run_once<width, height>(bitset<32>(rule_info), random);
				break;
			case 8:
				run_once<width, height>(bitset<8>(rule_info), random);
				break;
		}

	} else if(vm.count("name")) { // batch run

		// parallel scorer
		population_scorer<width, height, float> scorer;

		format pop_fmt("%s/%05d.pop");
		format gen_fmt("%s/%05d.gen");

		// load or create initial population
		auto pop = initial_population<32, population>(random);

		size_t start_gen = 0;
		if(exists(directory)) {
			// load the last generation as the next initial generation.
			// this will overwrite that generation, but it should be unscored anyway.
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
					pop[i] = rule_t(line);
				}
			}
		} else {
			create_directory(directory);
		}

		// run
		for(size_t g = 0 ; g < generations ; g++) {
			const size_t this_gen = g + start_gen;

			// score current population
			cout << "# generation " << setw(5) << this_gen << flush;
			const auto t_start = high_resolution_clock::now();
			const auto pop_scored = scorer(random, pop);
			const duration<double> dur = high_resolution_clock::now() - t_start;
			cout << " total " << dur.count() << "s" << endl;

			// save score
			ofstream pop_out(str(pop_fmt % directory % this_gen));
			pop_out << pop_scored << endl;

			// create next population, save parentage/elitism
			ofstream gen_out(str(gen_fmt % directory % (this_gen + 1)));
			pop = next_generation<elite>(random, pop_scored, gen_out);

			// save next population, overwrite with score in next step.
			ofstream next_pop_out(str(pop_fmt % directory % (this_gen + 1)));
			next_pop_out << pop << endl;
		}
	}

	return EXIT_SUCCESS;
}
