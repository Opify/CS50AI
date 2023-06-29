import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # takes in the count of a cell and the set 
        # of surrounding cells
        # returns none if it cannot conclude the mines in the set
        # of cells are all mines
        if len(self.cells) == self.count:
            return self.cells
        else:
            return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # takes in the count of a cell and the set 
        # of surrounding cells
        # returns none if it cannot conclude the mines in the set
        # of cells are all safe
        if self.count == 0:
            return self.cells
        else:
            return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # returns updated sentence
        self.cells.remove(cell)
        self.count -= 1
        return self


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # returns updated sentence
        self.cells.remove(cell)
        return self


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # mark cell as move made
        self.moves_made.add(cell)
        # mark cell as safe
        self.safes.add(cell)
        # add surrounding cells to knowledge base with selected
        # cell's count
        involved_cells = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # add to involved_cells if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    involved_cells.add((i, j))
        info = Sentence(cells=involved_cells, count=count)
        self.knowledge.append(info)
        # check if any sentence can allow cells to be marked as
        # safe or as mines
        for knowledge in self.knowledge:
            mines = knowledge.known_mines()
            if mines != None:
                self.mines.update(mines)
            safes = knowledge.known_safes()
            if safes != None:
                self.safes.update(safes)
        for i in range(len(self.knowledge)):
            for j in range(i, len(self.knowledge)):
                new_set = self.knowledge[i].cells - self.knowledge[j].cells
                # if len(new_set) != self.knowledge[i], it means
                # a new subset was found and so we add it to the knowledge
                # and remove the two sentences
                if len(new_set) < len(self.knowledge[i].cells):
                    new_count = self.knowledge[i].count - self.knowledge[j].count
                    new_sentence = Sentence(cells=new_set, count=new_count)
                    self.knowledge.append(new_sentence)
                    self.knowledge.remove(self.knowledge[i])
                    self.knowledge.remove(self.knowledge[j])
                # try self.knowledge[j].cells - self.knowledge[i].cells
                else:
                    new_set = self.knowledge[j].cells - self.knowledge[i].cells
                    if len(new_set) < len(self.knowledge[j].cells):
                        new_count = self.knowledge[j].count - self.knowledge[i].count
                    new_sentence = Sentence(cells=new_set, count=new_count)
                    self.knowledge.append(new_sentence)
                    self.knowledge.remove(self.knowledge[i])
                    self.knowledge.remove(self.knowledge[j])
                

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes:
            if move not in self.moves_made:
                return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        attempts = 0
        while attempts < 20:
            i = random.randrange(self.height)
            j = random.randrange(self.width)
            attempts += 1
            if (i, j) not in self.mines:
                if (i, j) not in self.moves_made:
                    return (i, j)
        return None
