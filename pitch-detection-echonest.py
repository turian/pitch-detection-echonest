#!/usr/bin/python

import os
import sys
import pyechonest.config as config
import echonest.remix.audio as audio
import numpy
import matplotlib.pyplot as plt


config.ECHO_NEST_API_KEY = os.environ["ECHO_NEST_API_KEY"]

if __name__ == "__main__":
    assert len(sys.argv) == 2
    filename = sys.argv[1]

    audiofile = audio.LocalAudioFile(filename)

    pitches = numpy.array([p.pitches for p in audiofile.analysis.segments])

    aspect = 1. / (audiofile.analysis.duration / 60.)

    loudness = numpy.array([p.mean_loudness() for p in audiofile.analysis.segments])
    ld = numpy.max(loudness) - numpy.min(loudness)
    normalized_loudness = (loudness - numpy.min(loudness)) / ld

    # Multiply each pitch by its loudness
    normalized_pitches = pitches.T * normalized_loudness

    durations = numpy.array([p.duration for p in audiofile.analysis.segments])
    segment_end_times = numpy.cumsum(durations)

    # Now, create an interpolated array that respects the duration of each segment
    BUCKETS = len(audiofile.analysis.segments) * 10
    duration_step = audiofile.analysis.duration / BUCKETS

    normalized_pitches_timestretched = numpy.zeros((12, BUCKETS))
    for i in range(12):
        pos = 0.
        segment_idx = 0
        for j in range(BUCKETS):
            # Find the segment that corresponds to this position
            while(segment_end_times[segment_idx] < pos and segment_idx < len(audiofile.analysis.segments)):
                segment_idx += 1

            normalized_pitches_timestretched[i,j] = normalized_pitches[i, segment_idx]

            # Advance the position
            pos += duration_step

    plt.clf()
    plt.imshow(normalized_pitches_timestretched, extent=[0,audiofile.analysis.duration,0,12])
    plt.show()

    plt.savefig('foo.pdf')
