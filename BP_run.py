import random
import concurrent.futures
import time
import BP_Class as Bp
from helpers_functions import *
from BP_Learn import LearnerBp

twenty_min = 1200
fifteen_min = 900
ten_min = 600
three_hours = 3600 * 3
five_hours = 3600 * 5


class BP_run:
    def __init__(self, bp_1: Bp.BP_class):
        self.bp = bp_1

    def run(self, minimal=False):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.bp.find_all_characteristic_sets_for_learning, 30, twenty_min)
            try:
                result = future.result(timeout=twenty_min)  # Set the desired timeout in seconds
                char_set, CS_time = result
                print("charset[pos]:\n", char_set['positive'])
                print("charset[neg]:\n", char_set['negative'])
            except concurrent.futures.TimeoutError:
                char_set, CS_time = {'positive': {}, 'negative': {}}, -1
            finally:
                if CS_time != -1:
                    char_set, _ = clean_char_set(char_set)
                learn_bp = LearnerBp(char_set, self.bp, CS_time,
                                     {'positive': {}, 'negative': {}})
                if learn_bp.solution['failed_converged']:
                    return None, None, learn_bp.solution
                learn_bp.learn(minimal)
                clean_rec = clean_receivers(learn_bp.bp.receivers)
                # print(f"learner actions = {learn_bp.bp.actions}\nlearner receivers = {learn_bp.bp.receivers}\n"
                #       f"clean receivers: {clean_rec}")
                return learn_bp.bp.actions, clean_rec, learn_bp.solution

    def run_no_cs(self, words_to_add, words_are_given, maximal_procs=20, maximal_length=20, minimal=False):
        """
        if words_are_given==True then words_to_add are sample dictionary.
        otherwise, words_to_add is an int of number of words to add.
        a run that add amount of words_to_add to the cs and run it
        :param minimal: whether we want to invoke BPInfMin or not
        :param words_to_add: int if words_are_given=False, otherwise a dictionary of sample
        :param words_are_given: boolean value
        :param maximal_procs: maximal allowed processes for word in the sample
        :param maximal_length: maximal allowed length of word in the sample
        :return:
        """
        char_set = {'positive': {}, 'negative': {}}
        start_time = time.perf_counter()
        if not words_are_given:
            char_set, additional_words = self.create_sample(words_to_add, char_set, maximal_procs, maximal_length)
        else:
            char_set = words_to_add
            additional_words = words_to_add
        end_time = time.perf_counter()
        print("words_added:", additional_words)
        learn_bp = LearnerBp(char_set, self.bp, end_time - start_time, additional_words)
        if learn_bp.solution['failed_converged']:
            return None, None, learn_bp.solution, additional_words
        learn_bp.learn(minimal)
        clean_rec_min = clean_receivers(learn_bp.bp.receivers)
        non_minimal_clean_rec = clean_receivers(learn_bp.ret_origin_self_bp.receivers)
        # printing_info(clean_rec, clean_rec_non_minimal, learn_bp)
        return learn_bp.bp.actions, clean_rec_min, learn_bp.ret_origin_self_bp.actions, non_minimal_clean_rec, learn_bp.solution, additional_words

    def run_no_cs_pos_perc(self, words_to_add, pos_perc, length_limit=20, procs_limit=20, minimal=False):
        """
        :param minimal: whether we want to invoke BPInfMin or not
        :param words_to_add: int amount of words to add
        :param pos_perc: positive % of total words
        :param length_limit: longest word limit
        :param procs_limit: maximal procs limit
        :return:
        """
        char_set = {'positive': {}, 'negative': {}}
        start_time = time.perf_counter()
        char_set, additional_words = self.create_sample_pos_perc(words_to_add, char_set, pos_perc, length_limit,
                                                                 procs_limit)
        end_time = time.perf_counter()
        learn_bp = LearnerBp(char_set, self.bp, end_time - start_time, additional_words)
        if learn_bp.solution['failed_converged']:
            return None, None, learn_bp.solution, additional_words
        learn_bp.learn(minimal)
        clean_rec_min = clean_receivers(learn_bp.bp.receivers)
        non_minimal_clean_rec = clean_receivers(learn_bp.ret_origin_self_bp.receivers)
        # printing_info(clean_rec, clean_rec_non_minimal, learn_bp)
        return learn_bp.bp.actions, clean_rec_min, learn_bp.ret_origin_self_bp.actions, non_minimal_clean_rec, \
               learn_bp.solution, additional_words

    def run_cs_to_a_limit(self, cutoff_limit, sample_limit, minimal=False):
        char_set, CS_time = {'positive': {}, 'negative': {}}, -1
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.bp.find_cs_to_a_limit, cutoff_limit, sample_limit)
            try:
                result = future.result(timeout=three_hours)
                char_set, CS_time = result
            except concurrent.futures.TimeoutError:
                char_set, CS_time = {'positive': {}, 'negative': {}}, -1
            finally:
                cutoff = None
                char_set, _ = clean_char_set(char_set)
                learn_bp = LearnerBp(char_set, self.bp, CS_time, char_set, cutoff)
                print("learn.bp.sol:", learn_bp.solution)
                if learn_bp.solution['failed_converged']:
                    return None, None, learn_bp.solution
                learn_bp.learn(minimal)
                clean_rec_min = clean_receivers(learn_bp.bp.receivers)
                non_minimal_clean_rec = clean_receivers(learn_bp.ret_origin_self_bp.receivers)
                # printing_info(clean_rec, clean_rec_non_minimal, learn_bp)
                return learn_bp.bp.actions, clean_rec_min, learn_bp.ret_origin_self_bp.actions, non_minimal_clean_rec, \
                       learn_bp.solution

    def run_subsume_cs(self, words_to_add, are_words_given, cutoff_lim=None, time_lim=None, word_lim=None,
                       minimal=False):
        """
        a run that add amount of words_to_add to the cs and run it
        :param minimal: A parameter that is fed to the learning procedure
        :param word_lim: Limitation on amount of word to be generated, in order to help with limited resources
        :param time_lim: If given, this is time limitation in sec
        :param cutoff_lim: If given, then cutoff limitation for running
        :param are_words_given: A boolean value representing whether we create a sample (not necessarily a CS)
        for words_to_add amount or is the words are already given to us
        :param words_to_add: Number of words if are_words_given==False or the set of words if are_words_given==True
        :return:
        """
        char_set, CS_time = {'positive': {}, 'negative': {}}, -1
        fifteen_hours = 15 * 3600
        t = fifteen_hours
        c_l = 45
        if cutoff_lim is not None:
            c_l = cutoff_lim
        if time_lim is not None:
            t = time_lim
        if word_lim is not None:
            char_set, CS_time = self.bp.find_all_characteristic_sets_for_learning(c_l, t, word_lim)
        else:
            char_set, CS_time = self.bp.find_all_characteristic_sets_for_learning(c_l, t)
        additional_words = {'positive': {}, 'negative': {}}
        cutoff = None
        if CS_time != -1:
            char_set, additional_words, cutoff = self.increase_cs(words_to_add, char_set, are_words_given)
        learn_bp = LearnerBp(char_set, self.bp, CS_time, additional_words, cutoff)
        if learn_bp.solution['failed_converged']:
            return None, None, None, None, learn_bp.solution
        learn_bp.learn(minimal)
        clean_rec_min = clean_receivers(learn_bp.bp.receivers)
        non_minimal_clean_rec = clean_receivers(learn_bp.ret_origin_self_bp.receivers)
        # printing_info(clean_rec, clean_rec_non_minimal, learn_bp)
        return learn_bp.bp.actions, clean_rec_min, learn_bp.ret_origin_self_bp.actions, non_minimal_clean_rec, learn_bp.solution

    def increase_cs(self, size_int, char_set, are_words_given):
        """
        add size_int more elements for the cs
        :param are_words_given: boolean value, does the extra words are given
        :param char_set: the CS
        :param size_int: amount of samples to add or if 'are_words_given' is the dict_val
        :return: the new CS
        """
        dict_val = dict()
        dict_val['positive'] = dict()
        dict_val['negative'] = dict()
        cutoff = max(max(list(char_set['positive'].keys())), max(list(
            char_set['negative'].keys())))
        if are_words_given:
            for pos_neg in size_int:
                for proc in size_int[pos_neg]:
                    for word_pn in size_int[pos_neg][proc]:
                        if proc not in char_set[pos_neg]:
                            char_set[pos_neg][proc] = [word_pn]
                        else:
                            if word_pn in char_set[pos_neg][proc]:
                                continue
                            else:
                                char_set[pos_neg][proc].append(word_pn)
            return char_set, size_int, cutoff
        longest = ''  # the longest word in cs
        for name_val in ['positive', 'negative']:
            for procs in char_set[name_val]:
                for word_p in char_set[name_val][procs]:
                    if len(word_p) > len(longest):
                        longest = word_p
        longest_word = len(longest)
        alphabet1 = get_alphabet(char_set)
        pos_words_to_add = set()
        neg_words_to_add = set()
        for i in range(1, 2 * cutoff + 1):
            dict_val['positive'][i] = []
            dict_val['negative'][i] = []
        # print("dict_val:", dict_val)
        while len(pos_words_to_add) + len(neg_words_to_add) < size_int:
            proc_amount = random.randint(1, 2 * cutoff)
            word_len = random.randint(1, longest_word)
            created_word = []
            for _ in range(word_len):
                created_word.append(random.choice(list(alphabet1)))
            if self.bp.is_feasible(proc_amount, created_word):
                if ''.join(created_word) in pos_words_to_add:
                    continue
                else:
                    if proc_amount not in char_set['positive']:
                        char_set['positive'][proc_amount] = [''.join(created_word)]
                        pos_words_to_add.add(''.join(created_word))
                        dict_val['positive'][proc_amount].append(''.join(created_word))
                    else:
                        if ''.join(created_word) in char_set['positive'][proc_amount]:
                            continue
                        else:
                            char_set['positive'][proc_amount].append(''.join(created_word))
                            pos_words_to_add.add(''.join(created_word))
                            dict_val['positive'][proc_amount].append(''.join(created_word))
            else:
                if ''.join(created_word) in neg_words_to_add:
                    continue
                else:
                    if proc_amount not in char_set['negative']:
                        char_set['negative'][proc_amount] = [''.join(created_word)]
                        neg_words_to_add.add(''.join(created_word))
                        dict_val['negative'][proc_amount].append(''.join(created_word))
                    else:
                        if ''.join(created_word) in char_set['negative'][proc_amount]:
                            continue
                        else:
                            char_set['negative'][proc_amount].append(''.join(created_word))
                            neg_words_to_add.add(''.join(created_word))
                            dict_val['negative'][proc_amount].append(''.join(created_word))
        dict_val = {key: {inner_key: inner_value for inner_key, inner_value in value.items() if inner_value} for
                    key, value in dict_val.items()}

        return char_set, dict_val, cutoff

    def create_sample_pos_perc(self, words_to_add, char_set, pos_perc, length_limit, procs_limit):
        """
        :param char_set: dict:{'positive': {}, 'negative': {}}
        :param procs_limit: maximal procs limit
        :param length_limit: longest word limit
        :param pos_perc: positive % of total words
        :param words_to_add: int amount of words to add
        :return:
        """
        dict_val = dict()
        dict_val['positive'] = dict()
        dict_val['negative'] = dict()
        longest_word = length_limit

        alphabet1 = self.get_bp_alphabet()
        pos_words_to_add = set()
        neg_words_to_add = set()
        for i in range(1, procs_limit + 1):
            dict_val['positive'][i] = []
            dict_val['negative'][i] = []

        while len(pos_words_to_add) < words_to_add * pos_perc:
            created_word = []
            proc_amount = random.randint(1, procs_limit)
            word_len = random.randint(1, longest_word)
            state_vec = {i: 0 for i in self.bp.actions}
            state_vec[self.bp.initial_state] = proc_amount
            for _ in range(word_len):
                feasible_set = self.bp.feasible_set(state_vec)
                chosen_act = random.choice(list(feasible_set))
                created_word.append(chosen_act)
                state_vec = self.bp.act_action(state_vec, chosen_act)
            if proc_amount not in char_set['positive']:
                char_set['positive'][proc_amount] = [''.join(created_word)]
                pos_words_to_add.add(''.join(created_word))
                dict_val['positive'][proc_amount].append(''.join(created_word))
            else:
                if ''.join(created_word) in char_set['positive'][proc_amount]:
                    continue
                else:
                    char_set['positive'][proc_amount].append(''.join(created_word))
                    pos_words_to_add.add(''.join(created_word))
                    dict_val['positive'][proc_amount].append(''.join(created_word))

        while len(neg_words_to_add) < words_to_add * (1 - pos_perc):
            proc_amount = random.randint(1, procs_limit)
            word_len = random.randint(1, longest_word)
            created_word = []
            for _ in range(word_len):
                created_word.append(random.choice(list(alphabet1)))
            if self.bp.is_feasible(proc_amount, created_word):
                continue
            else:
                if proc_amount not in char_set['negative']:
                    char_set['negative'][proc_amount] = [''.join(created_word)]
                    neg_words_to_add.add(''.join(created_word))
                    dict_val['negative'][proc_amount].append(''.join(created_word))
                else:
                    if ''.join(created_word) in char_set['negative'][proc_amount]:
                        continue
                    else:
                        char_set['negative'][proc_amount].append(''.join(created_word))
                        neg_words_to_add.add(''.join(created_word))
                        dict_val['negative'][proc_amount].append(''.join(created_word))
        dict_val = {key: {inner_key: inner_value for inner_key, inner_value in value.items() if inner_value} for
                    key, value in dict_val.items()}

        return char_set, dict_val

    def create_sample(self, size_int, char_set, maximal_procs, longest_word):
        """
        add size_int more elements for the cs
        :param longest_word: longest word (a.k.a sequance) in the sample
        :param maximal_procs:
        :param char_set: the CS
        :param size_int: amount of samples to add
        :return: the new CS
        """
        dict_val = dict()
        dict_val['positive'] = dict()
        dict_val['negative'] = dict()

        alphabet1 = self.get_bp_alphabet()
        pos_words_to_add = set()
        neg_words_to_add = set()
        for i in range(1, 2 * maximal_procs + 1):
            dict_val['positive'][i] = []
            dict_val['negative'][i] = []
        while len(pos_words_to_add) + len(neg_words_to_add) < size_int:
            proc_amount = random.randint(1, 2 * maximal_procs)
            word_len = random.randint(1, longest_word)
            created_word = []
            for _ in range(word_len):
                created_word.append(random.choice(list(alphabet1)))
            if self.bp.is_feasible(proc_amount, created_word):
                if ''.join(created_word) in pos_words_to_add:
                    continue
                else:
                    if proc_amount not in char_set['positive']:
                        char_set['positive'][proc_amount] = [''.join(created_word)]
                        pos_words_to_add.add(''.join(created_word))
                        dict_val['positive'][proc_amount].append(''.join(created_word))
                    else:
                        if ''.join(created_word) in char_set['positive'][proc_amount]:
                            continue
                        else:
                            char_set['positive'][proc_amount].append(''.join(created_word))
                            pos_words_to_add.add(''.join(created_word))
                            dict_val['positive'][proc_amount].append(''.join(created_word))
            else:
                if ''.join(created_word) in neg_words_to_add:
                    continue
                else:
                    if proc_amount not in char_set['negative']:
                        char_set['negative'][proc_amount] = [''.join(created_word)]
                        neg_words_to_add.add(''.join(created_word))
                        dict_val['negative'][proc_amount].append(''.join(created_word))
                    else:
                        if ''.join(created_word) in char_set['negative'][proc_amount]:
                            continue
                        else:
                            char_set['negative'][proc_amount].append(''.join(created_word))
                            neg_words_to_add.add(''.join(created_word))
                            dict_val['negative'][proc_amount].append(''.join(created_word))
        dict_val = {key: {inner_key: inner_value for inner_key, inner_value in value.items() if inner_value} for
                    key, value in dict_val.items()}

        return char_set, dict_val

    def get_bp_alphabet(self):
        unique_chars = set()
        for _, inner_dict in self.bp.actions.items():
            for char_key in inner_dict.keys():
                unique_chars.add(char_key)

        unique_chars_list = list(unique_chars)
        return unique_chars_list


def running(bp_1: Bp.BP_class, number):
    print(f"\nNew Scenario {number} :")
    bp1 = BP_run(bp_1)
    _, _, solution = bp1.run()
    return solution


def running_plus_words(bp_1: Bp.BP_class, number, words_to_add, are_words_given):
    print(f"\nNew Scenario {number} :")
    bp1 = BP_run(bp_1)
    _, _, solution = bp1.run_subsume_cs(words_to_add, are_words_given)
    return solution


def running_to_a_limit(bp_1: Bp.BP_class, number, cutoff_limit, sample_limit):
    print(f"\nNew Scenario {number} :")
    bp1 = BP_run(bp_1)
    min_actions, min_clean_rec, actions, clean_receive, solution = bp1.run_cs_to_a_limit(cutoff_limit, sample_limit)
    return solution


def running_no_cs_pos_percentage(bp_1: Bp.BP_class, number, words_to_add, pos_perc, length_limit, procs_limit):
    print(f"\nNew Scenario {number} :")
    bp1 = BP_run(bp_1)
    bp_actions, clean_receive, sol, _ = bp1.run_no_cs_pos_perc(words_to_add, pos_perc, length_limit, procs_limit)
    return bp_actions, clean_receive, sol


def running_no_cs(bp_1: Bp.BP_class, number, words_to_add, are_words_given):
    print(f"\nNew Scenario {number} :")
    bp1 = BP_run(bp_1)
    min_actions, clean_receive, non_min_actions, non_min_clean_rec, sol, words_added = bp1.run_no_cs(words_to_add,
                                                                                                     are_words_given)
    return min_actions, clean_receive, non_min_actions, non_min_clean_rec, sol, words_added


def is_right(cher_set, the_bp: Bp.BP_class):
    """
    is the given bp can read all those words
    """
    print("the bp ", the_bp)
    for p_c in cher_set['positive']:
        for p_word in cher_set['positive'][p_c]:
            char_list = []
            for char in p_word:
                char_list.append(char)
            if not the_bp.is_feasible(p_c, char_list):
                return False
    for n_c in cher_set['negative']:
        for n_word in cher_set['negative'][n_c]:
            char_list = []
            for char in n_word:
                char_list.append(char)
            if the_bp.is_feasible(n_c, char_list):
                return False
    return True
