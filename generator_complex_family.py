import concurrent.futures
import random

import pandas as pd

from BP_Class import BP_class
from BP_Learn import BP_run

a_val = 97
z_val = 122
A_val = 65
Z_val = 90
act_names = [str(chr(c)) for c in range(a_val, z_val + 1)] + [str(chr(c)) for c in range(A_val, Z_val + 1)] + [
    str(chr(n)) for n in range(0, 10)] + ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '[',
                                          ']', '{', '}', '|', '~', '`', ',']


def create_more_actions():
    more_act_names = []
    for a in act_names:
        for b in act_names:
            more_act_names.append(str(a + b))
    return more_act_names


longer_act_names = create_more_actions()

defaultive_ns = 2
defaultive_na = 1

class BP_generator:

    def __init__(self, min_number_of_states, min_number_of_act, max_number_of_states=None, max_number_of_act=None):
        """
        given these parameters, we create a BP that has ns as the number of states
        (between min_number_of_states and max_number_of_states)
        and na being the number of actions to be the number of extra actions to be distributed in the system
        if max_number_of_states (resp. max_number_of_act) is None
        then ns (resp. na) determent only by min_number_of_states (resp. min_number_of_act)
        """
        if min_number_of_states is None or not(type(min_number_of_states) == int):
            print("min number of states should be int, default value of 2 states was chosen. "
                  "If you want something else please reenter the data")
            ns = defaultive_ns
        else:
            ns = min_number_of_states
            if max_number_of_states is not None:
                if max_number_of_states < min_number_of_states:  # assume it should be the other way around
                    print("Seems like you misplaced the values for min and max number of states, don't worry, "
                          "we took care of it :)")
                    ns = random.randint(max_number_of_states, min_number_of_states)
                else:
                    ns = random.randint(min_number_of_states, max_number_of_states)
        if min_number_of_act is None or not(type(min_number_of_act) == int):
            print("min number of actions should be int, default value of 1 extra action was chosen. "
                  "If you want something else please reenter the data")
            na = defaultive_na
        else:
            na = min_number_of_act
            if max_number_of_act is not None:
                if max_number_of_act < min_number_of_act:  # assume it should be the other way around
                    print("Seems like you misplaced the values for min and max number of actions, don't worry, "
                          "we took care of it :)")
                    na = random.randint(max_number_of_act, min_number_of_act)
                else:
                    na = random.randint(min_number_of_act, max_number_of_act)
        self.number_of_act = na
        self.number_of_states = ns
        self.bp: BP_class = self.generate()
        pass

    def generate(self) -> BP_class:
        actions: {int: {str: int}} = {i: {} for i in range(self.number_of_states)}
        curr_number = 0
        for state in actions:
            rand_land = random.randint(0, self.number_of_states - 1)
            actions[state] |= {act_names[curr_number]: rand_land}
            curr_number += 1
        for a in act_names[curr_number: curr_number + self.number_of_act]:
            rand_state = random.randint(0, self.number_of_states - 1)
            rand_land = random.randint(0, self.number_of_states - 1)
            actions[rand_state] |= {a: rand_land}
        receivers: {int: {str: int}} = {i: {} for i in range(self.number_of_states)}
        for state in receivers:
            for act in act_names[:curr_number + self.number_of_act]:
                rand_land = random.randint(0, self.number_of_states - 1)
                receivers[state][act] = rand_land

        return BP_class(self.number_of_states, actions, 0, receivers)


def equivalent_bp(org_bp: BP_class, new_bp: BP_class, cutoff: int):
    """
    given two bp's, check they are equivalents
    :param org_bp: the original bp
    :param new_bp: the new bp returned from the learning process
    :return: bool value (same or not the same)
    """
    org_set_acts, org_number_act, org_max = amount_of_actions(org_bp)
    new_set_acts, new_number_act, new_max = amount_of_actions(new_bp)
    if not (new_set_acts <= org_set_acts):
        # The one we are creating may not detect
        # unreached actions, but it can't be it has action that not exists in the original one
        return False
    # procs_to_check = new_number_act ** 2
    procs_to_check = cutoff * 2
    org_state_amount = len(org_bp.actions)
    new_state_amount = len(new_bp.actions)
    is_false = False
    ret_val = None
    for n_proc in range(1, procs_to_check):
        if ret_val is not None:  # we increased the n_procs but found a counter example
            return ret_val
        for j in range(procs_to_check):  # 5 combination for each amount of n_proc
            state_vec_org = {i: 0 for i in range(org_state_amount)}
            state_vec_new = {i: 0 for i in range(new_state_amount)}
            state_vec_new[0] = n_proc
            state_vec_org[0] = n_proc
            acts = []
            for i in range(procs_to_check):
                feasible_set_org = org_bp.feasible_set(state_vec_org)
                feasible_set_new = new_bp.feasible_set(state_vec_new)
                if not (feasible_set_org <= feasible_set_new <= feasible_set_org):
                    if ret_val is not None:
                        last_proc, counter_example, _ = ret_val
                        if last_proc < n_proc:
                            return ret_val
                        elif len(counter_example) < len(acts):
                            continue
                        else:
                            ret_val = n_proc, ''.join(acts), False
                    else:
                        is_false = True
                        ret_val = n_proc, ''.join(acts), False

                # rnd_index = random.randint(0, len(feasible_set_org) - 1)
                random_act = random.choice(list(feasible_set_org))
                acts.append(random_act)
                state_vec_org = org_bp.act_action(state_vec_org, random_act)
                state_vec_new = new_bp.act_action(state_vec_new, random_act)
    if is_false:
        return ret_val
    return None, None, True


def amount_of_actions(given_bp: BP_class):
    """
    :return: amount of actions in the given automaton, maximal character representing an action, set of actions
    """
    amount_of_acts = 0
    max_act = ''
    set_of_acts = {}
    for entry in given_bp.actions:
        amount_of_acts += len(given_bp.actions.get(entry))
        try:
            max_act = max(max_act, max(given_bp.actions.get(entry)))
        except ValueError:  # empty list
            continue
        if set_of_acts == {}:
            set_of_acts = {k for k in given_bp.actions.get(entry).keys()}
        else:
            set_of_acts |= given_bp.actions.get(entry).keys()
    return set_of_acts, amount_of_acts, max_act


def single_loop(bp: BP_class):
    for act in bp.actions[bp.initial_state]:
        (state, _) = bp.receivers[bp.initial_state][act]
        if (bp.actions[bp.initial_state][act] == bp.initial_state) and (state == bp.initial_state):
            return True
    return False


def eliminate_no_cutoff(bp: BP_class, init_state: int, depth):
    """ if a condition for no cutoff, then retry"""
    if depth > len(bp.actions):
        return False
    for act in bp.actions[init_state]:
        (rec_location, _) = bp.receivers[init_state][act]
        if bp.actions[init_state][act] != init_state and rec_location == init_state:
            return True
        if bp.actions[init_state][act] != init_state and rec_location == bp.actions[init_state][act]:
            val = eliminate_no_cutoff(bp, bp.actions[init_state][act], depth + 1)
            if val:
                return True
    return False


one_hour = 3600
two_hours = 7200
three_hour = 3600 * 3
two_min = 120
half_hour = 1800


def generator_B_m_n_l(m, n, l, cutoff, timer_c):
    scenario_number = 1
    df = pd.DataFrame(
        columns=['failed_converged', 'timeout', 'amount_of_states_in_origin',
                 'amount_of_states_in_output', 'origin_BP', 'output_BP', 'cutoff',
                 'CS_development_time', 'CS_positive_size', 'CS_negative_size', 'words_added',
                 'longest_word_in_CS', 'solve_SMT_time', 'right_output', 'm', 'n', 'l'])
    actions = dict()
    responses = dict()
    number_of_states = m + n + l + 4
    state_to_num_dict = dict()
    counter = 0
    for i in ['i1', 'i2', 'top', 'bot']:
        state_to_num_dict[i] = counter
        counter += 1
    for i in range(1, m + 1):
        state_to_num_dict[f'm{i}'] = counter
        counter += 1
    for i in range(1, n + 1):
        state_to_num_dict[f'n{i}'] = counter
        counter += 1
    for i in range(1, l + 1):
        state_to_num_dict[f'h{i}'] = counter
        counter += 1

    # print("state_to_num_dict.values():", state_to_num_dict.values())
    for s in state_to_num_dict.values():
        actions[s] = {}
        responses[s] = {}
    print("state_to_num_dict:", state_to_num_dict)
    action_to_char_dict = dict()
    act_counter = 0
    a_actions = []
    h_actions = []
    for i in ['i1', 'i2']:
        action_to_char_dict[i] = act_names[act_counter]
        for s in state_to_num_dict.values():
            responses[s][act_names[act_counter]] = s  # first as a self loop, later fix the needed ones
        if i == 'i1':
            actions[state_to_num_dict['i1']][act_names[act_counter]] = state_to_num_dict[f'm{1}']
            responses[state_to_num_dict['i1']][act_names[act_counter]] = state_to_num_dict['i2']
        if i == 'i2':
            if l == 0:
                actions[state_to_num_dict['i2']][act_names[act_counter]] = state_to_num_dict[f'bot']
            else:
                actions[state_to_num_dict['i2']][act_names[act_counter]] = state_to_num_dict[f'h{1}']
            responses[state_to_num_dict['i2']][act_names[act_counter]] = state_to_num_dict[f'n1']
        act_counter += 1
    for i in ['c']:
        action_to_char_dict[i] = act_names[act_counter]
        for s_name in state_to_num_dict:
            if s_name == f'm{m}':
                responses[state_to_num_dict[s_name]][act_names[act_counter]] = state_to_num_dict['top']
            else:
                responses[state_to_num_dict[s_name]][act_names[act_counter]] = state_to_num_dict['bot']

            if s_name == f'n{n}':
                actions[state_to_num_dict[s_name]][act_names[act_counter]] = state_to_num_dict['bot']
        act_counter += 1

    for i in ['a_top']:
        action_to_char_dict[i] = act_names[act_counter]
        for s_name in state_to_num_dict:
            responses[state_to_num_dict[s_name]][act_names[act_counter]] = state_to_num_dict['top']
            if s_name == 'top':
                actions[state_to_num_dict[s_name]][act_names[act_counter]] = state_to_num_dict['top']
        act_counter += 1

    for b in range(1, m + 1):
        action_to_char_dict[f'b{b}'] = act_names[act_counter]
        for s in state_to_num_dict.values():
            responses[s][act_names[act_counter]] = s
        actions[state_to_num_dict[f'm{b}']][act_names[act_counter]] = state_to_num_dict[f'm{b}']
        act_counter += 1

    for a in range(1, n):
        action_to_char_dict[f'a{a}'] = act_names[act_counter]
        a_actions.append(act_names[act_counter])
        for s in state_to_num_dict.values():
            responses[s][act_names[act_counter]] = s  # first as a self loop, later fix the needed ones
        for i in range(1, m):
            responses[state_to_num_dict[f'm{i}']][act_names[act_counter]] = state_to_num_dict[f'm{i + 1}']
        responses[state_to_num_dict[f'm{m}']][act_names[act_counter]] = state_to_num_dict[f'm{1}']

        actions[state_to_num_dict[f'n{a}']][act_names[act_counter]] = state_to_num_dict['bot']
        responses[state_to_num_dict[f'n{a}']][act_names[act_counter]] = state_to_num_dict[f'n{a + 1}']
        act_counter += 1

    for h in range(1, l + 1):
        action_to_char_dict[f'h{h}'] = act_names[act_counter]
        h_actions.append(act_names[act_counter])
        for s in state_to_num_dict.values():
            responses[s][act_names[act_counter]] = s  # first as a self loop, later fix the needed ones
        for i in range(1, m):
            responses[state_to_num_dict[f'm{i}']][act_names[act_counter]] = state_to_num_dict[f'm{i + 1}']
        responses[state_to_num_dict[f'm{m}']][act_names[act_counter]] = state_to_num_dict[f'm{1}']
        responses[state_to_num_dict[f'n{n}']][act_names[act_counter]] = state_to_num_dict[f'n{1}']
        if h == l:
            actions[state_to_num_dict[f'h{h}']][act_names[act_counter]] = state_to_num_dict['bot']
        else:
            actions[state_to_num_dict[f'h{h}']][act_names[act_counter]] = state_to_num_dict[f'h{h + 1}']
        act_counter += 1

    action_to_char_dict['a_bot'] = act_names[act_counter]
    for s in state_to_num_dict.values():
        responses[s][act_names[act_counter]] = state_to_num_dict['bot']
    actions[state_to_num_dict['bot']][act_names[act_counter]] = state_to_num_dict['bot']
    print("action_to_char_dict:", action_to_char_dict)

    bp = BP_class(number_of_states, actions, state_to_num_dict['i1'], responses)

    print(f"scenario #{scenario_number}: {bp}")
    scenario_number += 1
    learner = BP_run(bp)
    bp_acts, bp_rec, origin_actions, rec_non_minimal, solution = learner.run_subsume_cs(0, False, cutoff, timer_c)
    solution['m'] = m
    solution['n'] = n
    solution['l'] = l
    if solution['failed_converged']:
        new_row = pd.DataFrame([solution],
                               columns=['failed_converged', 'timeout', 'amount_of_states_in_origin',
                                        'amount_of_states_in_output', 'origin_BP', 'output_BP', 'cutoff',
                                        'CS_development_time',
                                        'CS_positive_size', 'CS_negative_size', 'words_added',
                                        'longest_word_in_CS', 'solve_SMT_time',
                                        'right_output', 'm', 'n', 'l'])  # 'right_output'
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(f'BP_results_m{m}_n{n}_l{l}_cutoff{cutoff}_time{timer_c}.csv', index=False)
        return
    bp_learned = BP_class(len(bp_acts), bp_acts, 0, bp_rec)
    solution['right_output'] = equivalent_bp(bp, bp_learned, solution['cutoff'])
    print(f"scenario {scenario_number - 1}: the two BP's are equivalent?:",
          equivalent_bp(bp, bp_learned, solution['cutoff']))
    new_row = pd.DataFrame([solution],
                           columns=['failed_converged', 'timeout', 'amount_of_states_in_origin',
                                    'amount_of_states_in_output', 'origin_BP', 'output_BP', 'cutoff',
                                    'CS_development_time',
                                    'CS_positive_size', 'CS_negative_size', 'words_added',
                                    'longest_word_in_CS', 'solve_SMT_time',
                                    'right_output', 'm', 'n', 'l'])  # 'right_output'
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(f'BP_results_m{m}_n{n}_l{l}_cutoff{cutoff}_time{timer_c}.csv', index=False)
    return


# for h_ind in range(1, 4):
#     for m_ind in range(1, 10):
#         for n_ind in range(m_ind, 10):
#             generator_B_m_n_l(m_ind, n_ind, h_ind)

# for m_ind in range(1, 7):
#     for n_ind in range(m_ind, 10):
#         generator_B_m_n_l(m_ind, n_ind, 1)

time_count = 8 * 3600
# generator_B_m_n_l(4, 2, 1, 50, time_count)

bp = BP_generator(2, 0, 3, 1)
print("1:", bp.bp)

# bp = BP_generator(2, 3, 3)
# print("2:", bp.bp)
#
# bp = BP_generator(6, 3, 2, 4)
# print("3:", bp.bp)
#
# bp = BP_generator(5, 4, 2, 3)
# print("3-2:", bp.bp)
#
# bp = BP_generator(3, 3, max_number_of_act=4)
# print("4:", bp.bp)
# for m_ind in range(7, 10):
#     for n_ind in range(m_ind, 10):
#         generator_B_m_n_l(m_ind, n_ind, 1)
# generator_B_m_n_l(2, 3, 1)
# generator_B_m_n_l(1, 1, 1)
# generator_B_m_n_l(1, 2, 1)
# generator_B_m_n_l(1, 1, 2)
# generator_B_m_n_l(2, 1, 1)
# generator_B_m_n_l(2, 2, 1)
# generator_B_m_n_l(1, 2, 2)
# generator_B_m_n_l(2, 1, 2)
# generator_B_m_n_l(2, 2, 2)
# generator_B_m_n_l(2, 3, 1)
# generator_B_m_n_l(3, 5, 2)
# generator_B_m_n_l(2, 2, 1)
