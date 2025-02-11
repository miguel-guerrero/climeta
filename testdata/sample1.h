#ifndef __sample1_h__
#define __sample1_h__

typedef struct {
    const char * output;
    const char * lang;
    // positionals
    const char * input;
} Options;

#ifdef __cplusplus
extern "C" {
#endif

void reset_options(Options* opts);
int parse_options(int argc, const char ***argv, Options* opts);
void dump_options(Options *opts);

#ifdef __cplusplus
}
#endif

#endif