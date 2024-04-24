import sys

import pandas as pd

import ast

from BP_Class import *

import re

from BP_Run import BP_run

non_min_column = ['failed_converged', 'timeout', 'amount_of_states_in_origin',
                  'amount_of_states_in_output', 'origin_BP', 'output_BP', 'cutoff',
                  'CS_development_time',
                  'CS_positive_size', 'CS_negative_size', 'words_added',
                  'longest_word_in_CS', 'solve_SMT_time',
                  'right_output']


def generator_given_bp_and_sample(num_states, actions_dict, initial_state, receivers_dict,
                                  pos_dict, neg_dict, to_print=True, scenario_num=1):
    bp = BP_class(num_states, actions_dict, initial_state, receivers_dict)
    if to_print:
        print(f"scenario #{scenario_num}: {bp}")
    scenario_num += 1
    learner = BP_run(bp)
    given_words = {'positive': pos_dict, 'negative': neg_dict}
    bp_min_acts, bp_min_rec, bp_acts, bp_rec, sol, words_added = learner.run_no_cs(given_words, True)
    if to_print:
        print(f"bp_min_acts {bp_min_acts},\n"
              f"bp_min_rec {bp_min_rec},\n"
              f"bp_acts {bp_acts},\n"
              f"bp_rec {bp_rec}")
    if sol['failed_converged']:
        new_row = pd.DataFrame([sol], columns=non_min_column)
        return new_row
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
    new_row = pd.DataFrame([sol], columns=non_min_column)
    return new_row


def parse_template(template):
    """ Use regular expressions to extract information from the template """
    states_match = re.search(r"states: (\d+),\n ", template)
    if states_match:
        num_states = int(states_match.group(1))
    else:
        num_states = None

    actions_match = re.search(r"actions: ({(?:\d+: {(?:'\w': \d,? *)+},? *)+}),\n", template)
    if actions_match:
        actions_dict_str = actions_match.group(1)
        actions_dict = ast.literal_eval(actions_dict_str)  # Safely convert string to dictionary using ast.literal_eval
    else:
        actions_dict = None

    initial_match = re.search(r"initial: (\d+),\n", template)
    if initial_match:
        initial_state = int(initial_match.group(1))
    else:
        initial_state = None

    receivers_match = re.search(r"receivers: ({(?:\d+: {(?:'\w': \d,? *)+},? *)+})", template)
    if receivers_match:
        receivers_dict_str = receivers_match.group(1)
        receivers_dict = ast.literal_eval(
            receivers_dict_str)  # Safely convert string to dictionary using ast.literal_eval
    else:
        receivers_dict = None

    return num_states, actions_dict, initial_state, receivers_dict


def parse_words(template):
    words_match = re.search(r"'positive': ({[^}]+}),\s+'negative': ({[^}]+})", template)
    if words_match:
        positive_words_str = words_match.group(1)
        negative_words_str = words_match.group(2)
        positive_words_dict = ast.literal_eval(positive_words_str)  # Convert positive words string to dictionary
        negative_words_dict = ast.literal_eval(negative_words_str)  # Convert negative words string to dictionary
    else:
        positive_words_dict = None
        negative_words_dict = None
    return positive_words_dict, negative_words_dict


def replicate_experimental_results(name, to_print=False, subset_size=None):
    """
    Will take the file (i.e. results.csv) under Results folder and inference for the given BPs
    """
    file_path = './Results/results.csv'
    data = pd.DataFrame()
    df_origin = pd.read_csv(file_path)
    df1 = df_origin.copy()
    data = pd.concat([data, df1])

    data = data.drop_duplicates()
    data = data.drop_duplicates(subset=['origin_BP', 'output_BP', 'words_added'])

    data_origin = data['origin_BP'].copy()
    data_words = data['words_added'].copy()

    df = pd.DataFrame(columns=non_min_column)

    length = len(data)
    if subset_size is not None:
        length = subset_size
    for i in range(length):
        template_string = data_origin.iloc[i]
        num_states, actions_dict, initial_state, receivers_dict = parse_template(template_string)
        template_string = data_words.iloc[i]
        pos, neg = parse_words(template_string)

        new_r = generator_given_bp_and_sample(num_states, actions_dict, initial_state, receivers_dict, pos, neg,
                                              to_print=to_print, scenario_num=i)
        df = pd.concat([df if not df.empty else None, new_r], ignore_index=True)

        df.to_csv(f'{name}.csv', index=False)


"""
In order to reproduce the results for the first 5 BPs in the sample
If you want all of them just remove the last parameter, i.e.:
replicate_experimental_results("results_infer", True)

Please note that it will take several days and alot of computerized power
"""
# For running in pycharm environment instead of docker, comment the main part and uncomment the row below
# replicate_experimental_results("results_infer", True, 5)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python ReplicateExperimentalResults.py <arg1>,\n"
              "Please provide an argument, 1 for a representative subset and 0 for full evaluation")
        pass
    else:
        arg1 = sys.argv[1]

        if arg1 == '1':
            replicate_experimental_results("results_infer", True, 5)
        elif arg1 == '0':
            replicate_experimental_results("results_infer", True)
        else:
            print("Please enter 1 for a representative subset and 0 for full evaluation")
    pass
