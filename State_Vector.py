class State_vector:

    def __init__(self):
        self.vector = tuple([0] * 0)

    def update_state(self, number_of_states: int, state_amount: {int: int}):
        self.vector = [0] * number_of_states
        for state in state_amount:
            self.vector[state] = state_amount.get(state)
        return

    def get_state_vector(self):
        dictionary = {}
        for counter in range(len(self.vector)):
            dictionary[counter] = self.vector[counter]
        return dictionary

    def __str__(self):
        str_ret = "\n {"
        for counter in range(len(self.vector)):
            str_ret += str(counter) + ":" + str(self.vector[counter]) + ","
        str_ret = str_ret[:-1] + "}"
        return str_ret

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, State_vector):
            if len(other.vector) != len(self.vector):
                return False
            other_vec = list(other.vector)
            vec = list(self.vector)
            for entry in range(len(other_vec)):
                if vec[entry] != other_vec[entry]:
                    return False
            return True
        return False


def cont(known_actions: [str], act: str):
    for a in known_actions:
        if a == act:
            return True
    return False


def contain(info, char):
    """
    is one of the strings in info contains the given char
    :param info: several strings
    :param char: a given char (action)
    :return: True / False
    """
    for string in info:
        for index in info.get(string):
            if index == char:
                return True
    return False


def learn_two(characteristic_set, processes, positive_info: {str: str}, negative_info: {str: str}):
    """
    looking on the sequences received, finding out about what group of actions are origin in the same state
    :param characteristic_set: given be find_characteristic_set
    :param processes: number of procs we currently have (so for positive we will look on every thing less and for neg every thing greater)
    :param info: the set of actions so far {string of actions that get as to the current state : feasible now actions}
    :return: info
    """""
    # print(f"cs::: {characteristic_set}, counter is {processes}")
    pos_info = []
    for pos_counter in characteristic_set['positive']:
        if pos_counter <= processes:
            for pos_word in characteristic_set['positive'][pos_counter]:
                pos_info.append(pos_word)
        else:
            # Even though we are looking on a greater number of processes,
            # the first action must have been enabled from the initial state.
            for pos_word in characteristic_set['positive'][pos_counter]:
                pos_info.append(pos_word[0])
    pos_curr_info = [pos_word for pos_counter in characteristic_set['positive'] if pos_counter == processes
                     for pos_word in characteristic_set['positive'][pos_counter]]
    pos_curr_info = list(set(pos_curr_info))
    pos_info = list(set(pos_info))
    if pos_info:  # not empty
        maximal = max([len(x) for x in pos_info])
        for prefixSize in range(maximal + 1):
            for curr_word in pos_info:
                if len(curr_word) >= prefixSize:
                    prefix = curr_word[0:prefixSize]
                    for word in pos_info:
                        if len(word) > prefixSize and word.startswith(prefix):
                            letter = word[prefixSize]
                            if positive_info.get(prefix) is None:
                                positive_info[prefix] = letter
                            else:
                                if not (letter in positive_info.get(prefix)):
                                    positive_info[prefix] = positive_info.get(prefix) + letter
    # neg_info = []
    # neg_curr_info = []  # the list relevant for this number of processes only
    # for neg_counter in characteristic_set['negative']:
    #     if neg_counter > processes:  # Only greater equal amount of procs is relevant
    #         for neg_word in characteristic_set['negative'][neg_counter]:
    #             neg_info.append(neg_word)
    #     elif neg_counter == processes:
    #         for neg_word in characteristic_set['negative'][neg_counter]:
    #             neg_info.append(neg_word)
    #             neg_curr_info.append(neg_word)
    neg_info = [neg_word for neg_counter in characteristic_set['negative'] if neg_counter >= processes
                for neg_word in characteristic_set['negative'][neg_counter]]

    neg_curr_info = [neg_word for neg_counter in characteristic_set['negative'] if neg_counter == processes
                     for neg_word in characteristic_set['negative'][neg_counter]]
    neg_info = list(set(neg_info))
    neg_curr_info = list(set(neg_curr_info))
    # print("neg info ", neg_info)
    """
    Given a negative word $w in A^*$ such that $w=u cdot a$ s.t. $u in A^*$ and $a in A$
    such that u is a prefix of a word in pos_info
    we want to use this information that after u, the state-vector_u can be in a state where a is feasible from
    
    Furthermore, if no prefix in pos+info exists to represent u then the whole world w should be able
    I.e. if |w|=1 then act w is infeasible from teh initial state
    otherwise (|w|>1) then there exists some possible empty sequence of w that is feasible that afterwords the next 
    act is infeasible ... 
    """
    # for curr_word in neg_info:
    #     prefix = curr_word[:-1]
    #     for other_word in neg_info:
    #         if len(other_word) == len(curr_word) and other_word.startswith(prefix):
    #             letter = other_word[len(curr_word)-1]
    #             if negative_info.get(prefix) is None:
    #                 negative_info[prefix] = letter
    #             else:
    #                 if letter not in negative_info.get(prefix):
    #                     negative_info[prefix] = negative_info.get(prefix) + letter
    # return positive_info, negative_info

    return positive_info, pos_curr_info, neg_info, neg_curr_info


def learn_from_characteristic_set(characteristic_set, processes):
    return learn_two(characteristic_set, processes, {}, {})
