#include <errno.h>
#include <sndfile.h>
#include <stdio.h>
#include <stdlib.h>

#include "vad.h"
#include "vad_docopt.h"

#define DEBUG_VAD 0x1


int main(int argc, char *argv[]) {
    int verbose = 0; /* To show internal state of vad: verbose = DEBUG_VAD; */

    SNDFILE *sndfile_in, *sndfile_out = 0;
    SF_INFO sf_info;
    FILE *vadfile;
    int n_read = 0, i;

    VAD_DATA *vad_data;
    VAD_STATE state, last_state;

    float *buffer, *buffer_zeros;
    float frame_duration, time_since_change; /* in seconds */
    int frame_size;                          /* in samples */
    unsigned int t, last_t, frame_count;     /* in frames */

    char *input_wav, *output_vad, *output_wav;
    float alpha1, alpha2;
    int TV, TS; // Tiempos de Maybe Silence/Voice a Silence/Voice
    float min_silence_time, min_voice_time;

    DocoptArgs args = docopt(argc, argv, /* help */ 1, /* version */ "2.0");

    verbose             = args.verbose ? DEBUG_VAD : 0;
    input_wav           = args.input_wav;
    output_vad          = args.output_vad;
    output_wav          = args.output_wav;
    alpha1              = atof(args.alpha1);
    alpha2              = atof(args.alpha2);
    TV                  = atoi(args.TV);
    TS                  = atoi(args.TS);
    min_silence_time    = (float)atoi(args.min_silence) / 1000;
    min_voice_time      = (float)atoi(args.min_voice) / 1000;

    if (input_wav == 0 || output_vad == 0) {
        fprintf(stderr, "%s\n", args.usage_pattern);
        return -1;
    }

    /* Open input sound file */
    if ((sndfile_in = sf_open(input_wav, SFM_READ, &sf_info)) == 0) {
        fprintf(stderr, "Error opening input file %s (%s)\n", input_wav, strerror(errno));
        return -1;
    }

    if (sf_info.channels != 1) {
        fprintf(stderr, "Error: the input file has to be mono: %s\n", input_wav);
        return -2;
    }

    /* Open vad file */
    if ((vadfile = fopen(output_vad, "wt")) == 0) {
        fprintf(stderr, "Error opening output vad file %s (%s)\n", output_vad, strerror(errno));
        return -1;
    }

    /* Open output sound file, with same format, channels, etc. than input */
    if (output_wav) {
        if ((sndfile_out = sf_open(output_wav, SFM_WRITE, &sf_info)) == 0) {
            fprintf(stderr, "Error opening output wav file %s (%s)\n", output_wav, strerror(errno));
            return -1;
        }
    }

    vad_data = vad_open(sf_info.samplerate, alpha1, alpha2);
    /* Allocate memory for buffers */
    frame_size   = vad_frame_size(vad_data);
    buffer       = (float *) malloc(frame_size * sizeof(float));
    buffer_zeros = (float *) malloc(frame_size * sizeof(float));
    for (i=0; i< frame_size; ++i) buffer_zeros[i] = 0.0F;

    frame_duration = (float) frame_size / (float) sf_info.samplerate;
    last_state = ST_UNDEF;
    frame_count = 0;

    /* For each frame ... */
    for (t = last_t = 0;; t++) {
        /* End loop when file has finished (or there is an error) */
        if ((n_read = sf_read_float(sndfile_in, buffer, frame_size)) != frame_size)
            break;

        if (sndfile_out != 0) {
            sf_write_float(sndfile_out, buffer, frame_size);
            frame_count++;
        }

        state = vad(vad_data, buffer);
        if (verbose & DEBUG_VAD)
            vad_show_state(vad_data, stdout);

        /* DONE: print only SILENCE and VOICE labels */
        /* As it is, it prints UNDEF segments but is should be merge to the proper
         * value */
        // Si hay cambio de estado y esta definido
        if (state != last_state && state != ST_UNDEF) {
            
            // Mirar que se llegue al mínimo tiempo antes de decidir
            time_since_change = (t - last_t) * frame_duration;
            if ((last_state == ST_VOICE && time_since_change >= min_voice_time) ||
                (last_state == ST_SILENCE && time_since_change >= min_silence_time)) {

                fprintf(vadfile, "%.5f\t%.5f\t%s\n", last_t * frame_duration,
                        t * frame_duration, state2str(last_state));

                last_t = t;

                if (last_state == ST_VOICE) {
                    frame_count = 0;
                }
            }

            last_state = state;
        }

        if (sndfile_out != 0 && last_t == t) {
            sf_seek(sndfile_out, -frame_size*frame_count, SEEK_CUR);

            // Write zeros
            for (int i = 0; i < frame_count; i++)
                sf_write_float(sndfile_out, buffer_zeros, frame_size);
        }
    }

    state = vad_close(vad_data);
    /* DONE: what do you want to print, for last frames? */
    if (t != last_t) {
        fprintf(vadfile, "%.5f\t%.5f\t%s\n", last_t * frame_duration,
                t * frame_duration + n_read / (float) sf_info.samplerate,
                state2str(last_state));
    }

    if (sndfile_out != 0 && last_state == ST_SILENCE) {
        sf_seek(sndfile_out, -frame_size*frame_count, SEEK_CUR);

        // Write zeros
        for (int i = 0; i < frame_count; i++)
            sf_write_float(sndfile_out, buffer_zeros, frame_size);
    }

    /* clean up: free memory, close open files */
    free(buffer);
    free(buffer_zeros);
    sf_close(sndfile_in);
    fclose(vadfile);
    if (sndfile_out) sf_close(sndfile_out);
    return 0;
}
