import random

from BP_Class import BP_class

a_val = 97
z_val = 122
A_val = 65
Z_val = 90
act_names = [str(chr(c)) for c in range(a_val, z_val + 1)] + [str(chr(c)) for c in range(A_val, Z_val + 1)] + [
    str(chr(n)) for n in range(0, 10)] + ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '[',
                                          ']', '{', '}', '|', '~', '`', ',']
alphabet = [str(chr(c)) for c in range(a_val, z_val + 1)] + [str(chr(c)) for c in range(A_val, Z_val + 1)] + [
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

    def __init__(self, min_number_of_states, min_number_of_act, max_number_of_states=None, max_number_of_act=None,
                 print_info=False):
        """
        given these parameters, we create a BP that has ns as the number of states
        (between min_number_of_states and max_number_of_states)
        and na being the number of actions to be the number of extra actions to be distributed in the system
        if max_number_of_states (resp. max_number_of_act) is None
        then ns (resp. na) determent only by min_number_of_states (resp. min_number_of_act)
        """
        if min_number_of_states is None or not (type(min_number_of_states) == int):
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
        if min_number_of_act is None or not (type(min_number_of_act) == int):
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
        if print_info:
            print(f"min_state {min_number_of_states} mis acts {min_number_of_act}\n"
                  f"max state {max_number_of_states} max_act {max_number_of_act}\n"
                  f"ns = {ns} na = {na} and the bp:\n{self.bp}")
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
    :param cutoff:
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
