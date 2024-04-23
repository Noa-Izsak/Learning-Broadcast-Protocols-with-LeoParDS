import pandas as pd
import time
from z3 import *

import BP_Class as Bp
from BP_Run import *
from State_Vector import learn_from_characteristic_set
from Trie import Trie
from BP_Class import BP_class

from BP_gen import alphabet
from helpers_functions import *

print(z3.get_version_string())  # Was tested for 4.12.2

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
        # print("modified cs :", self.modified_full_cs)
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
                         }

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
                for c_s in range(1, counter + 1):  # counter +1 -> we access at most to counter index
                    if self.characteristic_set.get(c_s) is None:
                        continue
                    for pos_w in self.characteristic_set[c_s]:
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
        for act in can_be:
            other_acts = set(all_acts) - set(can_be[act])
            for o_a in other_acts:
                self.not_in_same_state.append((act, o_a))

        all_first_letters = [pos_w[0] for c_s in self.characteristic_set for pos_w in self.characteristic_set[c_s]]
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
                is_flfl_in_pos = False
                for element in self.characteristic_set[1]:
                    if element.startswith(str(f_l + f_l)):
                        is_flfl_in_pos = True
                if (not is_flfl_in_pos) and (str(f_l + f_l) not in all_negative_examples):
                    flag = True

        if not flag:
            # then we know how to separate the states
            states = dict()
            state_count = 1
            used_acts = set()
            for act in all_acts:
                set_intersect = set(can_be[act])
                if len(set_intersect) == 0:
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

    def learn(self, minimal=False):
        if self.solution['failed_converged']:
            return
        ''' 
        Modify negative examples in the Sample so that they will appears only once for greatest value processes numbers 
        '''
        current_seq_learn_pos, current_learn_pos, current_geq_learn_neg, current_learn_neg = learn_from_characteristic_set(
            self.modified_full_cs, 1)
        all_first_letters = [pos_w[0] for c_s in self.characteristic_set for pos_w in self.characteristic_set[c_s]]
        all_first_letters = list(set(all_first_letters))
        if self.characteristic_set.get(1) is None:
            if all_first_letters:  # not an empty list, there are some positive examples in the sample
                self.characteristic_set[1] = all_first_letters
            else:
                """ No positive example sin the sample, return defaultive agreeing BP """
                list_neg_letters = list(set(get_unique_letters(current_geq_learn_neg)))
                not_seen_act = list(set(alphabet) - set(list_neg_letters))[0]
                all_acts_list = list_neg_letters + [not_seen_act]
                self.bp = Bp.BP_class(2, {0: {not_seen_act: 0}, 1: {neg_el: 1 for neg_el in list_neg_letters}}, 0,
                                      {0: {a_el: 0 for a_el in all_acts_list}, 1: {a_el: 1 for a_el in all_acts_list}})
                for act in all_acts_list:
                    if act not in self.known_actions:
                        self.known_actions.append(act)
                        self.actions_smt[act] = Int(f'{act}')
                for s in [0, 1]:
                    self.known_states.append(s)
                    self.states_smt[s] = Int(str(s))
                self.clean_option_holders()
                self.deal_with_possibilities(minimal, positive=False)
                return
        states, all_acts, all_first_letters = self.a_and_b_are_separated_constraints()

        for curr_word in current_learn_pos:
            for i in range(len(curr_word) - 1):
                self.fsend_behaviours_by_acts.append((curr_word[i], curr_word[i + 1]))
        self.reset_states_by_feasible_in_one(current_learn_pos, current_seq_learn_pos, states)
        self.fsend_behaviours_by_acts = list(set(self.fsend_behaviours_by_acts))

        negative_acts_len_1 = filter_strings_by_length(current_geq_learn_neg, 1)
        self.add_neg_actions_to_smt(current_geq_learn_neg)
        self.add_actions_to_smt(current_seq_learn_pos)
        for init_act in all_first_letters:
            self.smt_constraint_copy.append(fst(self.actions_smt[init_act]) == self.states_smt[self.bp.initial_state])
            for not_init_act in negative_acts_len_1:
                self.not_in_same_state.append((init_act, not_init_act))
                self.smt_constraint_copy.append(
                    fst(self.actions_smt[not_init_act]) != self.states_smt[self.bp.initial_state])
        self.not_in_same_state = list(set(self.not_in_same_state))

        all_positive_acts = get_positive_alphabet(self.modified_full_cs['positive'])

        if all_positive_acts != all_acts and (states is None):
            for a_1 in list(set(all_acts) - set(all_positive_acts)):
                self.create_new_state_for_new_action(a_1)
                self.bp.update_self_loops(self.bp.receivers)
        elif all_positive_acts != all_acts:
            self.create_new_state_for_new_action(list(set(all_acts) - set(all_positive_acts)))
            self.bp.update_self_loops(self.bp.receivers)

        self.bp.update_self_loops(self.bp.receivers)
        self.main_round(current_seq_learn_pos, current_learn_neg, minimal)
        print(f"this is the BP:\nacts:{self.bp.actions}\nrec:{self.bp.receivers}")
        print(f"SMT values constrains")
        pass

    def main_round(self, current_learn_pos, current_learn_neg, minimal):
        """
        The Main procedure that creates the constraints based on the sample
        :param current_learn_pos:
        :param current_learn_neg:
        :param minimal: whether we invoke BPInf (minimal=False) of BPInfMin (minimal=True)
        :return:
        """
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
            # print("counter: ", counter)
            if counter == 1:
                # Then we already took care about the current_learn_pos, we also took care about current_learn_neg
                # for 1 action words, which are not enabled from the initial state.
                for w_neg in current_learn_neg:
                    ''' word is infeasible for 1 proc '''
                    # there is an *and* between word[:prefix_len] is feasible and word[prefix_len] is infeasible
                    # after words and for all options, there is an *or*
                    total_neg_constraints = self.negative_sample_constraint_builder(counter, w_neg)
                    if total_neg_constraints:
                        self.smt_constraint_copy.append(Or(*total_neg_constraints))
                continue
            plus_one_seq_learn_pos, plus_one_learn_pos, plus_one_geq_learn_neg, plus_one_learn_neg = \
                learn_from_characteristic_set(self.modified_full_cs, counter)
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
                    self.create_new_state_for_new_action(new_acts)
                    self.bp.update_self_loops(self.bp.receivers)

            for w_neg in plus_one_learn_pos:
                tot_constraint_pos = []
                constraints_init, procs_holder = self.init_procs_holders_for_prefix(counter, w_neg)
                if constraints_init:
                    tot_constraint_pos.append(And(*constraints_init))

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
                    for w in plus_one_geq_learn_neg:
                        if len(w) == len(w_neg[:k]) + 1 and w.startswith(w_neg[:k]):
                            neg_plus.append(w[-1])
                    if neg_plus:
                        for b in neg_plus:
                            for p in procs_holder:
                                neg_const.append(p[k] != fst(self.actions_smt[b]))
                        tot_constraint_pos.append(And(*neg_const))
                self.smt_constraint_copy.append(And(*tot_constraint_pos))

            for w_neg in plus_one_learn_neg:
                ''' word is infeasible for counter proc '''
                # there is an *and* between word[:prefix_len] is feasible and word[prefix_len] is infeasible after words
                # and for all options, there is an *or*
                total_neg_constraints = self.negative_sample_constraint_builder(counter, w_neg)
                if total_neg_constraints:
                    self.smt_constraint_copy.append(Or(*total_neg_constraints))

            current_learn_pos = plus_one_seq_learn_pos
        self.clean_option_holders()
        self.deal_with_possibilities(minimal)
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
            curr_constraint = []
            if prefix_len == 0:
                ''' make sure that the #counter processes starts in the initial state '''
                curr_constraint.append(
                    fst(self.actions_smt[w_neg[prefix_len]]) != self.states_smt[self.bp.initial_state])
            else:
                # there is a non-empty prefix of word that is feasible that after words is infeasible
                ''' make sure that the #counter processes starts in the initial state '''
                for i in range(counter):
                    curr_constraint.append(
                        procs_holder[i][0] == self.states_smt[self.bp.initial_state])
                curr_constraint.append(
                    procs_holder[0][0] == fst(self.actions_smt[w_neg[0]]))
                for k in range(1, len(w_neg)):
                    curr_constraint.append(
                        procs_holder[0][0] == Int(f'{w_neg[:k]}_{str(counter)}_{0}_{0}'))
                    self.constraints_total_for_procs.append(Int(f'{w_neg[:k]}_{str(counter)}_{0}_{0}'))
                for index in range(prefix_len):
                    someone_is_there = self.constraint_proc_in_act_state(index, w_neg, procs_holder)
                    curr_constraint.append(Or(*someone_is_there))
                    total_holder = self.rest_of_procs_constraint(index, w_neg, procs_holder)
                    curr_constraint.append(Or(*total_holder))
                temp_holder = []
                for i in range(counter):
                    temp_holder.append(
                        procs_holder[i][prefix_len] != fst(self.actions_smt[w_neg[prefix_len]]))
                if temp_holder:
                    curr_constraint.append(And(*temp_holder))
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
        :return: the list of constraint that ensure it
        """
        someone_is_there = []
        for p in procs_holder:
            someone_is_there.append(p[index] == fst(self.actions_smt[prefix[index]]))
        return someone_is_there

    def init_procs_holders_for_prefix(self, counter, prefix):
        """
        given a prefix, initiate counter x (len(prefix) +1) processes
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
                procs_holder[0][0] == Int(f'{prefix[:k]}_{str(counter)}_{0}_{0}'))
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
                self.known_actions.append(act)
                self.actions_smt[act] = Int(f'{act}')
        new_state_index = max(self.bp.actions) + 1
        if new_state_index not in self.known_states:
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
        pass

    # ------------------------------------- SCENARIOS --------------------------------------
    def deal_with_possibilities(self, minimal, positive=True):
        """
        :param minimal: are we looking for minimal
        :param positive: whether there are positive examples
        :return:
        """
        constraints1 = []
        self.not_in_same_state = list(set(self.not_in_same_state))
        for (a1, a2) in self.not_in_same_state:
            self.smt_constraint_copy.append(fst(self.actions_smt[a1]) != fst(self.actions_smt[a2]))

        self.fsend_behaviours = list(set(self.fsend_behaviours))
        for (a, b) in self.fsend_behaviours:
            self.smt_constraint_copy.append(fsend(self.actions_smt[a]) == self.states_smt[b])

        self.fsend_behaviours_by_acts = list(set(self.fsend_behaviours_by_acts))
        for (a, b) in self.fsend_behaviours_by_acts:
            self.smt_constraint_copy.append(fsend(self.actions_smt[a]) == fst(self.actions_smt[b]))

        self.fst_behaviours = list(set(self.fst_behaviours))
        for (a, b) in self.fst_behaviours:
            self.smt_constraint_copy.append(fst(a) == b)

        SMT2 = Solver()
        SMT2.set(unsat_core=True)
        SMT2.add(And(*self.smt_constraint_copy))
        self.basic_const_smt(constraints1)
        SMT2.add(And(*constraints1))
        self.proc_const_smt(SMT2)
        begin_time = time.perf_counter()
        if SMT2.check() == unsat:
            end_time = time.perf_counter()
            self.solution['solve_SMT_time'] = end_time - begin_time
            smt_core_val = SMT2.unsat_core()
            print("unsat - for this number of actions, hence, we are looking on a sample that is not "
                  "sufficiently complete and we need to add new actions")
            all_acts_list = list(set(list(get_positive_alphabet(self.modified_full_cs['positive'])) +
                                     list(get_positive_alphabet(self.modified_full_cs['negative']))))
            i = 0
            while i < 2 * self.cutoff:
                i += 1
                not_seen_act = list(set(alphabet) - set(all_acts_list))[0]
                all_acts_list.append(not_seen_act)
                self.create_new_state_for_new_action(not_seen_act)
                self.bp.update_self_loops(self.bp.receivers)

                SMT3 = Solver()
                SMT3.set(unsat_core=True)
                SMT3.add(And(*self.smt_constraint_copy))
                constraints1 = []
                self.basic_const_smt(constraints1)
                SMT3.add(And(*constraints1))
                self.proc_const_smt(SMT3)

                copied_actions = copy.deepcopy(self.bp.actions)
                copied_receivers = copy.deepcopy(self.bp.receivers)
                self.ret_origin_self_bp = Bp.BP_class(len(copied_actions), copied_actions, self.bp.initial_state,
                                                      copied_receivers)
                begin_time = time.perf_counter()
                if SMT3.check() == unsat:
                    end_time = time.perf_counter()
                    self.solution['solve_SMT_time'] = end_time - begin_time
                    print(f"unsat for extra {i} actions ")
                    print(f"the bp so far {self.bp}")
                    print(f"the cs info: {self.modified_full_cs}\n"
                          f"the cutoff: {self.cutoff}")
                    print("known states: ", self.known_states)
                    print("known actions: ", self.known_actions)
                    continue
                else:
                    end_time = time.perf_counter()
                    self.solution['solve_SMT_time'] = end_time - begin_time
                    print("SAT")

                    print("self known actions ", self.known_actions)
                    print("self known states ", self.known_states)
                    model = SMT3.model()

                    states_translation_smt = dict()
                    if model != []:
                        self.states_and_actions_translation_smt(get_key_by_value, model, states_translation_smt)
                    states_values = list(set(states_translation_smt.values()))

                    self.dill_with_duplicated_smt_values(states_translation_smt, states_values)

                    self.solution['output_BP'] = f'states: {len(set(self.bp.actions))},\nactions: {self.bp.actions},' \
                                                 f'\ninitial: {self.bp.initial_state},\n' \
                                                 f'receivers: {clean_receivers(self.bp.receivers)}'
                    self.solution['amount_of_states_in_output'] = len(set(self.bp.actions) - {-1})
                    i = 2 * self.cutoff
                    if minimal:
                        ''' Then we want to return a minimal representation '''
                        copied_actions = copy.deepcopy(self.bp.actions)
                        copied_receivers = copy.deepcopy(self.bp.receivers)
                        duplicated_self_bp = Bp.BP_class(len(copied_actions), copied_actions, 0, copied_receivers)
                        self.bp_inf_minimal(duplicated_self_bp, positive)
            pass

        else:
            end_time = time.perf_counter()
            self.solution['solve_SMT_time'] = end_time - begin_time
            print("SAT")

            print("self known actions ", self.known_actions)
            print("self known states ", self.known_states)
            model = SMT2.model()

            states_translation_smt = dict()
            if model != [] and positive:
                self.states_and_actions_translation_smt(get_key_by_value, model, states_translation_smt)

            # in case there are duplicated values in states_translation_smt, that means that states can be merged

            copied_actions = copy.deepcopy(self.bp.actions)
            copied_receivers = copy.deepcopy(self.bp.receivers)
            duplicated_self_bp = Bp.BP_class(len(copied_actions), copied_actions, 0, copied_receivers)
            states_values = list(set(states_translation_smt.values()))
            self.dill_with_duplicated_smt_values(states_translation_smt, states_values)

            self.solution['output_BP'] = f'states: {len(set(self.bp.actions))},\nactions: {self.bp.actions},\n' \
                                         f'initial: {self.bp.initial_state},\n' \
                                         f'receivers: {clean_receivers(self.bp.receivers)}'
            self.solution['amount_of_states_in_output'] = len(set(self.bp.actions) - {-1})

            copied_actions = copy.deepcopy(self.bp.actions)
            copied_receivers = copy.deepcopy(self.bp.receivers)
            self.ret_origin_self_bp = Bp.BP_class(len(copied_actions), copied_actions, self.bp.initial_state,
                                                  copied_receivers)
            # print("minimal", minimal)
            if minimal:
                if len(self.bp.actions) == 2:  # already minimal..
                    self.solution[
                        'minimal_output_BP'] = f'states: {len(set(self.bp.actions))},\nactions: {self.bp.actions},\n' \
                                               f'initial: {self.bp.initial_state},\n' \
                                               f'receivers: {clean_receivers(self.bp.receivers)}'
                    self.solution['amount_of_states_in_minimal_output'] = len(set(self.bp.actions) - {-1})
                    self.solution['minimal_solve_SMT_time'] = 0
                else:
                    self.bp_inf_minimal(duplicated_self_bp, positive)
        pass

    def bp_inf_minimal(self, duplicated_self_bp, is_positive=True):
        begin_time = time.perf_counter()
        model = self.minimal_distinct_values(begin_time, 1, list(self.states_smt.values()),
                                             And(*self.smt_constraint_copy))
        states_translation_smt = dict()
        self.bp = duplicated_self_bp
        if model != [] and is_positive:
            self.states_and_actions_translation_smt(get_key_by_value, model, states_translation_smt)
        states_values = list(set(states_translation_smt.values()))
        self.dill_with_duplicated_smt_values(states_translation_smt, states_values)
        self.solution['minimal_output_BP'] = f'states: {len(set(self.bp.actions))},\nactions: {self.bp.actions},\n' \
                                             f'initial: {self.bp.initial_state},\n' \
                                             f'receivers: {clean_receivers(self.bp.receivers)}'
        self.solution['amount_of_states_in_minimal_output'] = len(set(self.bp.actions) - {-1})

    def dill_with_duplicated_smt_values(self, states_translation_smt, states_values):
        """
        in case there are duplicated values in states_translation_smt, that means that states can be merged
        :param states_translation_smt:
        :param states_values:
        :return:
        """
        for sv in states_values:
            keys = get_keys_by_value(states_translation_smt, sv)
            if len(keys) == 1:
                continue
            else:
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
        pass

    def states_and_actions_translation_smt(self, get_key_by_val, model, states_translation_smt):
        self.known_states = list(set(self.known_states))
        for state in self.known_states:
            states_translation_smt[state] = int(model[self.states_smt[state]].as_long())
        action_translation_smt = dict()
        for action in self.known_actions:
            action_translation_smt[action] = model[self.actions_smt[action]].as_long()
        new_bp = BP_class(len(list(states_translation_smt.values())), dict(), self.bp.initial_state, dict())
        for act in self.known_actions:
            self.bp.update_action(
                get_key_by_val(states_translation_smt, model.eval(fst(self.actions_smt[act])).as_long()),
                act, get_key_by_val(states_translation_smt, model.evaluate(fsend(self.actions_smt[act])).as_long()))
            new_bp.update_action(
                get_key_by_val(states_translation_smt, model.eval(fst(self.actions_smt[act])).as_long()),
                act, get_key_by_val(states_translation_smt, model.evaluate(fsend(self.actions_smt[act])).as_long()))
            new_bp.update_self_loops(new_bp.receivers)

        for act in self.known_actions:
            for state in self.known_states:
                self.bp.update_receivers(
                    state, act, get_key_by_val(states_translation_smt,
                                               model.eval(
                                                   frec(self.actions_smt[act], self.states_smt[state])).as_long()),
                    True)
                new_bp.update_receivers(
                    state, act, get_key_by_val(states_translation_smt,
                                               model.eval(
                                                   frec(self.actions_smt[act], self.states_smt[state])).as_long()),
                    True)

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
        for act in union_result:
            if act in self.known_actions:
                continue
            else:
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

        action_builder = dict()
        act_to_state = dict()
        known_actions = set()
        state_index = 1
        for pref in sorted_dict:
            if pref == '':
                action_builder[self.bp.initial_state] = dict((x, -1) for x in sorted_dict.get(pref))  # make sure
                for x in sorted_dict.get(pref):
                    known_actions.add(x)
                    act_to_state[x] = self.bp.initial_state
            else:
                '''We have only a single processes, then if a single actions is known then the rest of actions are 
                too going there '''
                is_known, act = has_common_letter(sorted_dict.get(pref), known_actions)
                if is_known:
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
                else:  # not a known state
                    if action_builder.get(act_to_state[pref[-1]]) is None:
                        action_builder[act_to_state[pref[-1]]] = dict([(pref[-1], state_index)])
                        for x in sorted_dict.get(pref):
                            known_actions.add(x)
                            act_to_state[x] = state_index
                    else:
                        was_it_define = action_builder[act_to_state[pref[-1]]].get(pref[-1]) is not None
                        if was_it_define and (action_builder[act_to_state[pref[-1]]][pref[-1]] != -1):
                            ''' Then this action already knows where it goes, we only need to 
                            update the new action origin '''
                            for x in sorted_dict.get(pref):
                                known_actions.add(x)
                                act_to_state[x] = action_builder[act_to_state[pref[-1]]][pref[-1]]
                        else:
                            action_builder[act_to_state[pref[-1]]][pref[-1]] = state_index
                            for x in sorted_dict.get(pref):
                                known_actions.add(x)
                                act_to_state[x] = state_index
                    state_index += 1
        for org_state in action_builder:
            self.bp.actions[org_state] = action_builder.get(org_state)
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


if __name__ == '__main__':

    df = pd.DataFrame(columns=min_column)

    bp1_1 = BP_class(2, {0: {'a': 1}, 1: {'b': 0}}, 0, {0: {'a': 1, 'b': 0}, 1: {'a': 1, 'b': 0}})
    set_of_words_1_1 = {'positive': {1: ['ab'], 2: ['aba']},
                        'negative': {1: ['b', 'bb'],
                                     2: ['bab', 'b', 'baa']}}
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
                           columns=min_column)  # 'right_output'

    print("new_row:", new_row)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv('non_Cs_example.csv', index=False)
