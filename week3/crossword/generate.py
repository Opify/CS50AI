import sys
import copy
import math

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        domains_copy = copy.deepcopy(self.domains)
        for domain in domains_copy.items():
            # words are stored in index 1
            for word in domain[1]:
                # properties of a variable are stored
                # in index 0
                if len(word) != domain[0].length:
                    self.domains[domain[0]].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        # get all overlaps
        overlaps = self.crossword.overlaps
        if (x, y) in overlaps:
            # if there is an overlap between x and y
            if overlaps[(x, y)] is not None:
                # get tuple for overlap
                overlap = overlaps[(x, y)]
                # iterate through each word in
                # self.domains[x]
                # if a word in self.domains[x] cannot
                # satisfy any word in self.domains[y],
                # remove it and flag it was changed
                x_copy = copy.deepcopy(self.domains[x])
                y_copy = copy.deepcopy(self.domains[y])
                for word in x_copy:
                    match = False
                    for other_word in y_copy:
                        if word[overlap[0]] == other_word[overlap[1]]:
                            match = True
                            break
                    if not match:
                        self.domains[x].remove(word)
                        revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        arc_list = []
        if arcs is None:
            for overlap in self.crossword.overlaps:
                arc_list.append(overlap)
        while len(arc_list) != 0:
            arc = arc_list.pop(0)
            if self.revise(arc[0], arc[1]):
                if not len(self.domains[arc[0]]):
                    return False
                neighbours = self.crossword.neighbors(arc[0])
                for neighbour in neighbours:
                    if neighbour != arc[1]:
                        arc_list.append((neighbour, arc[0]))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == len(self.crossword.variables):
            return True
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # first, check if each assignment is unique
        check_unique = []
        for key in assignment:
            check_unique.append(assignment[key])
        if len(set(check_unique)) != len(check_unique):
            return False
        # then, check if each assignment fits its own
        # variable's length
        for var in assignment:
            if len(assignment[var]) != var.length:
                return False
        # finally, check if for each assignment there
        # is no conflict in overlapping cells
        for assign in assignment:
            # self.crossword.overlaps checks EVERY
            # possible combination of 2 nodes
            for overlap in self.crossword.variables:
                if assign != overlap:
                    # if there is an overlap
                    if self.crossword.overlaps[(assign, overlap)] is not None:
                        overlap_indices = self.crossword.overlaps[(assign, overlap)]
                        if overlap in assignment:
                            # if there is a conflict
                            if assignment[assign][overlap_indices[0]] != assignment[overlap][overlap_indices[1]]:
                                return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # list to hold set (number of conflicts, word)
        unsorted_result = []
        neigbours = self.crossword.neighbors(var)
        for word in self.domains[var]:
            # track number of conflicts for each word
            conflict = 0
            for neighbour in neigbours:
                if word in self.domains[neighbour]:
                    conflict += 1
            # store number of conflicts in index 0 and word in index 1
            unsorted_result.append((conflict, word))
        # sort by least number of conflicts first
        unsorted_result.sort(key=lambda set: set[0], reverse=True)
        # list to return result, keeping the list position of the words
        result = []
        for combo in unsorted_result:
            result.append(combo[1])
        return result

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        possibilities = []
        for var in self.domains:
            if var not in assignment:
                # get domain size of variable
                domain_size = len(self.domains[var])
                # get number of neighbours for variable
                neighbours = self.crossword.neighbors(var)
                # index 0 stores domain size, index 1 stores number of 
                # neighbours, index 2 stores variable
                possibilities.append((domain_size, neighbours, var))
        # sort by smallest domain size first
        possibilities.sort(key=lambda combo: combo[0])
        # then by largest network
        possibilities.sort(key=lambda combo: combo[1], reverse=True)
        return possibilities[0][2]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for word in self.order_domain_values(var, assignment):
            assignment.update({var: word})
            if self.consistent(assignment):
                # Todo: add inference throguh ac-3
                result = self.backtrack(assignment)
                if result != None:
                    return result
            assignment.pop(var)
        return None
            


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
