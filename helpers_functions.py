min_column = ['failed_converged', 'timeout', 'amount_of_states_in_origin',
              'amount_of_states_in_output', 'origin_BP', 'output_BP', 'cutoff',
              'CS_development_time',
              'CS_positive_size', 'CS_negative_size', 'words_added',
              'longest_word_in_CS', 'solve_SMT_time',
              'right_output', 'amount_of_states_in_minimal_output',
              'minimal_output_BP',
              'minimal_solve_SMT_time', 'minimal_right_output']

non_min_column = ['failed_converged', 'timeout', 'amount_of_states_in_origin',
                  'amount_of_states_in_output', 'origin_BP', 'output_BP', 'cutoff',
                  'CS_development_time',
                  'CS_positive_size', 'CS_negative_size', 'words_added',
                  'longest_word_in_CS', 'solve_SMT_time',
                  'right_output']


def get_key_by_value(dictionary, target_value):
    sorted_items = sorted(dictionary.items(), key=lambda x: x[0])
    for key, value in sorted_items:
        if value == target_value:
            return key
    return None


def get_keys_by_value(dictionary, target_value):
    keys_with_value = [key for key, value in dictionary.items() if value == target_value]
    return keys_with_value


def has_common_letter(actions, known_actions):
    """
    :param actions: feasible actions after "prefix"
    :param known_actions: already seen actions
    :return:
    """
    for a in actions:
        if a in known_actions:
            return True, a
    return False, None


def remove_duplicates(dictionary: dict()):
    unique_values = set()
    keys_to_remove = []

    for key, value in dictionary.items():
        if value <= unique_values:
            keys_to_remove.append(key)
        else:
            unique_values = unique_values | value

    for key in keys_to_remove:
        del dictionary[key]

    return dictionary


def get_unique_letters(list_negative_words):
    """
    :param list_negative_words: list of negative examples for 1 proc
    :return: the set of all the unique letters
    """
    all_letters = set()
    for value in list_negative_words:
        all_letters.update(set(value))

    return all_letters


def filter_strings_by_length(strings, n):
    return [s for s in strings if len(s) == n]


def get_positive_alphabet(pos_char_set):
    alpha = set()
    flat_pos_list = [string for sublist in list(pos_char_set.values()) for string in sublist]
    flat_pos_list = list(set(flat_pos_list))
    for value in flat_pos_list:
        alpha.update(set(value))
    return alpha


def clean_receivers(receivers):
    new_rec = {}
    for entry in receivers:
        if entry == -1:
            continue
        new_rec[entry] = {}
        for act in receivers.get(entry):
            (land, status) = receivers.get(entry).get(act)
            new_rec[entry][act] = land
    return new_rec


def clean_char_set(char_set):
    actions_in_pos = []
    actions_in_neg = []
    for counter in char_set['positive']:
        for w_pos in char_set['positive'][counter]:
            actions_in_pos = actions_in_pos + list(w_pos)
    actions_in_pos = list(set(actions_in_pos))
    for counter in char_set['negative']:
        for w_neg in char_set['negative'][counter]:
            actions_in_neg = actions_in_neg + list(w_neg)
    actions_in_neg = list(set(actions_in_neg))
    actions_to_remove = []
    for a_n in actions_in_neg:
        if a_n not in actions_in_pos:
            actions_to_remove.append(a_n)
    to_remove = dict()
    for counter in char_set['negative']:
        to_remove[counter] = []
        for w_neg in char_set['negative'][counter]:
            for act in w_neg:
                if act in actions_to_remove:
                    to_remove[counter].append(w_neg)
                    break
    for c in to_remove:
        char_set['negative'][c] = [x for x in char_set['negative'][c] if x not in to_remove[c]]
    return char_set, actions_to_remove


def get_alphabet(char_set):
    alpha = set()
    flat_pos_list = [string for sublist in list(char_set['positive'].values()) for string in sublist]
    flat_pos_list = list(set(flat_pos_list))
    flat_neg_list = [string for sublist in list(char_set['negative'].values()) for string in sublist]
    flat_neg_list = list(set(flat_neg_list))
    for value in flat_pos_list:
        alpha.update(set(value))

    for value in flat_neg_list:
        alpha.update(set(value))
    return alpha


def printing_info(clean_receiver, non_minimal_clean_rec, learn_bp):
    """
    In case we want to print the info while running
    """
    print(f"learner actions = {learn_bp.bp.actions}\nlearner receivers = {learn_bp.bp.receivers}\n"
          f"clean receivers: {clean_receiver}")
    print(
        f"non minimal:: learner actions = {learn_bp.ret_origin_self_bp.actions}\nlearner receivers = "
        f"{learn_bp.ret_origin_self_bp.receivers}\n"
        f"clean receivers: {non_minimal_clean_rec}")
