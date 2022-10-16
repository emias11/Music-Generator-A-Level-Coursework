from probabilities import get_final_dicts, get_channels_dict
import regulate_tracks
import mido
import numpy as np


# THIS FUNCTION IS ONLY USED IF RUNNING MARKOV.MAIN()
def get_song_inputs(msgs):
    # need something to get songs
    # need something to get program list from songs (remember its a dict with channels and corresponding programs)
    # N.B. the songs should be retrieved in regulate_tracks and brought here, not retrieved here
    print("dict is returned in format {program: channel}")
    channels_dict = get_channels_dict(msgs)
    print(channels_dict)
    programs = input("What programs do you want to include in the song?")
    programs = programs.split(", ")
    programs_channels = [channels_dict[int(program)] for program in programs]
    return programs_channels, programs


def make_list_for_parameter(length, par_dict, par_seed):
    """
    :param length: song note length (for size of output list)
    :param par_dict: the dictionary for a particular parameter
    :param par_seed: the starting value for a particular parameter
    :return: a sequence of length, from probabilities for that parameter
    """
    output_list = []
    first_seed = par_seed
    for i in range(length):
        try:
            probs = list(par_dict[par_seed].values())
            keys = list(par_dict[par_seed].keys())
            next1 = np.random.choice(keys, 1, replace=True, p=probs)
            output_list.append(int(next1))
        except KeyError:
            probs = list(par_dict[first_seed].values())
            keys = list(par_dict[first_seed].keys())
            next1 = np.random.choice(keys, 1, replace=True, p=probs)
            output_list.append(int(next1))
        par_seed = int(next1)
    return output_list


def make_lists_for_all_parameters(channel, msgs):
    """
    :param channel: the channel for which the sequences are found for
    :param msgs: a list of all the messages from a track
    :return: using probabilities.py, returns a sequence for each variable for a channel
    """
    song_note_length = 500
    dicts = get_final_dicts(msgs, channel)  # this is from probabilities.py HELLOOOOOOOOOOOOOOO
    # dict_list = [dicts[0], dicts[1], dicts[2], dicts[3], dicts[4]]
    # pitch_dict, velocity_on_dict, velocity_off_dict, note_lengths_dict, delays_dict
    pitch_dict, velocity_on_dict, velocity_off_dict, note_lengths_dict, delays_dict = dicts[0], dicts[1], dicts[2], dicts[3], dicts[4]
    pitch_seed = list(pitch_dict.keys())[0]
    velocity_on_seed = list(velocity_on_dict.keys())[0]
    new_velocity_on = make_list_for_parameter(song_note_length, velocity_on_dict, velocity_on_seed)
    try:
        velocity_off_seed = list(velocity_off_dict.keys())[0]
        new_velocity_off = make_list_for_parameter(song_note_length, velocity_off_dict, velocity_off_seed)
    except IndexError:
        new_velocity_off = new_velocity_on
    note_lengths_seed = list(note_lengths_dict.keys())[0]
    delays_seed = list(delays_dict.keys())[0]
    new_pitch = make_list_for_parameter(song_note_length, pitch_dict, pitch_seed)
    new_note_lengths = make_list_for_parameter(song_note_length, note_lengths_dict, note_lengths_seed)
    new_delays = make_list_for_parameter(song_note_length-1, delays_dict, delays_seed)
    return [new_pitch, new_note_lengths, new_delays, new_velocity_on, new_velocity_off]


def get_lists_for_all_channels(channels, msgs):
    """
    :param channels: a list of all the channels for the desired programs (instruments) to include in output song
    :param msgs: a list of all the messages in a track
    :return: a dictionary where the keys are the programs and the values are the generated lists (+ song length)
    """
    channels_dict = get_channels_dict(msgs)
    new_channels_dict = {value: key for key, value in channels_dict.items()}  # swaps all keys and values in the dict
    channel_lists_dict = {}
    for channel in channels:
        channel_lists_dict[new_channels_dict[channel]] = make_lists_for_all_parameters(channel, msgs)
    return channel_lists_dict


def main():
    output, ticksperbeat = regulate_tracks.main()
    list1 = output
    channels, programs = get_song_inputs(list1)
    """
    #make_lists_for_all_parameters(2, list1)  # NOTE YOU CHANGE THE CHANNEL HERE IT IS HARD CODED
    #print(get_lists_for_all_channels(channels, list1))
    """
    channels_lists_dict = get_lists_for_all_channels(channels, list1)
    # print(channels_lists_dict)
    return channels_lists_dict


if __name__ == '__main__':
    main()
