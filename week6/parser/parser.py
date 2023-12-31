import nltk
import sys
import re

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP
S -> NP Adv VP
S -> NP VP AdvP
S -> NP Adv VP AdvP
S -> NP Conj NP VP
S -> NP Conj NP Adv VP
S -> NP Conj NP VP AdvP
S -> Np Conj NP Adv VP AdvP
NP -> N | Det N | AdjP N | Det AdjP N
VP -> V | V NP | V NP PP | V PP | Adv V | Adv V NP | Adv V NP PP | Adv V PP
PP -> P NP
AdjP -> Adj | Adj AdjP
AdvP -> Adv | Adv AdvP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    result = nltk.tokenize.word_tokenize(sentence.lower())
    pattern = re.compile("[A-za-z]+")
    for word in result:
        if not pattern.search(word):
            result.remove(word)
    return result
    


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    # explore branches of the tree
    def branch_explore(branch):
        # if the branch is a string, it's a terminal word
        # and so nothing is returned
        if isinstance(branch, str):
            return
        elif branch.label() == 'NP':
            # once a NP branch is found, there is no need to
            # further recurse
            result.append(branch)
            return
        else:
            for child in branch:
                branch_explore(child)
    result = []
    # Since NP cannot be in a NP, we can simply recurse until
    # we reach NP
    for branch in tree:
        branch_explore(branch)
    return result


if __name__ == "__main__":
    main()
