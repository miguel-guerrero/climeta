all: \
	c-argparse0 c-argparse1 \
	cpp-cxxopts0 cpp-cxxopts1 cpp-cxxopts2 \
	python0 python1 python2 \
	bash0 bash1 bash2 \
	js0 js1 js2

TOOL=./climeta.py

# ----- C argparse -----

CFLAGS=-I 3rdparty -O0

sample%.c: args%.toml
	$(TOOL) $< --lang c-argparse -o $@

sample%: sample%.c
	$(CC) $(CFLAGS) $< 3rdparty/argparse.c test/c-argparse-main-$< -o $@

c-argparse%: sample%
	@echo "-----------------------------------------------"
	./$< -h

# ----- C++ cxxopts -----

CXXFLAGS=-std=c++11 -I 3rdparty -O0

sample%.cpp: args%.toml
	$(TOOL) $< --lang cpp-cxxopts -o $@

sample_cpp%: sample%.cpp
	$(CXX) $(CXXFLAGS) $< test/cpp-cxxopts-main-$< -o $@

cpp-cxxopts%: sample_cpp%
	@echo "-----------------------------------------------"
	./$< -h

# ----- python -----

sample%.py: args%.toml
	$(TOOL) $< --lang python -o $@

python%: sample%.py
	@echo "-----------------------------------------------"
	python3 $< -h

# ----- javascript -----

sample%.mjs: args%.toml
	$(TOOL) $< --lang js-cla -o $@

js%: sample%.mjs
	@echo "-----------------------------------------------"
	./test/js-cla-main-$< -h

# ----- bash -----

sample%.sh: args%.toml
	$(TOOL) $< --lang bash -o $@

bash%: sample%.sh
	@echo "-----------------------------------------------"
	./test/bash-main-$< -h


.PRECIOUS: \
	sample0.py sample1.py sample2.py \
	sample0.sh sample1.sh sample2.sh \
	sample0.c sample0.h sample0 \
	sample1.c sample1.h sample1 \
	sample0.hpp sample0.cpp sample_cpp0 \
	sample1.hpp sample1.cpp sample_cpp1 \
	sample2.hpp sample2.cpp sample_cpp2 \
	sample0.mjs sample1.mjs sample2.mjs \

# ----- cleanup -----

.PHONY: clean

clean:
	$(RM) -rf sample[0-1].dSYM sample_cpp[0-1].dSYM
	$(RM) sample[0-2] sample[0-2].* sample_cpp[0-2]
