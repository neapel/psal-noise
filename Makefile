CXXFLAGS += -Wall -Wextra --std=c++0x -O3 -fopenmp -mtune=native -march=native
packages = fftw3f
CXXFLAGS += `pkg-config --cflags $(packages)`
LDLIBS += `pkg-config --libs $(packages)` -lboost_filesystem -lboost_system -lboost_program_options

all : search
new : clean search

headers=ca.hh gen.hh linear_fit.hh score.hh
search : search.cc $(headers)
info : info.cc $(headers)

.PHONY : clean
clean :
	-rm search ca


