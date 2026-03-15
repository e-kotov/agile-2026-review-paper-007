def count_transitions(modes_str):
    modes_list = modes_str.split(';')
    transition_count = modes_list.count('transition')

    total_transition_count = (transition_count / 2) + 1
    # I always have 2 transitions even if I start with bike ( parent;transition;bike;transition;parent)
    # so /2 because I only want the first one and then +1 because we always account for walk.

    return total_transition_count

def calculate_mode_percentage(modes_str, lengths_str, target_mode):
    mode_list = modes_str.split(';')
    lengths_list = lengths_str.split(';')

    # Filter out 'fake' and 'transition' modes
    valid_data = [(mode, length) for mode, length in zip(mode_list, lengths_list) if mode not in ['fake', 'transition']]

    # Calculate the total length of the target mode
    total_target_length = sum(float(length) for mode, length in valid_data if mode == target_mode)

    # Calculate the total length of all valid modes
    total_valid_length = sum(float(length) for _, length in valid_data)

    # Calculate and return the percentage of the target mode
    if total_valid_length > 0:
        target_percentage = (total_target_length / total_valid_length) * 100
        return round(target_percentage, 3)
    else:
        return 0


#Rename 'transition' Function
def rename_transition_labels(label_sequence):
    labels = label_sequence.split(';')
    conditions = {
        'car': 'transition_car',
        'bike': 'transition_bike',
        'bus': 'transition_bus',
        'train': 'transition_train',
        'subway': 'transition_subway',
        'tram': 'transition_tram'
    }

    for i in range(len(labels)):
        if labels[i] == 'transition':
            for mode, new_label in conditions.items():
                if (i > 0 and labels[i-1] == mode) or (i < len(labels)-1 and labels[i+1] == mode):
                    labels[i] = new_label
                    break

    return ';'.join(labels)
