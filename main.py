# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import numpy as np
from matplotlib.ticker import FuncFormatter, MaxNLocator, MultipleLocator

font = 12


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def filter_strings(dictionary):
    filtered_dict = {}

    for key in sorted(dictionary.keys()):
        current_value = dictionary[key]
        filtered_value = [string for string in current_value if all(
            string not in lower_value for lower_key, lower_value in filtered_dict.items() if lower_key < key)]

        if filtered_value:
            filtered_dict[key] = filtered_value

    return filtered_dict


# Example usage:
your_dict = {
    1: ["apple", "banana", "orange"],
    2: ["banana", "grape", "kiwi"],
    3: ["orange", "kiwi", "pear"]
}


def SMT_vs_sample_size_cs_positive_with_respect_to_negative_3d_plot(selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    y = selected_data['CS_size'].values.tolist()
    x = selected_data['solve_SMT_time'].values.tolist()
    c = selected_data['CS_negative_size'].values.tolist()
    z = selected_data['CS_positive_size'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, z,
                         c=c, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='#negative words in the sample')
    # Adjust the limits of the z-axis if necessary
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    ax.set_title(
        '3D Scatter Plot of SMT duration (sec) vs #words in the sample vs positive sample with respect to #negative words in the sample')
    plt.xlabel('SMT duration (sec)', fontsize=font)
    plt.ylabel('#words in the sample', fontsize=font)
    ax.set_zlabel('#positive words in the sample', fontsize=font)
    plt.show()
    pass


def SMT_vs_sample_size_cs_positive_with_respect_to_negative_2d_plus_plot(selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    y = selected_data['CS_size'].values.tolist()
    x = selected_data['solve_SMT_time'].values.tolist()
    c = selected_data['CS_negative_size'].values.tolist()
    z = selected_data['CS_positive_size'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = plt.scatter(x, y, z,
                          c=c, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='#negative words in the sample')
    # Adjust the limits of the z-axis if necessary
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    ax.set_title(
        '3D Scatter Plot of SMT duration (sec) vs #words in the sample vs positive sample with respect to #negative words in the sample')
    plt.xlabel('SMT duration (sec)')
    plt.ylabel('#words in the sample')
    ax.set_zlabel('#positive words in the sample')
    plt.show()
    pass


def plot1(selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    y = selected_data['CS_negative_size'].values.tolist()
    x = selected_data['CS_positive_size'].values.tolist()
    c = selected_data['CS_size'].values.tolist()
    z = selected_data['solve_SMT_time'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, z,
                         c=c, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='#words in the sample')
    # Adjust the limits of the z-axis if necessary
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    # ax.set_title(
    #     '3D Scatter Plot of SMT duration (sec) vs sample size vs positive sample with respect to negative sample size')
    plt.xlabel('#positive words in the sample', fontsize=font)
    plt.ylabel('#negative words in the sample', fontsize=font)
    ax.set_zlabel('SMT duration (sec)', fontsize=font)
    plt.show()
    pass


def plot2(selected_data):
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
    # Adjust the limits of the z-axis if necessary
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    # ax.set_title(
    #     '3D Scatter Plot of SMT duration (sec) vs sample size vs positive sample with respect to negative sample size')
    plt.xlabel('#states', fontsize=font)
    plt.ylabel('#actions', fontsize=font)
    ax.set_zlabel('SMT duration (sec)', fontsize=font)
    plt.show()
    pass


def plot3(selected_data):
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
    # Adjust the limits of the z-axis if necessary
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    # ax.set_title(
    #     '3D Scatter Plot of SMT duration (sec) vs sample size vs positive sample with respect to negative sample size')
    plt.xlabel('#states', fontsize=font)
    plt.ylabel('#words in the sample', fontsize=font)
    ax.set_zlabel('SMT duration (sec)', fontsize=font)
    plt.show()
    pass


def plot4(selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    y = selected_data['positive_ratio'].values.tolist()
    x = selected_data['amount_of_states_in_origin'].values.tolist()
    c = selected_data['CS_size'].values.tolist()
    z = selected_data['solve_SMT_time'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, z,
                         c=c, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='#words in the sample')
    # Adjust the limits of the z-axis if necessary
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    # ax.set_title(
    #     '3D Scatter Plot of SMT duration (sec) vs sample size vs positive sample with respect to negative sample size')
    plt.xlabel('#states', fontsize=font)
    plt.ylabel('positive ratio', fontsize=font)
    ax.set_zlabel('SMT duration (sec)', fontsize=font)
    plt.show()
    pass


def plot5(selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    y = selected_data['positive_ratio'].values.tolist()
    x = selected_data['amount_of_actions'].values.tolist()
    c = selected_data['CS_size'].values.tolist()
    z = selected_data['solve_SMT_time'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, z,
                         c=c, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='#words in the sample')
    # Adjust the limits of the z-axis if necessary
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    # ax.set_title(
    #     '3D Scatter Plot of SMT duration (sec) vs sample size vs positive sample with respect to negative sample size')
    plt.xlabel('#actions', fontsize=font)
    plt.ylabel('positive ratio', fontsize=font)
    ax.set_zlabel('SMT duration (sec)', fontsize=font)
    plt.show()
    pass


def no_cs_printing():
    folder_path = './no_cs'
    folder_path0 = './no_cs with minimal'
    folder_path1 = './no_cs pos_perc/1'
    folder_path2 = './no_cs pos_perc/2'
    folder_path3 = './no_cs pos_perc/3'
    folder_path5 = './no_cs pos_perc/5'
    folder_path4 = './no_cs pos_perc'
    folder_path8 = './no_cs pos_perc/8'
    folder_path10 = './no_cs pos_perc/10'
    # Initialize an empty DataFrame to store the selected rows
    selected_data = pd.DataFrame()
    # Iterate over each file in the folder
    for fp in [folder_path0, folder_path1, folder_path2, folder_path3, folder_path4, folder_path5, folder_path8,
               folder_path10]:
        for filename in os.listdir(fp):
            if filename.endswith('.csv'):
                # Read the CSV file into a DataFrame
                file_path = os.path.join(fp, filename)
                df = pd.read_csv(file_path)
                df_1 = df[df['right_output'] == True]
                df_1 = df_1[df_1['minimal_right_output'] == True]
                df_1 = df_1[df_1['CS_positive_size'] > 0]
                df_1 = df_1[df_1['solve_SMT_time'] < 3600]
                selected_data = pd.concat([selected_data, df_1])
    for fp in [folder_path]:
        for filename in os.listdir(fp):
            if filename.endswith('.csv'):
                # Read the CSV file into a DataFrame
                file_path = os.path.join(fp, filename)
                df = pd.read_csv(file_path)
                df_1 = df[df['right_output'] == True]
                df_1 = df_1[df_1['CS_positive_size'] > 0]
                selected_data = pd.concat([selected_data, df_1])
    selected_data = selected_data.drop_duplicates()
    selected_data = selected_data.drop(['right_output', 'failed_converged'], axis=1)
    print("selected_data:", selected_data.columns)

    selected_data['CS_size'] = selected_data['CS_positive_size'] + selected_data['CS_negative_size']

    selected_data = selected_data.loc[:,
                    ['amount_of_states_in_origin', 'amount_of_states_in_output', 'CS_size', 'CS_positive_size',
                     'CS_negative_size',
                     'longest_word_in_CS', 'CS_development_time', 'solve_SMT_time']]
    x, y = None, None

    _, x, y = sample_size_longest_smt_time_plot(selected_data, x, y)

    cs_size_vs_longest_with_smt_time_3d_plot(cbar, selected_data, x, y)

    states_number_vs_positive_sample_size_plot(cbar, selected_data)

    states_number_vs_positive_sample_size_with_negative_size_3d_plot(cbar, selected_data)
    states_number_vs_positive_sample_size_with_negative_size_3d_plot_advances(cbar, selected_data)

    longest_word_vs_sample_size_with_SMT_solve_plot(selected_data)
    longest_word_vs_sample_size_with_SMT_solve_plot_advanced(selected_data)

    states_amount_positive_sample_plot(selected_data)

    states_amount_positive_sample_3d_plot(selected_data)

    SMT_vs_sample_size_cs_positive_with_respect_to_negative_3d_plot(selected_data)

    plot1(selected_data)  # amount_of_states_in_origin

    # SMT_vs_sample_size_cs_positive_with_respect_to_negative_2d_plus_plot(selected_data)

    selected_data.to_csv('no cs - all examples.csv', index=False)


def states_amount_positive_sample_plot(selected_data):
    scatter = plt.scatter(selected_data['amount_of_states_in_origin'].values.tolist(),
                          selected_data['amount_of_states_in_output'].values.tolist(),
                          selected_data['CS_size'].values.tolist(),
                          c=selected_data['CS_size'].values.tolist(), cmap='viridis')
    # cbar = plt.colorbar(scatter)
    # cbar.set_label('#words in the sample')
    plt.xlabel('#states in original bp', fontsize=font)
    plt.ylabel('#states in agreeing bp', fontsize=font)
    # plt.title('#states with respect to the #words in the sample')
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


def states_amount_positive_sample_3d_plot(selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x = selected_data['amount_of_states_in_origin'].values.tolist()
    y = selected_data['amount_of_states_in_output'].values.tolist()
    c = selected_data['CS_size'].values.tolist()
    z = selected_data['CS_positive_size'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, z,
                         c=c, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='#words in the sample')
    # Adjust the limits of the z-axis if necessary
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    # ax.set_title('3D Scatter Plot of #states with respect to the #words in the sample')
    plt.xlabel('#states in original bp', fontsize=font)
    plt.ylabel('#states in agreeing bp', fontsize=font)
    ax.set_zlabel('#positive words in the sample', fontsize=font)
    plt.show()


def longest_word_vs_sample_size_with_SMT_solve_plot(selected_data):
    jitter = 0  # 0.02
    x = selected_data['longest_word_in_CS'].values.tolist() + np.random.uniform(-jitter, jitter, size=len(
        selected_data['longest_word_in_CS'].values.tolist()))
    y = selected_data['CS_size'] + np.random.uniform(-jitter, jitter, size=len(selected_data['CS_size']))
    scatter = plt.scatter(x, y,
                          c=selected_data['solve_SMT_time'].values.tolist(), cmap='viridis', alpha=0.7)
    # cbar = plt.colorbar(scatter)
    # cbar.set_label('Solving SMT duration (sec)', fontsize=font)
    plt.ylabel('#words in the sample', fontsize=font)
    plt.xlabel('longest word in sample', fontsize=font)
    # plt.title('longest word vs #words in the sample in sample with Duration of solving the SMT (sec)')
    plt.show()


def longest_word_vs_sample_size_with_SMT_solve_plot_advanced(selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x = selected_data['longest_word_in_CS'].values.tolist()
    y = selected_data['CS_size'].values.tolist()
    z = selected_data['solve_SMT_time'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, z,
                         c=z, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='solving SMT duration (sec)')
    # Adjust the limits of the z-axis if necessary
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    # ax.set_title(
    #     '3D Scatter Plot of longest word in sample vs #words in the sample with respect to SMT solving time')
    plt.xlabel('longest word in sample', fontsize=font)
    plt.ylabel('#words in the sample', fontsize=font)
    ax.set_zlabel('solving SMT duration (sec)', fontsize=font)
    plt.show()


def states_number_vs_positive_sample_size_plot(selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x = selected_data['amount_of_states_in_origin'].values.tolist()
    y = selected_data['amount_of_states_in_output'].values.tolist()
    z = selected_data['CS_positive_size'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, z,
                         c=z, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='#positive words in the sample')
    # cbar.set_label('#positive words in the sample')
    # Adjust the limits of the z-axis if necessary
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    # ax.set_title('3D Scatter Plot of sample amount of states with #positive words in the sample')
    plt.xlabel('#states in original bp', fontsize=font)
    plt.ylabel('#states in agreeing bp', fontsize=font)
    ax.set_zlabel('#positive words in the sample', fontsize=font)
    plt.show()


def states_number_vs_positive_sample_size_plot1(selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x = selected_data['amount_of_states_in_origin'].values.tolist()
    y = selected_data['amount_of_states_in_output'].values.tolist()
    c = selected_data['CS_size'].values.tolist()
    z = selected_data['solve_SMT_time'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, z,
                         c=c, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='#words in the sample')
    # cbar.set_label('solving SMT duration (sec)')
    # Adjust the limits of the z-axis if necessary
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    # ax.set_title('3D Scatter Plot of sample amount of states with #positive words in the sample')
    plt.xlabel('#states in original bp', fontsize=font)
    plt.ylabel('#states in agreeing bp', fontsize=font)
    ax.set_zlabel('SMT duration (sec)', fontsize=font)
    plt.show()


def states_number_vs_positive_sample_size_plot2(cbar, selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x = selected_data['CS_positive_size'].values.tolist()
    y = selected_data['CS_negative_size'].values.tolist()
    z = selected_data['amount_of_states_in_output'].values.tolist()
    c = selected_data['solve_SMT_time'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, z,
                         c=c, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='#positive words in the sample')
    # cbar.set_label('solving SMT duration (sec)')
    # Adjust the limits of the z-axis if necessary
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    # ax.set_title('3D Scatter Plot of sample amount of states with #positive words in the sample')
    plt.xlabel('#positive words in the sample')
    plt.ylabel('#negative words in the sample')
    ax.set_zlabel('#states in agreeing bp')
    plt.show()


def states_number_vs_positive_sample_size_with_negative_size_3d_plot(cbar, selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x = selected_data['amount_of_states_in_origin'].values.tolist()
    y = selected_data['amount_of_states_in_output'].values.tolist()
    z = selected_data['CS_positive_size'].values.tolist()
    c = selected_data['CS_negative_size'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, z,
                         c=c, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='#negative words in the sample')
    cbar.set_label('#negative words in the sample')
    # Adjust the limits of the z-axis if necessary
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    ax.set_title('3D Scatter Plot of sample amount of states with #positive words in the sample')
    plt.xlabel('#states in original bp')
    plt.ylabel('#states in agreeing bp')
    ax.set_zlabel('#positive words in the sample')
    plt.show()


def states_number_vs_positive_sample_size_with_negative_size_3d_plot_advances(cbar, selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x = selected_data['amount_of_states_in_origin'].values.tolist()
    y = selected_data['amount_of_states_in_output'].values.tolist()
    z = selected_data['CS_positive_size'].values.tolist()
    c = selected_data['solve_SMT_time'].values.tolist()
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, z, bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, z,
                         c=c, cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='SMT solving time (sec)')
    cbar.set_label('SMT solving time (sec)')
    # Adjust the limits of the z-axis if necessary
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    ax.set_title(
        '3D Scatter Plot of sample amount of states with #positive words in the sample with SMT duration')
    plt.xlabel('#states in original bp')
    plt.ylabel('#states in agreeing bp')
    ax.set_zlabel('#positive words in the sample')
    plt.show()


def sample_size_longest_smt_time_plot(selected_data, x, y):
    jitter = 0  # 0.02
    x = selected_data['CS_size'].values.tolist()
    x_jittered = x + np.random.uniform(-jitter, jitter, size=len(x))
    y = selected_data['longest_word_in_CS']
    y_jittered = y + np.random.uniform(-jitter, jitter, size=len(y))
    scatter = plt.scatter(x_jittered, y_jittered,
                          c=selected_data['solve_SMT_time'].values.tolist(), cmap='viridis', alpha=0.7)
    # cbar = plt.colorbar(scatter)
    # cbar.set_label('Solving SMT duration (sec)')
    plt.xlabel('#words in the sample', fontsize=font)
    plt.ylabel('longest word in sample', fontsize=font)
    # plt.title('#words in the sample vs longest word in sample with Duration of solving the SMT (sec)')
    plt.show()
    return x, y


def cs_size_vs_longest_with_smt_time_3d_plot(selected_data, x, y):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # Scatter plot with color values as the third dimension
    # Set the z-axis to start from zero
    ax.bar(x, y, bottom=0, color='white', alpha=0, zorder=1)
    ax.bar(x, selected_data['solve_SMT_time'].values.tolist(), bottom=0, color='white', alpha=0, zorder=1)
    scatter = ax.scatter(x, y, selected_data['solve_SMT_time'].values.tolist(),
                         c=selected_data['solve_SMT_time'].values.tolist(), cmap='viridis', alpha=0.7, zorder=2)
    fig.colorbar(scatter, label='solve SMT time(sec)')
    # cbar.set_label('solve SMT time(sec)')
    # Adjust the limits of the z-axis if necessary
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(selected_data['solve_SMT_time'].values.tolist()),
                max(selected_data['solve_SMT_time'].values.tolist()))
    # ax.set_title(
    #     '3D Scatter Plot of #words in the sample vs longest word in sample with Duration of solving the SMT (sec)')
    ax.set_xlabel('#words in the sample', fontsize=font)
    ax.set_ylabel('longest word in sample', fontsize=font)
    ax.set_zlabel('solve SMT time(sec)', fontsize=font)
    plt.show()


def cutoff_vs_cs_size_with_org_states(selected_data):
    scatter = plt.scatter(selected_data['cutoff'].values.tolist(), selected_data['CS_size'].values.tolist(),
                          c=selected_data['amount_of_states_in_origin'].values.tolist(), cmap='viridis')
    cbar = plt.colorbar(scatter)
    cbar.set_label('original bp #states')
    plt.ylabel('CS size')
    plt.xlabel('cutoff')
    plt.title('CS size vs cutoff with respect to the original bp #states')
    plt.show()
    pass


def cutoff_vs_cs_size_with_out_states(selected_data):
    scatter = plt.scatter(selected_data['cutoff'].values.tolist(), selected_data['CS_size'].values.tolist(),
                          c=selected_data['amount_of_states_in_output'].values.tolist(), cmap='viridis')
    cbar = plt.colorbar(scatter)
    cbar.set_label('agreeing bp #states')
    plt.ylabel('CS size')
    plt.xlabel('cutoff')
    plt.title('CS size vs cutoff with respect to the agreeing bp #states')
    plt.show()
    pass


def m_n_l(selected_data):
    scatter = plt.scatter(selected_data['m'].values.tolist(),
                          selected_data['n'].values.tolist(),
                          c=selected_data['l'].values.tolist(), cmap='viridis')
    cbar = plt.colorbar(scatter)
    cbar.set_label('l')
    plt.xlabel('m')
    plt.ylabel('n')
    plt.show()
    pass


def cs_printing():
    global folder_path, selected_data, filename, file_path, df, df_1, scatter, cbar, fig, ax
    # folder_path = './runing full cs'
    # folder_path2 = './runing of cs plus extra words part 2'
    # folder_path3 = './runing of cs plus extra words'
    # folder_path4 = './runing cs plus extra words part3'
    folder_path = './B_m_n_l'  # './subsume_cs'
    # Initialize an empty DataFrame to store the selected rows
    selected_data = pd.DataFrame()
    # Iterate over each file in the folder
    for fold_name in [folder_path]:  # [folder_path, folder_path2, folder_path3]:
        for filename in os.listdir(fold_name):
            if filename.endswith('.csv'):
                # Read the CSV file into a DataFrame
                file_path = os.path.join(fold_name, filename)
                df = pd.read_csv(file_path)
                df_1 = df[df['right_output'] == '(None, None, True)']
                selected_data = pd.concat([selected_data, df_1])
    selected_data = selected_data.drop(['right_output', 'failed_converged'], axis=1)
    print("selected_data:", selected_data.columns)
    selected_data = selected_data.loc[:,
                    ['amount_of_states_in_origin', 'amount_of_states_in_output', 'origin_BP', 'output_BP',
                     'cutoff', 'CS_positive_size', 'CS_negative_size', 'longest_word_in_CS', 'solve_SMT_time','m','n','l']]
    selected_data['CS_size'] = selected_data['CS_positive_size'] + selected_data['CS_negative_size']
    cs_size_vs_cutoff_with_SMT_solving(selected_data)
    cutoff_vs_cs_size_with_SMT_solving(selected_data)
    cutoff_vs_cs_size_with_org_states(selected_data)
    cutoff_vs_cs_size_with_out_states(selected_data)
    cs_size_vs_cutoff_with_SMT_solve_3d_plot(cbar, selected_data)
    cutoff_vs_cs_size_with_SMT_solve_3d_plot(cbar, selected_data)
    number_states_with_cutoff_plot(selected_data)
    number_states_with_cutoff_3d_plot(cbar, selected_data)
    cs_size_vs_longest_word_with_cutoff_plot(selected_data)
    print("mote")
    cutoff_vs_cs_size_with_SMT_solving_3d_plot(cbar, selected_data)
    cutoff_vs_cs_size_with_SMT_solving_2d_with_circle_depth_plot(cbar, selected_data)
    m_n_l(selected_data)
    # cutoff_vs_cs_size_with_SMT_solve_surface_plot(selected_data)

    selected_data.to_csv('cs - B_m_n_l.csv', index=False)


def cs_size_vs_longest_word_with_cutoff_plot(selected_data):
    global scatter, cbar
    scatter = plt.scatter(selected_data['CS_size'].values.tolist(),
                          selected_data['longest_word_in_CS'].values.tolist(),
                          c=selected_data['cutoff'].values.tolist(), cmap='viridis')
    cbar = plt.colorbar(scatter)
    cbar.set_label('cutoff')
    plt.xlabel('size of CS')
    plt.ylabel('longest word in the sample')
    plt.title('CS size vs longest word in sample with respect to the cutoff')
    plt.show()


def number_states_with_cutoff_3d_plot(cbar, selected_data):
    global fig, ax, scatter
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # Scatter plot with color values as the third dimension
    scatter = ax.scatter(selected_data['amount_of_states_in_origin'].values.tolist(),
                         selected_data['amount_of_states_in_output'].values.tolist(),
                         selected_data['cutoff'].values.tolist(), c=selected_data['cutoff'].values.tolist(),
                         cmap='viridis', alpha=0.7)
    fig.colorbar(scatter, label='cutoff')
    cbar.set_label('cutoff')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.zaxis.set_major_locator(MaxNLocator(integer=True))
    # In case I want to explicit have the gap between column values.. i.e. 1 -> 1,2,3, .. while 2 is->2,4,6,8..
    # ax.xaxis.set_major_locator(MultipleLocator(base=1))
    # ax.yaxis.set_major_locator(MultipleLocator(base=1))
    # ax.zaxis.set_major_locator(MultipleLocator(base=1))
    ax.set_title('3D Scatter Plot #states with respect to the cutoff')
    ax.set_xlabel('#states in original bp')
    ax.set_ylabel('#states in output bp')
    ax.set_zlabel('cutoff')
    plt.show()
    pass


def number_states_with_cutoff_plot(selected_data):
    global scatter, cbar
    scatter = plt.scatter(selected_data['amount_of_states_in_origin'].values.tolist(),
                          selected_data['amount_of_states_in_output'].values.tolist(),
                          c=selected_data['cutoff'].values.tolist(), cmap='viridis')
    cbar = plt.colorbar(scatter)
    cbar.set_label('cutoff')
    plt.xlabel('#states in original bp')
    plt.ylabel('#states in output bp')
    plt.title('#states with respect to the cutoff')
    plt.show()
    pass


def cs_size_vs_cutoff_with_SMT_solve_3d_plot(cbar, selected_data):
    global fig, ax, scatter
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # Scatter plot with color values as the third dimension
    scatter = ax.scatter(selected_data['CS_size'].values.tolist(),
                         selected_data['cutoff'].values.tolist(),
                         selected_data['solve_SMT_time'].values.tolist(),
                         c=selected_data['solve_SMT_time'].values.tolist(),
                         cmap='viridis', alpha=0.7)
    fig.colorbar(scatter, label='Solving SMT duration(sec)')
    cbar.set_label('Solving SMT duration(sec)')
    ax.set_title('3D Scatter Plot CS size vs cutoff with respect to the SMT solving duration(sec)')
    ax.set_xlabel('CS size')
    ax.set_ylabel('cutoff')
    ax.set_zlabel('Solving SMT duration(sec)')
    plt.show()
    pass


def cutoff_vs_cs_size_with_SMT_solve_3d_plot(cbar, selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # Scatter plot with color values as the third dimension
    scatter = ax.scatter(selected_data['cutoff'].values.tolist(),
                         selected_data['CS_size'].values.tolist(),
                         selected_data['solve_SMT_time'].values.tolist(),
                         c=selected_data['solve_SMT_time'].values.tolist(),
                         cmap='viridis', alpha=0.7)
    fig.colorbar(scatter, label='Solving SMT duration(sec)')
    cbar.set_label('Solving SMT duration(sec)')
    ax.set_title('3D Scatter Plot cutoff vs CS size with respect to the SMT solving duration(sec)')
    ax.set_ylabel('CS size')
    ax.set_xlabel('cutoff')
    ax.set_zlabel('Solving SMT duration(sec)')
    plt.show()
    pass


from mpl_toolkits.mplot3d import Axes3D


def cutoff_vs_cs_size_with_SMT_solve_surface_plot(selected_data):
    # Scatter plot with color values as the third dimension
    x = selected_data['cutoff'].values.tolist()
    y = selected_data['CS_size'].values.tolist()
    z = selected_data['solve_SMT_time']

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surface = ax.plot_trisurf(x, y, z, cmap='viridis')
    ax.set_title('3D Scatter Plot cutoff vs CS size with respect to the SMT solving duration(sec)')
    ax.set_ylabel('CS size')
    ax.set_xlabel('cutoff')
    ax.set_zlabel('Solving SMT duration(sec)')
    cbar = fig.colorbar(surface, ax=ax, label='Solving SMT duration(sec)')
    plt.show()
    pass


def cs_size_vs_cutoff_with_SMT_solving(selected_data):
    global scatter, cbar
    scatter = plt.scatter(selected_data['CS_size'].values.tolist(), selected_data['cutoff'].values.tolist(),
                          c=selected_data['solve_SMT_time'].values.tolist(), cmap='viridis')
    cbar = plt.colorbar(scatter)
    cbar.set_label('Solving SMT duration(sec)')
    plt.xlabel('CS size')
    plt.ylabel('cutoff')
    plt.title('CS size vs cutoff with respect to the SMT solving duration(sec)')
    plt.show()


def cutoff_vs_cs_size_with_SMT_solving(selected_data):
    global scatter, cbar
    scatter = plt.scatter(selected_data['cutoff'].values.tolist(), selected_data['CS_size'].values.tolist(),
                          c=selected_data['solve_SMT_time'].values.tolist(), cmap='viridis')
    cbar = plt.colorbar(scatter)
    cbar.set_label('Solving SMT duration(sec)')
    plt.ylabel('CS size')
    plt.xlabel('cutoff')
    plt.title('CS size vs cutoff with respect to the SMT solving duration(sec)')
    plt.show()


def cutoff_vs_cs_size_with_SMT_solving_3d_plot(cbar, selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # Scatter plot with color values as the third dimension
    scatter = ax.scatter(selected_data['cutoff'].values.tolist(), selected_data['CS_size'].values.tolist(),
                         selected_data['solve_SMT_time'].values.tolist(),
                         c=selected_data['solve_SMT_time'].values.tolist(), cmap='viridis', alpha=0.7)
    # cbar = plt.colorbar(scatter)
    fig.colorbar(scatter, label='Solving SMT duration(sec)')
    cbar.set_label('Solving SMT duration(sec)')
    ax.set_title('3D plot of CS size vs cutoff with respect to the SMT solving duration(sec)')
    ax.set_ylabel('CS size')
    ax.set_xlabel('cutoff')
    ax.set_zlabel('Solving SMT duration(sec)')
    plt.show()
    pass


def cutoff_vs_cs_size_with_SMT_solving_2d_with_circle_depth_plot(cbar, selected_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # Scatter plot with color values as the third dimension
    scatter = plt.scatter(selected_data['cutoff'].values.tolist(), selected_data['CS_size'].values.tolist(),
                          selected_data['solve_SMT_time'].values.tolist(),
                          c=selected_data['solve_SMT_time'].values.tolist(), cmap='viridis', alpha=0.7)
    # cbar = plt.colorbar(scatter)
    fig.colorbar(scatter, label='Solving SMT duration(sec)')
    cbar.set_label('Solving SMT duration(sec)')
    ax.set_title('3D plot of CS size vs cutoff with respect to the SMT solving duration(sec)')
    ax.set_ylabel('CS size')
    ax.set_xlabel('cutoff')
    ax.set_zlabel('Solving SMT duration(sec)')
    plt.show()
    pass


# Press the green button in the gutter to run the script.
def time_comperison(filtered_df):
    plt.plot(filtered_df.index, filtered_df['minimal_solve_SMT_time'],
             label='Finding minimal time solve SMT duration', marker='o', color='blue')
    plt.plot(filtered_df.index, filtered_df['solve_SMT_time'],
             label='solve SMT duration', marker='x', color='maroon')

    plt.plot(filtered_df.index, filtered_df['amount_of_states_in_minimal_output'], linestyle='-', color='blue')
    plt.plot(filtered_df.index, filtered_df['amount_of_states_in_output'], linestyle='-', color='maroon')

    # Adding labels and legend
    plt.xlabel('Sample')
    plt.ylabel('Solving Time')
    plt.legend()
    plt.show()
    pass


def minimal_no_cs():
    folder_path = './no_cs with minimal'
    folder_path1 = './no_cs pos_perc/1'
    folder_path2 = './no_cs pos_perc/2'
    folder_path3 = './no_cs pos_perc/3'
    folder_path5 = './no_cs pos_perc/5'

    folder_path4 = './no_cs pos_perc'
    folder_path8 = './no_cs pos_perc/8'
    folder_path10 = './no_cs pos_perc/10'
    # Initialize an empty DataFrame to store the selected rows
    selected_data = pd.DataFrame()
    # Iterate over each file in the folder
    for fp in [folder_path, folder_path1, folder_path2, folder_path3, folder_path4, folder_path5, folder_path8,
               folder_path10]:  # , folder_path1]:
        for filename in os.listdir(fp):
            if filename.endswith('.csv'):
                # Read the CSV file into a DataFrame
                file_path = os.path.join(fp, filename)
                df = pd.read_csv(file_path)
                df_1 = df[df['right_output'] == True]
                df_1 = df_1[df_1['minimal_right_output'] == True]
                df_1 = df_1[df_1['CS_positive_size'] > 0]
                selected_data = pd.concat([selected_data, df_1])
    selected_data = selected_data.drop(['right_output', 'failed_converged'], axis=1)
    print("selected_data:", selected_data.columns)

    selected_data['CS_size'] = selected_data['CS_positive_size'] + selected_data['CS_negative_size']

    selected_data = selected_data.loc[:,
                    ['amount_of_states_in_origin', 'amount_of_states_in_output', 'CS_size', 'CS_positive_size',
                     'CS_negative_size',
                     'longest_word_in_CS', 'CS_development_time', 'solve_SMT_time',
                     'amount_of_states_in_minimal_output', 'minimal_solve_SMT_time', 'minimal_right_output']]

    # Filter rows where 'a' is not zero\
    filtered_df = selected_data[selected_data['minimal_solve_SMT_time'] != 0]
    filtered_df = filtered_df.reset_index()
    filtered_df.sort_index(inplace=True)
    filtered_df.to_csv('filtered_df.csv', index=False)
    # Plotting
    print("filtered_df.index: ", filtered_df.index)
    print("filtered_df['amount_of_states_in_minimal_output']: ", filtered_df['amount_of_states_in_minimal_output'])
    plt.plot(filtered_df.index, filtered_df['amount_of_states_in_minimal_output'],
             label='#states in minimal BP', marker='o', color='blue')
    plt.plot(filtered_df.index, filtered_df['amount_of_states_in_output'],
             label='#states in default output BP', marker='x', color='maroon')

    plt.plot(filtered_df.index, filtered_df['amount_of_states_in_minimal_output'], linestyle='-', color='blue')
    plt.plot(filtered_df.index, filtered_df['amount_of_states_in_output'], linestyle='-', color='maroon')

    # Adding labels and legend
    plt.xlabel('Sample')
    plt.ylabel('amount of states')
    plt.legend()

    # Show the plot
    plt.show()

    states_amount_pos_ratio_3d_plot(filtered_df)
    time_comperison(filtered_df)
    # states_amount_pos_ratio_3d_plot1(filtered_df)

    # statistics = filtered_df.describe()
    # with open('statistics.txt', 'w') as file:
    #     file.write(statistics.to_string())
    # statistics.to_csv('statistics.csv')
    #
    # with open('statistics1.txt', 'w') as file:
    #
    #     # Iterate through columns
    #     for column in filtered_df.columns:
    #         # Calculate statistics for each column
    #         column_stats = filtered_df[column].describe()
    #
    #         # Write column name to file
    #         file.write(f"\nStatistics for {column}:\n")
    #
    #         # Write statistics to file
    #         file.write(column_stats.to_string())
    #         file.write("\n" + "=" * 40 + "\n")

    print("Statistics written to 'statistics.txt'")
    pass


def states_amount_pos_ratio_3d_plot(filtered_df):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # Scatter plot with color values as the third dimension
    scatter1 = ax.scatter(filtered_df['CS_size'], filtered_df['CS_positive_size'] / filtered_df['CS_size'],
                          filtered_df['amount_of_states_in_minimal_output'],
                          label='#states in minimal BP', marker='o', color='blue',
                          alpha=0.7)
    scatter2 = ax.scatter(filtered_df['CS_size'], filtered_df['CS_positive_size'] / filtered_df['CS_size'],
                          filtered_df['amount_of_states_in_output'],
                          label='#states in default output BP', marker='x', color='maroon',
                          alpha=0.7)
    # cbar = plt.colorbar(scatter)
    # fig.colorbar(scatter, label='Solving SMT duration(sec)')
    # cbar.set_label('Solving SMT duration(sec)')
    ax.set_title('3D plot 123')
    ax.set_ylabel('Positive ratio')
    ax.set_xlabel('#words in the sample')
    ax.set_zlabel('#states')
    ax.legend()
    plt.show()


def states_amount_pos_ratio_3d_plot1(filtered_df):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Scatter plot with color values as the third dimension
    scatter = ax.scatter(filtered_df.index, filtered_df['CS_size'],
                         filtered_df['amount_of_states_in_output'],
                         c=filtered_df['CS_positive_size'] / filtered_df['CS_size'],
                         cmap='viridis',  # Use your preferred colormap
                         marker='o', alpha=0.7)

    # Adding a colorbar
    cbar = plt.colorbar(scatter, label='Positive ratio')

    # Adding labels and title
    ax.set_title('3D Scatter Plot')
    ax.set_ylabel('Positive ratio')
    ax.set_xlabel('#words in the sample')
    ax.set_zlabel('#states')

    # Creating 2D subplots for each unique combination of CS_size and amount_of_states_in_output
    unique_combinations = filtered_df[['CS_size', 'amount_of_states_in_output']].drop_duplicates()

    # Show the 3D plot
    plt.show()


import re
import ast

import ast


def extract_inner_keys(input_string):
    # Find the index of "actions: " in the input string
    actions_index = input_string.find("actions: ")

    # Find the index of the next comma followed by a newline after "actions: "
    comma_newline_index = input_string.find(",\n", actions_index)

    # Extract the substring containing the dictionary
    actions_substring = input_string[actions_index + len("actions: "):comma_newline_index]

    # Convert the substring to a dictionary using ast.literal_eval
    actions_dict = ast.literal_eval(actions_substring)

    # Extract inner keys from the dictionary
    inner_keys = set()
    for _, inner_dict in actions_dict.items():
        inner_keys.update(inner_dict.keys())

    return len(inner_keys)


# def extract_inner_keys(input_string):
#     actions_index = input_string.find("actions: ")
#     actions_substring = input_string[actions_index + len("actions: "):]
#     actions_dict = ast.literal_eval(actions_substring)
#
#     inner_keys = set()
#     for _, inner_dict in actions_dict.items():
#         inner_keys.update(inner_dict.keys())
#
#     return len(inner_keys)

# def extract_keys(dictionary_string):
#     # Use regular expression to find the dictionary string
#     match = re.search(r"actions: {(.*?)}", dictionary_string)
#
#     if match:
#         # Extract the matched dictionary string
#         inner_dict_str = match.group(1)
#
#         # Use regular expression to find all keys in the dictionary
#         keys = re.findall(r"'(\w+)'", inner_dict_str)
#
#         return set(keys)
#     else:
#         return set()


def extract_keys_and_length(dictionary_string):
    keys = extract_inner_keys(dictionary_string)
    return len(keys)


def smt_duration_percentage(sd, a, b):
    column_name = 'solve_SMT_time'
    within_range_count = np.sum((sd[column_name] >= a) & (sd[column_name] < b))
    print("the within range count:", within_range_count)
    # Calculate the percentage
    percentage_within_range = (within_range_count / len(sd)) * 100
    print(f"Percentage of smt duration in the range [{a}, {b}): {percentage_within_range:.2f}%")
    pass


def smt_duration_percentage2(sd, a, b):
    column_name = 'solve_SMT_time'
    within_range_count = np.sum((sd[column_name] >= a) & (sd[column_name] <= b))
    print("the within range count:", within_range_count)
    # Calculate the percentage
    percentage_within_range = (within_range_count / len(sd)) * 100
    print(f"Percentage of smt duration in the range [{a}, {b}]: {percentage_within_range:.2f}%")
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


import seaborn as sns


def plot_buckets_for_defaulted_and_min(selected_data):
    fig, ax = plt.subplots()

    # Melt the DataFrame to have a single column for 'duration' and a column for 'type'
    melted_data = pd.melt(selected_data, id_vars=['CS_size'], value_vars=['solve_SMT_time', 'minimal_solve_SMT_time'],
                          var_name='type', value_name='duration')

    # Bar plot with grouped bars
    # sns.barplot(data=melted_data, x='CS_size', y='duration', hue='type', errorbar='sd', ax=ax)
    # sns.barplot(data=melted_data, x='CS_size', y='duration', hue='type', errorbar='sd', ax=ax) #, err_kws={'color': 'red'}

    sns.barplot(data=melted_data, x='CS_size', y='duration', hue='type', errorbar='se', legend='full', ax=ax)
    # sns.barplot(data=melted_data, x='CS_size', y='duration', hue='type', color='navy', errorbar='se', ax=ax)
    # sd- standard deviation
    # 'se' - for standard error of the mean
    # 'ci'- confidence interval

    # Customize the plot as needed
    ax.set_xlabel('#words in the sample')
    ax.set_ylabel('SMT Duration (sec)')
    ax.legend(bbox_to_anchor=(0, 0.75), loc='lower left')
    plt.show()
    # fig, ax = plt.subplots()
    # selected_data_grouped = selected_data.groupby('CS_size')
    # color_a = 'blue'
    # color_a_min = 'red'
    # # Iterate through each group and plot the average and standard deviation
    # for name, group in selected_data_grouped:
    #     # Calculate average and standard deviation for 'a' and 'a_min'
    #     avg_a = group['solve_SMT_time'].mean()
    #     std_a = group['solve_SMT_time'].std()
    #     avg_a_min = group['minimal_solve_SMT_time'].mean()
    #     std_a_min = group['minimal_solve_SMT_time'].std()
    #
    #     # Plot the data using error bars for standard deviation
    #     ax.errorbar(name, avg_a, yerr=std_a, fmt='o', color=color_a)
    #     ax.errorbar(name, avg_a_min, yerr=std_a_min, fmt='s', color=color_a_min)
    #
    # ax.errorbar([], [], yerr=[], fmt='o', color=color_a, label='BPInf')
    # ax.errorbar([], [], yerr=[], fmt='s', color=color_a_min, label='BPInfMin')
    # # Customize the plot as needed
    # ax.set_xlabel('#words in the sample')
    # ax.set_ylabel('SMT duration (sec)')
    # ax.legend()
    # plt.show()
    pass


def plot_buckets_for_defaulted_and_min1(selected_data):
    fig, ax = plt.subplots()
    bins = [i * 10 for i in range(0, 11)]  # Adjust the bin edges as needed

    # Create a new column 'solve_SMT_time_bin' to store the bin labels
    selected_data['CS_size_bin'] = pd.cut(selected_data['CS_size'], bins=bins, right=False)
    # Melt the DataFrame to have a single column for 'duration' and a column for 'type'
    melted_data = pd.melt(selected_data, id_vars=['CS_size_bin'],
                          value_vars=['solve_SMT_time', 'minimal_solve_SMT_time'],
                          var_name='type', value_name='duration')

    sns.barplot(data=melted_data, x='CS_size_bin', y='duration', hue='type', errorbar='se', legend='full', ax=ax)
    # sd- standard deviation
    # 'se' - for standard error of the mean
    # 'ci'- confidence interval

    ax.set_xlabel('#words in the sample')
    ax.set_ylabel('SMT Duration (sec)')
    ax.legend(bbox_to_anchor=(0, 0.75), loc='lower left')
    plt.show()
    pass


def plot_buckets_for_defaulted_and_min2(selected_data):
    bins = [i * 300 for i in range(0, 13)]  # Adjust the bin edges as needed

    # Create a new column 'solve_SMT_time_bin' to store the bin labels
    selected_data['solve_SMT_time_bin'] = pd.cut(selected_data['solve_SMT_time'], bins=bins, right=False)

    # Create a figure and axis for plotting
    fig, ax = plt.subplots()

    # Melt the DataFrame to have a single column for 'duration' and a column for 'type'
    melted_data = pd.melt(selected_data, id_vars=['solve_SMT_time_bin'],
                          value_vars=['minimal_solve_SMT_time', 'solve_SMT_time'],
                          var_name='type', value_name='duration')
    # Bar plot with grouped bars and error bars (standard deviation)
    sns.barplot(data=melted_data, x='solve_SMT_time_bin', y='duration', hue='type', errorbar='sd', ax=ax)

    # Customize the plot as needed
    ax.set_xlabel('solve_SMT_time')
    ax.set_ylabel('SMT Duration (sec)')
    ax.legend(bbox_to_anchor=(0, 0.85), loc='lower left')
    plt.show()
    pass


def plot_buckets_for(selected_data):
    melted_data = pd.melt(selected_data, id_vars=['CS_size_bin'],
                          value_vars=['amount_of_states_in_minimal_output', 'amount_of_states_in_output'],
                          var_name='type', value_name='duration')

    # Create a Matplotlib axis
    fig, ax = plt.subplots()

    # Bar plot with grouped bars and error bars (min and max values)
    sns.barplot(data=melted_data, x='CS_size_bin', y='duration', hue='type', estimator=min, errorbar=None, ax=ax)
    sns.barplot(data=melted_data, x='CS_size_bin', y='duration', hue='type', estimator=max, errorbar=None, ax=ax)

    # Set legend outside the plot
    ax.legend(bbox_to_anchor=(0, 0.85), loc='lower left')

    # Show the plot
    plt.show()
    pass


def plot_buckets_for_defaulted_and_min3(selected_data):
    """
    a histogram comparing the #states, with sample size in the X-axis
    :param selected_data:
    :return:
    """
    # Create a figure and axis for plotting
    fig, ax = plt.subplots()

    # Melt the DataFrame to have a single column for 'duration' and a column for 'type'
    melted_data = pd.melt(selected_data, id_vars=['CS_size_bin'],
                          value_vars=['amount_of_states_in_minimal_output', 'amount_of_states_in_output'],
                          var_name='type', value_name='duration')
    # Bar plot with grouped bars and error bars (standard deviation)
    sns.barplot(data=melted_data, x='CS_size_bin', y='duration', hue='type', errorbar='sd', ax=ax)

    # Customize the plot as needed
    ax.set_xlabel('#words in the sample')
    ax.set_ylabel('#states')
    ax.legend(bbox_to_anchor=(0, 0.85), loc='lower left')
    plt.show()
    fig, ax = plt.subplots()

    # Melt the DataFrame to have a single column for 'duration' and a column for 'type'
    melted_data = pd.melt(selected_data, id_vars=['CS_size_bin'],
                          value_vars=['amount_of_states_in_minimal_output', 'amount_of_states_in_output'],
                          var_name='type', value_name='duration')
    # Bar plot with grouped bars and error bars (standard deviation)
    sns.barplot(data=melted_data, x='CS_size_bin', y='duration', hue='type', errorbar='se', ax=ax)

    # Customize the plot as needed
    ax.set_xlabel('#words in the sample')
    ax.set_ylabel('#states')
    ax.legend(bbox_to_anchor=(0, 0.85), loc='lower left')
    plt.show()
    pass


from collections import Counter


def no_cs_pos_perc_printing():
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
    folder_path_optional = './no_cs'
    # Initialize an empty DataFrame to store the selected rows
    selected_data = pd.DataFrame()
    timeouted_failed_conv_data = pd.DataFrame()
    # Iterate over each file in the folder
    for fp in [folder_path, folder_path1, folder_path2, folder_path3, folder_path4, folder_path5, folder_path8,
               folder_path10, folder_path25, folder_path32, folder_path39,
               folder_path45, folder_path48, folder_path52,
               folder_path_new]:  # , folder_path1]:
        for filename in os.listdir(fp):
            if filename.endswith('.csv'):
                # print("filename:", filename)
                # Read the CSV file into a DataFrame
                file_path = os.path.join(fp, filename)
                df = pd.read_csv(file_path)
                df_2 = df[(df['failed_converged'] == True) | (df['timeout'] == True)]
                df_1 = df[df['right_output'] == True]
                df_1 = df_1[df_1['minimal_right_output'] == True]
                df_1 = df_1[df_1['CS_positive_size'] > 0]
                # df_1 = df_1[df_1['CS_positive_size'] < 35]
                df_1 = df_1[df_1['solve_SMT_time'] <= 3600]
                selected_data = pd.concat([selected_data, df_1])
                timeouted_failed_conv_data = pd.concat([timeouted_failed_conv_data, df_2])
    print("maxx:", max(selected_data['amount_of_states_in_minimal_output'].tolist()))
    print("Counter:", Counter(selected_data['amount_of_states_in_minimal_output'].tolist()))
    selected_data = selected_data.drop_duplicates()
    timeouted_failed_conv_data = timeouted_failed_conv_data.drop_duplicates()
    print(f"in min version there are : {len(selected_data['solve_SMT_time'])}")
    print(
        f"in min version there are that timeouted_failed_conv_data : {len(timeouted_failed_conv_data['solve_SMT_time'])}")
    for fp in [folder_path_optional]:
        for filename in os.listdir(fp):
            if filename.endswith('.csv'):
                # print("filename:", filename)
                # Read the CSV file into a DataFrame
                file_path = os.path.join(fp, filename)
                df = pd.read_csv(file_path)
                df_2 = df[(df['failed_converged'] == True) | (df['timeout'] == True)]
                df_1 = df[df['right_output'] == True]
                df_1 = df_1[df_1['CS_positive_size'] > 0]
                # df_1 = df_1[df_1['CS_positive_size'] < 35]
                df_1 = df_1[df_1['solve_SMT_time'] <= 3600]
                selected_data = pd.concat([selected_data, df_1])
                timeouted_failed_conv_data = pd.concat([timeouted_failed_conv_data, df_2])

    selected_data = selected_data.drop_duplicates()
    print(f"in total ther are : {len(selected_data['solve_SMT_time'])}")
    timeouted_failed_conv_data = timeouted_failed_conv_data.drop_duplicates()
    print(f"in total there are that timeouted_failed_conv_data : {len(timeouted_failed_conv_data['solve_SMT_time'])}")

    selected_data = selected_data.drop(['right_output', 'failed_converged'], axis=1)
    print("selected_data:", selected_data.columns)

    selected_data['amount_of_actions'] = selected_data['origin_BP'].apply(extract_inner_keys)

    selected_data['CS_size'] = selected_data['CS_positive_size'] + selected_data['CS_negative_size']

    selected_data['positive_ratio'] = (100 * selected_data['CS_positive_size']) // selected_data['CS_size']
    print_info(selected_data)

    # selected_data = selected_data.loc[:,
    #                 ['amount_of_states_in_origin', 'amount_of_states_in_output', 'origin_BP', 'CS_size',
    #                  'CS_positive_size',
    #                  'CS_negative_size', 'words_added', 'amount_of_states_in_minimal_output',
    #                  'longest_word_in_CS', 'CS_development_time', 'solve_SMT_time', 'minimal_solve_SMT_time',
    #                  'amount_of_actions', 'positive_ratio']]
    selected_data = selected_data.loc[:,
                    ['amount_of_states_in_origin', 'amount_of_states_in_output', 'origin_BP', 'CS_size',
                     'CS_positive_size',
                     'CS_negative_size', 'words_added',
                     'longest_word_in_CS', 'CS_development_time', 'solve_SMT_time',
                     'amount_of_actions', 'positive_ratio']]
    x, y = None, None

    # other_plots(cbar, selected_data)

    # buckate_plot(selected_data)

    # _, x, y = sample_size_longest_smt_time_plot(selected_data, x, y)

    # cs_size_vs_longest_with_smt_time_3d_plot(selected_data, x, y)
    #
    states_number_vs_positive_sample_size_plot(selected_data)
    states_number_vs_positive_sample_size_plot1(selected_data)

    longest_word_vs_sample_size_with_SMT_solve_plot(selected_data)
    longest_word_vs_sample_size_with_SMT_solve_plot_advanced(selected_data)

    states_amount_positive_sample_plot(selected_data)
    #
    states_amount_positive_sample_3d_plot(selected_data)

    SMT_vs_sample_size_cs_positive_with_respect_to_negative_3d_plot(selected_data)

    plot1(selected_data)
    #
    plot2(selected_data)

    plot3(selected_data)

    plot4(selected_data)

    plot5(selected_data)
    #
    selected_data.to_csv('no cs - all examples 25-1.csv', index=False)
    timeouted_failed_conv_data.to_csv('timeout_failed_conv_data 25-1.csv', index=False)
    pass


def other_plots(cbar, selected_data):
    plot11(selected_data)
    plot11_2(selected_data)
    plot22(selected_data)
    plot22_2(selected_data)
    plot33(selected_data)
    plot33_2(selected_data)
    states_number_vs_positive_sample_size_plot2(cbar, selected_data)
    states_number_vs_positive_sample_size_with_negative_size_3d_plot(cbar, selected_data)
    states_number_vs_positive_sample_size_with_negative_size_3d_plot_advances(cbar, selected_data)
    SMT_vs_sample_size_cs_positive_with_respect_to_negative_2d_plus_plot(selected_data)
    pass


def buckate_plot(selected_data):
    plot_buckets_for_defaulted_and_min(selected_data)
    plot_buckets_for_defaulted_and_min1(selected_data)
    plot_buckets_for_defaulted_and_min3(selected_data)
    plot_buckets_for_defaulted_and_min2(selected_data)


def print_info(selected_data):
    smt_duration_percentage(selected_data, 0, 300)
    smt_duration_percentage(selected_data, 300, 1800)
    smt_duration_percentage2(selected_data, 1800, 3600)
    positive_percentage(selected_data, 0, 10)
    positive_percentage(selected_data, 10, 25)
    positive_percentage(selected_data, 25, 50)
    positive_percentage2(selected_data, 50, 100)
    num_states_percentage(selected_data, 2, 5)
    num_states_percentage(selected_data, 5, 10)
    num_states_percentage(selected_data, 10, 15)
    num_states_percentage2(selected_data, 15, 20)
    sample_size_percentage(selected_data, 0, 25)
    sample_size_percentage(selected_data, 25, 50)
    sample_size_percentage(selected_data, 50, 75)
    sample_size_percentage2(selected_data, 75, 100)


if __name__ == '__main__':
    import os
    import pandas as pd
    import matplotlib.pyplot as plt

    # no_cs_printing()
    #
    # no_cs_pos_perc_printing()

    # minimal_no_cs()

    cs_printing()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
