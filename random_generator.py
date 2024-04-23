from BP_Class import *
from BP_Run import *

from BP_gen import BP_generator, equivalent_bp, single_loop, eliminate_no_cutoff

import concurrent.futures

one_hour = 3600
two_hours = 7200
three_hours = 3 * 3600
five_hours = 5 * one_hour
two_min = 120
half_hour = 1800
twenty_min = 1200

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


def info_timeout(bp_1, is_minimal):
    if not is_minimal:
        return {'failed_converged': True,
                'timeout': True,
                'amount_of_states_in_origin': len(set(bp_1.actions)),
                'amount_of_states_in_output': 0,
                'origin_BP': f'states: {len(set(bp_1.actions))},\n '
                             f'actions: {bp_1.actions},\n'
                             f'initial: {bp_1.initial_state},\n'
                             f'receivers: {bp_1.receivers}',
                'output_BP': '',
                'cutoff': -1,
                'CS_development_time': -1,
                'CS_positive_size': 0,
                'CS_negative_size': 0,
                'words_added': {
                    'positive': {},
                    'negative': {}},
                'longest_word_in_CS': 0,
                'solve_SMT_time': 0.0}
    else:
        return {'failed_converged': True,
                'timeout': True,
                'amount_of_states_in_origin': len(
                    set(bp_1.actions)),
                'amount_of_states_in_output': 0,
                'origin_BP': f'states: {len(set(bp_1.actions))},\n '
                             f'actions: {bp_1.actions},\n'
                             f'initial: {bp_1.initial_state},\n'
                             f'receivers: {bp_1.receivers}',
                'output_BP': '',
                'cutoff': -1,
                'CS_development_time': -1,
                'CS_positive_size': 0,
                'CS_negative_size': 0,
                'words_added': {
                    'positive': {},
                    'negative': {}},
                'longest_word_in_CS': 0,
                'solve_SMT_time': 0.0,
                'amount_of_states_in_minimal_output': 0,
                'minimal_output_BP': '',
                'minimal_solve_SMT_time': 0.0}


def generator_and_check_subsume_cs(words_to_add: int, amount_to_generate: int, min_number_of_states: int,
                                   max_number_of_states: int, min_number_of_acts: int,
                                   max_number_of_acts: int, version: int, name: str,
                                   cutoff_lim=None, word_lim=None):
    """
    :param words_to_add: to pad the return CS according to the algorithm
    :param amount_to_generate: how many such random BPs to generate
    :param min_number_of_states:
    :param max_number_of_states:
    :param min_number_of_acts:
    :param max_number_of_acts:
    :param version: to be saved as a csv file
    :param name: to be saved as a csv file
    :param cutoff_lim: cutoff limit for finding the CS
    :param word_lim: CS size limitation
    :return:
    """
    scenario_num = 1
    df = pd.DataFrame(columns=min_column)
    for i in range(amount_to_generate):
        number_of_states = random.randint(min_number_of_states, max_number_of_states)
        number_of_acts = random.randint(min_number_of_acts, max_number_of_acts)
        bp = BP_generator(number_of_states, number_of_acts)
        no_cutoff_for_sure = eliminate_no_cutoff(bp.bp, bp.bp.initial_state, 0)
        is_single_loop = single_loop(bp.bp)
        while no_cutoff_for_sure or is_single_loop:
            bp = BP_generator(number_of_states, number_of_acts)
            no_cutoff_for_sure = eliminate_no_cutoff(bp.bp, bp.bp.initial_state, 0)
            is_single_loop = single_loop(bp.bp)

        print(f"scenario #{scenario_num}: {bp.bp}")
        scenario_num += 1

        learner = BP_run(bp.bp)
        amount_to_add = random.randint(1, max(words_to_add, 2))
        bp_min_acts, bp_min_rec, bp_acts, bp_rec, sol = learner.run_subsume_cs(amount_to_add, False,
                                                                               cutoff_lim=cutoff_lim,
                                                                               word_lim=word_lim)
        if sol['failed_converged']:
            new_row = pd.DataFrame([sol],
                                   columns=min_column)  # 'right_output'
            df = pd.concat([df if not df.empty else None, new_row], ignore_index=True)
            df.to_csv(f'BP_results_cs_subsumed_{name}_{version}_cutoff_20_45000.csv', index=False)
            continue

        learned_bp = BP_class(len(bp_acts), bp_acts, 0, bp_rec)
        sol['right_output'] = equivalent_bp(bp.bp, learned_bp, sol['cutoff'])
        print(f"scenario {scenario_num - 1}: the two BP's are equivalent?:",
              sol['right_output'])

        learned_bp = BP_class(len(bp_min_acts), bp_min_acts, 0, bp_min_rec)
        sol['minimal_right_output'] = equivalent_bp(bp.bp, learned_bp, sol['cutoff'])
        print(f"scenario {scenario_num - 1}: the two BP's are equivalent?: minimal:",
              sol['minimal_right_output'])
        new_row = pd.DataFrame([sol],
                               columns=min_column)
        df = pd.concat([df if not df.empty else None, new_row], ignore_index=True)
        df.to_csv(f'BP_results_cs_subsumed_{name}_{version}_cutoff_20_45000.csv', index=False)
    return


def generator_and_check_no_cs(words_to_add, amount_to_generate: int, min_number_of_states: int,
                              max_number_of_states: int, min_number_of_acts: int,
                              max_number_of_acts: int, version: int, name: str,
                              cutoff_lim=None, len_lim=None, minimal=False, pos_perc=None, to_print=True):
    scenario_num = 1
    if minimal:
        df = pd.DataFrame(columns=min_column)
    else:
        df = pd.DataFrame(columns=non_min_column)
    for i in range(amount_to_generate):
        number_of_states = random.randint(min_number_of_states, max_number_of_states)
        number_of_acts = random.randint(min_number_of_acts, max_number_of_acts)
        bp = BP_generator(number_of_states, number_of_acts)
        no_cutoff_for_sure = eliminate_no_cutoff(bp.bp, bp.bp.initial_state, 0)
        is_single_loop = single_loop(bp.bp)
        while no_cutoff_for_sure or is_single_loop:
            bp = BP_generator(number_of_states, number_of_acts)
            no_cutoff_for_sure = eliminate_no_cutoff(bp.bp, bp.bp.initial_state, 0)
            is_single_loop = single_loop(bp.bp)
        if to_print:
            print(f"scenario #{scenario_num}: {bp.bp}")
        scenario_num += 1
        learner = BP_run(bp.bp)
        bp_min_acts, bp_min_rec, bp_acts, bp_rec, sol, words_added = return_future(cutoff_lim, learner, len_lim,
                                                                                   minimal, pos_perc, words_to_add)

        if to_print:
            print(f"bp_min_acts {bp_min_acts},\n"
                  f"bp_min_rec {bp_min_rec},\n"
                  f"bp_acts {bp_acts},\n"
                  f"bp_rec {bp_rec}")
        if sol['failed_converged']:
            if minimal:
                new_row = pd.DataFrame([sol], columns=min_column)
            else:
                new_row = pd.DataFrame([sol], columns=non_min_column)
            df = pd.concat([df if not df.empty else None, new_row], ignore_index=True)
            df.to_csv(f'BP_results_no_cs_{name}_{version}_{str(words_to_add)} sample.csv', index=False)
            continue
        learned_bp = BP_class(len(bp_acts), bp_acts, 0, bp_rec)
        if to_print:
            print("bp_learned:", learned_bp)
        right_output = True
        if words_added['positive'] != dict():
            for n_c in words_added['positive']:
                for n_word in words_added['positive'][n_c]:
                    right_output &= learned_bp.is_feasible(n_c, list(n_word))
        if right_output:
            if words_added['negative'] != dict():
                for n_c in words_added['negative']:
                    for n_word in words_added['negative'][n_c]:
                        right_output &= not (learned_bp.is_feasible(n_c, list(n_word)))
        sol['right_output'] = right_output
        if to_print:
            print(f"scenario {scenario_num - 1}: the two BP's are equivalent?:", right_output)
        if minimal:
            learned_bp = BP_class(len(bp_min_acts), bp_min_acts, 0, bp_min_rec)
            if to_print:
                print("bp_learned:", learned_bp)
            right_output = True
            if words_added['positive'] != dict():
                for n_c in words_added['positive']:
                    for n_word in words_added['positive'][n_c]:
                        right_output &= learned_bp.is_feasible(n_c, list(n_word))
            if right_output:
                if words_added['negative'] != dict():
                    for n_c in words_added['negative']:
                        for n_word in words_added['negative'][n_c]:
                            right_output &= not (learned_bp.is_feasible(n_c, list(n_word)))
            sol['minimal_right_output'] = right_output
            if to_print:
                print(f"scenario {scenario_num - 1}: the two BP's are equivalent?: minimal:", right_output)
            new_row = pd.DataFrame([sol],
                                   columns=min_column)
        else:
            new_row = pd.DataFrame([sol],
                                   columns=non_min_column)
        df = pd.concat([df if not df.empty else None, new_row], ignore_index=True)
        df.to_csv(f'BP_results_no_cs_{name}_{version}_{str(words_to_add)} sample.csv', index=False)
    return


def return_future(cutoff_lim, learner, len_lim, minimal, pos_perc, words_to_add):
    if cutoff_lim is not None and len_lim is not None:
        if pos_perc is None:
            bp_min_acts, bp_min_rec, bp_acts, bp_rec, sol, words_added = learner.run_no_cs(words_to_add, False,
                                                                                           maximal_procs=cutoff_lim,
                                                                                           maximal_length=len_lim,
                                                                                           minimal=minimal)
        else:
            bp_min_acts, bp_min_rec, bp_acts, bp_rec, sol, words_added = learner.run_no_cs_pos_perc(words_to_add,
                                                                                                    pos_perc, len_lim,
                                                                                                    cutoff_lim, minimal)
    elif cutoff_lim is not None:
        if pos_perc is None:
            bp_min_acts, bp_min_rec, bp_acts, bp_rec, sol, words_added = learner.run_no_cs(words_to_add, False,
                                                                                           maximal_procs=cutoff_lim,
                                                                                           minimal=minimal)
        else:
            bp_min_acts, bp_min_rec, bp_acts, bp_rec, sol, words_added = learner.run_no_cs_pos_perc(words_to_add,
                                                                                                    pos_perc,
                                                                                                    procs_limit=cutoff_lim,
                                                                                                    minimal=minimal)
    elif len_lim is not None:
        if pos_perc is None:
            bp_min_acts, bp_min_rec, bp_acts, bp_rec, sol, words_added = learner.run_no_cs(words_to_add, False,
                                                                                           maximal_length=len_lim,
                                                                                           minimal=minimal)
        else:
            bp_min_acts, bp_min_rec, bp_acts, bp_rec, sol, words_added = learner.run_no_cs_pos_perc(words_to_add,
                                                                                                    pos_perc,
                                                                                                    length_limit=len_lim,
                                                                                                    minimal=minimal)
    else:
        if pos_perc is None:
            bp_min_acts, bp_min_rec, bp_acts, bp_rec, sol, words_added = learner.run_no_cs(words_to_add, False,
                                                                                           minimal=minimal)
        else:
            bp_min_acts, bp_min_rec, bp_acts, bp_rec, sol, words_added = learner.run_no_cs_pos_perc(words_to_add,
                                                                                                    pos_perc,
                                                                                                    minimal=minimal)
    return bp_min_acts, bp_min_rec, bp_acts, bp_rec, sol, words_added


def generator_and_check(amount_to_generate: int, min_number_of_states: int, max_number_of_states: int,
                        min_number_of_acts: int, max_number_of_acts: int, version: int, name: str):
    scenario_num = 1
    df = pd.DataFrame(
        columns=non_min_column)
    for i in range(amount_to_generate):
        number_of_states = random.randint(min_number_of_states, max_number_of_states)
        number_of_acts = random.randint(min_number_of_acts, max_number_of_acts)
        bp = BP_generator(number_of_states, number_of_acts)
        no_cutoff_for_sure = eliminate_no_cutoff(bp.bp, bp.bp.initial_state, 0)
        is_single_loop = single_loop(bp.bp)
        while no_cutoff_for_sure or is_single_loop:
            bp = BP_generator(number_of_states, number_of_acts)
            no_cutoff_for_sure = eliminate_no_cutoff(bp.bp, bp.bp.initial_state, 0)
            is_single_loop = single_loop(bp.bp)

        print(f"scenario #{scenario_num}: {bp.bp}")
        scenario_num += 1
        learner = BP_run(bp.bp)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(learner.run)
            try:
                result = future.result(timeout=one_hour)  # Set the desired timeout in seconds
                bp_acts, bp_rec, sol = result
            except concurrent.futures.TimeoutError:
                print("timeout")
                bp_acts, bp_rec, sol = bp.bp.actions, bp.bp.receivers, info_timeout(bp.bp, False)
            finally:
                if sol['failed_converged']:
                    new_row = pd.DataFrame([sol],
                                           columns=non_min_column)  # 'right_output'
                    df = pd.concat([df if not df.empty else None, new_row], ignore_index=True)
                    df.to_csv(f'BP_results_full_cs_2_{name}_{version}.csv', index=False)
                    continue
                learned_bp = BP_class(len(bp_acts), bp_acts, 0, bp_rec)
                sol['right_output'] = equivalent_bp(bp.bp, learned_bp, sol['cutoff'])
                print(f"scenario {scenario_num - 1}: the two BP's are equivalent?:",
                      equivalent_bp(bp.bp, learned_bp, sol['cutoff']))
                new_row = pd.DataFrame([sol], columns=non_min_column)  # 'right_output'
                df = pd.concat([df if not df.empty else None, new_row], ignore_index=True)
                df.to_csv(f'BP_results_full_cs_2_{name}_{version}.csv', index=False)
    return


''' 
    If you want to generate a batch, as we did in the experiments you can use the following function, 
    please take under account that it might take a long time as well as uses of CPU and memory 
'''
for fw in [10, 20]:  # fw is amount of words to add
    pr = 0.1
    # if you want to define the positive ratio you can call the next function:
    # generator_and_check_no_cs(fw, 50, 2, 4, 0, 2, 2, "bps_batch", 15, 20, pos_perc=pr, to_print=False)

    # if you want to see the printing while the inference procedure occurs you can change to_print to be True
    # (instead of False) or vice versa

    # If you want to check for both BPInf and BPInfMin please use "minimal=True"
    # If you want to check only BPInf please use "minimal=False"

    # An example for both positive percent being given and BPInfMin being generated:
    #     generator_and_check_no_cs(fw, 50, 2, 5, 0, 3, 3, "bps_batch", 15, 20, pos_perc=pr, minimal=True)

    generator_and_check_no_cs(fw, 10, 2, 5, 0, 3, 4, "bps_batch", 15, 20)

pass
