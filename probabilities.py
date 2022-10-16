import mido
import regulate_tracks


def get_channel_note_msgs(input_msgs, channel):
    # this just gets the note msgs (with cumulative time) for all of a particular channel
    channel_msgs = []
    for msg in input_msgs:
        if msg[0].type != "set_tempo" and msg[0].type != "program_change":
            if msg[0].channel == channel:
                channel_msgs.append(msg)
    return channel_msgs


def get_channels_dict(input_msgs):
    """
    :param input_msgs: a list of all messages from an input song (along with their cumulative time)
    :return: a dictionary of all programs used in a song (as keys) and their corresponding channels (as vals)
    """
    channels_dict = {}
    for i in range(len(input_msgs)):
        msg = input_msgs[i][0]
        if msg.type == "program_change":
            if msg.program not in channels_dict.keys():
                channels_dict[msg.program] = msg.channel
    keys = list(channels_dict.keys())
    for key in keys:
        if len(get_channel_note_msgs(input_msgs, channels_dict[key])) == 0:
            del channels_dict[key]
    return channels_dict


def notes_delays(channel_msgs):
    """
    :param channel_msgs: a list of all msgs for a particular channel (within a song)
    :return: returns a list of differences between note on msgs as well as a list of
    the length of notes in order with which they appear (N.B. this is different to
    just average time between note on/off msgs, as it's the length of each pitch's note
    in order)
    """
    """
    for i in range(len(channel_msgs)):
        msg = channel_msgs[i]
        next_msgs = channel_msgs[i+1]
        if msg[1] > next_msgs[1]:
            print("uh oh")
    """
    note_on_difs, note_lengths = [], []
    for i in range(len(channel_msgs)):
        msg = channel_msgs[i]
        y = 1
        note = msg[0].note
        boole = True
        if msg[0].type == 'note_on':
            if i == 0:
                current_time_note_on = msg[1]
            else:
                note_on_difs.append(msg[1] - current_time_note_on)
                current_time_note_on = msg[1]
            while boole:
                if i+y < len(channel_msgs):
                    if channel_msgs[i + y][0].type == 'note_off' and channel_msgs[i + y][0].note == note:
                        boole = False
                        note_lengths.append(channel_msgs[i + y][1] - msg[1])
                    else:
                        y += 1
                else:
                    note_lengths.append(0)
                    boole = False
    return note_on_difs, note_lengths


def list_to_dict(a_list):
    """
    :param a_list: any list
    :return: will return the corresponding dict:
    a generic function to take a list and convert it into a dictionary where each item
    is a key, and the values are a list of items that immediately proceed the key item
    """
    """
    last_element = a_list[-1]
    penultimate_element = a_list[-2]
    if a_list.count(last_element) == 1 or a_list.count(penultimate_element) == 1:
        a_list.remove(last_element)
        a_list.remove(penultimate_element)
    """
    r_dict = {}
    for i in range(1, len(a_list)):
        if a_list[i - 1] not in r_dict.keys():
            r_dict[a_list[i - 1]] = [a_list[i]]
        else:
            r_dict[a_list[i - 1]].append(a_list[i])
    return r_dict


def make_delay_and_len_dicts(note_on_difs, note_lengths):
    """
    :param note_on_difs: a list of the time differences between all note on messages for one channel
    :param note_lengths: a list of the time differences between all note off messages for one channel
    :return: dicts for the delays between note on messages and for the length of notes
    """

    delays_dict = list_to_dict(note_on_difs)
    note_lengths_dict = list_to_dict(note_lengths)
    return delays_dict, note_lengths_dict


def make_velocity_dicts(channel_msgs):
    #  note, note off messages have velocities too hence had to change this function (by adding note off)
    velocity_on_dict, velocity_off_dict = {}, {}
    prev_on_velocity, prev_off_velocity = -1, -1
    for i in range(1, len(channel_msgs)):
        msg = channel_msgs[i][0]
        if msg.type == "note_on":
            if prev_on_velocity == -1:
                pass
            elif prev_on_velocity not in velocity_on_dict.keys():
                velocity_on_dict[prev_on_velocity] = [msg.velocity]
            else:
                velocity_on_dict[prev_on_velocity].append(msg.velocity)
            prev_on_velocity = msg.velocity
        elif msg.type == "note_off":
            if prev_off_velocity == -1:
                pass
            elif prev_off_velocity not in velocity_off_dict.keys():
                velocity_off_dict[prev_off_velocity] = [msg.velocity]
            else:
                velocity_off_dict[prev_off_velocity].append(msg.velocity)
            prev_off_velocity = msg.velocity
    return velocity_on_dict, velocity_off_dict


def make_pitch_dict(channel_msgs):
    pitch_dict = {}
    prev_pitch = -1
    for i in range(1, len(channel_msgs)):
        msg = channel_msgs[i][0]
        if msg.type == "note_on":
            if prev_pitch == -1:
                pass
            elif prev_pitch not in pitch_dict.keys():
                pitch_dict[prev_pitch] = [msg.note]
            else:
                pitch_dict[prev_pitch].append(msg.note)
            prev_pitch = msg.note
    return pitch_dict


def make_dict_of_dicts(d):
    """
    :param dict: any dict
    :return: converts a dictionary of lists into a dictionary of dictionaries
    where the values in the sub-dicts is the occurrence count of the key
    eg. if have {a:[b,c,b]} will become {a:{b:2, c:1}}
    """
    for value in d.items():
        for i in range(len(d)):
            val_list = value[1]
            dict_of_dicts = {}
            for val in val_list:
                if val not in dict_of_dicts.keys():
                    dict_of_dicts[val] = 1
                else:
                    dict_of_dicts[val] += 1
            d[value[0]] = dict_of_dicts
    return d


def dict_vals_to_probs(dicts):
    """
    :param dicts: a dictionary of dictionaries
    :return: takes the values in the sub-dicts of each main dict key,
    and turns them into probabilities of the sum of values for that sub-dict
    then returns the main dict with probabilities instead of value counts
    """
    for a_dict in dicts.items():
        sub_dict = a_dict[1]
        total_occurences = sum(sub_dict.values())
        for value in sub_dict.items():
            sub_dict[value[0]] = value[1] / total_occurences
    return dicts


def get_final_dicts(msg_list, channel):
    """
    :param msg_list: a list of all the messages from a song
    :param channel: input channel
    :return: returns the pitch, velocities, note_length_, delays dicts (of dicts) for a particular channel
    """
    channel_msgs = get_channel_note_msgs(msg_list, channel)
    note_on_difs, note_lengths = notes_delays(channel_msgs)
    delays_dict = dict_vals_to_probs(make_dict_of_dicts(make_delay_and_len_dicts(note_on_difs, note_lengths)[0]))
    note_lengths_dict = dict_vals_to_probs(make_dict_of_dicts(make_delay_and_len_dicts(note_on_difs, note_lengths)[1]))
    velocity_on_dict = dict_vals_to_probs(make_dict_of_dicts(make_velocity_dicts(channel_msgs)[0]))
    velocity_off_dict = dict_vals_to_probs(make_dict_of_dicts(make_velocity_dicts(channel_msgs)[1]))
    pitch_dict = dict_vals_to_probs(make_dict_of_dicts(make_pitch_dict(channel_msgs)))
    return pitch_dict, velocity_on_dict, velocity_off_dict, note_lengths_dict, delays_dict


def main():
    output, ticksperbeat = regulate_tracks.main()
    list1 = output
    channels = (get_channels_dict(list1)).values()
    get_final_dicts(list1, 9)
    # THIS IS A PLACEHOLDER VALUE (for a channel)
    # doesn't actually matter unless you're testing as probabilities. main() not used elsewhere

    """

    for channel in channels:
        for dict1 in get_final_dicts(list1, channel): # put the channel in here
            print(dict1)
    
    """


if __name__ == '__main__':
    main()
