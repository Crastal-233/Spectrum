from sys import argv
from math import ceil, log10
from scipy.io import wavfile
from scipy.fftpack import fft
from PIL import Image, ImageDraw

FPS = 30

TEXTURE_WIDTH = 1024
TEXTURE_HEIGHT = 1024

FFT_SCOPE = 1024
FFT_UNIFORM = 64

def FFT(s1):
	global fft_max
	n = len(s1) 
	p = fft(s1)
	nUniquePts = int(ceil((n+1)/2.0))
	p = p[0:nUniquePts]
	p = abs(p)
	p = p / float(n)
	p = p**2

	if n % 2 > 0:
		p[1:len(p)] = p[1:len(p)] * 2
	else:
		p[1:len(p) -1] = p[1:len(p) - 1] * 2

	return p
	
def plot(x):
	return abs(10 * log10(x ** 2 + 1e-15))

def gen(fn):
	sampFreq, snd = wavfile.read(fn)

	snd = snd / (2.0 ** 15)
	soundLength = len(snd) / sampFreq
	s1 = snd[:,0]

	print "INFO: Fps = ", FPS
	print "INFO: Sound length = ", int(soundLength * FPS)
	print "INFO: Left channel size =", len(s1)

	img = Image.new("RGBA", (TEXTURE_WIDTH,TEXTURE_HEIGHT), color=(0,0,0,0))

	draw = ImageDraw.Draw(img)

	rangeStep = sampFreq / FPS
	rangeLimits = int(soundLength * FPS);

	limit_max = 0.0;
	limit_min = 255;

	for i in xrange(rangeLimits):
		start_index = rangeStep * i
		end_index = start_index + FFT_SCOPE

		if  end_index >= len(s1):
			end_index = len(s1) - 1

		if (start_index > 0.5 * rangeStep):
			start_index -= 0.5 * rangeStep
			end_index -= 0.5 * rangeStep

		fft_data = s1[int(start_index):int(end_index)]
		fft_ret = FFT(fft_data)
		fft_ret_len = len(fft_ret)

		limit_max = max(limit_max, plot(fft_ret[0]))
		limit_min = min(limit_min, plot(fft_ret[0]))

	print "INFO: Min limit =", limit_min
	print "INFO: Max limit =", limit_max

	for i in xrange(rangeLimits):
		start_index = rangeStep * i
		end_index = start_index + FFT_SCOPE

		if  end_index >= len(s1):
			end_index = len(s1) - 1
			
		if (start_index > 0.5 * rangeStep):
			start_index -= 0.5 * rangeStep
			end_index -= 0.5 * rangeStep

		fft_data = s1[int(start_index):int(end_index)]
		fft_ret = FFT(fft_data)
		fft_ret_len = len(fft_ret)

		px = i % TEXTURE_WIDTH;
		py = i / TEXTURE_HEIGHT * FFT_UNIFORM;

		for j in xrange(FFT_UNIFORM):
			index = j * 4;

			v1 = int(255 * (1 - (plot(fft_ret[index]) ) / limit_max))
			v2 = int(255 * (1 - (plot(fft_ret[index + 1]) ) / limit_max))
			v3 = int(255 * (1 - (plot(fft_ret[index + 2]) ) / limit_max))
			v4 = int(255 * (1 - (plot(fft_ret[index + 3]) ) / limit_max))

			draw.point((px, py + j), fill=(v1,v2,v3,v4))

	img.save(fn+".fft.png", 'png')

if __name__ == "__main__":
	if len(argv) == 2:
		fn = argv[1]
		gen(fn)
		print 'DONE...'
	else:
		print "ERROR! Please enter a path to a wav file..."

	raw_input()
