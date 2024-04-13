import random
import pandas as pd
from z3 import *

import BP_Class as Bp
from State_Vector import learn_from_characteristic_set
from Trie import Trie
from BP_Class import BP_class

print(z3.get_version_string())
"""
first : find the original state actions...
for 1 proc we know all the actions that are feasible...
2 procs, learn about responses going in a different ways
above 2, for n procs , n>=2:
check feasible diff from n+1 to n procs.
    *   if new actions are feasible (the group of feasibility for n+1 != the group that is feasible for n)
        then the n+1 proc want to a diff location then the other n, the group of new act that is feasible is the acts
        that are feasible from the state it reached
    *   else, no new actions are feasible, then the n+1 proc 'joined' one of the other n procs.
            *   if they are all together then we know for certain where it is.
            *   else, there are multiple locations that the n procs are and the n+1 proc joined one of them.

                -- There is several options for a response to go, act is necessarily known where it gets,
                might be that a response for an action and the act is unclear with one goes where. --

                in that case we would hold all the possibilities (in a trie / other data structure).
                keep going until no new info, until (according to 'find_all_characteristic_sets_for_learning',
                stops when: characteristic set from n+1 procs. == characteristic set from n procs.)

    After all of it, we remain with the possibilities trie, need to create paths from top to bottom(to leaves)
    if a path of chooses return the origin tree according to the characteristic set, finished.
    else, run the same sequence of actions as the one that led to the contradiction.
        * if in the end of the sequence the missing location (the entry in the vec that was ment to be the word to read)
        then eliminate those entries.
        * else, is feasible for this sequence, continue hold this seq of possibilities.
            (Might be better to hold a quick vec calculater to know the curr vec for each sequence of possibilities)
            --  Need to proof that is bounded ... By the number of procs and number of words, possibilities trie is log.
                then be each choice we need to check log of possibilities... (height of the tree)
        DONE, found the correct one (eliminate the rest or find the specific one)
"""

a_val = 97
z_val = 122
A_val = 65
Z_val = 90
act_names = [str(chr(c)) for c in range(a_val, z_val + 1)] + [str(chr(c)) for c in range(A_val, Z_val + 1)]

alphabet = [str(chr(c)) for c in range(a_val, z_val + 1)] + [str(chr(c)) for c in range(A_val, Z_val + 1)] + [
    str(chr(n)) for n in range(0, 10)] + ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '[',
                                          ']', '{', '}', '|', '~', '`', ',']

twenty_min = 1200
fifteen_min = 900
ten_min = 600
three_hours = 3600 * 3
five_hours = 3600 * 5

''' --- creating the SMT functions : --- '''
''' Given an action, return where the action lands '''
fsend = Function('fsend', IntSort(), IntSort())
''' given an action, and a state, return where the receiver lands '''
frec = Function('frec', IntSort(), IntSort(), IntSort())
fst = Function('fst', IntSort(), IntSort())  # Given an action, return the state, The state of an action
''' recursively use the frec, recFrec(word, state), so where this state will land after responding to all of w.
    for a word w=ua. recfrec('',s)=s. recfrec(w,s)=frec(a, recfrec(u,s))'''
recFrec = RecFunction('rec_frec', IntSort(), IntSort())


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


class LearnerBp:
    def __init__(self, characteristic_sets, real_bp: BP_class, CS_time, words_addition,
                 cutoff=None):
        """
        :param characteristic_sets: for each number of proces: characteristic set

        :param real_bp: the real bp to compare to
        """
        self.ret_origin_self_bp = None
        self.actions_smt = dict()  # the keys are the actions and the values are the Int in SMT
        self.states_smt = dict()  # the keys are the states and the values are the Int in SMT
        self.real_bp = real_bp

        self.options_holder: {str: {int: [(int, int)]}} = dict()  # {prefix:{counter:[(from_state, to_state)]}}
        self.not_in_same_state = []  # act *not* in SMT, act *not* in SMT
        self.fst_behaviours = []  # action smt, state smt
        self.fsend_behaviours = []  # action in smt, state in smt
        self.fsend_behaviours_by_acts = []  # act a,b non smt s.t. fsend(self.actions_smt[a])=fst(self.actions_smt[b])

        self.smt_constraint_copy = []
        self.constraints_total_for_procs = []  # iterate over them and make sure they are in the right set
        self.known_actions = []
        self.known_states = []
        self.bp = Bp.BP_class(1, {}, 0, {})  # initial partial BP
        self.full_cs = characteristic_sets
        self.modified_full_cs = None
        self.characteristic_set = None
        self.negative_cs = None
        self.modify_cs(self.full_cs)

        # max number of processes in the positive and negative examples is the cutoff
        list_pos = list(characteristic_sets['positive'].keys())
        if not list_pos:  # list_pos == []
            list_pos = 0
        else:
            list_pos = max(list_pos)

        list_neg = list(characteristic_sets['negative'].keys())
        if not list_neg:  # list_neg == []
            list_neg = 0
        else:
            list_neg = max(list_neg)
        default_cutoff = 5
        if cutoff is not None:
            self.cutoff = cutoff
        else:
            # in case no CS is given, hence neg and pos are empty, we will take defaultive size
            self.cutoff = max(list_pos, list_neg)
            if self.cutoff == 0:
                self.cutoff = default_cutoff
        self.trie_info = Trie()
        self.unresolved_possibilities: {
            str: {int: {(int, str, int)}}} = {}  # responses unknown : {prefix:{counter:{(from, act, to)}}}
        self.unresolved_act_possibilities: {
            str: {int: {str: [int]}}} = {}  # actions unknown : {prefix:{from_state:{act:[landing_states]}}}
        longest = ''  # the longest word in cs
        for name_val in ['positive', 'negative']:
            for procs in self.modified_full_cs[name_val]:
                for w in self.modified_full_cs[name_val][procs]:
                    if len(w) > len(longest):
                        longest = w
        self.solution = {'failed_converged': CS_time == -1,
                         'timeout': False,
                         'amount_of_states_in_origin': len(set(self.real_bp.actions)),
                         'amount_of_states_in_output': 0,
                         'origin_BP': f'states: {len(set(self.real_bp.actions))},\n actions: {self.real_bp.actions},\n'
                                      f'initial: {self.real_bp.initial_state},\n'
                                      f'receivers: {clean_receivers(self.real_bp.receivers)}', 'output_BP': '',
                         'cutoff': self.cutoff, 'CS_development_time': CS_time,
                         'CS_positive_size': sum(len(cs) for cs in self.modified_full_cs['positive'].values()),
                         'CS_negative_size': sum(len(cs) for cs in self.modified_full_cs['negative'].values()),
                         'words_added': words_addition,
                         'longest_word_in_CS': len(longest),
                         'solve_SMT_time': 0.0,
                         'amount_of_states_in_minimal_output': 0,
                         'minimal_output_BP': '',
                         'minimal_solve_SMT_time': 0.0
                         }  # 'right_output'

    def a_and_b_are_separated_constraints(self):
        """
        states:
        in case a division of the actions to states was found, return it.
        Otherwise, not a CS, no division is found bot only constraint on who can't be with whom...
        all_acts:
        the set of all actions seen in the sample set (both positive and negative examples)
        all_first_letters:
        all actions that are for sure enabled from teh initial state
        :return: states, all_acts, all_first_letters
        """
        cant_be_together = dict()
        all_acts = set()
        for counter in self.negative_cs:
            for neg_w in self.negative_cs.get(counter):
                for nl in neg_w:
                    if nl not in all_acts:
                        all_acts.add(nl)
                        if cant_be_together.get(nl) is None:
                            cant_be_together[nl] = []
                for c in range(1, counter + 1):  # counter +1 -> we access at most to counter index
                    if self.characteristic_set.get(c) is None:
                        continue
                    for pos_w in self.characteristic_set[c]:
                        for lis in pos_w:
                            if lis not in all_acts:
                                all_acts.add(lis)
                                if cant_be_together.get(lis) is None:
                                    cant_be_together[lis] = []
                        if len(pos_w) >= len(neg_w) and pos_w.startswith(neg_w[:-1]):
                            if (neg_w[-1], pos_w[len(neg_w) - 1]) not in self.not_in_same_state:
                                self.not_in_same_state.append((neg_w[-1], pos_w[len(neg_w) - 1]))
                            cant_be_together[neg_w[-1]].append(pos_w[len(neg_w) - 1])
                            cant_be_together[pos_w[len(neg_w) - 1]].append(neg_w[-1])
        can_be = dict()
        for act in cant_be_together:
            can_be[act] = all_acts - set(cant_be_together[act])

        # clean can_be : in case there is an action that appears in several options of union,
        # then arbitrary chose one.
        flag = False  # if it became True, then for sure it's not a CS
        for act in can_be:
            appears_with = set(can_be[act])
            for act_2 in can_be:
                if (act in set(can_be[act_2])) and len(set(can_be[act_2]).symmetric_difference(appears_with)) != 0:
                    flag = True
        # makesure: the above for was already done in:
        #  if len(pos_w) >= len(neg_w) and pos_w.startswith(neg_w[:-1]):
        #    if (neg_w[-1], pos_w[len(neg_w) - 1]) not in self.not_in_same_state:
        #        self.not_in_same_state.append((neg_w[-1], pos_w[len(neg_w) - 1]))
        for act in can_be:
            other_acts = set(all_acts) - set(can_be[act])
            for o_a in other_acts:
                self.not_in_same_state.append((act, o_a))

        all_first_letters = [pos_w[0] for c in self.characteristic_set for pos_w in self.characteristic_set[c]]
        all_first_letters = list(set(all_first_letters))
        all_negative_examples = []
        for i in self.negative_cs:
            all_negative_examples += self.negative_cs[i]
        all_negative_examples = list(set(all_negative_examples))
        for f_l in all_first_letters:
            if can_be.get(f_l) is None:
                flag = True
            elif len(set(can_be[f_l]).symmetric_difference(set(all_first_letters))) > 0:
                flag = True
            elif self.characteristic_set.get(1) is not None:
                # list_of_options = []
                is_flfl_in_pos = False
                for element in self.characteristic_set[1]:
                    # if element.startswith(f_l):
                    #     list_of_options.append(f_l)
                    if element.startswith(str(f_l + f_l)):
                        is_flfl_in_pos = True
                if (not is_flfl_in_pos) and (str(f_l + f_l) not in all_negative_examples):
                    flag = True
        # return None, all_acts
        # Todo: check about it
        # We for sure knows who is not with one another (two actions that are from different states)

        if not flag:
            # then we know how to separate the states
            # makesure: that it can't be "triked", if it relay means we can separate all actions to states...
            states = dict()
            state_count = 1
            used_acts = set()
            # print("all acts ", all_acts)
            for act in all_acts:
                set_intersect = set(can_be[act])
                if len(set_intersect) == 0:
                    # print(f"look at {set_intersect} for act {act}")
                    continue
                if set_intersect in states.values():
                    continue
                states[state_count] = set_intersect
                state_count += 1
                used_acts.union(set_intersect)
            states = remove_duplicates(states)
            return states, all_acts, all_first_letters
        else:
            return None, all_acts, all_first_letters

    def learn(self):
        if self.solution['failed_converged']:
            return
        ''' 
        Modify negative examples in the Sample so that they will appears only once for greatest value processes numbers 
        '''
        """
        current_seq_learn_pos : a dict of prefixes and next letters...
                feasible words for counter processes, i.e. smaller equal to this. 
                (i.e. by the given sample this is the minimal number for which this is feasible)
        current_learn_pos : a list of feasible words for this exact number of processes
        current_geq_learn_neg: a list of infeasible for counter processes or more
        current_learn_neg : a list of infeasible words for exactly this number 
                (i.e. by the given sample this is the maximal number for which this is infeasible)
        """
        current_seq_learn_pos, current_learn_pos, current_geq_learn_neg, current_learn_neg = learn_from_characteristic_set(
            self.modified_full_cs, 1)
        # print("current_seq_learn_pos:", current_seq_learn_pos)
        # print("current_learn_pos:", current_learn_pos)
        all_first_letters = [pos_w[0] for c in self.characteristic_set for pos_w in self.characteristic_set[c]]
        all_first_letters = list(set(all_first_letters))
        if self.characteristic_set.get(1) is None:
            if all_first_letters:  # not an empty list, there are some positive examples in the sample
                self.characteristic_set[1] = all_first_letters
            else:
                """
                That means we have no positive examples so no element was chosen here,
                in that case a BP of the empty language is O.K.
                For us, it would be an initial state with act not seen in the negative examples as a self-loop and
                another not reachable state with all other actions as self loop """
                list_neg_letters = list(set(get_unique_letters(current_geq_learn_neg)))
                not_seen_act = list(set(alphabet) - set(list_neg_letters))[0]
                all_acts_list = list_neg_letters + [not_seen_act]
                print("all_acts_list ", all_acts_list)
                self.bp = Bp.BP_class(2, {0: {not_seen_act: 0}, 1: {neg_el: 1 for neg_el in list_neg_letters}}, 0,
                                      {0: {a_el: 0 for a_el in all_acts_list}, 1: {a_el: 1 for a_el in all_acts_list}})
                self.clean_option_holders()
                self.deal_with_possibilities()
                return
        # print(f"the bp2 {self.bp}")
        states, all_acts, all_first_letters = self.a_and_b_are_separated_constraints()
        # print("current_seq_learn_pos:", current_seq_learn_pos)
        # print("states:", states)
        for curr_word in current_learn_pos:
            for i in range(len(curr_word) - 1):
                self.fsend_behaviours_by_acts.append((curr_word[i], curr_word[i + 1]))
        self.reset_states_by_feasible_in_one(current_learn_pos, current_seq_learn_pos, states)
        self.fsend_behaviours_by_acts = list(set(self.fsend_behaviours_by_acts))
        # print(f"the bp3 {self.bp}")
        # print("fsend_behaviours_by_acts: ", self.fsend_behaviours_by_acts)
        negative_acts_len_1 = filter_strings_by_length(current_geq_learn_neg, 1)
        self.add_neg_actions_to_smt(current_geq_learn_neg)
        self.add_actions_to_smt(current_seq_learn_pos)
        for init_act in all_first_letters:
            self.smt_constraint_copy.append(fst(self.actions_smt[init_act]) == self.states_smt[self.bp.initial_state])
            for not_init_act in negative_acts_len_1:
                # print(f"init_act: {init_act} and not_init_act {not_init_act}")
                self.not_in_same_state.append((init_act, not_init_act))
                self.smt_constraint_copy.append(
                    fst(self.actions_smt[not_init_act]) != self.states_smt[self.bp.initial_state])
        self.not_in_same_state = list(set(self.not_in_same_state))

        all_positive_acts = get_positive_alphabet(self.modified_full_cs['positive'])

        if all_positive_acts != all_acts and (states is None):
            # print(f"all acts:{set(all_acts)}\n all_positive_acts{set(all_positive_acts)}")
            for a_1 in list(set(all_acts) - set(
                    all_positive_acts)):  # note: updated... (the list was in the self.create , where now is a_1)
                self.create_new_state_for_new_action(a_1)
                self.bp.update_self_loops(self.bp.receivers)
        elif all_positive_acts != all_acts:
            # print(f"all acts:{set(all_acts)}\n all_positive_acts{set(all_positive_acts)}")
            self.create_new_state_for_new_action(list(set(all_acts) - set(all_positive_acts)))
            self.bp.update_self_loops(self.bp.receivers)

        self.bp.update_self_loops(self.bp.receivers)
        # print(f"the bp4 {self.bp}")
        self.first_round2(current_seq_learn_pos, current_learn_neg)
        print(f"this is the BP:\nacts:{self.bp.actions}\nrec:{self.bp.receivers}")
        # print(f"option holder : {self.options_holder}")
        print(f"SMT values constrains")
        # self.missing_words_2() # currently not needed, using SMT for the options
        pass

    def first_round2(self, current_learn_pos, current_learn_neg):
        list_pos = list(self.modified_full_cs['positive'].keys())
        if not list_pos:  # list_pos == []
            list_pos = 0
        else:
            list_pos = max(list_pos)

        list_neg = list(self.modified_full_cs['negative'].keys())
        if not list_neg:  # list_neg == []
            list_neg = 0
        else:
            list_neg = max(list_neg)
        limit_run_procs = max(list_pos,
                              list_neg)
        for counter in range(1, limit_run_procs + 1):
            if counter == 1:
                # Then we already took care about the current_learn_pos, we also took care about current_learn_neg
                # for 1 action words, which are not enabled from the initial state.
                for w_neg in current_learn_neg:
                    ''' word is infeasible for 1 proc '''
                    # there is an *and* between word[:prefix_len] is feasible and word[prefix_len] is infeasible
                    # after words and for all options, there is an *or* NOTE: I'm here! -> 23-12-23 14:32
                    total_neg_constraints = self.negative_sample_constraint_builder(counter, w_neg)
                    if total_neg_constraints:
                        self.smt_constraint_copy.append(Or(*total_neg_constraints))
                continue
            plus_one_seq_learn_pos, plus_one_learn_pos, plus_one_geq_learn_neg, plus_one_learn_neg = learn_from_characteristic_set(
                self.modified_full_cs,
                counter)
            # to this amount of processes
            self.add_actions_to_smt(plus_one_seq_learn_pos)
            for prefix in plus_one_seq_learn_pos:
                curr_prefix = ''
                if current_learn_pos.get(prefix) is not None:
                    curr_prefix = current_learn_pos.get(prefix)
                plus_prefix = ''
                if plus_one_seq_learn_pos.get(prefix) is not None:
                    plus_prefix = plus_one_seq_learn_pos.get(prefix)

                if plus_prefix == curr_prefix == '':
                    continue

                new_acts = list(
                    filter(lambda x: self.bp.get_state_index_by_action(x) == -1, plus_prefix))
                if new_acts:  # if isn't an empty list
                    # for new_a in new_acts:
                    #     self.create_new_state_for_new_action([new_a])
                    #     self.bp.update_self_loops(self.bp.receivers)
                    # makesure about note below
                    ''' 
                    if it is a CS:
                    then, adding a single processes enabled some set of actions, 
                    hence they are all from the same new state
                    
                    if it is not a CS, this might be from different states,
                    so we need to create new states for each action, and make sure that so far, 
                    they don't contradict each other,
                    later on, they might be joined together if same values given by the SMT
                    
                    But we start by assuming it is a CS, so we add them together. if the SMT fails, then we assume not 
                    a CS and rebuild it'''
                    self.create_new_state_for_new_action(new_acts)
                    self.bp.update_self_loops(self.bp.receivers)

            # print(f"plus_one_learn_pos: for counter :{counter}:", plus_one_learn_pos)
            for w_neg in plus_one_learn_pos:
                tot_constraint_pos = []
                constraints_init, procs_holder = self.init_procs_holders_for_prefix(counter, w_neg)
                if constraints_init:
                    tot_constraint_pos.append(And(*constraints_init))

                # constraints = []
                for index in range(len(w_neg)):
                    someone_is_there = self.constraint_proc_in_act_state(index, w_neg, procs_holder)
                    if someone_is_there:
                        tot_constraint_pos.append(Or(*someone_is_there))
                    total_holder = self.rest_of_procs_constraint(index, w_neg, procs_holder)
                    if total_holder:
                        tot_constraint_pos.append(Or(*total_holder))

                neg_const = []

                for k in range(len(w_neg) + 1):
                    neg_plus = []
                    # print(f"word  in iter {k} is {word[:k]}")
                    # print(f"plus_one_geq_learn_neg: for counter :{counter}:", plus_one_geq_learn_neg)
                    for w in plus_one_geq_learn_neg:
                        if len(w) == len(w_neg[:k]) + 1 and w.startswith(w_neg[:k]):
                            # print(f"pos word is {word} and neg word is {w} for counter {counter}")
                            neg_plus.append(w[-1])
                    if neg_plus:
                        for b in neg_plus:
                            for p in procs_holder:
                                neg_const.append(p[k] != fst(self.actions_smt[b]))
                        tot_constraint_pos.append(And(*neg_const))
                self.smt_constraint_copy.append(And(*tot_constraint_pos))

            # print(f"plus_one_learn_neg: for counter :{counter}:", plus_one_learn_neg)
            for w_neg in plus_one_learn_neg:
                ''' word is infeasible for counter proc '''
                # there is an *and* between word[:prefix_len] is feasible and word[prefix_len] is infeasible after words
                # and for all options, there is an *or*
                total_neg_constraints = self.negative_sample_constraint_builder(counter, w_neg)
                if total_neg_constraints:
                    self.smt_constraint_copy.append(Or(*total_neg_constraints))

            current_learn_pos = plus_one_seq_learn_pos
        self.clean_option_holders()
        self.deal_with_possibilities()
        return

    def negative_sample_constraint_builder(self, counter, w_neg):
        total_neg_constraints = []
        procs_holder = []
        for i in range(counter):
            procs_holder.append([])
            procs_holder[i] = dict()
            for a in range(len(w_neg) + 1):
                procs_holder[i][a] = Int(f'{w_neg}_{str(counter)}_{i}_{a}')
                self.constraints_total_for_procs.append(procs_holder[i][a])
        for prefix_len in range(len(w_neg)):
            # -1 because even for the last option after reading word[:-1] then word[-1] is infeasible..
            # and in case len(word)==1 we already took care of it
            curr_constraint = []
            if prefix_len == 0:
                ''' make sure that the #counter processes starts in the initial state '''
                # for i in range(counter): #note: the line below was in the for
                curr_constraint.append(
                    fst(self.actions_smt[w_neg[prefix_len]]) != self.states_smt[self.bp.initial_state])
                # curr_constraint.append(
                #     procs_holder[i][0] != self.states_smt[self.bp.initial_state])
            # for k in range(1, len(word)):
            #     curr_constraint.append(
            #         procs_holder[0][0] == Int(f'{word[:k]}_{str(counter)}_{0}_{0}'))  # note - newly added
            #     self.constraints_total_for_procs.append(Int(f'{word[:k]}_{str(counter)}_{0}_{0}'))
            else:
                # there is a non-empty prefix of word that is feasible that after words is infeasible

                ''' make sure that the #counter processes starts in the initial state '''
                for i in range(counter):
                    curr_constraint.append(
                        procs_holder[i][0] == self.states_smt[self.bp.initial_state])
                curr_constraint.append(
                    procs_holder[0][0] == fst(self.actions_smt[w_neg[0]]))  # note - newly added,
                # if the initial one is in the right state then the rest of procs in the beginning are in the tight state
                for k in range(1, len(w_neg)):
                    curr_constraint.append(
                        procs_holder[0][0] == Int(f'{w_neg[:k]}_{str(counter)}_{0}_{0}'))  # note - newly added
                    self.constraints_total_for_procs.append(Int(f'{w_neg[:k]}_{str(counter)}_{0}_{0}'))
                for index in range(prefix_len):
                    someone_is_there = self.constraint_proc_in_act_state(index, w_neg, procs_holder)
                    curr_constraint.append(Or(*someone_is_there))
                    total_holder = self.rest_of_procs_constraint(index, w_neg, procs_holder)
                    curr_constraint.append(Or(*total_holder))
                temp_holder = []
                for i in range(counter):
                    # print(f"the word is {word} and prefix_len is {prefix_len}")
                    # print("word[prefix_len]", word[prefix_len])
                    temp_holder.append(
                        procs_holder[i][prefix_len] != fst(self.actions_smt[w_neg[prefix_len]]))
                if temp_holder:
                    curr_constraint.append(And(*temp_holder))
            # print(f"curr_constraint counter:{counter}, word{word}, prefix_len{prefix_len}:", curr_constraint)
            if curr_constraint:
                total_neg_constraints.append(And(*curr_constraint))
        return total_neg_constraints

    def rest_of_procs_constraint(self, index, prefix, procs_holder):
        """
        given that one processes was in the state where prefix[index] enables from,
        the rest of processes should respond accordingly.
        so each element is total holder is an option for a proc to act and the rest to respond accordingly
        :param index:
        :param prefix:
        :param procs_holder:
        :return:
        """
        total_holder = []
        for p in procs_holder:
            rest_of_procs_const = [p[index] == fst(self.actions_smt[prefix[index]]),
                                   p[index + 1] == fsend(self.actions_smt[prefix[index]])]
            for p1 in procs_holder:
                if p != p1:
                    rest_of_procs_const.append(
                        p1[index + 1] == frec(self.actions_smt[prefix[index]], p1[index]))
            total_holder.append(And(*rest_of_procs_const))
        return total_holder

    def constraint_proc_in_act_state(self, index, prefix, procs_holder):
        """
        making sure that there is a processes in the state where prefix[index] is enabled from
        :param index:
        :param prefix:
        :param procs_holder:
        :return: the list of constraint that ensure it
        """
        someone_is_there = []
        # print(f"11:: the index: {index} and the word len is {len(prefix)}")
        for p in procs_holder:
            someone_is_there.append(p[index] == fst(self.actions_smt[prefix[index]]))
        return someone_is_there

    def init_procs_holders_for_prefix(self, counter, prefix):
        """
        given a prefix, initiate counter x (len(prefix) +1) processes
        :param counter:
        :param prefix:
        :return:
        """
        procs_holder = []
        ''' make sure that the #counter processes starts in the initial state '''
        constraints_init = []
        for i in range(counter):
            procs_holder.append([])
            procs_holder[i] = dict()
            for a in range(len(prefix) + 1):
                procs_holder[i][a] = Int(f'{prefix}_{str(counter)}_{i}_{a}')
                if a == 0:
                    constraints_init.append(procs_holder[i][a] == self.states_smt[self.bp.initial_state])
                self.constraints_total_for_procs.append(procs_holder[i][a])
        constraints_init.append(procs_holder[0][0] == fst(self.actions_smt[prefix[0]]))
        for k in range(1, len(prefix)):
            constraints_init.append(
                procs_holder[0][0] == Int(f'{prefix[:k]}_{str(counter)}_{0}_{0}'))  # note - newly added
            self.constraints_total_for_procs.append(Int(f'{prefix[:k]}_{str(counter)}_{0}_{0}'))
        return constraints_init, procs_holder

    def create_new_state_for_new_action(self, act_indexes: []):
        """
        for each of the new action that is feasible from teh new state,
        create a new state that all the actions are from there
        :param act_indexes: array of all actions that are feasible from the new unknown state
        :return:
        """

        for act in act_indexes:
            if act not in self.known_actions:
                # print(f"known create {act}")
                self.known_actions.append(act)
                self.actions_smt[act] = Int(f'{act}')
        new_state_index = max(self.bp.actions) + 1
        if new_state_index not in self.known_states:  # note - newly added, was without the if, always the inside of if happend
            self.known_states.append(new_state_index)
            self.states_smt[new_state_index] = Int(str(new_state_index))
        self.bp.actions[new_state_index] = {act_index: -1 for act_index in act_indexes}
        for act in act_indexes:
            self.fst_behaviours.append((self.actions_smt[act], self.states_smt[new_state_index]))
        self.bp.actions[-1] = {}  # sink state
        pass

    def clean_option_holders(self):
        filtered_dict = {
            key: {inner_key: inner_value for inner_key, inner_value in nested_dict.items() if inner_value}
            for key, nested_dict in self.options_holder.items()
            if any(nested_dict.values())
        }
        self.options_holder = filtered_dict

    # ------------------------------------- SCENARIOS --------------------------------------
    def deal_with_possibilities(self):
        """
        for each counter of procs, deal with the given possibilities
        all problematic characteristic word for a given counter -> solve them
        {str: [[(int:from_state, int: land_state)]]} == prefix, where prefix[-1] is the action,
        list of 'must for a given option' each sub-list is a permutation of actions/receivers that must be taken,
       and sometimes there is a sub-sub-list that describe the 'free' options, this that need to join on eof the
       existing options.
        """
        print(f"CURR SITUATION: ")
        # print(f"actions: {self.bp.actions},\n rec: {self.bp.receivers}")
        print(f"OPTION HOLDER---- {self.options_holder}")
        print(f"smt actions ---- {self.actions_smt}")
        print(f"smt states ---- {self.states_smt}")
        print("self bp actions ", self.bp.actions)
        print("self bp receivers ", self.bp.receivers)
        constraints1 = []
        self.not_in_same_state = list(set(self.not_in_same_state))
        for (a1, a2) in self.not_in_same_state:
            self.smt_constraint_copy.append(fst(self.actions_smt[a1]) != fst(self.actions_smt[a2]))

        self.fsend_behaviours = list(set(self.fsend_behaviours))
        # print("fsend behavior ", self.fsend_behaviours)
        for (a, b) in self.fsend_behaviours:
            self.smt_constraint_copy.append(fsend(self.actions_smt[a]) == self.states_smt[b])
        # print("fsend_behaviours_by_acts ", self.fsend_behaviours_by_acts)
        for (a, b) in self.fsend_behaviours_by_acts:
            self.smt_constraint_copy.append(fsend(self.actions_smt[a]) == fst(self.actions_smt[b]))

        self.fst_behaviours = list(set(self.fst_behaviours))
        # print("self.fst_behaviours ", self.fst_behaviours)
        for (a, b) in self.fst_behaviours:
            self.smt_constraint_copy.append(fst(a) == b)

        # print("self.known_states: ", self.known_states)
        SMT2 = Solver()
        SMT2.set(unsat_core=True)
        SMT2.add(And(*self.smt_constraint_copy))
        self.basic_const_smt(constraints1)
        SMT2.add(And(*constraints1))
        self.proc_const_smt(SMT2)
        print("statistics for the last check method...")
        print("CONST1")
        # with open("constraints_output.txt", "w") as file:
        #     for constraint in SMT2.assertions():
        #         file.write(str(constraint.sexpr()) + "\n")
        # for constraint in SMT2.assertions():
        #     print(constraint)
        print("checking sat")
        # SMT2.add(fsend(self.actions_smt['b'])==fst(self.actions_smt['a']))
        begin_time = time.perf_counter()
        if SMT2.check() == unsat:
            end_time = time.perf_counter()
            self.solution['solve_SMT_time'] = end_time - begin_time
            smt_core_val = SMT2.unsat_core()
            print(len(smt_core_val))
            for state in self.states_smt:
                print(f" state{state} {self.states_smt[state] in smt_core_val}")
            print("NO SMT SOLUTION")

            all_acts_list = list(set(list(get_positive_alphabet(self.modified_full_cs['positive'])) +
                                     list(get_positive_alphabet(self.modified_full_cs['negative']))))
            i = 0
            while i < self.cutoff:
                i += 1
                not_seen_act = list(set(alphabet) - set(all_acts_list))[0]
                # print("not_seen_act:", not_seen_act)
                all_acts_list = all_acts_list + [not_seen_act]
                self.create_new_state_for_new_action(not_seen_act)
                self.bp.update_self_loops(self.bp.receivers)

                print(f"the bp: {self.bp}")

                SMT3 = Solver()
                SMT3.set(unsat_core=True)
                SMT3.add(And(*self.smt_constraint_copy))
                self.basic_const_smt(constraints1)
                SMT3.add(And(*constraints1))
                self.proc_const_smt(SMT3)
                # SMT2.add(fst(self.actions_smt['e']) == fst(self.actions_smt['f']))
                print("statistics for the last check method...")
                print(f"CONST {i}")
                # with open(f"constraints_output{i}.txt", "w") as file:
                #     for constraint in SMT3.assertions():
                #         file.write(str(constraint.sexpr()) + "\n")
                # for constraint in SMT2.assertions():
                #     print(constraint)
                copied_actions = copy.deepcopy(self.bp.actions)
                copied_receivers = copy.deepcopy(self.bp.receivers)
                self.ret_origin_self_bp = Bp.BP_class(len(copied_actions), copied_actions, self.bp.initial_state,
                                                      copied_receivers)
                print("checking sat")
                begin_time = time.perf_counter()
                if SMT3.check() == unsat:
                    end_time = time.perf_counter()
                    self.solution['solve_SMT_time'] = end_time - begin_time
                    print("NO SMT SOLUTION ", i)
                    continue
                else:
                    end_time = time.perf_counter()
                    self.solution['solve_SMT_time'] = end_time - begin_time
                    print("FINE")

                    print("Current constraints:")
                    print("states:::")
                    print("self known actions ", self.known_actions)
                    print("self known states ", self.known_states)
                    model = SMT3.model()

                    states_translation_smt = dict()
                    if model != []:
                        self.states_and_actions_translation_smt(get_key_by_value, model, states_translation_smt)
                    states_values = list(set(states_translation_smt.values()))
                    print("states_values: ", states_values)
                    print(f"before bp: acts:{self.bp.actions}, res: {self.bp.receivers}")
                    self.dill_with_duplicated_smt_values(states_translation_smt, states_values)
                    print(f"after bp: acts:{self.bp.actions}, res: {self.bp.receivers}")

                    self.solution['output_BP'] = f'states: {len(set(self.bp.actions))},\nactions: {self.bp.actions},\n' \
                                                 f'initial: {self.bp.initial_state},\n' \
                                                 f'receivers: {clean_receivers(self.bp.receivers)}'
                    self.solution['amount_of_states_in_output'] = len(set(self.bp.actions) - {-1})
                    i = self.cutoff
            pass

        else:
            end_time = time.perf_counter()
            self.solution['solve_SMT_time'] = end_time - begin_time
            print("FINE")

            print("Current constraints:")
            print("states:::")
            print("self known actions ", self.known_actions)
            print("self known states ", self.known_states)
            model = SMT2.model()

            states_translation_smt = dict()
            if model != []:
                self.states_and_actions_translation_smt(get_key_by_value, model, states_translation_smt)

            # in case there are duplicated values in states_translation_smt, that means that states can be merged

            copied_actions = copy.deepcopy(self.bp.actions)
            copied_receivers = copy.deepcopy(self.bp.receivers)
            duplicated_self_bp = Bp.BP_class(len(copied_actions), copied_actions, 0, copied_receivers)
            print(f"duplicated_self_bp {duplicated_self_bp}")
            states_values = list(set(states_translation_smt.values()))
            print("states_values: ", states_values)
            print("states_translation_smt: ", states_translation_smt)
            print(f"before bp: acts:{self.bp.actions}, res: {self.bp.receivers}")
            self.dill_with_duplicated_smt_values(states_translation_smt, states_values)
            print(f"after bp: acts:{self.bp.actions}, res: {self.bp.receivers}")

            self.solution['output_BP'] = f'states: {len(set(self.bp.actions))},\nactions: {self.bp.actions},\n' \
                                         f'initial: {self.bp.initial_state},\n' \
                                         f'receivers: {clean_receivers(self.bp.receivers)}'
            self.solution['amount_of_states_in_output'] = len(set(self.bp.actions) - {-1})

            copied_actions = copy.deepcopy(self.bp.actions)
            copied_receivers = copy.deepcopy(self.bp.receivers)
            self.ret_origin_self_bp = Bp.BP_class(len(copied_actions), copied_actions, self.bp.initial_state,
                                                  copied_receivers)
            print(f"ret_origin_self_bp {self.ret_origin_self_bp}")
            """'amount_of_states_in_minimal_output': 0,
                         'minimal_output_BP': '',
                         'minimal_solve_SMT_time': 0.0"""

            if len(self.bp.actions) == 2:  # already minimal..
                self.solution[
                    'minimal_output_BP'] = f'states: {len(set(self.bp.actions))},\nactions: {self.bp.actions},\n' \
                                           f'initial: {self.bp.initial_state},\n' \
                                           f'receivers: {clean_receivers(self.bp.receivers)}'
                self.solution['amount_of_states_in_minimal_output'] = len(set(self.bp.actions) - {-1})
                self.solution['minimal_solve_SMT_time'] = 0
            else:
                begin_time = time.perf_counter()
                print("self.known_states: ", self.known_states)
                print("self.states_smt: ", self.states_smt.values())
                print("self.states_smt: ", list(self.states_smt.values()))
                model = self.minimal_distinct_values(begin_time, 1, list(self.states_smt.values()),
                                                     And(*self.smt_constraint_copy))

                states_translation_smt = dict()
                self.bp = duplicated_self_bp
                if model != []:
                    self.states_and_actions_translation_smt(get_key_by_value, model, states_translation_smt)

                # in case there are duplicated values in states_translation_smt, that means that states can be merged

                states_values = list(set(states_translation_smt.values()))
                print("states_values minimal: ", states_values)
                print(f"before bp minimal: acts:{self.bp.actions}, res: {self.bp.receivers}")
                self.dill_with_duplicated_smt_values(states_translation_smt, states_values)
                print(f"after bp minimal : acts:{self.bp.actions}, res: {self.bp.receivers}")

                self.solution[
                    'minimal_output_BP'] = f'states: {len(set(self.bp.actions))},\nactions: {self.bp.actions},\n' \
                                           f'initial: {self.bp.initial_state},\n' \
                                           f'receivers: {clean_receivers(self.bp.receivers)}'
                self.solution['amount_of_states_in_minimal_output'] = len(set(self.bp.actions) - {-1})

        # _, _, self.solution['right_output'] = equivalent_bp(self.real_bp, self.bp, False)
        pass

    def dill_with_duplicated_smt_values(self, states_translation_smt, states_values):
        """
        in case there are duplicated values in states_translation_smt, that means that states can be merged
        :param states_translation_smt:
        :param states_values:
        :return:
        """
        print("states_translation_smt:", states_translation_smt)
        print("states_values:", states_values)
        for sv in states_values:
            keys = get_keys_by_value(states_translation_smt, sv)
            if len(keys) == 1:
                continue
            else:
                print("set(keys):", set(keys))
                print("min(keys):", min(keys))
                duplicated_keys = list(set(keys) - {min(keys)})
                for k in duplicated_keys:
                    if k in self.bp.actions:
                        del self.bp.actions[k]
                    if k in self.bp.receivers:
                        del self.bp.receivers[k]
                for o_s in self.bp.actions:
                    for act_s in self.bp.actions[o_s]:
                        if self.bp.actions[o_s][act_s] in duplicated_keys:
                            self.bp.actions[o_s][act_s] = min(keys)
                for o_s in self.bp.receivers:
                    for act_s in self.bp.receivers[o_s]:
                        if self.bp.receivers[o_s][act_s] in duplicated_keys:
                            self.bp.receivers[o_s][act_s] = min(keys)

    def states_and_actions_translation_smt(self, get_key_by_value, model, states_translation_smt):
        self.known_states = list(set(self.known_states))
        for state in self.known_states:
            print(
                f"state: {state} int(model[self.states_smt[state]].as_long()): {int(model[self.states_smt[state]].as_long())}")
            states_translation_smt[state] = int(model[self.states_smt[state]].as_long())
        print("states_translation_smt:: ", states_translation_smt)
        action_translation_smt = dict()
        for action in self.known_actions:
            action_translation_smt[action] = model[self.actions_smt[action]].as_long()
            print(f"look at: action {action}: {model[self.actions_smt[action]].as_long()}")
        new_bp = BP_class(len(list(states_translation_smt.values())), dict(), self.bp.initial_state, dict())
        for act in self.known_actions:
            print(f"234:: act {act} in known actions {self.known_actions}")
            self.bp.update_action(
                get_key_by_value(states_translation_smt, model.eval(fst(self.actions_smt[act])).as_long()),
                act, get_key_by_value(states_translation_smt, model.evaluate(fsend(self.actions_smt[act])).as_long()))
            # new_bp.update_self_loops(new_bp.receivers)
            new_bp.update_action(
                get_key_by_value(states_translation_smt, model.eval(fst(self.actions_smt[act])).as_long()),
                act, get_key_by_value(states_translation_smt, model.evaluate(fsend(self.actions_smt[act])).as_long()))
            new_bp.update_self_loops(new_bp.receivers)
            print(
                f"23:: for act {act} from state {get_key_by_value(states_translation_smt, model.eval(fst(self.actions_smt[act])).as_long())}, landing is {get_key_by_value(states_translation_smt, model.evaluate(fsend(self.actions_smt[act])).as_long())}")
        for act in self.known_actions:
            for state in self.known_states:
                print(f"state {state}, and act:{act} receivers:")
                self.bp.update_receivers(
                    state, act, get_key_by_value(states_translation_smt,
                                                 model.eval(
                                                     frec(self.actions_smt[act], self.states_smt[state])).as_long()),
                    True)
                new_bp.update_receivers(
                    state, act, get_key_by_value(states_translation_smt,
                                                 model.eval(
                                                     frec(self.actions_smt[act], self.states_smt[state])).as_long()),
                    True)

        print("self bp: before new_bp\n", self.bp)
        print("new_bp: ", new_bp)
        self.bp.actions = new_bp.actions
        self.bp.receivers = new_bp.receivers
        self.bp.initial_state = new_bp.initial_state

    def proc_const_smt(self, sol):
        for p in self.constraints_total_for_procs:
            or_p = []
            for s in self.known_states:
                or_p.append(self.states_smt[s] == p)
            sol.add(Or(*or_p))

    def basic_const_smt(self, constraints1):
        for act in self.known_actions:
            or_list_fst = []
            or_list_fsend = []
            for state in self.known_states:
                or_list_fst.append(fst(self.actions_smt[act]) == self.states_smt[state])
                or_list_fsend.append(fsend(self.actions_smt[act]) == self.states_smt[state])
                sub_or_list = []
                for sub_state in self.known_states:
                    sub_or_list.append(
                        frec(self.actions_smt[act], self.states_smt[state]) == self.states_smt[sub_state])
                constraints1.append(Or(*sub_or_list))
            constraints1.append(Or(*or_list_fst))
            constraints1.append(Or(*or_list_fsend))

    def add_actions_to_smt(self, plus_one_learn):
        actions = set(''.join(list(plus_one_learn.values())))  # all the actions in those words
        actions2 = set(''.join(list(plus_one_learn.keys())))

        union_result = actions.union(actions2)
        # print(f"actions44 {actions}")
        for act in union_result:
            if act in self.known_actions:
                continue
            else:
                # print(f"known a {act}")
                self.known_actions.append(act)
                self.actions_smt[act] = Int(str(act))
        pass

    def add_neg_actions_to_smt(self, plus_one_learn_neg):
        """
        need to be called only once for 1 proc because every thing for higher number of processes is already subsumed
        :param plus_one_learn_neg: is a list
        :return:
        """
        actions = set()  # all the actions in those words
        for s in plus_one_learn_neg:
            actions.update(set(s))
        # print(f"actions54 {actions}")
        for act in actions:
            if act in self.known_actions:
                continue
            else:
                self.known_actions.append(act)
                self.actions_smt[act] = Int(str(act))
        pass

    def modify_cs(self, full_cs):
        """ given the full cs, modify the negative examples, so they will appear only once for greatest number of
        processes they are at """
        filtered_dict = {}
        filtered_dict1 = dict()
        filtered_dict2 = dict()

        for key in sorted(full_cs['positive'].keys()):
            current_value = full_cs['positive'][key]
            filtered_value = [string for string in current_value if all(
                string not in lower_value for lower_key, lower_value in filtered_dict2.items() if lower_key < key)]

            if filtered_value:
                filtered_dict2[key] = filtered_value

        filtered_dict1['positive'] = filtered_dict2
        for key, value in sorted(full_cs['negative'].items(), reverse=True):
            # Filter out strings that appear in lists of higher keys
            filtered_strings = [string for string in value if all(
                string not in higher_value for higher_key, higher_value in filtered_dict.items())]

            if filtered_strings:
                filtered_dict[key] = filtered_strings

        filtered_dict1['negative'] = filtered_dict
        self.modified_full_cs = filtered_dict1
        self.characteristic_set = filtered_dict2
        self.negative_cs = filtered_dict
        pass

    def minimal_distinct_values(self, begin_time, n, states, curr_const):
        """
        make sure that the states are at most n values, if not increase until succeeded
        :param begin_time:
        :param curr_const:
        :param n:
        :param states:
        :return:
        """
        print("n:: ", n)
        new_values = [Int(f"new_{i}") for i in range(n)]
        # Create a Z3 solver
        solver = Solver()
        solver.set(unsat_core=True)

        # Add the Distinct constraint to ensure new values are distinct
        solver.add(Distinct(new_values))
        solver.add(curr_const)
        constraints1 = []
        self.basic_const_smt(constraints1)
        solver.add(And(*constraints1))
        self.proc_const_smt(solver)

        # Add constraints to ensure each existing value is equal to at least one new value
        for existing_value in states:
            solver.add(Or(*[existing_value == new_value for new_value in new_values]))

        # with open(f"constraints_output22_{n}.txt", "w") as file:
        #    for constraint in solver.assertions():
        #        file.write(str(constraint.sexpr()) + "\n")

        # Check for satisfiability
        if solver.check() == unsat:
            return self.minimal_distinct_values(begin_time, n + 1, states, curr_const)
        else:
            end_time = time.perf_counter()
            self.solution['minimal_solve_SMT_time'] = end_time - begin_time
            model = solver.model()
            return model
        pass

    def reset_states_by_feasible_in_one(self, current_learn_pos, current_seq_learn_pos, states):
        """
        :param current_learn_pos: all feasible words in a single processes
        :param current_seq_learn_pos: {prefix to the action : actions that are feasible}
        :param states: division of states if exists
        :return:
        """
        sorted_dict = dict(sorted(current_seq_learn_pos.items(), key=lambda x: (len(x[0]), x[0])))

        # print("current_seq_learn_pos: ", sorted_dict)
        action_builder = dict()
        act_to_state = dict()
        known_actions = set()
        state_index = 1
        for pref in sorted_dict:
            if pref == '':
                # print("action_builder: ", action_builder)
                action_builder[self.bp.initial_state] = dict((x, -1) for x in sorted_dict.get(pref))  # make sure
                # print("action_builder: ", action_builder)
                for x in sorted_dict.get(pref):
                    known_actions.add(x)
                    act_to_state[x] = self.bp.initial_state
                # print("act_to_state: ", act_to_state)
            else:
                '''We have only a single processes, then if a single actions is known then the rest of actions are 
                too going there '''
                is_known, act = has_common_letter(sorted_dict.get(pref), known_actions)
                if is_known:
                    # print("action_builder: before: ", action_builder)
                    if action_builder.get(act_to_state[pref[-1]]) is None:
                        action_builder[act_to_state[pref[-1]]] = dict([(pref[-1], act_to_state[act])])
                        for x in sorted_dict.get(pref):
                            known_actions.add(x)
                            act_to_state[x] = act_to_state[act]
                    else:
                        was_it_define = action_builder[act_to_state[pref[-1]]].get(pref[-1]) is not None
                        if was_it_define and (action_builder[act_to_state[pref[-1]]][pref[-1]] != -1):
                            '''
                            Then this action already knows where it goes, we only need to update the new action origin
                            '''
                            for x in sorted_dict.get(pref):
                                known_actions.add(x)
                                act_to_state[x] = action_builder[act_to_state[pref[-1]]][pref[-1]]
                        else:
                            action_builder[act_to_state[pref[-1]]][pref[-1]] = act_to_state[act]
                            for x in sorted_dict.get(pref):
                                known_actions.add(x)
                                act_to_state[x] = act_to_state[act]
                    # print("action_builder: after: ", action_builder)
                    # for x in sorted_dict.get(pref):
                    #     known_actions.add(x)
                    #     act_to_state[x] = act_to_state[pref[-1]]
                    # print("act_to_state: ", act_to_state)
                else:  # not a known state
                    if action_builder.get(act_to_state[pref[-1]]) is None:
                        action_builder[act_to_state[pref[-1]]] = dict([(pref[-1], state_index)])
                        for x in sorted_dict.get(pref):
                            known_actions.add(x)
                            act_to_state[x] = state_index
                    else:
                        was_it_define = action_builder[act_to_state[pref[-1]]].get(pref[-1]) is not None
                        if was_it_define and (action_builder[act_to_state[pref[-1]]][pref[-1]] != -1):
                            '''Then this action already knows where it goes, we only need to update the new action origin'''
                            for x in sorted_dict.get(pref):
                                known_actions.add(x)
                                act_to_state[x] = action_builder[act_to_state[pref[-1]]][pref[-1]]
                        else:
                            action_builder[act_to_state[pref[-1]]][pref[-1]] = state_index
                            for x in sorted_dict.get(pref):
                                known_actions.add(x)
                                act_to_state[x] = state_index
                    # print("action_builder: ", action_builder)
                    # print("act_to_state: ", act_to_state)
                    state_index += 1
        # print("FINAL action_builder: ", action_builder)
        # print("Actions before:\n", self.bp.actions)
        for org_state in action_builder:
            self.bp.actions[org_state] = action_builder.get(org_state)
        # print("Actions after:\n", self.bp.actions)
        """ updating SAT """
        for org_state in self.bp.actions:
            if org_state not in self.known_states:
                self.known_states.append(org_state)
                self.states_smt[org_state] = Int(str(org_state))
            for act in self.bp.actions[org_state]:
                if act not in self.known_actions:
                    self.known_actions.append(act)
                    self.actions_smt[act] = Int(str(act))
                self.fst_behaviours.append((self.actions_smt[act], self.states_smt[org_state]))
                land_state = self.bp.actions[org_state][act]
                if land_state >= 0:  # not a sink state
                    if land_state not in self.known_states:
                        self.known_states.append(land_state)
                        self.states_smt[land_state] = Int(str(land_state))
                    self.fsend_behaviours.append((act, land_state))
        pass


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


import concurrent.futures
import time


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


class BP_run:
    def __init__(self, bp_1: Bp.BP_class):
        self.bp = bp_1

    def run(self):
        fifteen_min = 900
        twenty_min = 1200
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
                learn_bp.learn()
                clean_rec = clean_receivers(learn_bp.bp.receivers)
                print(f"learner actions = {learn_bp.bp.actions}\nlearner receivers = {learn_bp.bp.receivers}\n"
                      f"clean receivers: {clean_rec}")
                return learn_bp.bp.actions, clean_rec, learn_bp.solution

    def run_no_cs(self, words_to_add, words_are_given, maximal_procs=20, maximal_length=20):
        """
        if words_are_given==True then words_to_add are sample dictionary.
        otherwise, words_to_add is an int of number of words to add.
        a run that add amount of words_to_add to the cs and run it
        :param words_to_add: int if words_are_given=False, otherwise a dictionary of sample
        :param words_are_given: boolean value
        :param maximal_procs: maximal allowed length of word in the sample
        :param maximal_length:
        :return:
        """
        char_set = {'positive': {}, 'negative': {}}
        start_time = time.perf_counter()
        if not words_are_given:
            char_set, words_added = self.create_sample(words_to_add, char_set, maximal_procs, maximal_length)
        else:
            char_set = words_to_add
            words_added = words_to_add
        end_time = time.perf_counter()

        learn_bp = LearnerBp(char_set, self.bp, end_time - start_time, words_added)
        if learn_bp.solution['failed_converged']:
            return None, None, learn_bp.solution, words_added
        learn_bp.learn()
        clean_rec = clean_receivers(learn_bp.bp.receivers)
        clean_rec_non_minimal = clean_receivers(learn_bp.ret_origin_self_bp.receivers)
        print(f"learner actions = {learn_bp.bp.actions}\nlearner receivers = {learn_bp.bp.receivers}\n"
              f"clean receivers: {clean_rec}")
        print(
            f"non minimal:: learner actions = {learn_bp.ret_origin_self_bp.actions}\nlearner receivers = {learn_bp.ret_origin_self_bp.receivers}\n"
            f"clean receivers: {clean_rec_non_minimal}")
        return learn_bp.bp.actions, clean_rec, learn_bp.ret_origin_self_bp.actions, clean_rec_non_minimal, learn_bp.solution, words_added

    def run_no_cs_pos_perc(self, words_to_add, pos_perc, length_limit, procs_limit):
        """
        :param words_to_add: int amount of words to add
        :param pos_perc: positive % of total words
        :param length_limit: longest word limit
        :param procs_limit: maximal procs limit
        :return:
        """
        char_set = {'positive': {}, 'negative': {}}
        start_time = time.perf_counter()
        char_set, words_added = self.create_sample_pos_perc(words_to_add, char_set, pos_perc, length_limit, procs_limit)
        end_time = time.perf_counter()
        learn_bp = LearnerBp(char_set, self.bp, end_time - start_time, words_added)
        if learn_bp.solution['failed_converged']:
            return None, None, learn_bp.solution, words_added
        learn_bp.learn()
        clean_rec = clean_receivers(learn_bp.bp.receivers)
        clean_rec_non_minimal = clean_receivers(learn_bp.ret_origin_self_bp.receivers)
        print(f"learner actions = {learn_bp.bp.actions}\nlearner receivers = {learn_bp.bp.receivers}\n"
              f"clean receivers: {clean_rec}")
        print(
            f"non minimal:: learner actions = {learn_bp.ret_origin_self_bp.actions}\n"
            f"learner receivers = {learn_bp.ret_origin_self_bp.receivers}\n"
            f"clean receivers: {clean_rec_non_minimal}")
        return learn_bp.bp.actions, clean_rec, learn_bp.ret_origin_self_bp.actions, clean_rec_non_minimal, learn_bp.solution, words_added

    def run_cs_to_a_limit(self, cutoff_limit, sample_limit):
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
                learn_bp.learn()
                clean_rec = clean_receivers(learn_bp.bp.receivers)
                clean_rec_non_minimal = clean_receivers(learn_bp.ret_origin_self_bp.receivers)
                print(f"learner actions = {learn_bp.bp.actions}\nlearner receivers = {learn_bp.bp.receivers}\n"
                      f"clean receivers: {clean_rec}")
                print(
                    f"non minimal:: learner actions = {learn_bp.ret_origin_self_bp.actions}\n"
                    f"learner receivers = {learn_bp.ret_origin_self_bp.receivers}\n"
                    f"clean receivers: {clean_rec_non_minimal}")
                return learn_bp.bp.actions, clean_rec, learn_bp.ret_origin_self_bp.actions, clean_rec_non_minimal, learn_bp.solution

    def run_subsume_cs(self, words_to_add, are_words_given, cutoff_lim=None, time_lim=None):
        """
        a run that add amount of words_to_add to the cs and run it
        :param time_lim: If given, this is time limitation in sec
        :param cutoff_lim: If given, then cutoff limitation for running
        :param are_words_given: A boolean value representing whether we create a sample (not necessarily a CS)
        for words_to_add amount or is the words are already given to us
        :param words_to_add: Number of words if are_words_given==False or the set of words if are_words_given==True
        :return:
        """
        char_set, CS_time = {'positive': {}, 'negative': {}}, -1
        fiftheen_hours = 15 * 3600
        t = fiftheen_hours
        c = 45
        if cutoff_lim is not None:
            c = cutoff_lim
        if time_lim is not None:
            t = time_lim
        char_set, CS_time = self.bp.find_all_characteristic_sets_for_learning(c, t)
        words_added = {'positive': {}, 'negative': {}}
        cutoff = None
        if CS_time != -1:
            char_set, words_added, cutoff = self.increase_cs(words_to_add, char_set, are_words_given)
        learn_bp = LearnerBp(char_set, self.bp, CS_time, words_added, cutoff)
        if learn_bp.solution['failed_converged']:
            return None, None, None, None, learn_bp.solution
        learn_bp.learn()
        clean_rec = clean_receivers(learn_bp.bp.receivers)
        clean_rec_non_minimal = clean_receivers(learn_bp.ret_origin_self_bp.receivers)
        print(f"learner actions = {learn_bp.bp.actions}\nlearner receivers = {learn_bp.bp.receivers}\n"
              f"clean receivers: {clean_rec}")
        print(
            f"non minimal:: learner actions = {learn_bp.ret_origin_self_bp.actions}\n"
            f"learner receivers = {learn_bp.ret_origin_self_bp.receivers}\n"
            f"clean receivers: {clean_rec_non_minimal}")
        return learn_bp.bp.actions, clean_rec, learn_bp.ret_origin_self_bp.actions, clean_rec_non_minimal, learn_bp.solution

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
                    for word in size_int[pos_neg][proc]:
                        if proc not in char_set[pos_neg]:
                            char_set[pos_neg][proc] = [word]
                        else:
                            if word in char_set[pos_neg][proc]:
                                continue
                            else:
                                char_set[pos_neg][proc].append(word)
            return char_set, size_int, cutoff
        longest = ''  # the longest word in cs
        for name_val in ['positive', 'negative']:
            for procs in char_set[name_val]:
                for word in char_set[name_val][procs]:
                    if len(word) > len(longest):
                        longest = word
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
        print("self actions", self.bp.actions)
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
    min_actions, min_clean_rec, actions, clean_rec, solution = bp1.run_cs_to_a_limit(cutoff_limit, sample_limit)
    return solution


def running_no_cs_pos_percentage(bp_1: Bp.BP_class, number, words_to_add, pos_perc, length_limit, procs_limit):
    print(f"\nNew Scenario {number} :")
    bp1 = BP_run(bp_1)
    bp_actions, clean_rec, sol, _ = bp1.run_no_cs_pos_perc(words_to_add, pos_perc, length_limit, procs_limit)
    return bp_actions, clean_rec, sol


def running_no_cs(bp_1: Bp.BP_class, number, words_to_add, are_words_given):
    print(f"\nNew Scenario {number} :")
    bp1 = BP_run(bp_1)
    min_actions, clean_rec, non_min_actions, clean_rec_non_minimal, sol, words_added = bp1.run_no_cs(words_to_add,
                                                                                                     are_words_given)
    return min_actions, clean_rec, non_min_actions, clean_rec_non_minimal, sol, words_added


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


def failed_in_min_debug():
    global df
    folder_path1 = './no_cs pos_perc/1'
    folder_path2 = './no_cs pos_perc/2'
    folder_path3 = './no_cs pos_perc/3'
    folder_path5 = './no_cs pos_perc/5'
    folder_path4 = './no_cs pos_perc'
    folder_path8 = './no_cs pos_perc/8'
    folder_path10 = './no_cs pos_perc/10'
    folder_path25 = './no_cs pos_perc/25'
    folder_path32 = './no_cs pos_perc/32'
    folder_path39 = './no_cs pos_perc/39'
    folder_path45 = './no_cs pos_perc/45'
    folder_path48 = './no_cs pos_perc/48'
    folder_path52 = './no_cs pos_perc/52'
    folder_path_new = './no_cs pos_perc/after25-1'
    folder_path = './no_cs with minimal'
    # Initialize an empty DataFrame to store the selected rows
    selected_data = pd.DataFrame()
    # Iterate over each file in the folder
    for fp in [folder_path, folder_path1, folder_path2, folder_path3, folder_path4, folder_path5, folder_path8,
               folder_path10, folder_path25, folder_path32, folder_path39,
               folder_path45, folder_path48, folder_path52,
               folder_path_new]:
        for filename in os.listdir(fp):
            if filename.endswith('.csv'):
                # Read the CSV file into a DataFrame
                file_path = os.path.join(fp, filename)
                df = pd.read_csv(file_path)
                df_1 = df[df['right_output'] == True]
                df_1 = df_1[df_1['minimal_right_output'] == False]
                df_1 = df_1[df_1['CS_positive_size'] > 0]
                # df_1 = df_1[df_1['CS_positive_size'] < 35]
                df_1 = df_1[df_1['solve_SMT_time'] <= 3600]
                selected_data = pd.concat([selected_data, df_1])
    print("maxx:", max(selected_data['amount_of_states_in_minimal_output'].tolist()))
    selected_data = selected_data.drop_duplicates()
    print(f"in min version there are : {len(selected_data['solve_SMT_time'])}")
    selected_data = selected_data.drop_duplicates()
    selected_data.to_csv('failed in min.csv', index=False)


if __name__ == '__main__':

    df = pd.DataFrame(
        columns=['failed_converged', 'timeout', 'amount_of_states_in_origin',
                 'amount_of_states_in_output',
                 'origin_BP', 'output_BP', 'cutoff',
                 'CS_development_time',
                 'CS_positive_size', 'CS_negative_size', 'words_added',
                 'longest_word_in_CS', 'solve_SMT_time', 'amount_of_states_in_minimal_output',
                 'minimal_output_BP', 'minimal_solve_SMT_time', 'right_output',
                 'minimal_right_output'])  # 'right_output'

    # bp1_1 = BP_class(8, {0: {'d': 4}, 1: {'c': 7}, 2: {'b': 0}, 3: {'e': 0}, 4: {'f': 4, 'h': 6}, 5: {'g': 7},
    #                      6: {'a': 3}, 7: {'i': 0}}, 0,
    #                  {0: {'a': 3, 'b': 3, 'c': 1, 'd': 3, 'e': 7, 'f': 1, 'g': 2, 'h': 0, 'i': 0},
    #                   1: {'a': 2, 'b': 6, 'c': 7, 'd': 5, 'e': 0, 'f': 5, 'g': 6, 'h': 1, 'i': 1},
    #                   2: {'a': 7, 'b': 5, 'c': 7, 'd': 3, 'e': 4, 'f': 4, 'g': 0, 'h': 4, 'i': 2},
    #                   3: {'a': 2, 'b': 6, 'c': 3, 'd': 3, 'e': 1, 'f': 3, 'g': 5, 'h': 1, 'i': 3},
    #                   4: {'a': 4, 'b': 1, 'c': 3, 'd': 6, 'e': 3, 'f': 1, 'g': 4, 'h': 1, 'i': 4},
    #                   5: {'a': 3, 'b': 7, 'c': 2, 'd': 1, 'e': 1, 'f': 3, 'g': 3, 'h': 4, 'i': 5},
    #                   6: {'a': 4, 'b': 3, 'c': 6, 'd': 2, 'e': 2, 'f': 1, 'g': 0, 'h': 6, 'i': 6},
    #                   7: {'a': 7, 'b': 1, 'c': 5, 'd': 1, 'e': 0, 'f': 5, 'g': 6, 'h': 5, 'i': 7}})
    bp1_1 = BP_class(7, {0: {'f': 4}, 1: {'d': 4}, 2: {'h': 3}, 3: {'i': 5}, 4: {'c': 4, 'g': 2},
                         5: {'a': 6, 'b': 4, 'e': 6}, 6: {'j': 1}}, 0,
                     {0: {'a': 4, 'b': 2, 'c': 0, 'd': 2, 'e': 2, 'f': 6, 'g': 5, 'h': 0, 'i': 0, 'j': 0},
                      1: {'a': 5, 'b': 1, 'c': 2, 'd': 4, 'e': 2, 'f': 4, 'g': 1, 'h': 1, 'i': 1, 'j': 1},
                      2: {'a': 3, 'b': 0, 'c': 0, 'd': 2, 'e': 5, 'f': 4, 'g': 1, 'h': 2, 'i': 2, 'j': 2},
                      3: {'a': 3, 'b': 6, 'c': 3, 'd': 4, 'e': 5, 'f': 3, 'g': 3, 'h': 3, 'i': 3, 'j': 3},
                      4: {'a': 1, 'b': 2, 'c': 0, 'd': 1, 'e': 4, 'f': 5, 'g': 1, 'h': 4, 'i': 4, 'j': 4},
                      5: {'a': 2, 'b': 5, 'c': 1, 'd': 2, 'e': 4, 'f': 5, 'g': 4, 'h': 5, 'i': 5, 'j': 5},
                      6: {'a': 0, 'b': 0, 'c': 5, 'd': 5, 'e': 4, 'f': 0, 'g': 2, 'h': 6, 'i': 6, 'j': 6}})

    bp1_1 = BP_class(13, {0: {'d': 3, 'k': 8}, 1: {'n': 11}, 2: {'o': 6},
                          3: {'b': 1}, 4: {'p': 0}, 5: {'a': 4, 'j': 11}, 6: {'c': 6, 'i': 6}, 7: {'l': 8},
                          8: {'e': 10}, 9: {'q': 6},
                          10: {'f': 5, 'm': 11}, 11: {'r': 10}, 12: {'g': 6, 'h': 0}}, 0,
                     {0: {'a': 5, 'b': 6, 'c': 5, 'd': 1, 'e': 12, 'f': 0, 'g': 7, 'h': 8, 'i': 1, 'j': 4,
                          'k': 5, 'l': 5, 'm': 6, 'n': 0, 'o': 0, 'p': 0, 'q': 0, 'r': 0},
                      1: {'a': 1, 'b': 5, 'c': 6, 'd': 2, 'e': 1, 'f': 8, 'g': 8, 'h': 9,
                          'i': 12, 'j': 0, 'k': 5, 'l': 10, 'm': 4, 'n': 1, 'o': 1, 'p': 1, 'q': 1, 'r': 1},
                      2: {'a': 1, 'b': 7, 'c': 1, 'd': 0, 'e': 0, 'f': 3, 'g': 8, 'h': 9, 'i': 7,
                          'j': 8, 'k': 3, 'l': 2, 'm': 7, 'n': 2, 'o': 2, 'p': 2, 'q': 2, 'r': 2},
                      3: {'a': 7, 'b': 12, 'c': 4, 'd': 4, 'e': 2, 'f': 0, 'g': 3, 'h': 12, 'i': 8,
                          'j': 10, 'k': 4, 'l': 5, 'm': 4, 'n': 3, 'o': 3, 'p': 3, 'q': 3, 'r': 3},
                      4: {'a': 3, 'b': 4, 'c': 0, 'd': 10, 'e': 10, 'f': 2, 'g': 4, 'h': 4, 'i': 12,
                          'j': 0, 'k': 6, 'l': 3, 'm': 11, 'n': 4, 'o': 4, 'p': 4, 'q': 4, 'r': 4},
                      5: {'a': 0, 'b': 1, 'c': 4, 'd': 12, 'e': 5, 'f': 2, 'g': 10, 'h': 1, 'i': 0, 'j': 11, 'k': 5,
                          'l': 4, 'm': 7, 'n': 5, 'o': 5, 'p': 5, 'q': 5, 'r': 5},
                      6: {'a': 0, 'b': 3, 'c': 4, 'd': 11, 'e': 8, 'f': 8, 'g': 0, 'h': 2, 'i': 3, 'j': 12, 'k': 2,
                          'l': 4, 'm': 1, 'n': 6, 'o': 6, 'p': 6, 'q': 6, 'r': 6},
                      7: {'a': 4, 'b': 5, 'c': 7, 'd': 1, 'e': 1, 'f': 5, 'g': 2, 'h': 9, 'i': 1, 'j': 10,
                          'k': 8, 'l': 12, 'm': 9, 'n': 7, 'o': 7, 'p': 7, 'q': 7, 'r': 7},
                      8: {'a': 8, 'b': 12, 'c': 2, 'd': 12, 'e': 9, 'f': 6, 'g': 10, 'h': 12, 'i': 4, 'j': 2, 'k': 12,
                          'l': 1, 'm': 3, 'n': 8, 'o': 8, 'p': 8, 'q': 8, 'r': 8},
                      9: {'a': 9, 'b': 5, 'c': 7, 'd': 12, 'e': 8, 'f': 12, 'g': 10, 'h': 11, 'i': 7, 'j': 10, 'k': 12,
                          'l': 4, 'm': 10, 'n': 9, 'o': 9, 'p': 9, 'q': 9, 'r': 9},
                      10: {'a': 0, 'b': 12, 'c': 1, 'd': 12, 'e': 11, 'f': 12, 'g': 8, 'h': 8, 'i': 1, 'j': 11, 'k': 5,
                           'l': 9, 'm': 3, 'n': 10, 'o': 10, 'p': 10, 'q': 10, 'r': 10},
                      11: {'a': 4, 'b': 1, 'c': 9, 'd': 4, 'e': 8, 'f': 10, 'g': 12, 'h': 11, 'i': 2, 'j': 11, 'k': 0,
                           'l': 9, 'm': 2, 'n': 11, 'o': 11, 'p': 11, 'q': 11, 'r': 11},
                      12: {'a': 1, 'b': 9, 'c': 12, 'd': 9, 'e': 11, 'f': 0, 'g': 8, 'h': 10, 'i': 4, 'j': 3, 'k': 9,
                           'l': 2, 'm': 1, 'n': 12, 'o': 12, 'p': 12, 'q': 12, 'r': 12}})

    bp1_1 = BP_class(14, {0: {'e': 5, 'k': 6}, 1: {'o': 2}, 2: {'p': 2}, 3: {'b': 9, 'd': 13, 'h': 7}, 4: {'n': 0},
                          5: {'a': 7, 'c': 13, 'i': 6}, 6: {'q': 13}, 7: {'r': 4}, 8: {'f': 12, 'j': 6}, 9: {'s': 7},
                          10: {'t': 3}, 11: {'g': 3, 'l': 6, 'm': 3}, 12: {'u': 4}, 13: {'v': 3}}, 0,
                     {0: {'a': 11, 'b': 4, 'c': 12, 'd': 11, 'e': 6, 'f': 5, 'g': 7, 'h': 13, 'i': 6, 'j': 1, 'k': 3,
                          'l': 2, 'm': 2, 'n': 4, 'o': 0, 'p': 0, 'q': 0, 'r': 0, 's': 0, 't': 0, 'u': 0, 'v': 0},
                      1: {'a': 6, 'b': 5, 'c': 1, 'd': 11, 'e': 5, 'f': 10, 'g': 1, 'h': 13, 'i': 4, 'j': 6, 'k': 0,
                          'l': 8, 'm': 1, 'n': 0, 'o': 1, 'p': 1, 'q': 1, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 1},
                      2: {'a': 3, 'b': 1, 'c': 8, 'd': 10, 'e': 3, 'f': 1, 'g': 7, 'h': 11, 'i': 8, 'j': 8, 'k': 3,
                          'l': 10, 'm': 5, 'n': 5, 'o': 2, 'p': 2, 'q': 2, 'r': 2, 's': 2, 't': 2, 'u': 2, 'v': 2},
                      3: {'a': 0, 'b': 8, 'c': 7, 'd': 1, 'e': 6, 'f': 1, 'g': 4, 'h': 7, 'i': 2, 'j': 3, 'k': 1,
                          'l': 13, 'm': 1, 'n': 6, 'o': 3, 'p': 3, 'q': 3, 'r': 3, 's': 3, 't': 3, 'u': 3, 'v': 3},
                      4: {'a': 0, 'b': 4, 'c': 10, 'd': 7, 'e': 13, 'f': 3, 'g': 7, 'h': 9, 'i': 9, 'j': 4, 'k': 0,
                          'l': 12, 'm': 1, 'n': 8, 'o': 4, 'p': 4, 'q': 4, 'r': 4, 's': 4, 't': 4, 'u': 4, 'v': 4},
                      5: {'a': 5, 'b': 13, 'c': 4, 'd': 4, 'e': 8, 'f': 2, 'g': 6, 'h': 2, 'i': 10, 'j': 1, 'k': 2,
                          'l': 5, 'm': 9, 'n': 10, 'o': 5, 'p': 5, 'q': 5, 'r': 5, 's': 5, 't': 5, 'u': 5, 'v': 5},
                      6: {'a': 2, 'b': 4, 'c': 2, 'd': 12, 'e': 9, 'f': 11, 'g': 5, 'h': 8, 'i': 2, 'j': 5, 'k': 4,
                          'l': 2, 'm': 13, 'n': 4, 'o': 6, 'p': 6, 'q': 6, 'r': 6, 's': 6, 't': 6, 'u': 6, 'v': 6},
                      7: {'a': 12, 'b': 6, 'c': 13, 'd': 2, 'e': 10, 'f': 10, 'g': 7, 'h': 9, 'i': 0, 'j': 4, 'k': 13,
                          'l': 0, 'm': 1, 'n': 2, 'o': 7, 'p': 7, 'q': 7, 'r': 7, 's': 7, 't': 7, 'u': 7, 'v': 7},
                      8: {'a': 6, 'b': 10, 'c': 4, 'd': 7, 'e': 3, 'f': 8, 'g': 2, 'h': 6, 'i': 6, 'j': 4, 'k': 10,
                          'l': 10, 'm': 11, 'n': 9, 'o': 8, 'p': 8, 'q': 8, 'r': 8, 's': 8, 't': 8, 'u': 8, 'v': 8},
                      9: {'a': 11, 'b': 6, 'c': 12, 'd': 9, 'e': 4, 'f': 5, 'g': 5, 'h': 2, 'i': 1, 'j': 1, 'k': 8,
                          'l': 0, 'm': 0, 'n': 9, 'o': 9, 'p': 9, 'q': 9, 'r': 9, 's': 9, 't': 9, 'u': 9, 'v': 9},
                      10: {'a': 6, 'b': 2, 'c': 4, 'd': 0, 'e': 1, 'f': 4, 'g': 3, 'h': 7, 'i': 3, 'j': 1, 'k': 5,
                           'l': 10, 'm': 12, 'n': 5, 'o': 10, 'p': 10, 'q': 10, 'r': 10, 's': 10, 't': 10, 'u': 10,
                           'v': 10},
                      11: {'a': 6, 'b': 8, 'c': 10, 'd': 5, 'e': 13, 'f': 9, 'g': 1, 'h': 5, 'i': 3, 'j': 11, 'k': 0,
                           'l': 5, 'm': 6, 'n': 8, 'o': 11, 'p': 11, 'q': 11, 'r': 11, 's': 11, 't': 11, 'u': 11,
                           'v': 11},
                      12: {'a': 10, 'b': 12, 'c': 12, 'd': 11, 'e': 12, 'f': 11, 'g': 5, 'h': 1, 'i': 6, 'j': 13,
                           'k': 6, 'l': 1, 'm': 12, 'n': 11, 'o': 12, 'p': 12, 'q': 12, 'r': 12, 's': 12, 't': 12,
                           'u': 12, 'v': 12},
                      13: {'a': 13, 'b': 3, 'c': 13, 'd': 2, 'e': 2, 'f': 11, 'g': 5, 'h': 13, 'i': 9, 'j': 3,
                           'k': 12, 'l': 8, 'm': 8, 'n': 13, 'o': 13, 'p': 13, 'q': 13, 'r': 13, 's': 13, 't': 13,
                           'u': 13, 'v': 13}})
    # set_of_words_1_1 = {'positive': {1: ['dhaedfffhaedhaed'], 4: ['dhcaedhc', 'deccgebeccgie'],
    #                                  9: ['dha'], 12: ['de'], 15: ['dffhaehca'], 17: ['dhcaed'],
    #                                  19: ['dhaehdbiidgifeeiiide']},
    #                     'negative': {1: ['fegdedd'], 3: ['hgbieafdghafbafh', 'iff'],
    #                                  4: ['beiegadebieeihhcci', 'iah', 'hfadggegidcgfdhhad', 'cdgadfhhfeb',
    #                                      'cbihfgbbdidgg'], 5: ['hfcabdbcdiccg'],
    #                                  6: ['cffaaigaddfig', 'afegichddf', 'checbgdhca', 'ggbdcb'],
    #                                  7: ['agaibahh', 'cddcbbcbfachhc', 'gi', 'cfhdhcdb', 'ddeaebi'],
    #                                  8: ['abdgefeeddhgdagddaa', 'hehfdbhhhhgecfhd', 'diic', 'eadiadabedgghdgh',
    #                                      'cbaabfbida', 'bbbhffdhaddh'],
    #                                  9: ['aefbbdhcahceg', 'gcifbiahbidaecga', 'hbaabhih'],
    #                                  10: ['ecgfah', 'hiibcfa', 'bc'],
    #                                  11: ['idiceaabbab', 'bbehcficbfhgifbgea', 'hegbegbgaiidcdbihdch'],
    #                                  12: ['iehbbfih', 'dbdeegdibi'],
    #                                  13: ['abgad', 'ghdhgigbhcfb', 'fbfaaihaggfehi', 'cfbghiedbiaehe'],
    #                                  14: ['idififeefahggfac', 'egbhcfedgiffiidahdai', 'ifcbhahhefeagaia', 'fibcgd',
    #                                       'a'], 15: ['heb', 'ceaedcabhgffhiddach', 'chieeecbfaebdb'],
    #                                  16: ['hdgbggfgd', 'hcdfiggbefghbcc', 'di'],
    #                                  17: ['fafhcihg', 'eeciiac', 'bifb', 'bieefbhdgcbeghidbfih'],
    #                                  18: ['cc', 'ehibafiffe', 'gcg', 'hcbeecggffibbc', 'chagbc', 'bbe',
    #                                       'ibdeffbcgcah'], 19: ['edgifahheegaa', 'ceghiaa', 'hfeaefb', 'ihhiahdiihb'],
    #                                  20: ['iabbahfeffffhgdfdi', 'igffaecgihceh', 'egfagfbbdhaeeicgb']}}

    set_of_words_1_1 = {'positive': {1: ['fcghibcghiejdghib', 'fghiejdghibcccccgh'],
                                     2: ['fghhiai', 'fjgdghdcgaieghih'],
                                     3: ['fcegdhhiiah'], 4: ['fjjgdhhcgiibgai'],
                                     6: ['fjj', 'fghhhhihaiecbdghd'], 8: ['fjdcccgeghcfej'],
                                     9: ['fcadg'], 10: ['fcegdhihgdghdgh'],
                                     12: ['fjdecajccg'], 17: ['fcbbbgbgbfe', 'fjjdddcc'],
                                     18: ['fghieecfjecccgajh', 'fcecehighdgh']},
                        'negative': {2: ['gjbjbhfhcfghibedejc'], 5: ['ag', 'gehcfdchafe'],
                                     7: ['cciicibccgiggfde'],
                                     8: ['hg', 'gbgdhgcdhabaeffceigf'],
                                     9: ['fhjbbcicggbcfdbea', 'ichbfa'],
                                     10: ['be'], 11: ['heebeae', 'eej'],
                                     12: ['efbeiaebccgidcchhe'],
                                     14: ['acggdbbebde', 'aefgajjadebidgbcj', 'fgbgabfbb', 'hgaiddj',
                                          'dffahaabajaggjahcc'], 16: ['gij'],
                                     17: ['ebebeeafahb', 'fifaidbdafjhbjcbchah', 'bfadhhccaicigad', 'beg'],
                                     19: ['biceegigfbejahaffff', 'e'], 20: ['fdcj']}}

    set_of_words_1_1 = {'positive': {1: ['kefjrfa'], 2: ['kemleficjhdbpkae'], 4: ['db', 'k'], 5: ['keml'],
                                     6: ['dnbnjkkhkefjr'], 7: ['dbanpdnrfeqcc', 'dnbnjd'], 10: ['kejrmooiic'],
                                     12: ['kjoiilpglpqdh', 'kefoci', 'dnrfdgiccjdqbbabhdf'],
                                     14: ['dbnjrrrfgiihdh'], 15: ['kem', 'kapkaeg'], 19: ['dbnapp'],
                                     20: ['dnnnrmpkbchdg']},
                        'negative': {4: ['jrjkpgghk', 'lgholhkdejldch', 'okbfplkkg'],
                                     5: ['iieeiocn', 'rdeeqirgagbgpcido', 'fcare'],
                                     7: ['gafbiqmgfghq'], 8: ['jlhcdaqfir'],
                                     13: ['dbiafhhmjreqaopen', 'fijddpeqbairdcmgbkhk', 'heodgmggffambaf',
                                          'aiparqd', 'rhfchafli'], 14: ['n'], 15: ['bpddbloqqn', 'oci', 'ooflpd'],
                                     16: ['egohmjkdih', 'ogcchh', 'iff'],
                                     19: ['aclipmnrmfnl', 'hjj', 'kkhpohldodkdllrc'],
                                     20: ['cncgqej', 'naicchdpeegrqecm', 'hjpram', 'e']}}

    set_of_words_1_1 = {'positive': {1: ['ecvbsrneiqvhrnecvhr'], 2: ['kqhrnecjbsrnfiqvb'],
                                     3: ['kdvhovpbqvh'], 4: ['kbffmaqv', 'e'], 5: ['kdu'],
                                     6: ['eaprnal', 'kdvbcnghma'], 7: ['ea'], 8: ['ecpp', 'eaprppppnecvnj'],
                                     9: ['kbjqvneds'], 12: ['ecvhrgdlqaq', 'eipqvhlearneiss'],
                                     14: ['kbnkqvf'], 17: ['earnkqvpboo', 'khrneips'],
                                     18: ['eapprnithrjn', 'eipqvphliq'], 19: ['khjqvnjarkesrvbv']},
                        'negative': {1: ['rmbnoicamfkmo', 'ljt'],
                                     2: ['argghboaunagsf', 'cbplbvtg', 'dajnirmolhipkaarurno'],
                                     3: ['ilb', 'dpdjlmtsmebcpklro'], 4: ['nomsaulvtauokrhtr', 'cdcqt'],
                                     5: ['bbtk', 'vg'], 6: ['fvpfreahla', 'r'],
                                     7: ['uh', 'fsnuqubvidlg', 'tbesgqiddqne'],
                                     8: ['jjetrnudmm', 'plqlvhgmnmrd'], 9: ['lkcvcfn', 'isnme'],
                                     10: ['iionhuhjue'],
                                     12: ['jcvsarllmatngilthrmr', 'nqivitiqaourvfscdvdj', 'drgimop'],
                                     13: ['fmqnphcmtpqkk', 'nsgagvhahbaqghldb', 'coljju', 'quftencgddn'],
                                     14: ['bkmcoqpjgeihprcnqkiu', 'cbjmhslf', 'vtdsdmgubtotcjo',
                                          'bbtvkquiotrblnomjvcf'],
                                     15: ['maqgbarojqoelndb', 'cienlkaflde'], 16: ['ugm'],
                                     17: ['jslfr', 'bqlon', 'enbhbgor'], 18: ['fjmbpkduakjosmf'],
                                     19: ['caesenlqfo', 'glb', 'tauliojpmbil']}}
    min_actions, clean_rec, non_min_actions, clean_rec_non_minimal, solution, words_added = running_no_cs(bp1_1, 0,
                                                                                                          set_of_words_1_1,
                                                                                                          True)

    scenario_number = 345
    bp_learned = BP_class(len(non_min_actions), non_min_actions, 0, clean_rec_non_minimal)
    right_output = True
    if words_added['positive'] != dict():
        for c in words_added['positive']:
            for word in words_added['positive'][c]:
                right_output &= bp_learned.is_feasible(c, list(word))
                if not bp_learned.is_feasible(c, list(word)):
                    print(f"{list(word)} should have been feasible for {c} but isn't")
    if right_output:
        if words_added['negative'] != dict():
            for c in words_added['negative']:
                for word in words_added['negative'][c]:
                    right_output &= not (bp_learned.is_feasible(c, list(word)))
                    if bp_learned.is_feasible(c, list(word)):
                        print(f"{list(word)} should have been infeasible for {c} but isn't")
    solution['right_output'] = right_output
    print(f"scenario {scenario_number - 1}: the two BP's are equivalent?: non minimal",
          right_output)

    bp_learned = BP_class(len(min_actions), min_actions, 0, clean_rec)
    right_output = True
    if words_added['positive'] != dict():
        for c in words_added['positive']:
            for word in words_added['positive'][c]:
                right_output &= bp_learned.is_feasible(c, list(word))
    if right_output:
        if words_added['negative'] != dict():
            for c in words_added['negative']:
                for word in words_added['negative'][c]:
                    right_output &= not (bp_learned.is_feasible(c, list(word)))
    solution['minimal_right_output'] = right_output
    print(f"scenario {scenario_number - 1}: the two BP's are equivalent?: minimal:",
          right_output)
    new_row = pd.DataFrame([solution],
                           columns=['failed_converged', 'timeout', 'amount_of_states_in_origin',
                                    'amount_of_states_in_output',
                                    'origin_BP', 'output_BP', 'cutoff',
                                    'CS_development_time',
                                    'CS_positive_size', 'CS_negative_size', 'words_added',
                                    'longest_word_in_CS', 'solve_SMT_time', 'amount_of_state/s_in_minimal_output',
                                    'minimal_output_BP', 'minimal_solve_SMT_time', 'right_output',
                                    'minimal_right_output'])  # 'right_output'

    print("new_row:", new_row)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv('curr128_1_output_1_after_fix_3.csv', index=False)

# TODO: 06/04/24, Need to keep cleaning, the part on the end was making sure all problematic part from before are
#   resolved, from file min_failed or wrong_output...
#   the part in the CLUSTER are for the paper, still running, making sure how it goes...
#   and in general go over the paper and make sure regarding the feedbacks what can be changed.. --- Talk to Dana ! ---
