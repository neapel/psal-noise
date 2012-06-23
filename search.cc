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


using namespace std;
using namespace std::chrono;
using namespace boost::program_options;



int main(int argc, char **argv) {
	options_description desc("Options");
	desc.add_options()
		("new", "Start a new simulation")
		("resume", value<string>(), "Resume a simulation")
		("generations", value<size_t>(), "Run for this many generations");
	
	variables_map vm;
	store(parse_command_line(argc, argv, desc), vm);
	notify(vm);

	

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

	string base(argv[1]);

	auto pop = initial_population<32, population>(random);
	for(size_t g = 0 ; g < generations || true ; g++) {
		ofstream pop_out(base + ".pop", ios::app);
		ofstream gen_out(base + ".gen", ios::app);

		cout << "# generation " << setw(4) << g << flush;
		const auto t_start = high_resolution_clock::now();
		const auto pop_scored = scorer(random, pop);
		const duration<double> dur = high_resolution_clock::now() - t_start;
		cout << " total " << dur.count() << "s" << endl;

		pop_out << pop_scored << endl;
		pop = next_generation<elite>(random, pop_scored, gen_out);
	}

	return 0;
}
