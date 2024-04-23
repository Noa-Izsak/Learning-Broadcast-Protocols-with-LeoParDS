import pandas as pd

from BP_Run import *
from BP_gen import act_names, equivalent_bp

one_hour = 3600
two_hours = 7200
three_hour = 3600 * 3
two_min = 120
half_hour = 1800


def generator_B_m_n_l(m, n, l, cutoff, timer_c, word_lim):
    scenario_num = 1
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

    print(f"scenario #{scenario_num}: {bp}")
    scenario_num += 1
    learner = BP_run(bp)
    bp_acts, bp_rec, origin_actions, rec_non_minimal, solution = learner.run_subsume_cs(0, False, cutoff_lim=cutoff,
                                                                                        time_lim=timer_c,
                                                                                        word_lim=word_lim)
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
    learned_bp = BP_class(len(bp_acts), bp_acts, 0, bp_rec)
    solution['right_output'] = equivalent_bp(bp, learned_bp, solution['cutoff'])
    print(f"scenario {scenario_num - 1}: the two BP's are equivalent?:",
          equivalent_bp(bp, learned_bp, solution['cutoff']))
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

time_count = 8 * 3600
generator_B_m_n_l(2, 1, 2, 35, time_count, 8500)

