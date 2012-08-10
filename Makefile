CXXFLAGS += -Wall -Wextra --std=c++0x -O3 -fopenmp -mtune=native -march=native
packages = fftw3f
CXXFLAGS += `pkg-config --cflags $(packages)`
LDLIBS += `pkg-config --libs $(packages)` -lboost_filesystem -lboost_system -lboost_program_options

all : search
new : clean search

search : search.cc

.PHONY : clean
clean :
	-rm search


