import mido
import pygame
from regulate_tracks import get_all_lists_and_tpb
from probabilities import get_channels_dict
from Markov import get_song_inputs, get_lists_for_all_channels

all_instruments = {0: 'Acoustic Grand Piano', 1: 'Bright Acoustic Piano', 2: 'Electric Grand Piano', 3: 'Honky-tonk Piano', 4: 'Electric Piano 1', 5: 'Electric Piano 2', 6: 'Harpsichord', 7: 'Clavi', 8: 'Celesta', 9: 'Glockenspiel', 10: 'Music Box', 11: 'Vibraphone', 12: 'Marimba', 13: 'Xylophone', 14: 'Tubular Bells', 15: 'Dulcimer', 16: 'Drawbar Organ', 17: 'Percussive Organ', 18: 'Rock Organ', 19: 'Church Organ', 20: 'Reed Organ', 21: 'Accordion', 22: 'Harmonica', 23: 'Tango Accordion', 24: 'Acoustic Guitar (nylon)', 25: 'Acoustic Guitar (steel)', 26: 'Electric Guitar (jazz)', 27: 'Electric Guitar (clean)', 28: 'Electric Guitar (muted)', 29: 'Overdriven Guitar', 30: 'Distortion Guitar', 31: 'Guitar harmonics', 32: 'Acoustic Bass', 33: 'Electric Bass (finger)', 34: 'Electric Bass (pick)', 35: 'Fretless Bass', 36: 'Slap Bass 1', 37: 'Slap Bass 2', 38: 'Synth Bass 1', 39: 'Synth Bass 2', 40: 'Violin', 41: 'Viola', 42: 'Cello', 43: 'Contrabass', 44: 'Tremolo Strings', 45: 'Pizzicato Strings', 46: 'Orchestral Harp', 47: 'Timpani', 48: 'String Ensemble 1', 49: 'String Ensemble 2', 50: 'SynthStrings 1', 51: 'SynthStrings 2', 52: 'Choir Aahs', 53: 'Voice Oohs', 54: 'Synth Voice', 55: 'Orchestra Hit', 56: 'Trumpet', 57: 'Trombone', 58: 'Tuba', 59: 'Muted Trumpet', 60: 'French Horn', 61: 'Brass Section', 62: 'SynthBrass 1', 63: 'SynthBrass 2', 64: 'Soprano Sax', 65: 'Alto Sax', 66: 'Tenor Sax', 67: 'Baritone Sax', 68: 'Oboe', 69: 'English Horn', 70: 'Bassoon', 71: 'Clarinet', 72: 'Piccolo', 73: 'Flute', 74: 'Recorder', 75: 'Pan Flute', 76: 'Blown Bottle', 77: 'Shakuhachi', 78: 'Whistle', 79: 'Ocarina', 80: 'Lead 1 (square)', 81: 'Lead 2 (sawtooth)', 82: 'Lead 3 (calliope)', 83: 'Lead 4 (chiff)', 84: 'Lead 5 (charang)', 85: 'Lead 6 (voice)', 86: 'Lead 7 (fifths)', 87: 'Lead 8 (bass + lead)', 88: 'Pad 1 (new age)', 89: 'Pad 2 (warm)', 90: 'Pad 3 (polysynth)', 91: 'Pad 4 (choir)', 92: 'Pad 5 (bowed)', 93: 'Pad 6 (metallic)', 94: 'Pad 7 (halo)', 95: 'Pad 8 (sweep)', 96: 'FX 1 (rain)', 97: 'FX 2 (soundtrack)', 98: 'FX 3 (crystal)', 99: 'FX 4 (atmosphere)', 100: 'FX 5 (brightness)', 101: 'FX 6 (goblins)', 102: 'FX 7 (echoes)', 103: 'FX 8 (sci-fi)', 104: 'Sitar', 105: 'Banjo', 106: 'Shamisen', 107: 'Koto', 108: 'Kalimba', 109: 'Bag pipe', 110: 'Fiddle', 111: 'Shanai', 112: 'Tinkle Bell', 113: 'Agogo', 114: 'Steel Drums', 115: 'Woodblock', 116: 'Taiko Drum', 117: 'Melodic Tom', 118: 'Synth Drum', 119: 'Reverse Cymbal', 120: 'Guitar Fret Noise', 121: 'Breath Noise', 122: 'Seashore', 123: 'Bird Tweet', 124: 'Telephone Ring', 125: 'Helicopter', 126: 'Applause', 127: 'Gunshot'}

reverse_all_instruments = {value: key for key, value in all_instruments.items()}


def note_to_messages(note, current_time, duration, velocity_on, velocity_off, note_message_list, channel):
    x = mido.Message('note_on', channel=channel, note=note, velocity=velocity_on, time=0)
    y = mido.Message('note_off', channel=channel, note=note, velocity=velocity_off, time=0)
    note_message_list.append([x, current_time])
    note_message_list.append([y, current_time+duration])


def generate_note_on_offs(list_of_lists, channel):
    current_time = 0
    note_message_list = []
    new_pitch = list_of_lists[0]
    new_note_lengths = list_of_lists[1]
    new_delays = list_of_lists[2]
    new_velocity_on = list_of_lists[3]
    new_velocity_off = list_of_lists[4]
    """
    print(channel)
    for delay in new_delays:
        if delay < 0:
            print(delay)
    print()
    """
    for i in range(500):
        note_to_messages(new_pitch[i], current_time, new_note_lengths[i], new_velocity_on[i],
                         new_velocity_off[i], note_message_list, channel)
        try:
            current_time += new_delays[i]
        except IndexError:
            current_time += 0
    return note_message_list


def append_notes(note_message_list, track):
    # for all messages, index the list backwards then take the last instance.
    # With one instrument should just be all the notes
    # maybe add dummy messages to test before u get variables passing
    sorted_note_message_list = sorted(note_message_list, key=lambda x: x[1])
    # above sorts by second element of list which is (CUMULATIVE?) time
    running_time = 0
    for item in sorted_note_message_list:
        msg = item[0]
        time = item[1] - running_time
        msg.time = abs(time)
        running_time += time
        track.append(msg)


def play_with_pygame(song):
    pygame.init()
    pygame.mixer.music.load(song)
    length = pygame.time.get_ticks()
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(length)


def put_together_song(track, channels_lists_dict, list1, channels, programs, channels_dict):
    for item in list1:
        msg = item[0]
        if msg.type == 'program_change':
            msg.time = 0
            track.append(mido.Message('program_change', channel=msg.channel, program=msg.program, time=0))

    extended_list_of_msgs = []
    for program in programs:
        note_message_list = generate_note_on_offs(channels_lists_dict[int(program)], channels_dict[int(program)])
        # note_message_list is an ordered list of just msgs (no cumulative time) and their appropriate delta times
        for item in note_message_list:
            extended_list_of_msgs.append(item)

    append_notes(extended_list_of_msgs, track)


def get_songs_msgs(all_mid):
    """
    :param all_mid: a list of all the midi file names you will use
    :return: run regulate tracks on them to get an ordered filtered list of their messages
    """
    output, ticksperbeat = get_all_lists_and_tpb(all_mid)  # input songs as parameters here?
    list1 = output
    return list1


def get_ticksperbeat(all_mid):
    output, ticksperbeat = get_all_lists_and_tpb(all_mid)
    return ticksperbeat


def get_instruments(all_msgs):
    channels_dict = get_channels_dict(all_msgs)
    instruments = []
    programs = channels_dict.keys()
    for program in programs:
        instruments.append(all_instruments[int(program)])
    print(instruments)
    return instruments


def programs_for_names(names):
    programs = []
    for name in names:
        programs.append(reverse_all_instruments[name])
    return programs


def play_song_or_save(all_mid, save, programs):
    list1 = get_songs_msgs(all_mid)
    ticksperbeat = get_ticksperbeat(all_mid)

    channels_dict = get_channels_dict(list1)
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    mid.ticks_per_beat = ticksperbeat
    track.ticks_per_beat = ticksperbeat

    channels = []
    for program in programs:
        channels.append(channels_dict[program])

    channels_lists_dict = get_lists_for_all_channels(channels, list1)

    put_together_song(track, channels_lists_dict, list1, channels, programs, channels_dict)

    if save:
        mid.save('new_song.mid')  # need to change this
    else:
        mid.save('new_song.mid')
        play_with_pygame('new_song.mid')


def main():
    all_mid = [' (Yiruma).mid']  # can enter songs here
    # all_mid = ['ItsBeginningToLookALotLikeChristmas.mid', 'BohemianRhapsody.mid']
    #all_mid = ['BohemianRhapsody.mid']
    list1 = get_songs_msgs(all_mid)
    ticksperbeat = get_ticksperbeat(all_mid)

    channels_dict = get_channels_dict(list1)
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    mid.ticks_per_beat = ticksperbeat
    track.ticks_per_beat = ticksperbeat

    # functions from Markov.py
    channels, programs = get_song_inputs(list1)
    channels_lists_dict = get_lists_for_all_channels(channels, list1)
    # creates dict where {program: [list of lists for sequences of each parameter}

    put_together_song(track, channels_lists_dict, list1, channels, programs, channels_dict)

    mid.save('new_song.mid')
    play_with_pygame('new_song.mid')


if __name__ == '__main__':
    main()


