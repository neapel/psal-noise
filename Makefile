CXXFLAGS += -Wall -Wextra --std=c++0x -O3 -fopenmp -mtune=native -march=native
packages = fftw3f
CXXFLAGS += `pkg-config --cflags $(packages)`
LDLIBS += `pkg-config --libs $(packages)`

new : clean search info

search : search.cc ca.hh gen.hh linear_fit.hh
info : info.cc ca.hh linear_fit.hh

.PHONY : clean
clean :
	-rm search info ca
