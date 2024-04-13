# from :https://albertauyeung.github.io/2020/06/15/python-trie.html/
class TrieNode:
    """A node in the trie structure"""

    def __init__(self, char):
        # the character stored in this node
        self.char = char

        # whether this can be the end of a word
        self.is_end = False

        # a counter indicating how many times a word is inserted
        # (if this node's is_end is True)
        self.counter = 0

        # a dictionary of child nodes
        # keys are characters, values are nodes
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
        # Use a variable within the class to keep all possible outputs
        # As there can be more than one word with such prefix
        self.output = []
        node = self.root

        # Check if the prefix is in the trie
        for char in x:
            if char in node.children:
                node = node.children[char]
            else:
                # cannot found the prefix, return empty list
                return []

        # Traverse the trie to get all candidates
        self.dfs(node, x[:-1])

        # Sort the results in reverse order and return
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
    print("is new word and pref, the (?) new word is ", new_word)
    set_words = set()
    for procs in cs_words:
        if procs < curr_proc:
            for cs_w in cs_words[procs]:
                set_words.add(cs_w)
    # print("set of words :: ", set_words)
    if new_word in set_words:
        return False, "", set_words
    for i in range(len(new_word), 0, -1):
        print("new_word[:i]", new_word[:i])
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
    print("sub_tree_for_compare", sub_tree_for_compare)
    if sub_tree_for_compare == {''}:
        return True, ""
    prev_list = list(prev_set)  # prev_set === trie_prev.query("")
    prev_list.sort(reverse=True, key=lambda x: len(x))
    bad_prefixes = set()  # if some prefixes already known to have wrong words then we wouldn't use them
    '''check if there is a node (a pref) in the prev_trie s.t. its sub tree is equal to sub_tree_for_compare'''
    for prev_pref in prev_list:
        print("prev_pref :: ", prev_pref)
        print("the bad prefixes is ", bad_prefixes)
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
        print("prev subtree ", prev_subtree_to_compare)
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
    print("the pref to compare is  ", pref_to_compare)
    print("size is ", size)
    for (curr_word, _) in trie_curr.query(pref_to_compare):
        # print("curr word ", curr_word)
        # print("curr_word[size:] ", curr_word[size:])
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


# TODO - Create a general func that check for each of the new nodes in the curr_trie,
#       if there is a subtree in the previous iteration
#       taking under account that for some there is the \epsilon-connection
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


''' example : '''

trie_info = Trie()
cs = {1: ['a', 'af'], 2: ['abc', 'adf', 'abf', 'abce', 'abcef']}
# trie_info.insert('a')
# trie_info.insert('abc')
# trie_info.insert('adf')
# trie_info.insert('abf')
# trie_info.insert('abce')
# trie_info.insert('abcef')
for proc in cs:
    for w in cs.get(proc):
        trie_info.insert(w)
print("trie_info.query('ab')", trie_info.query('ab'))

prev_set = set()
for (prev_word, _) in trie_info.query(""):
    prev_set.add(prev_word)
prev_list = list(prev_set)

# print("new scenario: ")
# print(check_sub_trees(cs, 2, 'abc'))
#
# ''' example 2: '''
# print("-------- example 2 --------")
# cs1 = {1: ['', 'a', 'ab', 'abb'], 2: ['', 'a', 'ab', 'abb', 'aba', 'aa', 'aab', 'aabb']}
# print("print: ", is_all_new_nodes_homomorphic(cs1, 2))
#
# ''' example 3: '''
# print("~~~~~~~~~ example 3: ~~~~~~~~~")
# cs2 = {1: ['qzz', 'qzd', 'qzi', 'qdecc', 'qiecc'],
#        2: ['qzz', 'qzd', 'qzi', 'qzf', 'qdec', 'qdfc', 'qiec', 'qfcc', 'qiabc', 'qiazzz', 'qiazcz', 'qiazzd', 'qiazcd',
#            'qiazzi', 'qiazci', 'qiazzc', 'qiazcc', 'qiadec', 'qiaiec', 'qiaibc', 'qiadwz', 'qiadwd', 'qiadwi', 'qiadwf',
#            'qiazdec', 'qiaziec', 'qiazdce', 'qiazice', 'qiazdcc', 'qiazicc'],
#        3: ['qzz', 'qzd', 'qzi', 'qzf', 'qdec', 'qdfc', 'qiec', 'qfcc', 'qiabc', 'qiafc', 'qiazzz', 'qiazcz', 'qiazzd',
#            'qiazcd', 'qiazzi', 'qiazci', 'qiazzc', 'qiazcc', 'qiazzf', 'qiazcf', 'qiazfc', 'qiadec', 'qiadfc', 'qiaiec',
#            'qiaibc', 'qiadwz', 'qiadwd', 'qiadwi', 'qiadwf', 'qiazdec', 'qiazdfc', 'qiaziec', 'qiaiabc', 'qiazdce',
#            'qiazdcc', 'qiazdcf', 'qiazice', 'qiazicc', 'qiazica', 'qiaziazz', 'qiaiazzz', 'qiaiazcz', 'qiaziazd',
#            'qiaiazzd', 'qiaiazcd', 'qiaziazi', 'qiaiazzi', 'qiaiazci', 'qiaziazc', 'qiaiazzc', 'qiaiazcc', 'qiaziacz',
#            'qiaziacd', 'qiaziaci', 'qiaziacc', 'qiaziacb', 'qiaziabc', 'qiaiadec', 'qiaiaiec', 'qiaiaibc', 'qiaiadwz',
#            'qiaiadwd', 'qiaiadwi', 'qiaiadwb', 'qiaiadwf', 'qiaiazdec', 'qiaiaziec', 'qiaziadce', 'qiaziadcc',
#            'qiaziadcw', 'qiaziadwz', 'qiaziadwd', 'qiaziadwi', 'qiaziadwc', 'qiaziadwf', 'qiaziaice', 'qiaziaicc',
#            'qiaziaicb', 'qiaiazdce', 'qiaiazice', 'qiaiazdcc', 'qiaiazicc'],
#        4: ['qzz', 'qzd', 'qzi', 'qzf', 'qdec', 'qdfc', 'qiec', 'qfcc', 'qiabc', 'qiafc', 'qiazzz', 'qiazcz', 'qiazzd',
#            'qiazcd', 'qiazzi', 'qiazci', 'qiazzc', 'qiazcc', 'qiazzf', 'qiazcf', 'qiazfc', 'qiadec', 'qiadfc', 'qiaiec',
#            'qiaibc', 'qiadwz', 'qiadwd', 'qiadwi', 'qiadwf', 'qiazdec', 'qiazdfc', 'qiaziec', 'qiaiabc', 'qiaiafc',
#            'qiazdce', 'qiazdcc', 'qiazdcf', 'qiazice', 'qiazicc', 'qiazica', 'qiaziazz', 'qiaiazzz', 'qiaiazcz',
#            'qiaziazd', 'qiaiazzd', 'qiaiazcd', 'qiaziazi', 'qiaiazzi', 'qiaiazci', 'qiaziazc', 'qiaiazzc', 'qiaiazcc',
#            'qiaziazf', 'qiaiazzf', 'qiaiazcf', 'qiaziacz', 'qiaziacd', 'qiaziaci', 'qiaziacc', 'qiaziacb', 'qiaziacf',
#            'qiaziabc', 'qiaziafc', 'qiaiazfc', 'qiaiadec', 'qiaiadfc', 'qiaiaiec', 'qiaiaibc', 'qiaiadwz', 'qiaiadwd',
#            'qiaiadwi', 'qiaiadwb', 'qiaiadwf', 'qiaziadec', 'qiaziadfc', 'qiaziaiec', 'qiaziaibc', 'qiaiazdec',
#            'qiaiazdfc', 'qiaiaziec', 'qiaiaiabc', 'qiaziadce', 'qiaziadcc', 'qiaziadcf', 'qiaziadcw', 'qiaziadwz',
#            'qiaziadwd', 'qiaziadwi', 'qiaziadwc', 'qiaziadwf', 'qiaziaice', 'qiaziaicc', 'qiaziaicb', 'qiaziaica',
#            'qiaiazdce', 'qiaiazdcc', 'qiaiazdcf', 'qiaiazice', 'qiaiazicc', 'qiaiazica', 'qiaziaiazz', 'qiaiaziazz',
#            'qiaiaiazzz', 'qiaiaiazcz', 'qiaziaiazd', 'qiaiaziazd', 'qiaiaiazzd', 'qiaiaiazcd', 'qiaziaiazi',
#            'qiaiaziazi', 'qiaiaiazzi', 'qiaiaiazci', 'qiaziaiazc', 'qiaiaziazc', 'qiaiaiazzc', 'qiaiaiazcc',
#            'qiaziaiacz', 'qiaziaiacd', 'qiaziaiaci', 'qiaziaiacc', 'qiaziaiacb', 'qiaziaiabc', 'qiaiaziabc',
#            'qiaiaiadec', 'qiaiaiaiec', 'qiaiaiaibc', 'qiaiaziacz', 'qiaiaziacd', 'qiaiaziaci', 'qiaiaziacc',
#            'qiaiaziacb', 'qiaiaiadwz', 'qiaiaiadwd', 'qiaiaiadwi', 'qiaiaiadwb', 'qiaiaiadwf', 'qiaiaiazdec',
#            'qiaiaiaziec', 'qiaziaiadce', 'qiaziaiadcc', 'qiaziaiadcw', 'qiaziaiadwz', 'qiaziaiadwd', 'qiaziaiadwi',
#            'qiaziaiadwc', 'qiaziaiadwb', 'qiaziaiadwf', 'qiaziaiaice', 'qiaziaiaicc', 'qiaziaiaicb', 'qiaiaziadce',
#            'qiaiaziadcc', 'qiaiaziadcw', 'qiaiaziadwz', 'qiaiaziadwd', 'qiaiaziadwi', 'qiaiaziadwc', 'qiaiaziadwf',
#            'qiaiaziaice', 'qiaiaziaicc', 'qiaiaziaicb', 'qiaiaiazdce', 'qiaiaiazice', 'qiaiaiazdcc', 'qiaiaiazicc'],
#        5: ['qzz', 'qzd', 'qzi', 'qzf', 'qdec', 'qdfc', 'qiec', 'qfcc', 'qiabc', 'qiafc', 'qiazzz', 'qiazcz', 'qiazzd',
#            'qiazcd', 'qiazzi', 'qiazci', 'qiazzc', 'qiazcc', 'qiazzf', 'qiazcf', 'qiazfc', 'qiadec', 'qiadfc', 'qiaiec',
#            'qiaibc', 'qiadwz', 'qiadwd', 'qiadwi', 'qiadwf', 'qiazdec', 'qiazdfc', 'qiaziec', 'qiaiabc', 'qiaiafc',
#            'qiazdce', 'qiazdcc', 'qiazdcf', 'qiazice', 'qiazicc', 'qiazica', 'qiaziazz', 'qiaiazzz', 'qiaiazcz',
#            'qiaziazd', 'qiaiazzd', 'qiaiazcd', 'qiaziazi', 'qiaiazzi', 'qiaiazci', 'qiaziazc', 'qiaiazzc', 'qiaiazcc',
#            'qiaziazf', 'qiaiazzf', 'qiaiazcf', 'qiaziacz', 'qiaziacd', 'qiaziaci', 'qiaziacc', 'qiaziacb', 'qiaziacf',
#            'qiaziabc', 'qiaziafc', 'qiaiazfc', 'qiaiadec', 'qiaiadfc', 'qiaiaiec', 'qiaiaibc', 'qiaiadwz', 'qiaiadwd',
#            'qiaiadwi', 'qiaiadwb', 'qiaiadwf', 'qiaziadec', 'qiaziadfc', 'qiaziaiec', 'qiaziaibc', 'qiaiazdec',
#            'qiaiazdfc', 'qiaiaziec', 'qiaiaiabc', 'qiaiaiafc', 'qiaziadce', 'qiaziadcc', 'qiaziadcf', 'qiaziadcw',
#            'qiaziadwz', 'qiaziadwd', 'qiaziadwi', 'qiaziadwc', 'qiaziadwf', 'qiaziaice', 'qiaziaicc', 'qiaziaicb',
#            'qiaziaica', 'qiaiazdce', 'qiaiazdcc', 'qiaiazdcf', 'qiaiazice', 'qiaiazicc', 'qiaiazica', 'qiaziaiazz',
#            'qiaiaziazz', 'qiaiaiazzz', 'qiaiaiazcz', 'qiaziaiazd', 'qiaiaziazd', 'qiaiaiazzd', 'qiaiaiazcd',
#            'qiaziaiazi', 'qiaiaziazi', 'qiaiaiazzi', 'qiaiaiazci', 'qiaziaiazc', 'qiaiaziazc', 'qiaiaiazzc',
#            'qiaiaiazcc', 'qiaziaiazf', 'qiaiaziazf', 'qiaiaiazzf', 'qiaiaiazcf', 'qiaziaiacz', 'qiaziaiacd',
#            'qiaziaiaci', 'qiaziaiacc', 'qiaziaiacb', 'qiaziaiacf', 'qiaziaiabc', 'qiaziaiafc', 'qiaiaziabc',
#            'qiaiaziafc', 'qiaiaiazfc', 'qiaiaiadec', 'qiaiaiadfc', 'qiaiaiaiec', 'qiaiaiaibc', 'qiaiaziacz',
#            'qiaiaziacd', 'qiaiaziaci', 'qiaiaziacc', 'qiaiaziacb', 'qiaiaziacf', 'qiaiaiadwz', 'qiaiaiadwd',
#            'qiaiaiadwi', 'qiaiaiadwb', 'qiaiaiadwf', 'qiaziaiadec', 'qiaziaiadfc', 'qiaziaiaiec', 'qiaziaiaibc',
#            'qiaiaziadec', 'qiaiaziadfc', 'qiaiaziaiec', 'qiaiaziaibc', 'qiaiaiazdec', 'qiaiaiazdfc', 'qiaiaiaziec',
#            'qiaiaiaiabc', 'qiaziaiadce', 'qiaziaiadcc', 'qiaziaiadcf', 'qiaziaiadcw', 'qiaziaiadwz', 'qiaziaiadwd',
#            'qiaziaiadwi', 'qiaziaiadwc', 'qiaziaiadwb', 'qiaziaiadwf', 'qiaziaiaice', 'qiaziaiaicc', 'qiaziaiaicb',
#            'qiaziaiaica', 'qiaiaziadce', 'qiaiaziadcc', 'qiaiaziadcf', 'qiaiaziadcw', 'qiaiaziadwz', 'qiaiaziadwd',
#            'qiaiaziadwi', 'qiaiaziadwc', 'qiaiaziadwf', 'qiaiaziaice', 'qiaiaziaicc', 'qiaiaziaicb', 'qiaiaziaica',
#            'qiaiaiazdce', 'qiaiaiazdcc', 'qiaiaiazdcf', 'qiaiaiazice', 'qiaiaiazicc', 'qiaiaiazica', 'qiaziaiaiazz',
#            'qiaiaziaiazz', 'qiaiaiaziazz', 'qiaiaiaiazzz', 'qiaiaiaiazcz', 'qiaziaiaiazd', 'qiaiaziaiazd',
#            'qiaiaiaziazd', 'qiaiaiaiazzd', 'qiaiaiaiazcd', 'qiaziaiaiazi', 'qiaiaziaiazi', 'qiaiaiaziazi',
#            'qiaiaiaiazzi', 'qiaiaiaiazci', 'qiaziaiaiazc', 'qiaiaziaiazc', 'qiaiaiaziazc', 'qiaiaiaiazzc',
#            'qiaiaiaiazcc', 'qiaziaiaiacz', 'qiaziaiaiacd', 'qiaziaiaiaci', 'qiaziaiaiacc', 'qiaziaiaiacb',
#            'qiaziaiaiabc', 'qiaiaziaiabc', 'qiaiaiaziabc', 'qiaiaiaiadec', 'qiaiaiaiaiec', 'qiaiaiaiaibc',
#            'qiaiaziaiacz', 'qiaiaziaiacd', 'qiaiaziaiaci', 'qiaiaziaiacc', 'qiaiaziaiacb', 'qiaiaiaziacz',
#            'qiaiaiaziacd', 'qiaiaiaziaci', 'qiaiaiaziacc', 'qiaiaiaziacb', 'qiaiaiaiadwz', 'qiaiaiaiadwd',
#            'qiaiaiaiadwi', 'qiaiaiaiadwb', 'qiaiaiaiadwf', 'qiaiaiaiazdec', 'qiaiaiaiaziec', 'qiaziaiaiadce',
#            'qiaziaiaiadcc', 'qiaziaiaiadcw', 'qiaziaiaiadwz', 'qiaziaiaiadwd', 'qiaziaiaiadwi', 'qiaziaiaiadwc',
#            'qiaziaiaiadwb', 'qiaziaiaiadwf', 'qiaziaiaiaice', 'qiaziaiaiaicc', 'qiaziaiaiaicb', 'qiaiaziaiadce',
#            'qiaiaziaiadcc', 'qiaiaziaiadcw', 'qiaiaziaiadwz', 'qiaiaziaiadwd', 'qiaiaziaiadwi', 'qiaiaziaiadwc',
#            'qiaiaziaiadwb', 'qiaiaziaiadwf', 'qiaiaziaiaice', 'qiaiaziaiaicc', 'qiaiaziaiaicb', 'qiaiaiaziadce',
#            'qiaiaiaziadcc', 'qiaiaiaziadcw', 'qiaiaiaziadwz', 'qiaiaiaziadwd', 'qiaiaiaziadwi', 'qiaiaiaziadwc',
#            'qiaiaiaziadwf', 'qiaiaiaziaice', 'qiaiaiaziaicc', 'qiaiaiaziaicb', 'qiaiaiaiazdce', 'qiaiaiaiazice',
#            'qiaiaiaiazdcc', 'qiaiaiaiazicc'],
#        6: ['qzz', 'qzd', 'qzi', 'qzf', 'qdec', 'qdfc', 'qiec', 'qfcc', 'qiabc', 'qiafc', 'qiazzz', 'qiazcz', 'qiazzd',
#            'qiazcd', 'qiazzi', 'qiazci', 'qiazzc', 'qiazcc', 'qiazzf', 'qiazcf', 'qiazfc', 'qiadec', 'qiadfc', 'qiaiec',
#            'qiaibc', 'qiadwz', 'qiadwd', 'qiadwi', 'qiadwf', 'qiazdec', 'qiazdfc', 'qiaziec', 'qiaiabc', 'qiaiafc',
#            'qiazdce', 'qiazdcc', 'qiazdcf', 'qiazice', 'qiazicc', 'qiazica', 'qiaziazz', 'qiaiazzz', 'qiaiazcz',
#            'qiaziazd', 'qiaiazzd', 'qiaiazcd', 'qiaziazi', 'qiaiazzi', 'qiaiazci', 'qiaziazc', 'qiaiazzc', 'qiaiazcc',
#            'qiaziazf', 'qiaiazzf', 'qiaiazcf', 'qiaziacz', 'qiaziacd', 'qiaziaci', 'qiaziacc', 'qiaziacb', 'qiaziacf',
#            'qiaziabc', 'qiaziafc', 'qiaiazfc', 'qiaiadec', 'qiaiadfc', 'qiaiaiec', 'qiaiaibc', 'qiaiadwz', 'qiaiadwd',
#            'qiaiadwi', 'qiaiadwb', 'qiaiadwf', 'qiaziadec', 'qiaziadfc', 'qiaziaiec', 'qiaziaibc', 'qiaiazdec',
#            'qiaiazdfc', 'qiaiaziec', 'qiaiaiabc', 'qiaiaiafc', 'qiaziadce', 'qiaziadcc', 'qiaziadcf', 'qiaziadcw',
#            'qiaziadwz', 'qiaziadwd', 'qiaziadwi', 'qiaziadwc', 'qiaziadwf', 'qiaziaice', 'qiaziaicc', 'qiaziaicb',
#            'qiaziaica', 'qiaiazdce', 'qiaiazdcc', 'qiaiazdcf', 'qiaiazice', 'qiaiazicc', 'qiaiazica', 'qiaziaiazz',
#            'qiaiaziazz', 'qiaiaiazzz', 'qiaiaiazcz', 'qiaziaiazd', 'qiaiaziazd', 'qiaiaiazzd', 'qiaiaiazcd',
#            'qiaziaiazi', 'qiaiaziazi', 'qiaiaiazzi', 'qiaiaiazci', 'qiaziaiazc', 'qiaiaziazc', 'qiaiaiazzc',
#            'qiaiaiazcc', 'qiaziaiazf', 'qiaiaziazf', 'qiaiaiazzf', 'qiaiaiazcf', 'qiaziaiacz', 'qiaziaiacd',
#            'qiaziaiaci', 'qiaziaiacc', 'qiaziaiacb', 'qiaziaiacf', 'qiaziaiabc', 'qiaziaiafc', 'qiaiaziabc',
#            'qiaiaziafc', 'qiaiaiazfc', 'qiaiaiadec', 'qiaiaiadfc', 'qiaiaiaiec', 'qiaiaiaibc', 'qiaiaziacz',
#            'qiaiaziacd', 'qiaiaziaci', 'qiaiaziacc', 'qiaiaziacb', 'qiaiaziacf', 'qiaiaiadwz', 'qiaiaiadwd',
#            'qiaiaiadwi', 'qiaiaiadwb', 'qiaiaiadwf', 'qiaziaiadec', 'qiaziaiadfc', 'qiaziaiaiec', 'qiaziaiaibc',
#            'qiaiaziadec', 'qiaiaziadfc', 'qiaiaziaiec', 'qiaiaziaibc', 'qiaiaiazdec', 'qiaiaiazdfc', 'qiaiaiaziec',
#            'qiaiaiaiabc', 'qiaiaiaiafc', 'qiaziaiadce', 'qiaziaiadcc', 'qiaziaiadcf', 'qiaziaiadcw', 'qiaziaiadwz',
#            'qiaziaiadwd', 'qiaziaiadwi', 'qiaziaiadwc', 'qiaziaiadwb', 'qiaziaiadwf', 'qiaziaiaice', 'qiaziaiaicc',
#            'qiaziaiaicb', 'qiaziaiaica', 'qiaiaziadce', 'qiaiaziadcc', 'qiaiaziadcf', 'qiaiaziadcw', 'qiaiaziadwz',
#            'qiaiaziadwd', 'qiaiaziadwi', 'qiaiaziadwc', 'qiaiaziadwf', 'qiaiaziaice', 'qiaiaziaicc', 'qiaiaziaicb',
#            'qiaiaziaica', 'qiaiaiazdce', 'qiaiaiazdcc', 'qiaiaiazdcf', 'qiaiaiazice', 'qiaiaiazicc', 'qiaiaiazica',
#            'qiaziaiaiazz', 'qiaiaziaiazz', 'qiaiaiaziazz', 'qiaiaiaiazzz', 'qiaiaiaiazcz', 'qiaziaiaiazd',
#            'qiaiaziaiazd', 'qiaiaiaziazd', 'qiaiaiaiazzd', 'qiaiaiaiazcd', 'qiaziaiaiazi', 'qiaiaziaiazi',
#            'qiaiaiaziazi', 'qiaiaiaiazzi', 'qiaiaiaiazci', 'qiaziaiaiazc', 'qiaiaziaiazc', 'qiaiaiaziazc',
#            'qiaiaiaiazzc', 'qiaiaiaiazcc', 'qiaziaiaiazf', 'qiaiaziaiazf', 'qiaiaiaziazf', 'qiaiaiaiazzf',
#            'qiaiaiaiazcf', 'qiaziaiaiacz', 'qiaziaiaiacd', 'qiaziaiaiaci', 'qiaziaiaiacc', 'qiaziaiaiacb',
#            'qiaziaiaiacf', 'qiaziaiaiabc', 'qiaziaiaiafc', 'qiaiaziaiabc', 'qiaiaziaiafc', 'qiaiaiaziabc',
#            'qiaiaiaziafc', 'qiaiaiaiazfc', 'qiaiaiaiadec', 'qiaiaiaiadfc', 'qiaiaiaiaiec', 'qiaiaiaiaibc',
#            'qiaiaziaiacz', 'qiaiaziaiacd', 'qiaiaziaiaci', 'qiaiaziaiacc', 'qiaiaziaiacb', 'qiaiaziaiacf',
#            'qiaiaiaziacz', 'qiaiaiaziacd', 'qiaiaiaziaci', 'qiaiaiaziacc', 'qiaiaiaziacb', 'qiaiaiaziacf',
#            'qiaiaiaiadwz', 'qiaiaiaiadwd', 'qiaiaiaiadwi', 'qiaiaiaiadwb', 'qiaiaiaiadwf', 'qiaziaiaiadec',
#            'qiaziaiaiadfc', 'qiaziaiaiaiec', 'qiaziaiaiaibc', 'qiaiaziaiadec', 'qiaiaziaiadfc', 'qiaiaziaiaiec',
#            'qiaiaziaiaibc', 'qiaiaiaziadec', 'qiaiaiaziadfc', 'qiaiaiaziaiec', 'qiaiaiaziaibc', 'qiaiaiaiazdec',
#            'qiaiaiaiazdfc', 'qiaiaiaiaziec', 'qiaiaiaiaiabc', 'qiaziaiaiadce', 'qiaziaiaiadcc', 'qiaziaiaiadcf',
#            'qiaziaiaiadcw', 'qiaziaiaiadwz', 'qiaziaiaiadwd', 'qiaziaiaiadwi', 'qiaziaiaiadwc', 'qiaziaiaiadwb',
#            'qiaziaiaiadwf', 'qiaziaiaiaice', 'qiaziaiaiaicc', 'qiaziaiaiaicb', 'qiaziaiaiaica', 'qiaiaziaiadce',
#            'qiaiaziaiadcc', 'qiaiaziaiadcf', 'qiaiaziaiadcw', 'qiaiaziaiadwz', 'qiaiaziaiadwd', 'qiaiaziaiadwi',
#            'qiaiaziaiadwc', 'qiaiaziaiadwb', 'qiaiaziaiadwf', 'qiaiaziaiaice', 'qiaiaziaiaicc', 'qiaiaziaiaicb',
#            'qiaiaziaiaica', 'qiaiaiaziadce', 'qiaiaiaziadcc', 'qiaiaiaziadcf', 'qiaiaiaziadcw', 'qiaiaiaziadwz',
#            'qiaiaiaziadwd', 'qiaiaiaziadwi', 'qiaiaiaziadwc', 'qiaiaiaziadwf', 'qiaiaiaziaice', 'qiaiaiaziaicc',
#            'qiaiaiaziaicb', 'qiaiaiaziaica', 'qiaiaiaiazdce', 'qiaiaiaiazdcc', 'qiaiaiaiazdcf', 'qiaiaiaiazice',
#            'qiaiaiaiazicc', 'qiaiaiaiazica', 'qiaziaiaiaiazz', 'qiaiaziaiaiazz', 'qiaiaiaziaiazz', 'qiaiaiaiaziazz',
#            'qiaiaiaiaiazzz', 'qiaiaiaiaiazcz', 'qiaziaiaiaiazd', 'qiaiaziaiaiazd', 'qiaiaiaziaiazd', 'qiaiaiaiaziazd',
#            'qiaiaiaiaiazzd', 'qiaiaiaiaiazcd', 'qiaziaiaiaiazi', 'qiaiaziaiaiazi', 'qiaiaiaziaiazi', 'qiaiaiaiaziazi',
#            'qiaiaiaiaiazzi', 'qiaiaiaiaiazci', 'qiaziaiaiaiazc', 'qiaiaziaiaiazc', 'qiaiaiaziaiazc', 'qiaiaiaiaziazc',
#            'qiaiaiaiaiazzc', 'qiaiaiaiaiazcc', 'qiaziaiaiaiacz', 'qiaziaiaiaiacd', 'qiaziaiaiaiaci', 'qiaziaiaiaiacc',
#            'qiaziaiaiaiacb', 'qiaziaiaiaiabc', 'qiaiaziaiaiabc', 'qiaiaiaziaiabc', 'qiaiaiaiaziabc', 'qiaiaiaiaiadec',
#            'qiaiaiaiaiaiec', 'qiaiaiaiaiaibc', 'qiaiaziaiaiacz', 'qiaiaziaiaiacd', 'qiaiaziaiaiaci', 'qiaiaziaiaiacc',
#            'qiaiaziaiaiacb', 'qiaiaiaziaiacz', 'qiaiaiaziaiacd', 'qiaiaiaziaiaci', 'qiaiaiaziaiacc', 'qiaiaiaziaiacb',
#            'qiaiaiaiaziacz', 'qiaiaiaiaziacd', 'qiaiaiaiaziaci', 'qiaiaiaiaziacc', 'qiaiaiaiaziacb', 'qiaiaiaiaiadwz',
#            'qiaiaiaiaiadwd', 'qiaiaiaiaiadwi', 'qiaiaiaiaiadwb', 'qiaiaiaiaiadwf', 'qiaiaiaiaiazdec', 'qiaiaiaiaiaziec',
#            'qiaziaiaiaiadce', 'qiaziaiaiaiadcc', 'qiaziaiaiaiadcw', 'qiaziaiaiaiadwz', 'qiaziaiaiaiadwd',
#            'qiaziaiaiaiadwi', 'qiaziaiaiaiadwc', 'qiaziaiaiaiadwb', 'qiaziaiaiaiadwf', 'qiaziaiaiaiaice',
#            'qiaziaiaiaiaicc', 'qiaziaiaiaiaicb', 'qiaiaziaiaiadce', 'qiaiaziaiaiadcc', 'qiaiaziaiaiadcw',
#            'qiaiaziaiaiadwz', 'qiaiaziaiaiadwd', 'qiaiaziaiaiadwi', 'qiaiaziaiaiadwc', 'qiaiaziaiaiadwb',
#            'qiaiaziaiaiadwf', 'qiaiaziaiaiaice', 'qiaiaziaiaiaicc', 'qiaiaziaiaiaicb', 'qiaiaiaziaiadce',
#            'qiaiaiaziaiadcc', 'qiaiaiaziaiadcw', 'qiaiaiaziaiadwz', 'qiaiaiaziaiadwd', 'qiaiaiaziaiadwi',
#            'qiaiaiaziaiadwc', 'qiaiaiaziaiadwb', 'qiaiaiaziaiadwf', 'qiaiaiaziaiaice', 'qiaiaiaziaiaicc',
#            'qiaiaiaziaiaicb', 'qiaiaiaiaziadce', 'qiaiaiaiaziadcc', 'qiaiaiaiaziadcw', 'qiaiaiaiaziadwz',
#            'qiaiaiaiaziadwd', 'qiaiaiaiaziadwi', 'qiaiaiaiaziadwc', 'qiaiaiaiaziadwf', 'qiaiaiaiaziaice',
#            'qiaiaiaiaziaicc', 'qiaiaiaiaziaicb', 'qiaiaiaiaiazdce', 'qiaiaiaiaiazice', 'qiaiaiaiaiazdcc',
#            'qiaiaiaiaiazicc'],
#        7: ['qzz', 'qzd', 'qzi', 'qzf', 'qdec', 'qdfc', 'qiec', 'qfcc', 'qiabc', 'qiafc', 'qiazzz', 'qiazcz', 'qiazzd',
#            'qiazcd', 'qiazzi', 'qiazci', 'qiazzc', 'qiazcc', 'qiazzf', 'qiazcf', 'qiazfc', 'qiadec', 'qiadfc', 'qiaiec',
#            'qiaibc', 'qiadwz', 'qiadwd', 'qiadwi', 'qiadwf', 'qiazdec', 'qiazdfc', 'qiaziec', 'qiaiabc', 'qiaiafc',
#            'qiazdce', 'qiazdcc', 'qiazdcf', 'qiazice', 'qiazicc', 'qiazica', 'qiaziazz', 'qiaiazzz', 'qiaiazcz',
#            'qiaziazd', 'qiaiazzd', 'qiaiazcd', 'qiaziazi', 'qiaiazzi', 'qiaiazci', 'qiaziazc', 'qiaiazzc', 'qiaiazcc',
#            'qiaziazf', 'qiaiazzf', 'qiaiazcf', 'qiaziacz', 'qiaziacd', 'qiaziaci', 'qiaziacc', 'qiaziacb', 'qiaziacf',
#            'qiaziabc', 'qiaziafc', 'qiaiazfc', 'qiaiadec', 'qiaiadfc', 'qiaiaiec', 'qiaiaibc', 'qiaiadwz', 'qiaiadwd',
#            'qiaiadwi', 'qiaiadwb', 'qiaiadwf', 'qiaziadec', 'qiaziadfc', 'qiaziaiec', 'qiaziaibc', 'qiaiazdec',
#            'qiaiazdfc', 'qiaiaziec', 'qiaiaiabc', 'qiaiaiafc', 'qiaziadce', 'qiaziadcc', 'qiaziadcf', 'qiaziadcw',
#            'qiaziadwz', 'qiaziadwd', 'qiaziadwi', 'qiaziadwc', 'qiaziadwf', 'qiaziaice', 'qiaziaicc', 'qiaziaicb',
#            'qiaziaica', 'qiaiazdce', 'qiaiazdcc', 'qiaiazdcf', 'qiaiazice', 'qiaiazicc', 'qiaiazica', 'qiaziaiazz',
#            'qiaiaziazz', 'qiaiaiazzz', 'qiaiaiazcz', 'qiaziaiazd', 'qiaiaziazd', 'qiaiaiazzd', 'qiaiaiazcd',
#            'qiaziaiazi', 'qiaiaziazi', 'qiaiaiazzi', 'qiaiaiazci', 'qiaziaiazc', 'qiaiaziazc', 'qiaiaiazzc',
#            'qiaiaiazcc', 'qiaziaiazf', 'qiaiaziazf', 'qiaiaiazzf', 'qiaiaiazcf', 'qiaziaiacz', 'qiaziaiacd',
#            'qiaziaiaci', 'qiaziaiacc', 'qiaziaiacb', 'qiaziaiacf', 'qiaziaiabc', 'qiaziaiafc', 'qiaiaziabc',
#            'qiaiaziafc', 'qiaiaiazfc', 'qiaiaiadec', 'qiaiaiadfc', 'qiaiaiaiec', 'qiaiaiaibc', 'qiaiaziacz',
#            'qiaiaziacd', 'qiaiaziaci', 'qiaiaziacc', 'qiaiaziacb', 'qiaiaziacf', 'qiaiaiadwz', 'qiaiaiadwd',
#            'qiaiaiadwi', 'qiaiaiadwb', 'qiaiaiadwf', 'qiaziaiadec', 'qiaziaiadfc', 'qiaziaiaiec', 'qiaziaiaibc',
#            'qiaiaziadec', 'qiaiaziadfc', 'qiaiaziaiec', 'qiaiaziaibc', 'qiaiaiazdec', 'qiaiaiazdfc', 'qiaiaiaziec',
#            'qiaiaiaiabc', 'qiaiaiaiafc', 'qiaziaiadce', 'qiaziaiadcc', 'qiaziaiadcf', 'qiaziaiadcw', 'qiaziaiadwz',
#            'qiaziaiadwd', 'qiaziaiadwi', 'qiaziaiadwc', 'qiaziaiadwb', 'qiaziaiadwf', 'qiaziaiaice', 'qiaziaiaicc',
#            'qiaziaiaicb', 'qiaziaiaica', 'qiaiaziadce', 'qiaiaziadcc', 'qiaiaziadcf', 'qiaiaziadcw', 'qiaiaziadwz',
#            'qiaiaziadwd', 'qiaiaziadwi', 'qiaiaziadwc', 'qiaiaziadwf', 'qiaiaziaice', 'qiaiaziaicc', 'qiaiaziaicb',
#            'qiaiaziaica', 'qiaiaiazdce', 'qiaiaiazdcc', 'qiaiaiazdcf', 'qiaiaiazice', 'qiaiaiazicc', 'qiaiaiazica',
#            'qiaziaiaiazz', 'qiaiaziaiazz', 'qiaiaiaziazz', 'qiaiaiaiazzz', 'qiaiaiaiazcz', 'qiaziaiaiazd',
#            'qiaiaziaiazd', 'qiaiaiaziazd', 'qiaiaiaiazzd', 'qiaiaiaiazcd', 'qiaziaiaiazi', 'qiaiaziaiazi',
#            'qiaiaiaziazi', 'qiaiaiaiazzi', 'qiaiaiaiazci', 'qiaziaiaiazc', 'qiaiaziaiazc', 'qiaiaiaziazc',
#            'qiaiaiaiazzc', 'qiaiaiaiazcc', 'qiaziaiaiazf', 'qiaiaziaiazf', 'qiaiaiaziazf', 'qiaiaiaiazzf',
#            'qiaiaiaiazcf', 'qiaziaiaiacz', 'qiaziaiaiacd', 'qiaziaiaiaci', 'qiaziaiaiacc', 'qiaziaiaiacb',
#            'qiaziaiaiacf', 'qiaziaiaiabc', 'qiaziaiaiafc', 'qiaiaziaiabc', 'qiaiaziaiafc', 'qiaiaiaziabc',
#            'qiaiaiaziafc', 'qiaiaiaiazfc', 'qiaiaiaiadec', 'qiaiaiaiadfc', 'qiaiaiaiaiec', 'qiaiaiaiaibc',
#            'qiaiaziaiacz', 'qiaiaziaiacd', 'qiaiaziaiaci', 'qiaiaziaiacc', 'qiaiaziaiacb', 'qiaiaziaiacf',
#            'qiaiaiaziacz', 'qiaiaiaziacd', 'qiaiaiaziaci', 'qiaiaiaziacc', 'qiaiaiaziacb', 'qiaiaiaziacf',
#            'qiaiaiaiadwz', 'qiaiaiaiadwd', 'qiaiaiaiadwi', 'qiaiaiaiadwb', 'qiaiaiaiadwf', 'qiaziaiaiadec',
#            'qiaziaiaiadfc', 'qiaziaiaiaiec', 'qiaziaiaiaibc', 'qiaiaziaiadec', 'qiaiaziaiadfc', 'qiaiaziaiaiec',
#            'qiaiaziaiaibc', 'qiaiaiaziadec', 'qiaiaiaziadfc', 'qiaiaiaziaiec', 'qiaiaiaziaibc', 'qiaiaiaiazdec',
#            'qiaiaiaiazdfc', 'qiaiaiaiaziec', 'qiaiaiaiaiabc', 'qiaiaiaiaiafc', 'qiaziaiaiadce', 'qiaziaiaiadcc',
#            'qiaziaiaiadcf', 'qiaziaiaiadcw', 'qiaziaiaiadwz', 'qiaziaiaiadwd', 'qiaziaiaiadwi', 'qiaziaiaiadwc',
#            'qiaziaiaiadwb', 'qiaziaiaiadwf', 'qiaziaiaiaice', 'qiaziaiaiaicc', 'qiaziaiaiaicb', 'qiaziaiaiaica',
#            'qiaiaziaiadce', 'qiaiaziaiadcc', 'qiaiaziaiadcf', 'qiaiaziaiadcw', 'qiaiaziaiadwz', 'qiaiaziaiadwd',
#            'qiaiaziaiadwi', 'qiaiaziaiadwc', 'qiaiaziaiadwb', 'qiaiaziaiadwf', 'qiaiaziaiaice', 'qiaiaziaiaicc',
#            'qiaiaziaiaicb', 'qiaiaziaiaica', 'qiaiaiaziadce', 'qiaiaiaziadcc', 'qiaiaiaziadcf', 'qiaiaiaziadcw',
#            'qiaiaiaziadwz', 'qiaiaiaziadwd', 'qiaiaiaziadwi', 'qiaiaiaziadwc', 'qiaiaiaziadwf', 'qiaiaiaziaice',
#            'qiaiaiaziaicc', 'qiaiaiaziaicb', 'qiaiaiaziaica', 'qiaiaiaiazdce', 'qiaiaiaiazdcc', 'qiaiaiaiazdcf',
#            'qiaiaiaiazice', 'qiaiaiaiazicc', 'qiaiaiaiazica', 'qiaziaiaiaiazz', 'qiaiaziaiaiazz', 'qiaiaiaziaiazz',
#            'qiaiaiaiaziazz', 'qiaiaiaiaiazzz', 'qiaiaiaiaiazcz', 'qiaziaiaiaiazd', 'qiaiaziaiaiazd', 'qiaiaiaziaiazd',
#            'qiaiaiaiaziazd', 'qiaiaiaiaiazzd', 'qiaiaiaiaiazcd', 'qiaziaiaiaiazi', 'qiaiaziaiaiazi', 'qiaiaiaziaiazi',
#            'qiaiaiaiaziazi', 'qiaiaiaiaiazzi', 'qiaiaiaiaiazci', 'qiaziaiaiaiazc', 'qiaiaziaiaiazc', 'qiaiaiaziaiazc',
#            'qiaiaiaiaziazc', 'qiaiaiaiaiazzc', 'qiaiaiaiaiazcc', 'qiaziaiaiaiazf', 'qiaiaziaiaiazf', 'qiaiaiaziaiazf',
#            'qiaiaiaiaziazf', 'qiaiaiaiaiazzf', 'qiaiaiaiaiazcf', 'qiaziaiaiaiacz', 'qiaziaiaiaiacd', 'qiaziaiaiaiaci',
#            'qiaziaiaiaiacc', 'qiaziaiaiaiacb', 'qiaziaiaiaiacf', 'qiaziaiaiaiabc', 'qiaziaiaiaiafc', 'qiaiaziaiaiabc',
#            'qiaiaziaiaiafc', 'qiaiaiaziaiabc', 'qiaiaiaziaiafc', 'qiaiaiaiaziabc', 'qiaiaiaiaziafc', 'qiaiaiaiaiazfc',
#            'qiaiaiaiaiadec', 'qiaiaiaiaiadfc', 'qiaiaiaiaiaiec', 'qiaiaiaiaiaibc', 'qiaiaziaiaiacz', 'qiaiaziaiaiacd',
#            'qiaiaziaiaiaci', 'qiaiaziaiaiacc', 'qiaiaziaiaiacb', 'qiaiaziaiaiacf', 'qiaiaiaziaiacz', 'qiaiaiaziaiacd',
#            'qiaiaiaziaiaci', 'qiaiaiaziaiacc', 'qiaiaiaziaiacb', 'qiaiaiaziaiacf', 'qiaiaiaiaziacz', 'qiaiaiaiaziacd',
#            'qiaiaiaiaziaci', 'qiaiaiaiaziacc', 'qiaiaiaiaziacb', 'qiaiaiaiaziacf', 'qiaiaiaiaiadwz', 'qiaiaiaiaiadwd',
#            'qiaiaiaiaiadwi', 'qiaiaiaiaiadwb', 'qiaiaiaiaiadwf', 'qiaziaiaiaiadec', 'qiaziaiaiaiadfc',
#            'qiaziaiaiaiaiec', 'qiaziaiaiaiaibc', 'qiaiaziaiaiadec', 'qiaiaziaiaiadfc', 'qiaiaziaiaiaiec',
#            'qiaiaziaiaiaibc', 'qiaiaiaziaiadec', 'qiaiaiaziaiadfc', 'qiaiaiaziaiaiec', 'qiaiaiaziaiaibc',
#            'qiaiaiaiaziadec', 'qiaiaiaiaziadfc', 'qiaiaiaiaziaiec', 'qiaiaiaiaziaibc', 'qiaiaiaiaiazdec',
#            'qiaiaiaiaiazdfc', 'qiaiaiaiaiaziec', 'qiaiaiaiaiaiabc', 'qiaziaiaiaiadce', 'qiaziaiaiaiadcc',
#            'qiaziaiaiaiadcf', 'qiaziaiaiaiadcw', 'qiaziaiaiaiadwz', 'qiaziaiaiaiadwd', 'qiaziaiaiaiadwi',
#            'qiaziaiaiaiadwc', 'qiaziaiaiaiadwb', 'qiaziaiaiaiadwf', 'qiaziaiaiaiaice', 'qiaziaiaiaiaicc',
#            'qiaziaiaiaiaicb', 'qiaziaiaiaiaica', 'qiaiaziaiaiadce', 'qiaiaziaiaiadcc', 'qiaiaziaiaiadcf',
#            'qiaiaziaiaiadcw', 'qiaiaziaiaiadwz', 'qiaiaziaiaiadwd', 'qiaiaziaiaiadwi', 'qiaiaziaiaiadwc',
#            'qiaiaziaiaiadwb', 'qiaiaziaiaiadwf', 'qiaiaziaiaiaice', 'qiaiaziaiaiaicc', 'qiaiaziaiaiaicb',
#            'qiaiaziaiaiaica', 'qiaiaiaziaiadce', 'qiaiaiaziaiadcc', 'qiaiaiaziaiadcf', 'qiaiaiaziaiadcw',
#            'qiaiaiaziaiadwz', 'qiaiaiaziaiadwd', 'qiaiaiaziaiadwi', 'qiaiaiaziaiadwc', 'qiaiaiaziaiadwb',
#            'qiaiaiaziaiadwf', 'qiaiaiaziaiaice', 'qiaiaiaziaiaicc', 'qiaiaiaziaiaicb', 'qiaiaiaziaiaica',
#            'qiaiaiaiaziadce', 'qiaiaiaiaziadcc', 'qiaiaiaiaziadcf', 'qiaiaiaiaziadcw', 'qiaiaiaiaziadwz',
#            'qiaiaiaiaziadwd', 'qiaiaiaiaziadwi', 'qiaiaiaiaziadwc', 'qiaiaiaiaziadwf', 'qiaiaiaiaziaice',
#            'qiaiaiaiaziaicc', 'qiaiaiaiaziaicb', 'qiaiaiaiaziaica', 'qiaiaiaiaiazdce', 'qiaiaiaiaiazdcc',
#            'qiaiaiaiaiazdcf', 'qiaiaiaiaiazice', 'qiaiaiaiaiazicc', 'qiaiaiaiaiazica', 'qiaziaiaiaiaiazz',
#            'qiaiaziaiaiaiazz', 'qiaiaiaziaiaiazz', 'qiaiaiaiaziaiazz', 'qiaiaiaiaiaziazz', 'qiaiaiaiaiaiazzz',
#            'qiaiaiaiaiaiazcz', 'qiaziaiaiaiaiazd', 'qiaiaziaiaiaiazd', 'qiaiaiaziaiaiazd', 'qiaiaiaiaziaiazd',
#            'qiaiaiaiaiaziazd', 'qiaiaiaiaiaiazzd', 'qiaiaiaiaiaiazcd', 'qiaziaiaiaiaiazi', 'qiaiaziaiaiaiazi',
#            'qiaiaiaziaiaiazi', 'qiaiaiaiaziaiazi', 'qiaiaiaiaiaziazi', 'qiaiaiaiaiaiazzi', 'qiaiaiaiaiaiazci',
#            'qiaziaiaiaiaiazc', 'qiaiaziaiaiaiazc', 'qiaiaiaziaiaiazc', 'qiaiaiaiaziaiazc', 'qiaiaiaiaiaziazc',
#            'qiaiaiaiaiaiazzc', 'qiaiaiaiaiaiazcc', 'qiaziaiaiaiaiacz', 'qiaziaiaiaiaiacd', 'qiaziaiaiaiaiaci',
#            'qiaziaiaiaiaiacc', 'qiaziaiaiaiaiacb', 'qiaziaiaiaiaiabc', 'qiaiaziaiaiaiabc', 'qiaiaiaziaiaiabc',
#            'qiaiaiaiaziaiabc', 'qiaiaiaiaiaziabc', 'qiaiaiaiaiaiadec', 'qiaiaiaiaiaiaiec', 'qiaiaiaiaiaiaibc',
#            'qiaiaziaiaiaiacz', 'qiaiaziaiaiaiacd', 'qiaiaziaiaiaiaci', 'qiaiaziaiaiaiacc', 'qiaiaziaiaiaiacb',
#            'qiaiaiaziaiaiacz', 'qiaiaiaziaiaiacd', 'qiaiaiaziaiaiaci', 'qiaiaiaziaiaiacc', 'qiaiaiaziaiaiacb',
#            'qiaiaiaiaziaiacz', 'qiaiaiaiaziaiacd', 'qiaiaiaiaziaiaci', 'qiaiaiaiaziaiacc', 'qiaiaiaiaziaiacb',
#            'qiaiaiaiaiaziacz', 'qiaiaiaiaiaziacd', 'qiaiaiaiaiaziaci', 'qiaiaiaiaiaziacc', 'qiaiaiaiaiaziacb',
#            'qiaiaiaiaiaiadwz', 'qiaiaiaiaiaiadwd', 'qiaiaiaiaiaiadwi', 'qiaiaiaiaiaiadwb', 'qiaiaiaiaiaiadwf',
#            'qiaiaiaiaiaiazdec', 'qiaiaiaiaiaiaziec', 'qiaziaiaiaiaiadce', 'qiaziaiaiaiaiadcc', 'qiaziaiaiaiaiadcw',
#            'qiaziaiaiaiaiadwz', 'qiaziaiaiaiaiadwd', 'qiaziaiaiaiaiadwi', 'qiaziaiaiaiaiadwc', 'qiaziaiaiaiaiadwb',
#            'qiaziaiaiaiaiadwf', 'qiaziaiaiaiaiaice', 'qiaziaiaiaiaiaicc', 'qiaziaiaiaiaiaicb', 'qiaiaziaiaiaiadce',
#            'qiaiaziaiaiaiadcc', 'qiaiaziaiaiaiadcw', 'qiaiaziaiaiaiadwz', 'qiaiaziaiaiaiadwd', 'qiaiaziaiaiaiadwi',
#            'qiaiaziaiaiaiadwc', 'qiaiaziaiaiaiadwb', 'qiaiaziaiaiaiadwf', 'qiaiaziaiaiaiaice', 'qiaiaziaiaiaiaicc',
#            'qiaiaziaiaiaiaicb', 'qiaiaiaziaiaiadce', 'qiaiaiaziaiaiadcc', 'qiaiaiaziaiaiadcw', 'qiaiaiaziaiaiadwz',
#            'qiaiaiaziaiaiadwd', 'qiaiaiaziaiaiadwi', 'qiaiaiaziaiaiadwc', 'qiaiaiaziaiaiadwb', 'qiaiaiaziaiaiadwf',
#            'qiaiaiaziaiaiaice', 'qiaiaiaziaiaiaicc', 'qiaiaiaziaiaiaicb', 'qiaiaiaiaziaiadce', 'qiaiaiaiaziaiadcc',
#            'qiaiaiaiaziaiadcw', 'qiaiaiaiaziaiadwz', 'qiaiaiaiaziaiadwd', 'qiaiaiaiaziaiadwi', 'qiaiaiaiaziaiadwc',
#            'qiaiaiaiaziaiadwb', 'qiaiaiaiaziaiadwf', 'qiaiaiaiaziaiaice', 'qiaiaiaiaziaiaicc', 'qiaiaiaiaziaiaicb',
#            'qiaiaiaiaiaziadce', 'qiaiaiaiaiaziadcc', 'qiaiaiaiaiaziadcw', 'qiaiaiaiaiaziadwz', 'qiaiaiaiaiaziadwd',
#            'qiaiaiaiaiaziadwi', 'qiaiaiaiaiaziadwc', 'qiaiaiaiaiaziadwf', 'qiaiaiaiaiaziaice', 'qiaiaiaiaiaziaicc',
#            'qiaiaiaiaiaziaicb', 'qiaiaiaiaiaiazdce', 'qiaiaiaiaiaiazice', 'qiaiaiaiaiaiazdcc', 'qiaiaiaiaiaiazicc']}
#
# # print("print2: ",is_all_new_nodes_homomorphic(cs2, 2))
# # print("print3: ", is_all_new_nodes_homomorphic(cs2, 3))
# print("print4: ",is_all_new_nodes_homomorphic(cs2, 4))
# print("print5: ",is_all_new_nodes_homomorphic(cs2, 5))
# # print("print6: ",is_all_new_nodes_homomorphic(cs2, 6))
# # print("print7: ",is_all_new_nodes_homomorphic(cs2, 7))
