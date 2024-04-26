from BP_Class import BP_class
import time
import pandas as pd
import ast

from BP_Run import BP_run
from BP_gen import equivalent_bp, BP_generator

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


def test_is_correct_non_cs(bp_acts, bp_rec, bp_min_acts, bp_min_rec, words_added, solution, minimal):
    learned_bp = BP_class(len(bp_acts), bp_acts, 0, bp_rec)
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
    solution['right_output'] = right_output
    print(f"Are the two BP's are equivalent?:", right_output)
    if minimal:
        learned_bp = BP_class(len(bp_min_acts), bp_min_acts, 0, bp_min_rec)
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
        solution['minimal_right_output'] = right_output
        print(f"Are the two BP's are equivalent?: Minimal", right_output)
        new_row = pd.DataFrame([solution], columns=min_column)
    else:
        new_row = pd.DataFrame([solution], columns=non_min_column)
    return new_row


def run_a_given_bp_example(bp_example, name, is_partial):
    """
    :param bp_example: The Bp we test for
    :param name: File name, where the results will be saved
    :param is_partial: Whether we run for CS or for Random Generated sample
    :return:
    """
    # start = time.perf_counter()
    if is_partial:
        df1 = pd.DataFrame(columns=min_column)
    else:
        df1 = pd.DataFrame(columns=non_min_column)
    cutoff = 15
    timer_c = 900  # 15 min in seconds
    max_len = 15

    learner = BP_run(bp_example)
    minimal = is_partial
    if is_partial:
        bp_min_acts, bp_min_rec, bp_acts, bp_rec, sol, add_words = learner.run_no_cs(10, False, cutoff, max_len,
                                                                                     minimal)
    else:
        bp_min_acts, bp_min_rec, bp_acts, bp_rec, sol = learner.run_subsume_cs(0, False, cutoff, word_lim=1500)
    if sol['failed_converged']:
        if is_partial:
            new_row1 = pd.DataFrame([sol], columns=min_column)
            df1 = pd.concat([df1 if not df1.empty else None, new_row1], ignore_index=True)
            df1.to_csv(f'BP_results_non_cs_{name}.csv', index=False)
        else:
            new_row1 = pd.DataFrame([sol], columns=non_min_column)
            df1 = pd.concat([df1 if not df1.empty else None, new_row1], ignore_index=True)
            df1.to_csv(f'BP_results_subsume_cs_{name}.csv', index=False)
        print(f"The random generated BP has either no cutoff or it is greater then {cutoff} "
              f"or one of the other parameters exceeded")
    else:
        if is_partial:
            new_row1 = test_is_correct_non_cs(bp_acts, bp_rec, bp_min_acts, bp_min_rec, add_words, sol, minimal)
            df1 = pd.concat([df1 if not df1.empty else None, new_row1], ignore_index=True)
            df1.to_csv(f'BP_results_non_cs_{name}.csv', index=False)
        else:
            bp_learned = BP_class(len(bp_acts), bp_acts, 0, bp_rec)
            sol['right_output'] = equivalent_bp(bp_example, bp_learned, sol['cutoff'])
            print(f"Are the two BP's are equivalent?:", sol['right_output'])
            new_row1 = pd.DataFrame([sol], columns=non_min_column)
            df1 = pd.concat([df1 if not df1.empty else None, new_row1], ignore_index=True)
            df1.to_csv(f'BP_results_subsume_cs_{name}.csv', index=False)
        # end = time.perf_counter()
        # print(f"example {name} took {end - start} sec")
        pass


def run_a_random_bp_example(minimal=False):
    """
    Whether we want to run BPInf or BPInfMin
    :param minimal:
    :return:
    """
    if minimal:
        df2 = pd.DataFrame(columns=min_column)
    else:
        df2 = pd.DataFrame(columns=non_min_column)
    cutoff = 15
    timer_c = 900  # 15 min in seconds
    word_lim = 1500
    bp_2 = BP_generator(3, 1, max_number_of_act=2)
    learner = BP_run(bp_2.bp)
    bp_min_acts, bp_min_rec, bp_acts, bp_rec, sol = learner.run_subsume_cs(0, False, cutoff, timer_c,
                                                                           word_lim=word_lim, minimal=minimal)

    if sol['failed_converged']:
        if minimal:
            new_row2 = pd.DataFrame([sol], columns=min_column)
        else:
            new_row2 = pd.DataFrame([sol], columns=non_min_column)
        df2 = pd.concat([df2 if not df2.empty else None, new_row2], ignore_index=True)
        df2.to_csv(f'BP_results_cs_subsumed.csv', index=False)
        print(f"The random generated BP has either no cutoff or it is greater then {cutoff} "
              f"or one of the other parameters exceeded")
    else:
        bp_learned = BP_class(len(bp_acts), bp_acts, 0, bp_rec)
        sol['right_output'] = equivalent_bp(bp_2.bp, bp_learned, sol['cutoff'])
        print(f"Are the two BP's are equivalent?:", sol['right_output'])

        if minimal:
            bp_learned = BP_class(len(bp_min_acts), bp_min_acts, 0, bp_min_rec)
            sol['minimal_right_output'] = equivalent_bp(bp_2.bp, bp_learned, sol['cutoff'])
            print(f"Are the two BP's are equivalent?: minimal:", sol['minimal_right_output'])
        if minimal:
            new_row2 = pd.DataFrame([sol], columns=min_column)
        else:
            new_row2 = pd.DataFrame([sol], columns=non_min_column)
        df2 = pd.concat([df2 if not df2.empty else None, new_row2], ignore_index=True)
        df2.to_csv(f'BP_results_cs_subsumed.csv', index=False)
        pass

    """ 
    Several examples you can run, 5 for a given BP and one random 
    For each of the 5 given BP we run once for CS generation and once for a random sample of 20 words up to length 20
    """


bp1 = BP_class(3, {0: {'a': 2}, 1: {'b': 1}, 2: {'c': 1}}, 0,
               {0: {'a': 1, 'b': 0, 'c': 2}, 1: {'a': 0, 'b': 1, 'c': 1}, 2: {'a': 2, 'b': 1, 'c': 1}})
bp2 = BP_class(3, {0: {'a': 0, 'd': 0}, 1: {'b': 0}, 2: {'c': 2, 'e': 2}}, 0,
               {0: {'a': 0, 'b': 0, 'c': 1, 'd': 0, 'e': 1},
                1: {'a': 0, 'b': 2, 'c': 1, 'd': 2, 'e': 1},
                2: {'a': 1, 'b': 1, 'c': 0, 'd': 1, 'e': 0}})
bp3 = BP_class(2, {0: {'a': 0}, 1: {'b': 1, 'c': 1}}, 0, {0: {'a': 1, 'b': 1, 'c': 1}, 1: {'a': 0, 'b': 1, 'c': 1}})
bp4 = BP_class(2, {0: {'a': 0}, 1: {'b': 1, 'c': 1, 'd': 0}}, 0,
               {0: {'a': 1, 'b': 0, 'c': 0, 'd': 0}, 1: {'a': 1, 'b': 0, 'c': 0, 'd': 0}})
bp5 = BP_class(2, {0: {'a': 1}, 1: {'b': 0}}, 0, {0: {'a': 1, 'b': 0}, 1: {'a': 1, 'b': 0}})

for partial in [True, False]:
    run_a_given_bp_example(bp1, "1", partial)
    run_a_given_bp_example(bp2, "2", partial)
    run_a_given_bp_example(bp3, "3", partial)
    run_a_given_bp_example(bp4, "4", partial)
    run_a_given_bp_example(bp5, "5", partial)

"""
Another example you may run, because it is randomly generated it might take more or less in each time it executed
"""
# run_a_random_bp_example()
