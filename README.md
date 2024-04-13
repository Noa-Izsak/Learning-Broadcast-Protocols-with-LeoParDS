# Learning-Broadcast-Protocols-with-LeoParDS

This repository contains the artifacts for the paper ``Learning Broadcast Protocols with LeoParDS''.
It contains all the necesery code and inforamtion for using the code as showen in the paper and for new reserach and experements to be done.

More details on the algorithm and Broadcast Protocols (BPs) can be found in the paper, the rest of this file will explain the input and output file format as well as how to use our program.

## BPGen - BP_generator:
  ```python
class BP_generator:
    def __init__(self, min_number_of_states, min_number_of_act, max_number_of_states=None, max_number_of_act=None):
      ...
      self.number_of_act = na #as defined in the function
      self.number_of_states = ns #as defined in the function
      self.bp: BP_class = self.generate()
      
    def generate(self) -> BP_class:
      ...
      # returnes a BP object that has @number_of_states states and each state
      # has a unique action so it wouldn't be hidden and another @number_of_act
      # randomly distributed actions
```
  Creating a random BP with number of states between 2 and 3 and number of actions between 1 and 2
  
  ```python
  bp = BP_generator(2, 1, 3, 2)
  ```

So a possible randomly generated BP is:
```python
THE BP:
 initial state: 0
 actions: {0: {'a': 0, 'c': 1}, 1: {'b': 0}}
 receivers: {0: {'a': (0, False), 'b': (1, False), 'c': (1, False)}, 1: {'a': (1, False), 'b': (1, False), 'c': (0, False)}}
  ```
This is the result of ```print(bp.bp)```

An illustration of this BP is as follows:

![image](https://github.com/Noa-Izsak/Learning-Broadcast-Protocols-with-LeoParDS/assets/62952579/73fc305e-f98f-48fb-a27e-2959d976b1da)

## CSGen 
### CSGen - run_cs_to_a_limit

Under ```BP_Learn.py```, you can find the following function:
  ```python
def run_cs_to_a_limit(self, cutoff_limit, sample_limit):
```
The BP that we create this CS for is $self.bp$, cutoff_limit is ${\overline{\mbox{M}}_{p}}$ from the paper, represnting a bound on the number of processes.
This is, in order to ensure termination also in case the given BP does not have a cutoff.
We also have as input a $sample_limit$, in case you run on a computer with low memory resources, you can bound the size of the sample so if it is too high it will stop.
This function is more direct as there are less inputs to tune, if you do want to make it more personal for diffrent uses see the fucntion below.

### CSGen - run_subsume_cs
Under ```BP_Learn.py```, you can find the following function:
  ```python
def run_subsume_cs(self, words_to_add, are_words_given, cutoff_lim=None, time_lim=None):
      """
        a run that add amount of words_to_add to the cs and run it
        :param time_lim: If given, this is time limitation in sec
        :param cutoff_lim: If given, then cutoff limitation for running
        :param are_words_given: A boolean value representing whether we create a sample (not necessarily a CS)
                                for words_to_add amount or is the words are already given to us
        :param words_to_add: Number of words if are_words_given==False or the set of words if are_words_given==True
      """
      ...
```
As in the previous run function, the BP that we create this CS for is $self.bp$, cutoff_lim is ${\overline{\mbox{M}}_{p}}$ from the paper, represnting a bound on the number of processes. This run function create a CS for the BP by the algorithm that we created and then potantialy padding it with additional words ($words_to_add$), either create it by itself or randomly generate new words (depends on $are_words_given$).


## C



## About Broadcast Protocols (in short BPs):

**Broadcast protocols** (in short BPs) are a powerful concurrent computational model, allowing the synchronous communication of the sender of an action with an arbitrary number of receivers. 

The basic model assumes that communication and processes are reliable, i.e., it does not consider communication failures or faulty processes.
BPs have mainly been studied in the context of parameterized verification, i.e., 
proving functional correctness according to a formal specification, for all systems where an arbitrary number of processes execute a given protocol.


The challenge in reasoning about parameterized systems such as BPs is that a parameterized system concisely represents an **infinite family** of systems: for each natural number $n$ it includes the system where $n$ indistinguishable
processes interact. 
The system is correct only if it satisfies the specification for any number $n$ of processes interacting.

### Formal definition - BP

A **broadcast protocol** $B=(S,s_0,L,R)$ consists of a finite set of states $S$ with an initial state $s_0 \in S$, a set of labels $L$
and a transition relation $R\subseteq S \times L \times S$, where $L = \{a!!, a?? \mid a \in A\}$ for some set of actions $A$. A transition labeled with $a!!$ is a broadcast **sending  transition**, and a transition labeled with $a??$ is a broadcast **receiving transition**, also called a **response**.

