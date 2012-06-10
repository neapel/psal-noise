#include "linear_fit.hh"
#include "ca.hh"
#include <iostream>
#include <string>
#include <sstream>

using namespace std;

int main(int, char**) {
	const size_t height = 3000, width = 700;

	plan_t<height, double> plan;

	// create and seed RNG
	random_device dev;
	mt19937 random(dev());

	while(cin) {
		// rule is first on the line, ignore rest.
		string line, rule_s;
		getline(cin, line);
		istringstream ss(line);
		ss >> rule_s;
		bitset<32> rule{rule_s};

		// evaluate
		const auto init = initial<width>(random);
		const auto lines = eval<width, height>(rule, init);
		const auto spec = spectrum<height/2>(plan, lines);
		double fit, alpha, beta;
		tie(fit, alpha, beta) = fitness<10, 100>(spec);

		// plot
		cout << "set logscale xy\n"
		     << "plot '-' w l t 'fitness=" << fit << "',"
		     << "exp(" << alpha << " + " << beta << " * log(x)) w l\n";
		for(size_t i = 0 ; i < spec.size() ; i++)
			cout << (i + 1) << ' ' << spec[i] << '\n';
		cout << 'e' << endl;
		cout << "pause mouse any" << endl;
	}

	return 0;
}
