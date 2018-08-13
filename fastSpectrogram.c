#include <complex.h>
#include <stdlib.h>
#include <fftw3.h>
#include <math.h>
	
void absSpectrogram(float* wave, float* spectrogram, int len, int hopsize, int framesize, float* window)
{

	int specsize = (int) floor(framesize/2 + 1);
	int nBlocks = (int) floor(len / hopsize - framesize/hopsize + 1);

	// allocate fft memory
	float* source;
	complex float* target;

	// fftwf_import_wisdom_from_filename("./wisdom.sav");

	source = fftwf_alloc_real(framesize);
	target = fftwf_alloc_complex(specsize);

	// plan ffts
	fftwf_plan plan;
	plan = fftwf_plan_dft_r2c_1d(framesize, source, target, FFTW_MEASURE);

	// fftwf_export_wisdom_to_filename("./wisdom.sav");

	int indexWave = 0;
	int indexSpectrogram = 0;
	for (int i = 0; i < nBlocks; ++i)
	{
		for (int k = 0; k < framesize; ++k)
			source[k] = wave[indexWave+k] * window[k];

		fftwf_execute(plan);
		
        for (int k = 0; k < specsize; ++k)
		{
			spectrogram[indexSpectrogram] = cabsf(target[k]);
			++indexSpectrogram;
		}
		indexWave += hopsize;
	}	

	fftwf_free(source);
	fftwf_free(target);
	fftwf_destroy_plan(plan);

}
//
//	
//
//void main(void)
//{
//
//	float* A;
//	float* window;
//	int len = 22050 * 30;
//	int hopsize = 256;
//	int framesize = 1024;
//
//	A = malloc(len * sizeof(float));
//	window = malloc(framesize * sizeof(float));
//	
//	for (int i = 0; i < framesize; ++i)
//		window[i] = 1;
//
//	for (int i = 0; i < len; ++i)
//		A[i] = rand();
//
//	int specsize = (int) floor(framesize/2 + 1);
//	int nBlocks = (int) floor(len / hopsize - framesize/hopsize + 1);
//
//	float* output;
//	output = malloc(nBlocks * specsize * sizeof(float));
//
//
//	s2(A, output, len, hopsize, framesize);
//	absSpec2(A, output, len, hopsize, framesize, window);
//	rhythmo3d(A, output, 10, 66150, 128, 512, 256);
////void rhythmo3d(float* input, float* output, int rowsInput, int colsInput, int hopsize, int framesize, int reducedSize)
//	
//	free(A);
//	free(output);
//	free(window);
//}
//	
