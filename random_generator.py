import random

import pandas as pd

from BP_Class import BP_class
from BP_run import BP_run

from BP_gen import BP_generator, act_names, equivalent_bp, amount_of_actions, single_loop, eliminate_no_cutoff

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
    :param words_to_add: to padded the return CS according to the algorithm
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
    scenario_number = 1
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

        print(f"scenario #{scenario_number}: {bp.bp}")
        scenario_number += 1

        learner = BP_run(bp.bp)
        amount_to_add = random.randint(1, max(words_to_add, 2))
        bp_min_acts, bp_min_rec, bp_acts, bp_rec, solution = learner.run_subsume_cs(amount_to_add, False,
                                                                                    cutoff_lim=cutoff_lim,
                                                                                    word_lim=word_lim)
        if solution['failed_converged']:
            new_row = pd.DataFrame([solution],
                                   columns=min_column)  # 'right_output'
            df = pd.concat([df if not df.empty else None, new_row], ignore_index=True)
            df.to_csv(f'BP_results_cs_subsumed_{name}_{version}_cutoff_20_45000.csv', index=False)
            continue

        bp_learned = BP_class(len(bp_acts), bp_acts, 0, bp_rec)
        solution['right_output'] = equivalent_bp(bp.bp, bp_learned, solution['cutoff'])
        print(f"scenario {scenario_number - 1}: the two BP's are equivalent?:",
              solution['right_output'])

        bp_learned = BP_class(len(bp_min_acts), bp_min_acts, 0, bp_min_rec)
        solution['minimal_right_output'] = equivalent_bp(bp.bp, bp_learned, solution['cutoff'])
        print(f"scenario {scenario_number - 1}: the two BP's are equivalent?: minimal:",
              solution['minimal_right_output'])
        new_row = pd.DataFrame([solution],
                               columns=min_column)
        df = pd.concat([df if not df.empty else None, new_row], ignore_index=True)
        df.to_csv(f'BP_results_cs_subsumed_{name}_{version}_cutoff_20_45000.csv', index=False)
    return


def generator_and_check_no_cs(words_to_add: int, amount_to_generate: int, min_number_of_states: int,
                              max_number_of_states: int, min_number_of_acts: int,
                              max_number_of_acts: int, version: int, name: str,
                              cutoff_lim=None, len_lim=None, minimal=False, pos_perc=None):
    scenario_number = 1
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

        print(f"scenario #{scenario_number}: {bp.bp}")
        scenario_number += 1
        learner = BP_run(bp.bp)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = return_feuture(cutoff_lim, executor, learner, len_lim, minimal, pos_perc, words_to_add)
            try:
                result = future.result(timeout=one_hour)  # Set the desired timeout in seconds
                bp_min_acts, bp_min_rec, bp_acts, bp_rec, solution, words_added = result
                print(f"bp_min_acts {bp_min_acts},\n"
                      f"bp_min_rec {bp_min_rec},\n"
                      f"bp_acts {bp_acts},\n"
                      f"bp_rec {bp_rec}")
            except concurrent.futures.TimeoutError:
                print("timeouted")
                bp_acts, bp_rec, solution, words_added = bp.bp.actions, bp.bp.receivers, info_timeout(bp.bp, minimal), \
                                                         {'positive': {}, 'negative': {}}
            finally:
                if solution['failed_converged']:
                    if minimal:
                        new_row = pd.DataFrame([solution], columns=min_column)
                    else:
                        new_row = pd.DataFrame([solution], columns=non_min_column)
                    df = pd.concat([df if not df.empty else None, new_row], ignore_index=True)
                    df.to_csv(f'BP_results_no_cs_{name}_{version}_{str(words_to_add)} sample.csv', index=False)
                    continue
                bp_learned = BP_class(len(bp_acts), bp_acts, 0, bp_rec)
                print("bp_learned:", bp_learned)
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
                solution['right_output'] = right_output
                print(f"scenario {scenario_number - 1}: the two BP's are equivalent?:",
                      right_output)
                if minimal:
                    bp_learned = BP_class(len(bp_min_acts), bp_min_acts, 0, bp_min_rec)
                    print("bp_learned:", bp_learned)
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
                    print(f"scenario {scenario_number - 1}: the two BP's are equivalent?:",
                          right_output)
                    new_row = pd.DataFrame([solution],
                                           columns=min_column)
                else:
                    new_row = pd.DataFrame([solution],
                                           columns=non_min_column)
                df = pd.concat([df if not df.empty else None, new_row], ignore_index=True)
                df.to_csv(f'BP_results_no_cs_{name}_{version}_{str(words_to_add)} sample.csv', index=False)
    return


def return_feuture(cutoff_lim, executor, learner, len_lim, minimal, pos_perc, words_to_add):
    if cutoff_lim is not None and len_lim is not None:
        if pos_perc is None:
            future = executor.submit(learner.run_no_cs, words_to_add, False, maximal_procs=cutoff_lim,
                                     maximal_length=len_lim, minimal=minimal)
        else:
            future = executor.submit(learner.run_no_cs_pos_perc, words_to_add, pos_perc, len_lim, cutoff_lim,
                                     minimal)

    elif cutoff_lim is not None:
        if pos_perc is None:
            future = executor.submit(learner.run_no_cs, words_to_add, False, maximal_procs=cutoff_lim,
                                     minimal=minimal)
        else:
            future = executor.submit(learner.run_no_cs_pos_perc, words_to_add, pos_perc, procs_limit=cutoff_lim,
                                     minimal=minimal)
    elif len_lim is not None:
        if pos_perc is None:
            future = executor.submit(learner.run_no_cs, words_to_add, False, maximal_length=len_lim,
                                     minimal=minimal)
        else:
            future = executor.submit(learner.run_no_cs_pos_perc, words_to_add, pos_perc, length_limit=len_lim,
                                     minimal=minimal)
    else:
        if pos_perc is None:
            future = executor.submit(learner.run_no_cs, words_to_add, False, minimal=minimal)
        else:
            future = executor.submit(learner.run_no_cs_pos_perc, words_to_add, pos_perc, minimal=minimal)
    return future


def generator_and_check(amount_to_generate: int, min_number_of_states: int, max_number_of_states: int,
                        min_number_of_acts: int, max_number_of_acts: int, version: int, name: str):
    scenario_number = 1
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

        print(f"scenario #{scenario_number}: {bp.bp}")
        scenario_number += 1
        learner = BP_run(bp.bp)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(learner.run)
            try:
                result = future.result(timeout=one_hour)  # Set the desired timeout in seconds
                bp_acts, bp_rec, solution = result
            except concurrent.futures.TimeoutError:
                print("timeouted")
                bp_acts, bp_rec, solution = bp.bp.actions, bp.bp.receivers, info_timeout(bp.bp, False)
            finally:
                if solution['failed_converged']:
                    new_row = pd.DataFrame([solution],
                                           columns=non_min_column)  # 'right_output'
                    df = pd.concat([df if not df.empty else None, new_row], ignore_index=True)
                    df.to_csv(f'BP_results_full_cs_2_{name}_{version}.csv', index=False)
                    continue
                bp_learned = BP_class(len(bp_acts), bp_acts, 0, bp_rec)
                solution['right_output'] = equivalent_bp(bp.bp, bp_learned, solution['cutoff'])
                print(f"scenario {scenario_number - 1}: the two BP's are equivalent?:",
                      equivalent_bp(bp.bp, bp_learned, solution['cutoff']))
                new_row = pd.DataFrame([solution],
                                       columns=non_min_column)  # 'right_output'
                df = pd.concat([df if not df.empty else None, new_row], ignore_index=True)
                df.to_csv(f'BP_results_full_cs_2_{name}_{version}.csv', index=False)
    return


# if __name__ == "__main__":
# generator_and_check_line_family(10)
#     args = sys.argv[1:]
#     generator_and_check(200, 2, 6, 1, 5, 1, str(args[0]))
#     generator_and_check(200, 2, 8, 1, 2, 2, str(args[0]))
#     generator_and_check(200, 2, 5, 0, 2, 3, str(args[0]))
# generator_and_check(5000, 4, 5, 1, 3, 1, "bp8")
# generator_and_check_line_family(20)
# generator_and_check_line_family(10)

# TO RUN FROM HERE:
# generator_and_check(50, 2, 10, 1, 4, 3, "new full cs 2-10-1-4 cutoff20 time120 25-12-23")


def run_a_given_bp_example(bp_example):
    df = pd.DataFrame(columns=non_min_column)
    cutoff = 15
    timer_c = 900  # 15 min in seconds
    # bp = BP_generator(3, 1, max_number_of_act=2)
    learner = BP_run(bp_example)
    bp_min_acts, bp_min_rec, bp_acts, bp_rec, solution = learner.run_subsume_cs(0, False, cutoff, timer_c,
                                                                                word_lim=1500)
    if solution['failed_converged']:
        new_row = pd.DataFrame([solution],
                               columns=min_column)  # 'right_output'
        df = pd.concat([df if not df.empty else None, new_row], ignore_index=True)
        df.to_csv(f'BP_results_no_cs.csv', index=False)
        print(f"The random generated BP has either no cutoff or it is greater then {cutoff} "
              f"or one of the other parameters exceeded")
    else:
        bp_learned = BP_class(len(bp_acts), bp_acts, 0, bp_rec)
        solution['right_output'] = equivalent_bp(bp_example, bp_learned, solution['cutoff'])
        print(f"Are the two BP's are equivalent?:",
              solution['right_output'])
        new_row = pd.DataFrame([solution],
                               columns=min_column)
        df = pd.concat([df if not df.empty else None, new_row], ignore_index=True)
        df.to_csv(f'BP_results_no_cs.csv', index=False)
        pass


bp = BP_class(2, {0: {'a': 1}, 1: {'b': 0}}, 0, {0: {'a': 1, 'b': 0}, 1: {'a': 1, 'b': 0}})


# run_a_given_bp_example(bp)


def run_a_random_bp_example(minimal=False):
    """
    Whether we want to run BPInf or BPInfMin
    :param minimal:
    :return:
    """
    if minimal:
        df = pd.DataFrame(columns=min_column)
    else:
        df = pd.DataFrame(columns=non_min_column)
    cutoff = 15
    timer_c = 900  # 15 min in seconds
    word_lim = 1500
    bp = BP_generator(3, 1, max_number_of_act=2)
    learner = BP_run(bp.bp)
    bp_min_acts, bp_min_rec, bp_acts, bp_rec, solution = learner.run_subsume_cs(0, False, cutoff, timer_c,
                                                                                word_lim=word_lim, minimal=minimal)

    if solution['failed_converged']:
        if minimal:
            new_row = pd.DataFrame([solution], columns=min_column)
        else:
            new_row = pd.DataFrame([solution], columns=non_min_column)
        df = pd.concat([df if not df.empty else None, new_row], ignore_index=True)
        df.to_csv(f'BP_results_cs_subsumed.csv', index=False)
        print(f"The random generated BP has either no cutoff or it is greater then {cutoff} "
              f"or one of the other parameters exceeded")
    else:
        bp_learned = BP_class(len(bp_acts), bp_acts, 0, bp_rec)
        solution['right_output'] = equivalent_bp(bp.bp, bp_learned, solution['cutoff'])
        print(f"Are the two BP's are equivalent?:", solution['right_output'])

        if minimal:
            bp_learned = BP_class(len(bp_min_acts), bp_min_acts, 0, bp_min_rec)
            solution['minimal_right_output'] = equivalent_bp(bp.bp, bp_learned, solution['cutoff'])
            print(f"Are the two BP's are equivalent?: minimal:", solution['minimal_right_output'])
        if minimal:
            new_row = pd.DataFrame([solution], columns=min_column)
        else:
            new_row = pd.DataFrame([solution], columns=non_min_column)
        df = pd.concat([df if not df.empty else None, new_row], ignore_index=True)
        df.to_csv(f'BP_results_cs_subsumed.csv', index=False)
        pass


run_a_random_bp_example()

bp = BP_class(4, {0: {'a': 0, 'e': 2}, 1: {'b': 1}, 2: {'c': 1}, 3: {'d': 0}}, 0,
              {0: {'a': 1, 'b': 1, 'c': 3, 'd': 3, 'e': 1},
               1: {'a': 0, 'b': 2, 'c': 1, 'd': 3, 'e': 0},
               2: {'a': 2, 'b': 2, 'c': 1, 'd': 0, 'e': 3},
               3: {'a': 3, 'b': 0, 'c': 0, 'd': 0, 'e': 2}})
pass
