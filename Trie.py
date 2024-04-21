# from :https://albertauyeung.github.io/2020/06/15/python-trie.html/
class TrieNode:
    """A node in the trie structure"""

    def __init__(self, char):
        self.char = char
        self.is_end = False
        self.counter = 0
        self.children = {}


class Trie(object):
    """The trie object"""

    def __init__(self):
        """
        The trie has at least the root node.
        The root node does not store any character
        """
        self.root = TrieNode("")
        self.output = []

    def insert(self, word_to_insert):
        """Insert a word into the trie"""
        node = self.root

        # Loop through each character in the word
        # Check if there is no child containing the character, create a new child for the current node
        for char in word_to_insert:
            if char in node.children:
                node = node.children[char]
            else:
                # If a character is not found,
                # create a new node in the trie
                new_node = TrieNode(char)
                node.children[char] = new_node
                node = new_node

        # Mark the end of a word
        node.is_end = True

        # Increment the counter to indicate that we see this word once more
        node.counter += 1

    def dfs(self, node, prefix):
        """Depth-first traversal of the trie

        Args:
            - node: the node to start with
            - prefix: the current prefix, for tracing a
                word while traversing the trie
        """
        if node.is_end:
            self.output.append((prefix + node.char, node.counter))

        for child in node.children.values():
            self.dfs(child, prefix + node.char)

    def query(self, x):
        """Given an input (a prefix), retrieve all words stored in
        the trie with that prefix, sort the words by the number of
        times they have been inserted
        """
        self.output = []
        node = self.root

        for char in x:
            if char in node.children:
                node = node.children[char]
            else:
                return []

        self.dfs(node, x[:-1])

        return sorted(self.output, key=lambda xi: xi[1], reverse=True)


def is_new_word(cs_words, curr_proc, new_word):
    """
    given the cs words and a curr amount of procs, check if for less process this word already existed
    if yes - return False (not new)
    else - return True, is new
    """
    for procs in cs_words:
        if procs < curr_proc:
            for curr_word in cs_words[procs]:
                if new_word == curr_word:
                    return False
    return True


def is_new_word_and_prefix(cs_words, curr_proc, new_word):
    """
    :param cs_words: the cs words - dictionary of key is the number of procs, value is the set of words
    :param curr_proc: curr amount of procs that the new word is from
    :param new_word: the new word to check if appeared before
    """
    set_words = set()
    for procs in cs_words:
        if procs < curr_proc:
            for cs_w in cs_words[procs]:
                set_words.add(cs_w)
    # print("set of words :: ", set_words)
    if new_word in set_words:
        return False, "", set_words
    for i in range(len(new_word), 0, -1):
        if len(list(filter(lambda x: x.startswith(new_word[:i]), set_words))) > 0:
            # if there are words that started the same
            return True, new_word[:i], set_words
    return True, "", set_words


def check_sub_trees(cs_word, curr_proc, pref_to_compare):
    """
    :param cs_word: the cs word {proc amount : [set of words in this amount]}
    :param curr_proc: curr amount of procs that the pref_to_compare is related to
    :param pref_to_compare: the prefix that we will lock on the existence of the subtree
    """
    prev_set, trie_curr, trie_prev = init_tries(cs_word, curr_proc)

    ''' travers on trie_prev, check if the subtree of 'trie_curr.query(pref_to_compare)' 
        which is 'sub_tree_for_compare' exists in the prev tree '''
    sub_tree_for_compare = generate_subtree_for_compare(pref_to_compare, trie_curr)
    if sub_tree_for_compare == {''}:
        return True, ""
    prev_list = list(prev_set)  # prev_set === trie_prev.query("")
    prev_list.sort(reverse=True, key=lambda x: len(x))
    bad_prefixes = set()  # if some prefixes already known to have wrong words then we wouldn't use them
    '''check if there is a node (a pref) in the prev_trie s.t. its sub tree is equal to sub_tree_for_compare'''
    for prev_pref in prev_list:
        prev_subtree_to_compare = set()
        prev_subtree_to_compare.add('')
        if len(list(filter(lambda x: x.startswith(prev_pref), bad_prefixes))) > 0:
            ''' In case prev_pref starts with the same prefix as one of those that's is the bad_prefixes'''
            continue
        for (prev_w, _) in trie_prev.query(prev_pref):
            prev_subtree_to_compare.add(prev_w[len(prev_pref):])
        if prev_subtree_to_compare.issubset(sub_tree_for_compare) and sub_tree_for_compare.issubset(
                prev_subtree_to_compare):
            return True, prev_pref
        check_subtree_is_bad_prefix(bad_prefixes, prev_pref, prev_subtree_to_compare, sub_tree_for_compare)
    return False, ""


def generate_subtree_for_compare(pref_to_compare, trie_curr):
    """
    generating the subtree for compares ,
    given the trie return the set of the subtrees for this prefix
    """
    sub_tree_for_compare = set()  # the subtree of the node to is to_compare
    sub_tree_for_compare.add('')
    size = len(pref_to_compare)
    for (curr_word, _) in trie_curr.query(pref_to_compare):
        sub_tree_for_compare.add(curr_word[size:])
    return sub_tree_for_compare


def init_tries(cs_word, curr_proc):
    """
    given the cs (procs: list of words), create two tries,
    trie prev for procs < curr_proc
    trie curr for procs <= curr_proc
    prev_set is the set of all the words of trie_prev
    """
    trie_prev = Trie()
    trie_curr = Trie()
    prev_set = set()  # the set of words from trie_prev
    prev_set.add('')
    for procs in cs_word:
        if procs < curr_proc:
            for cs_w in cs_word.get(procs):
                trie_prev.insert(cs_w)
                trie_curr.insert(cs_w)
                prev_set.add(cs_w)
        if procs == curr_proc:
            for cs_w in cs_word.get(procs):
                trie_curr.insert(cs_w)
    return prev_set, trie_curr, trie_prev


def check_subtree_is_bad_prefix(bad_prefixes, prev_pref, prev_subtree_to_compare, sub_tree_for_compare):
    """
    a function that given the 'prev_subtree_to_compare', check if there is a "wrong" suffix,
    if some suffix doesn't belong to none of those of 'sub_tree_for_compare'. Then this is a wrong subtree
    :param bad_prefixes: the bad prefixes so far
    """
    for w in prev_subtree_to_compare:
        if prev_pref in bad_prefixes:
            break
        if len(list(filter(lambda x: x.endswith(w), sub_tree_for_compare))) == 0:
            bad_prefixes.add(prev_pref)
    pass


def is_all_new_nodes_homomorphic(cs_words, curr_proc):
    """
    given cs words and cuu_procs, check if the newly added words (in curr proc amount)
    have some subtree they look like in the previous tree (less than curr_proc)
    if all of them have a homomorphic tree then return True, else return False
    """
    for p in cs_words:
        if p == curr_proc:
            for w in cs_words.get(curr_proc):
                bool_val, pref, set_words = is_new_word_and_prefix(cs_words, curr_proc, w)
                print("bool val ", bool_val)
                if bool_val:
                    print("set of words :: ", set_words)
                    print("pref ", pref)
                    for i in range(len(pref) + 1, len(w) + 1):
                        bool_val2, pref2 = check_sub_trees(cs_words, curr_proc, w[:i])
                        if not bool_val2:  # if no one is similar to the new node
                            return False
    return True


def example_run():
    """ example """
    trie_info = Trie()
    cs = {1: ['a', 'af'], 2: ['abc', 'adf', 'abf', 'abce', 'abcef']}
    for proc in cs:
        for w in cs.get(proc):
            trie_info.insert(w)
    print("trie_info.query('ab')", trie_info.query('ab'))
    prev_set = set()
    for (prev_word, _) in trie_info.query(""):
        prev_set.add(prev_word)
    prev_list = list(prev_set)

# example_run()
