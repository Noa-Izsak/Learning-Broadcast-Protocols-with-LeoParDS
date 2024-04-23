import time


def number_of_procs_in_vector(state_vector):
    procs = 0
    for entry in state_vector:
        if entry == -1:
            continue
        procs += state_vector.get(entry)
    return procs


class BP_class:

    def __init__(self, states_amount: int, actions: {int: {str: int}}, initial_state: int,
                 receivers: {int: {str: (int, bool)}}):
        """
        :param states_amount: states are marked as : 0, 1, .... , (states_amount - 1)
        :param actions: {state: {set of actions feasible from the given state}}
                        specifically: {from_state: {action: to_state}}
        :param initial_state: int val of the appropriate state
        :param receivers: {from_state: {action: (to_state, is_changed)}}
                          is_changed=True, has been chosen as this location, else, default
        """
        if initial_state >= states_amount:
            print("initial state must be in the area of 0 to %s", states_amount)
            pass
        self.initial_state = initial_state
        self.actions = actions
        self.receivers = {}
        self.update_self_loops(receivers)
        pass

    def update_receivers(self, origin_state_int_index, action, landing_state_int_index, known):
        """
        update receivers
        :param origin_state_int_index: origin state, from state
        :param action: the action
        :param landing_state_int_index: destination state
        :param known: is it known or is a guess, known = True, guess = False
        :return:
        """
        if self.receivers.get(origin_state_int_index) is not None:
            if self.receivers.get(origin_state_int_index).get(action) is not None:
                (state_ind, status) = self.receivers.get(origin_state_int_index).get(action)
            else:
                return
        else:
            return
        self.receivers[origin_state_int_index][action] = (landing_state_int_index, known)
        pass

    def update_action(self, org_state, action, landing):
        """
        update a given action
        :param org_state: each action for a specific given action...
        :param action: the action
        :param landing: lending state for acting
        :return:
        """
        if self.actions.get(org_state) is not None:
            self.actions.get(org_state)[action] = landing
        else:
            self.actions[org_state] = dict()
            self.actions.get(org_state)[action] = landing

        pass

    def get_state_index_by_action(self, action) -> int:
        """
        get the index representing the state the action is feasible from
        :param action: str for the given action
        :return: return the appropriate int for the state this action is feasible from, -1 if not found
        """
        return max([v[0] if action in v[1] else -1 for v in self.actions.items()])

    def act_action(self, state_vector, act):
        """
        for current state vector change it accord to the act
        :param state_vector: current state vector {state_index: number_of_procs}
        :param act: str of current action to perform
        :return: the appropriate state vector after acting the given action
        """
        new_state_vector = {x: 0 for x in self.actions}
        index = self.get_state_index_by_action(act)
        for state in state_vector:
            if state == -1 or state_vector.get(state) == 0:
                continue
            (state_index, status) = self.receivers.get(state).get(act)
            if index == state:
                new_state_vector[self.actions.get(state).get(act)] += 1
                if state_vector.get(state) > 1:
                    new_state_vector[state_index] += (state_vector.get(state) - 1)
            else:
                new_state_vector[state_index] += state_vector.get(state)
        procs1 = 0
        for entry in new_state_vector:
            procs1 += new_state_vector.get(entry)
        return new_state_vector

    def is_feasible(self, number_of_proc: int, set_of_actions: [str]):
        """
        is the set of actions is feasible for the given BP
        :param number_of_proc: number of proc
        :param set_of_actions: sequence of actions
        :return: boolean value - is feasible or not
        """
        state_vector = {x: 0 for x in self.actions}
        state_vector[self.initial_state] = number_of_proc
        for act in set_of_actions:
            if state_vector.get(self.get_state_index_by_action(act)) >= 1:
                state_vector = self.act_action(state_vector, act)  # act the action and check the next
                continue
            else:
                return False
        return True

    def characteristic_set_part2(self, known_actions: {str}, all_acts: {str}, known_vectors: {tuple},
                                 current_heads: {tuple: [str]}, set_ret: [str], neg_ret: [str]) -> [str]:
        """
        find the characteristic_set from the actions
        :param all_acts: all actions in the BP
        :param known_actions: so far seen actions
        :param known_vectors: so far seen vectors
        :param current_heads: heads to follow  frozenset{(state:int,amount:int)}:[str]
        :param set_ret: positive samples to return
        :param neg_ret: negative samples to return
        :return: set_ret, neg_ret
        """
        dict_ret = dict()
        set_ret_1 = []
        for w in set_ret:
            for i in range(len(w)):
                set_ret_1.append(w[:i + 1])  # all the feasible sub states
        dict_ret['positive'] = list(set(set_ret_1))
        dict_ret['negative'] = list(set(neg_ret))
        if len(current_heads) == 0:
            return dict_ret
        new_current_heads = {}

        for state_vector in current_heads:
            s_vec = list(state_vector)
            for head in range(len(s_vec)):
                if s_vec[head] != 0:
                    for act in self.actions.get(head):
                        def get_state_vector(vec: []):
                            """ dictionary representation of the vector as a list"""
                            dictionary = {}
                            for counter in range(len(vec)):
                                dictionary[counter] = vec[counter]
                            return dictionary

                        if (act in known_actions) and (state_vector in known_vectors):
                            new_dict_state_vector = self.act_action(get_state_vector(s_vec), act)
                            new_state = tuple(new_dict_state_vector.values())
                            s_new_vec = list(new_state)
                            for new_head in range(len(s_new_vec)):
                                if s_new_vec[new_head] != 0:
                                    for new_act in self.actions.get(new_head):
                                        [set_ret.append(''.join(x) + act + new_act) for x in
                                         list(current_heads.get(state_vector))]
                                else:
                                    for new_act in self.actions.get(new_head):
                                        [neg_ret.append(''.join(x) + act + new_act) for x in
                                         list(current_heads.get(state_vector))]
                            set_ret_1 = []
                            for w in set_ret:
                                for i in range(len(w)):
                                    set_ret_1.append(w[:i + 1])
                            dict_ret['positive'] += list(set(set_ret_1))
                            dict_ret['positive'] = list(set(dict_ret['positive']))
                            dict_ret['negative'] += list(set(neg_ret))
                            dict_ret['negative'] = list(set(dict_ret['negative']))
                            # return dict_ret
                            # break
                        else:
                            new_dict_state_vector = self.act_action(get_state_vector(s_vec), act)
                            new_state = tuple(new_dict_state_vector.values())
                            if new_current_heads.get(new_state) is None:
                                head_to_call = dict()
                                if len(current_heads.get(state_vector)) > 1:
                                    temp = []
                                    for h in current_heads.get(state_vector):
                                        temp += [''.join(h) + act]
                                    head_to_call[new_state] = temp
                                else:
                                    head_to_call[new_state] = [' '.join(current_heads.get(state_vector)) + act]
                                new_known_vectors = known_vectors.copy()
                                new_known_vectors.add(state_vector)
                                new_known_action = known_actions.copy()
                                if act not in known_actions:
                                    new_known_action.add(act)
                                dict_ret11 = self.characteristic_set_part2(new_known_action, all_acts,
                                                                           new_known_vectors, head_to_call, set_ret,
                                                                           neg_ret)

                                dict_ret['positive'] = list(set(dict_ret['positive'] + dict_ret11['positive']))
                                dict_ret['negative'] = list(set(dict_ret['negative'] + dict_ret11['negative']))
                            else:
                                head_to_call = dict()
                                if len(current_heads.get(state_vector)) > 1:
                                    temp = []
                                    for h in current_heads.get(state_vector):
                                        temp += [''.join(h) + act]
                                    head_to_call[new_state] = head_to_call[new_state] + temp
                                else:
                                    head_to_call[new_state] = head_to_call[new_state] + [
                                        ' '.join(current_heads.get(state_vector)) + act]
                                new_known_vectors = known_vectors.copy()
                                new_known_vectors.add(state_vector)
                                new_known_action = known_actions.copy()
                                if act not in known_actions:
                                    new_known_action.add(act)
                                dict_ret11 = self.characteristic_set_part2(new_known_action, all_acts,
                                                                           new_known_vectors,
                                                                           head_to_call, set_ret, neg_ret)

                                dict_ret['positive'] = list(set(dict_ret['positive'] + dict_ret11['positive']))
                                dict_ret['negative'] = list(set(dict_ret['negative'] + dict_ret11['negative']))
                else:  # is 0
                    for act in self.actions[head]:
                        if not list(current_heads.get(state_vector)):  # is empty
                            neg_ret.append(act)
                        else:
                            [neg_ret.append(''.join(x) + act) for x in list(current_heads.get(state_vector))]

        set_ret_1 = []
        for w in set_ret:
            for i in range(len(w)):
                set_ret_1.append(w[:i + 1])  # all the feasible sub states
        dict_ret['positive'] += list(set(set_ret_1))
        dict_ret['positive'] = list(set(dict_ret['positive']))
        dict_ret['negative'] += list(set(neg_ret))
        dict_ret['negative'] = list(set(dict_ret['negative']))
        return dict_ret

    def characteristic_set(self, known_actions: {str}, all_acts: {str}, known_vectors: {tuple},
                           current_heads: {tuple: [str]}, set_ret: [str], neg_ret: [str]) -> [str]:
        """
        find the characteristic_set from the actions
        :param all_acts: all actions in the BP
        :param known_actions: so far seen actions
        :param known_vectors: so far seen vectors
        :param current_heads: heads to follow  frozenset{(state:int,amount:int)}:[str]
        :param set_ret: positive samples to return
        :param neg_ret: negative samples to return
        :return: set_ret, neg_ret
        """
        dict_ret = dict()
        set_ret_1 = []
        for w in set_ret:
            for i in range(len(w)):
                set_ret_1.append(w[:i + 1])  # all the feasible sub states
        dict_ret['positive'] = list(set(set_ret_1))
        dict_ret['negative'] = list(set(neg_ret))
        if len(current_heads) == 0:
            return dict_ret
        new_current_heads = {}
        vectors_to_append = []
        for state_vector in current_heads:
            s_vec = list(state_vector)
            for head in range(len(s_vec)):
                if s_vec[head] != 0:
                    for act in self.actions.get(head):
                        def get_state_vector(vec: []):
                            """ dictionary representation of the vector as a list"""
                            dictionary = {}
                            for counter in range(len(vec)):
                                dictionary[counter] = vec[counter]
                            return dictionary

                        if (act in known_actions) and (state_vector in known_vectors):
                            new_dict_state_vector = self.act_action(get_state_vector(s_vec), act)
                            new_state = tuple(new_dict_state_vector.values())
                            s_new_vec = list(new_state)
                            for new_head in range(len(s_new_vec)):
                                if s_new_vec[new_head] != 0:
                                    for new_act in self.actions.get(new_head):
                                        [set_ret.append(''.join(x) + act + new_act) for x in
                                         list(current_heads.get(state_vector))]
                                else:
                                    for new_act in self.actions.get(new_head):
                                        [neg_ret.append(''.join(x) + act + new_act) for x in
                                         list(current_heads.get(state_vector))]
                            # break
                        else:
                            if act not in known_actions:
                                known_actions.add(act)
                            if state_vector not in known_vectors:
                                vectors_to_append.append(state_vector)

                            new_dict_state_vector = self.act_action(get_state_vector(s_vec), act)
                            new_state = tuple(new_dict_state_vector.values())
                            if new_current_heads.get(new_state) is None:
                                if len(current_heads.get(state_vector)) > 1:
                                    temp = []
                                    for h in current_heads.get(state_vector):
                                        temp += [''.join(h) + act]
                                    new_current_heads[new_state] = temp
                                else:
                                    new_current_heads[new_state] = [' '.join(current_heads.get(state_vector)) + act]
                            else:
                                if len(current_heads.get(state_vector)) > 1:
                                    temp = []
                                    for h in current_heads.get(state_vector):
                                        temp += [''.join(h) + act]
                                    new_current_heads[new_state] = new_current_heads[new_state] + temp
                                else:
                                    new_current_heads[new_state] = new_current_heads[new_state] + [
                                        ' '.join(current_heads.get(state_vector)) + act]
                else:  # is 0
                    for act in self.actions[head]:
                        if not list(current_heads.get(state_vector)):  # is empty
                            neg_ret.append(act)
                        else:
                            [neg_ret.append(''.join(x) + act) for x in list(current_heads.get(state_vector))]
        vectors_to_append = list(set(vectors_to_append))
        for v in vectors_to_append:
            known_vectors.add(v)

        return self.characteristic_set(known_actions, all_acts, known_vectors, new_current_heads, set_ret, neg_ret)

    def get_all_chars(self):
        """ return all actions set (returns A) """
        all_chars = set()
        for sub_dict in self.actions.values():
            all_chars.update(sub_dict.keys())
        return all_chars

    def find_characteristic_set_multi_procs(self, procs):
        """
        given number of procs find the appropriate sub characteristic_sets
        :param procs: number of process the BP run for
        :return: the characteristic_sets for number of @procs
        """
        state_vector = [0] * len(self.actions)
        state_vector[self.initial_state] = procs
        state_vector = tuple(state_vector)
        all_acts = self.get_all_chars()
        return self.characteristic_set_part2(set(), all_acts, set(), {state_vector: {}}, [], [])

    def has_receive_action(self, receiver_dict: {int: {str: int}}, known):
        """
        :param receiver_dict:
        :param known:  is it known or a guess
        :return:
        """
        for rec_state in receiver_dict:
            for act_state in self.actions:
                for act in self.actions.get(act_state):
                    if receiver_dict.get(rec_state).get(act) is None:
                        receiver_dict[rec_state][act] = (rec_state, known)
        pass

    def update_self_loops(self, receiver: {int: {str: int}}):
        """
        if some receive weren't defined then make them a self loop
        :param receiver: given receivers to define
        """
        for state_index in self.actions:
            if receiver.get(state_index) is not None:
                for act in receiver.get(state_index):
                    if not (type(receiver.get(state_index).get(act)) is tuple):  # set default self loops
                        receiver.get(state_index)[act] = (receiver.get(state_index).get(act), False)
                self.receivers[state_index] = receiver.get(state_index)
            else:
                self.receivers[state_index] = {}
        self.has_receive_action(self.receivers, False)  # set the missing values
        pass

    def find_cs_to_a_limit(self, cutoff_limit, sample_limit):
        counter = 1
        characteristic_sets = dict()
        characteristic_sets['positive'] = dict()
        characteristic_sets['negative'] = dict()
        start_time = time.perf_counter()
        curr = self.find_characteristic_set_multi_procs(counter)
        characteristic_sets['positive'][counter] = list(set(curr['positive']))
        characteristic_sets['negative'][counter] = list(set(curr['negative']))

        tot_pos_new = set(curr['positive'])
        tot_neg_new = set(curr['negative'])

        next_set = self.find_characteristic_set_multi_procs(counter + 1)
        while set(curr['positive']) != set(next_set['positive']) and set(curr['negative']) != set(next_set['negative']):
            counter += 1
            print("counter ", counter)
            curr['positive'] = next_set['positive']
            curr['negative'] = next_set['negative']

            curr_time = time.perf_counter()
            if len(curr['positive']) + len(curr['negative']) > sample_limit:
                return characteristic_sets, float(curr_time - start_time)
            characteristic_sets['positive'][counter] = list(set(curr['positive']))
            characteristic_sets['negative'][counter] = list(set(curr['negative']))
            pos_copy = set(curr['positive']).copy()
            nrg_copy = set(curr['negative']).copy()
            tot_pos_new.update(pos_copy)
            tot_neg_new.update(nrg_copy)
            curr_time = time.perf_counter()
            if counter >= cutoff_limit:
                return characteristic_sets, float(curr_time - start_time)
            next_set = self.find_characteristic_set_multi_procs(counter + 1)
        characteristic_sets['positive'][counter + 1] = list(set(next_set['positive']))
        characteristic_sets['negative'][counter + 1] = list(set(next_set['negative']))
        end_time = time.perf_counter()
        return characteristic_sets, float(end_time - start_time)

    def find_all_characteristic_sets_for_learning(self, cutoff_limit, cs_creation_time_limit, words_limit=50000):
        """
        for the given BP -self , find all the characteristic_sets
        :return: {number of proc : characteristic_sets} for all number of procs until maximal number required
        """
        counter = 1
        characteristic_sets = dict()
        characteristic_sets['positive'] = dict()
        characteristic_sets['negative'] = dict()

        start_time = time.perf_counter()
        curr = self.find_characteristic_set_multi_procs(counter)
        characteristic_sets['positive'][counter] = list(set(curr['positive']))
        characteristic_sets['negative'][counter] = list(set(curr['negative']))

        tot_pos_new = set(curr['positive'])
        tot_neg_new = set(curr['negative'])

        next_set = self.find_characteristic_set_multi_procs(counter + 1)
        while set(curr['positive']) != set(next_set['positive']) and set(curr['negative']) != set(next_set['negative']):
            counter += 1
            print("counter ", counter)
            curr['positive'] = next_set['positive']
            curr['negative'] = next_set['negative']

            curr_time = time.perf_counter()
            if float(curr_time - start_time) > cs_creation_time_limit or \
                    (len(curr['positive']) + len(curr['negative']) > words_limit):
                return characteristic_sets, -1
            characteristic_sets['positive'][counter] = list(set(curr['positive']))
            characteristic_sets['negative'][counter] = list(set(curr['negative']))
            pos_copy = set(curr['positive']).copy()
            nrg_copy = set(curr['negative']).copy()
            tot_pos_new.update(pos_copy)
            tot_neg_new.update(nrg_copy)

            if counter >= cutoff_limit:
                return characteristic_sets, -1
            next_set = self.find_characteristic_set_multi_procs(counter + 1)
        characteristic_sets['positive'][counter + 1] = list(set(next_set['positive']))
        characteristic_sets['negative'][counter + 1] = list(set(next_set['negative']))
        end_time = time.perf_counter()
        return characteristic_sets, float(end_time - start_time)

    def __str__(self):
        str_ret = "\nTHE BP:\n initial state: " + str(self.initial_state) + "\n actions: " + str(self.actions) + \
                  "\n receivers: " + str(self.receivers)
        return str_ret

    def __repr__(self):
        return str(self)

    def feasible_set(self, state_vec: {int: int}):
        non_empty_entries = list(filter(lambda x: state_vec[x] > 0, state_vec))
        if -1 in non_empty_entries:
            non_empty_entries.remove(-1)
        if not non_empty_entries:  # non_empty_entries == []
            return set()
        acts = set()
        for e in non_empty_entries:
            acts |= set(self.actions[e].keys())
        return acts
