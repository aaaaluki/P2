#include <math.h>

#include "pav_analysis.h"

/**
 * Funcion signo, definida de la siguiente manera:
 *      1 : x > 0
 *      0 : x = 0
 *     -1 : x < 0
 */
#define SGN(x) ((x > 0) ? 1 : ((x < 0) ? -1 : 0))

float compute_power(const float *x, unsigned int N) {
    // Valor para que la pot. mínima sea -120 dB (consejo para la P2)
    float power = 1.e-5;

    for (int i = 0; i < N; i++) {
        power += x[i] * x[i];       //calculamos la potencia   
    }

    return 10*log10f(power / N);
}

float compute_am(const float *x, unsigned int N) {
    float a = 0.0f;

    for (int i = 0; i < N; i++) {
        a += fabsf(x[i]);
    }

    return a / N;
}

float compute_zcr(const float *x, unsigned int N, float fm) {
    const float scaling = 0.5f * fm / (N - 1);
    float zcr = 0.0f;

    for (int i = 1; i < N; i++) {
        if (SGN(x[i]) != SGN(x[i - 1])) {
            zcr++;
        }
	}

    return scaling*zcr;
}
