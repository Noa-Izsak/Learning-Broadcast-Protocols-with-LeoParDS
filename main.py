import ast

import numpy as np

font = 12


def plot_6_a(data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x = data['amount_of_states_in_origin'].values.tolist()
    y = data['amount_of_states_in_output'].values.tolist()
    c = data['CS_size'].values.tolist()
    z = data['solve_SMT_time'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, z,
                         c=c, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='#words in the sample')
    # Adjust the limits of the z-axis if necessary
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    plt.xlabel('#states in original bp', fontsize=font)
    plt.ylabel('#states in agreeing bp', fontsize=font)
    ax.set_zlabel('SMT duration (sec)', fontsize=font)
    plt.savefig('plot 6(a).png')
    pass

def plot_6_b(selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    y = selected_data['CS_size'].values.tolist()
    x = selected_data['amount_of_states_in_origin'].values.tolist()
    c = selected_data['CS_size'].values.tolist()
    z = selected_data['solve_SMT_time'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, z,
                         c=c, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='#words in the sample')
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    plt.xlabel('#states', fontsize=font)
    plt.ylabel('#words in the sample', fontsize=font)
    ax.set_zlabel('SMT duration (sec)', fontsize=font)
    plt.savefig('plot 6(b).png')
    pass


def plot_7_a(selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    y = selected_data['amount_of_actions'].values.tolist()
    x = selected_data['amount_of_states_in_origin'].values.tolist()
    c = selected_data['CS_size'].values.tolist()
    z = selected_data['solve_SMT_time'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, z,
                         c=c, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='#words in the sample')
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    plt.xlabel('#states', fontsize=font)
    plt.ylabel('#actions', fontsize=font)
    ax.set_zlabel('SMT duration (sec)', fontsize=font)
    plt.savefig('plot 7(a).png')
    plt.show()
    pass


def plot_7_b(data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    y = data['CS_negative_size'].values.tolist()
    x = data['CS_positive_size'].values.tolist()
    c = data['CS_size'].values.tolist()
    z = data['solve_SMT_time'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, z,
                         c=c, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='#words in the sample')
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    plt.xlabel('#positive words in the sample', fontsize=font)
    plt.ylabel('#negative words in the sample', fontsize=font)
    ax.set_zlabel('SMT duration (sec)', fontsize=font)
    plt.savefig('plot 7(b).png')
    pass


def plot4(data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    y = data['positive_ratio'].values.tolist()
    x = data['amount_of_states_in_origin'].values.tolist()
    c = data['CS_size'].values.tolist()
    z = data['solve_SMT_time'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, z,
                         c=c, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='#words in the sample')
    # Adjust the limits of the z-axis if necessary
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    plt.xlabel('#states', fontsize=font)
    plt.ylabel('positive ratio', fontsize=font)
    ax.set_zlabel('SMT duration (sec)', fontsize=font)
    pass


def states_amount_positive_sample_plot(selected_data):

    scatter = plt.scatter(selected_data['amount_of_states_in_origin'].values.tolist(),
                          selected_data['amount_of_states_in_output'].values.tolist(),
                          selected_data['CS_size'].values.tolist(),
                          c=selected_data['CS_size'].values.tolist(), cmap='viridis')
    plt.xlabel('#states in original bp', fontsize=font)
    plt.ylabel('#states in agreeing bp', fontsize=font)
    plt.show()


def plot11(selected_data):
    scatter = plt.scatter(selected_data['amount_of_states_in_origin'].values.tolist(),
                          selected_data['solve_SMT_time'].values.tolist(),
                          c=selected_data['CS_size'].values.tolist(), cmap='viridis')
    cbar = plt.colorbar(scatter)
    cbar.set_label('#words in the sample')
    plt.xlabel('#states in original bp')
    plt.ylabel('Solving SMT duration (sec)')
    plt.show()


def plot11_2(selected_data):
    scatter = plt.scatter(selected_data['amount_of_states_in_origin'].values.tolist(),
                          selected_data['solve_SMT_time'].values.tolist(),
                          c=selected_data['amount_of_states_in_origin'].values.tolist(), cmap='viridis')
    cbar = plt.colorbar(scatter)
    cbar.set_label('#states in original bp')
    plt.xlabel('#states in original bp')
    plt.ylabel('Solving SMT duration (sec)')
    plt.show()


def plot22(selected_data):
    scatter = plt.scatter(selected_data['CS_size'].values.tolist(),
                          selected_data['solve_SMT_time'].values.tolist(),
                          c=selected_data['CS_size'].values.tolist(), cmap='viridis')
    cbar = plt.colorbar(scatter)
    cbar.set_label('#words in the sample')
    plt.xlabel('#words in the sample')
    plt.ylabel('Solving SMT duration (sec)')
    plt.show()
    pass


def plot22_2(selected_data):
    """ fig 6(A) in the paper"""
    scatter = plt.scatter(selected_data['CS_size'].values.tolist(),
                          selected_data['solve_SMT_time'].values.tolist(),
                          c=selected_data['amount_of_states_in_origin'].values.tolist(), cmap='viridis')
    cbar = plt.colorbar(scatter)
    cbar.set_label('#states in original bp')
    plt.xlabel('#words in the sample')
    plt.ylabel('Solving SMT duration (sec)')
    plt.show()
    pass


def plot33(selected_data):
    scatter = plt.scatter(selected_data['amount_of_actions'].values.tolist(),
                          selected_data['solve_SMT_time'].values.tolist(),
                          c=selected_data['CS_size'].values.tolist(), cmap='viridis')
    cbar = plt.colorbar(scatter)
    cbar.set_label('#words in the sample')
    plt.xlabel('#actions in original bp')
    plt.ylabel('Solving SMT duration (sec)')
    plt.show()
    pass


def plot33_2(selected_data):
    scatter = plt.scatter(selected_data['amount_of_actions'].values.tolist(),
                          selected_data['solve_SMT_time'].values.tolist(),
                          c=selected_data['amount_of_states_in_origin'].values.tolist(), cmap='viridis')
    cbar = plt.colorbar(scatter)
    cbar.set_label('#states in original bp')
    plt.xlabel('#actions in original bp')
    plt.ylabel('Solving SMT duration (sec)')
    plt.show()


def extract_inner_keys(input_string):
    actions_index = input_string.find("actions: ")

    comma_newline_index = input_string.find(",\n", actions_index)

    actions_substring = input_string[actions_index + len("actions: "):comma_newline_index]

    actions_dict = ast.literal_eval(actions_substring)

    inner_keys = set()
    for _, inner_dict in actions_dict.items():
        inner_keys.update(inner_dict.keys())

    return len(inner_keys)


def smt_duration_percentage(sd, a, b):
    column_name = 'solve_SMT_time'
    within_range_count = np.sum((sd[column_name] >= a) & (sd[column_name] < b))
    print("the within range count:", within_range_count)
    # Calculate the percentage
    percentage_within_range = (within_range_count / len(sd)) * 100
    print(f"Percentage of smt duration in the range [{a}, {b}): {percentage_within_range:.2f}%")
    pass


def positive_percentage(sd, a, b):
    column_name = 'positive_ratio'
    within_range_count = np.sum((sd[column_name] >= a) & (sd[column_name] < b))
    print("the within range count:", within_range_count)
    # Calculate the percentage
    percentage_within_range = (within_range_count / len(sd)) * 100

    print(f"Percentage positive_ratio of samples in the range [{a}, {b}): {percentage_within_range:.2f}%")
    pass


def positive_percentage2(sd, a, b):
    column_name = 'positive_ratio'
    within_range_count = np.sum((sd[column_name] >= a) & (sd[column_name] <= b))
    print("the within range count:", within_range_count)
    # Calculate the percentage
    percentage_within_range = (within_range_count / len(sd)) * 100

    print(f"Percentage positive_ratio of samples in the range [{a}, {b}]: {percentage_within_range:.2f}%")
    pass


def num_states_percentage(sd, a, b):
    column_name = 'amount_of_states_in_origin'
    within_range_count = np.sum((sd[column_name] >= a) & (sd[column_name] < b))
    print("the within range count:", within_range_count)
    # Calculate the percentage
    percentage_within_range = (within_range_count / len(sd)) * 100

    print(f"Percentage amount_of_states_in_origin of samples in the range [{a}, {b}): {percentage_within_range:.2f}%")
    pass


def num_states_percentage2(sd, a, b):
    column_name = 'amount_of_states_in_origin'
    within_range_count = np.sum((sd[column_name] >= a) & (sd[column_name] <= b))
    print("the within range count:", within_range_count)
    # Calculate the percentage
    percentage_within_range = (within_range_count / len(sd)) * 100

    print(f"Percentage amount_of_states_in_origin of samples in the range [{a}, {b}]: {percentage_within_range:.2f}%")
    pass


def sample_size_percentage(sd, a, b):
    column_name = 'CS_size'
    within_range_count = np.sum((sd[column_name] >= a) & (sd[column_name] < b))
    print("the within range count:", within_range_count)
    # Calculate the percentage
    percentage_within_range = (within_range_count / len(sd)) * 100

    print(f"Percentage sample_size of samples in the range [{a}, {b}): {percentage_within_range:.2f}%")
    pass


def sample_size_percentage2(sd, a, b):
    column_name = 'CS_size'
    within_range_count = np.sum((sd[column_name] >= a) & (sd[column_name] <= b))
    print("the within range count:", within_range_count)
    # Calculate the percentage
    percentage_within_range = (within_range_count / len(sd)) * 100

    print(f"Percentage sample_size of samples in the range [{a}, {b}]: {percentage_within_range:.2f}%")
    pass


def no_cs_pos_perc_printing():
    file_path = './Results/results.csv'
    data = pd.DataFrame()
    df_origin = pd.read_csv(file_path)
    df1 = df_origin.copy()
    data = pd.concat([data, df1])
    data = data.drop_duplicates()
    print(f"in min version there are : {len(data['solve_SMT_time'])}")

    data = data.drop_duplicates(subset=['origin_BP', 'output_BP', 'words_added'])
    print(f"in total there are : {len(data['solve_SMT_time'])}")

    data['amount_of_actions'] = data['origin_BP'].apply(extract_inner_keys)

    data['CS_size'] = data['CS_positive_size'] + data['CS_negative_size']

    data['positive_ratio'] = (100 * data['CS_positive_size']) // data['CS_size']

    """The statistical info in the Table"""
    print_info(data)

    data = data.loc[:, ['amount_of_states_in_origin', 'amount_of_states_in_output', 'origin_BP', 'output_BP', 'CS_size',
                        'CS_positive_size', 'CS_negative_size', 'words_added',
                        'longest_word_in_CS', 'CS_development_time', 'solve_SMT_time',
                        'amount_of_actions', 'positive_ratio']]

    """ Plot 6(a) in the paper"""
    plot_6_a(data)

    """ Plot 6(b) in the paper"""
    plot_6_b(data)

    """ Plot 7(b) in the paper"""
    plot_7_b(data)

    """ Plot 7(a) in the paper"""
    plot_7_a(data)

    # """ some other plots """
    # plot4(data)
    #
    # states_amount_positive_sample_plot(data)
    #
    # other_plots(data)

    data.to_csv('all the examples.csv', index=False)
    pass


def other_plots(data):
    plot11(data)
    plot11_2(data)
    plot22(data)
    plot22_2(data)
    plot33(data)
    plot33_2(data)
    pass


def print_info(data):
    """The statistical info in the Table"""
    smt_duration_percentage(data, 0, 300)
    smt_duration_percentage(data, 300, 1800)
    smt_duration_percentage(data, 1800, 3600)
    positive_percentage(data, 0, 10)
    positive_percentage(data, 10, 25)
    positive_percentage(data, 25, 50)
    positive_percentage2(data, 50, 100)
    num_states_percentage(data, 2, 5)
    num_states_percentage(data, 5, 10)
    num_states_percentage(data, 10, 15)
    num_states_percentage2(data, 15, 20)
    sample_size_percentage(data, 0, 25)
    sample_size_percentage(data, 25, 50)
    sample_size_percentage(data, 50, 75)
    sample_size_percentage2(data, 75, 100)


if __name__ == '__main__':
    import pandas as pd
    import matplotlib.pyplot as plt

    """
    Here you can find the plot printing given the output we generated and inferred
    """
    no_cs_pos_perc_printing()
