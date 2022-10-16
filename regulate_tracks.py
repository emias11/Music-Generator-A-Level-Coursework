import mido
import pygame


# check is midi file is type 2 (and removes if so) - this is unlikely but can happen on old sites
def remove_type_2(midi):
    return True if midi.type == 2 else False


# add time from start to message data (for sorting and adjusted delta time purposes)
def add_cumulative_time(msg, current_time):
    add_on = msg.time
    current_time += add_on
    return current_time, add_on

"""
# removes tempo duplicates and only keeps the last tempo stated for a particular cumulative time
def remove_extra_tempo(msg, msgwithtempos, current_time):
    if not msgwithtempos:  # if the list is empty
        msgwithtempos.append([msg, current_time])  # append the tempo message along with the cumulative time
    else:
        for i in range(len(msgwithtempos)):  # iterate through the current list of tempo messages + cumulative_times
            msgwithtempo = msgwithtempos[i]  # allocate to the variable msgwithtempo the i item in the list
            if msgwithtempo[1] == current_time:  # this checks for cumulative time duplicates
                msgwithtempos.remove(msgwithtempo)  # removes from the list if duplicate (if found)
        msgwithtempos.append([msg, current_time])  # adds the new tempo to the list (with its cumulative time)
    return msgwithtempos
"""


def filter_and_time(mid, all_messages):  # for each track (then message) do the following
    msgwithtempos = []
    for i, track in enumerate(mid.tracks):
        current_time = 0
        # print(f"Track {i}: {track.name}")
        for msg in track:
            current_time = add_cumulative_time(msg, current_time)[0]
            allowed_types = ["note_on", "note_off", "set_tempo", "program_change"]
            # can add control_changes
            if msg.type in allowed_types:
                all_messages.append([msg, current_time])
            # elif msg.type == "set_tempo":
                # all_messages.append([msg, current_time])
                # msgwithtempos = remove_extra_tempo(msg, msgwithtempos, current_time)
            else:
                pass
            # else:
                # all_messages.append([msg, current_time])
    return all_messages, msgwithtempos


def unify_program_changes(list_of_msgs):
    new_list_of_msgs = []
    channels_and_programs = {}
    # {program: channel}
    for item in list_of_msgs:
        msg = item[0]
        if msg.type == 'program_change':
            # situation 1: channel not used and program not used, no change to message
            if msg.program not in channels_and_programs.keys() and msg.channel not in channels_and_programs.values():
                channels_and_programs[msg.program] = msg.channel
                new_list_of_msgs.append(
                    [mido.Message('program_change', channel=msg.channel, program=msg.program, time=0), item[1]])
            # situation 2: channel not used but program used (ie. program has already been allocated)
            elif msg.program in channels_and_programs.keys() and msg.channel not in channels_and_programs.values():
                pass  # (don't add to new list of msgs)
            # situation 3: channel used but program not used (can only happen in a song that isn't first)
            elif msg.program not in channels_and_programs.keys() and msg.channel in channels_and_programs.values():
                i = 0
                while i in channels_and_programs.values():
                    i += 1
                if i < 15:
                    msg.channel = i
                    new_list_of_msgs.append(
                        [mido.Message('program_change', channel=i, program=msg.program, time=0), item[1]])
                else:
                    pass  # (and it'll make the program what it previously was for that channel)
        else:
            new_list_of_msgs.append(item)
    list_of_msgs = new_list_of_msgs
    list_of_msgs = sorted(list_of_msgs, key=lambda x: x[1])
    return list_of_msgs


def get_all_lists_and_tpb(all_mid):
    all_lists = []
    ticksperbeat = 0
    for i in range(0, len(all_mid)):
        all_messages = []
        mid = mido.MidiFile(all_mid[i])
        ticksperbeat += mid.ticks_per_beat  # change this to be average ticks per beat
        if not remove_type_2(mid):
            all_messages, msgwithtempos = filter_and_time(mid, all_messages)
            final_messages = all_messages + msgwithtempos
            final_messages = sorted(final_messages, key=lambda x: x[1])
            all_lists += final_messages
    try:
        ticksperbeat = ticksperbeat // len(all_mid)
    except ZeroDivisionError:
        ticksperbeat = 480

    for i, item in enumerate(all_lists):
        # this gets rid of excess set_tempo messages
        if all_lists[i][0].type == "set_tempo":
            while all_lists[i + 1][0].type == "set_tempo":  # talk about trying this with i and i-1?
                all_lists.pop(i)

    all_lists = unify_program_changes(all_lists)

    """
    count = 0
    for item in all_lists:
        if item[0].type == 'program_change':
            print(item[0])
            count += 1
    print(count)
    """

    return all_lists, ticksperbeat


def main():  # for each midi file do the following
    # place-holder until database implemented
    # all_mid = ['major-scale.mid']
    # all_mid = ['Gloria-Mozart.MID.mid']
    # all_mid = ['BohemianRhapsody.mid']
    #all_mid = [' (Yiruma).mid']
    all_mid = ['ItsBeginningToLookALotLikeChristmas.mid', 'BohemianRhapsody.mid']
    get_all_lists_and_tpb(all_mid)


if __name__ == '__main__':
    main()


