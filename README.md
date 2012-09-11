My implementation of Shigeru Ninagawa's 2007 paper [Evolution of one-dimensional Cellular Automata by 1/f noise](http://dx.doi.org/10.1007/978-3-540-74913-4) for a seminar on artificial life.

**search.cc** — Main program. C++11, uses OpenMP, FFTw and Boost Program Options & Filesystem. Use `--name` to specify an output directory for the run, the program will put `%05d.{pop,gen}` files for each generation there or continue a previous run.

**\*.py** — Read the output files and produce GNUplot/CairoLaTeX-terminal code.
