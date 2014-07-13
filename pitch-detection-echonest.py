#!/usr/bin/python

import os
import sys
import pyechonest.config as config
import echonest.remix.audio as audio
import numpy
import matplotlib.pyplot as plt

from midiutil.MidiFile import MIDIFile


config.ECHO_NEST_API_KEY = os.environ["ECHO_NEST_API_KEY"]

def normalize_loudness(audiofile):
    loudness = numpy.array([p.mean_loudness() for p in audiofile.analysis.segments])
    ld = numpy.max(loudness) - numpy.min(loudness)
    return (loudness - numpy.min(loudness)) / ld

def generate_image(audiofile):
    pitches = numpy.array([p.pitches for p in audiofile.analysis.segments])

    aspect = 1. / (audiofile.analysis.duration / 60.)
    normalized_loudness = normalize_loudness(audiofile)

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

def generate_midi(audiofile):
    # Create the MIDIFile Object with 1 track
    MyMIDI = MIDIFile(1)

    # Tracks are numbered from zero. Times are measured in beats.
    track = 0   
    time = 0

    print "Tempo:", audiofile.analysis.tempo

    # Add track name and tempo.
    MyMIDI.addTrackName(track,time,"Sample Track")
    MyMIDI.addTempo(track,time,audiofile.analysis.tempo["value"])

    durations = numpy.array([p.duration for p in audiofile.analysis.segments])
    segment_end_times = numpy.cumsum(durations)
    segment_start_times = segment_end_times - durations

    normalized_loudness = normalize_loudness(audiofile)

    track = 0
    channel = 0
    for i in range(len(audiofile.analysis.segments)):
        for j in range(12):
            pitch = j + 60
            time = segment_start_times[i]
            duration = durations[i]
            volume = int(normalized_loudness[i] * audiofile.analysis.segments[i].pitches[j] * 100)

            # Now add the note.
            MyMIDI.addNote(track,channel,pitch,time,duration,volume)

    # And write it to disk.
    binfile = open("output.mid", 'wb')
    MyMIDI.writeFile(binfile)
    binfile.close()

if __name__ == "__main__":
    assert len(sys.argv) == 2
    filename = sys.argv[1]

    audiofile = audio.LocalAudioFile(filename)

#    generate_image(audiofile)
    generate_midi(audiofile)
