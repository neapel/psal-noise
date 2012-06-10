CXXFLAGS += -Wall -Wextra --std=c++0x -O3 -fopenmp -mtune=native -march=native
LDLIBS += -lfftw3 -lfftw3f

new : clean search info

search : search.cc ca.hh gen.hh linear_fit.hh
info : info.cc ca.hh linear_fit.hh

.PHONY : clean
clean :
	-rm search info ca
