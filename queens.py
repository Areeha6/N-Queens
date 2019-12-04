##
## LAB 3 -- CS 4222/5222 -- Fall 2019
##
##
## 1. You need to decide how you will implement an action
##
## 2. You need to complete the implementation of the board class
##
## 3. You need to finish the code for Simulated Annealing
##
## 4. When you get it running, try out different parameters for the
## algorithms

import time
import random
import numpy as np
import math
from itertools import chain


class Board(object):
    """An N-queens candidate solution ."""

    def __init__(self,N):
        """A random N-queens instance"""
        self.queens = dict()
        for col in range(N): 
            row = random.choice(range(N)) #decides position of queens in rows, looping over columns for e.g: 0th col,1st row has queen
            self.queens[col] = row 

    def copy(self,board):
        """Copy a board (prevent aliasing)"""
        self.queens = board.queens.copy()
        
    def actions(self):
        """Return a list of POSSIBLE actions given the current placements."""
        # YOU FILL THIS IN
        #a= np.any(diff(np.sort(self, axis=0), axis=0) == 0) #if any of the column-wise differences in the column-wise sorted array are zero, return True. A zero difference in the sorted array means that there are identical elements. axis=0 makes sort and diff operate on each column individually.
        #if a==1:
        #swap the columns with some random no.s
        #list=[]
        
        list_of_plays = []
        for i in range(len(self.queens)):
            play = Board(len(self.queens))
            play.queens = self.queens.copy()
            play.queens[i]=random.choice(range(len(self.queens)))
            list_of_plays.append(play)
            #print(self)
        return list_of_plays

    def neighbor(self, action):
        """Return a Board instance like this one but with the corresponding
action made."""
        play = Board(len(self.queens))
        play.queens=action.queens.copy()
        return play
    
    def crossover(self, board):
        """Return a Board instance that is a recombination with its argument."""
        # YOU FILL THIS IN
        x=random.choice(range(len(self.queens)))
        #self.queens[x:]+board.queens[:x]
        

        for i in range(len(self.queens)):
            if i > x:
                board.queens[i]=self.queens[i]
        return board
    
    def cost(self):
        """Compute the cost of this solution."""
        # YOU FILL THIS IN
        #cost of a solution is the no. of conflicts queens have
        #cst=0
        #a= np.any(diff(np.sort(self, axis=0), axis=0) == 0) #if any of the column-wise differences in the column-wise sorted array are zero, return True. A zero difference in the sorted array means that there are identical elements. axis=0 makes sort and diff operate on each column individually.
        #if a==1:
        # finding duplicate values from dictionary using set 
        dup_dict = {} 
        for key, value in self.queens.items(): 
            dup_dict.setdefault(value, set()).add(key)
        result = set(chain.from_iterable(values for key, values in dup_dict.items()if len(values) > 1)) 
  
        conflict_in_columns = len(result)

        conflict_in_diagonals = 0
        N = len(self.queens)

        for col1, row1 in self.queens.items():

            # diagonal 1
            # loop 1

            column = int(col1)
            row = int(row1)

            while column < (N-1) and row < (N-1):
                column +=1
                row +=1
                if column in self.queens and self.queens[column]==row:
                    conflict_in_diagonals += 1

            # loop 2

            column = int(col1)
            row = int(row1)

            while column > 0 and row > 0:
                column -=1
                row -=1
                if column in self.queens and self.queens[column]==row:
                    conflict_in_diagonals += 1


            
            # diagonal 2
            # loop 3

            column = int(col1)
            row = int(row1)

            while column < (N-1) and row > 0:
                column +=1
                row -=1
                if column in self.queens and self.queens[column]==row:
                    conflict_in_diagonals += 1

                    
            # loop 4

            column = int(col1)
            row = int(row1)

            while column > 0 and row < (N-1):
                column -=1
                row += 1
                if column in self.queens and self.queens[column]==row:
                    conflict_in_diagonals += 1

        all_conflicts = conflict_in_columns + conflict_in_diagonals
        # printing result 
        #print("resultant key", str(result))
        #print len(result)
        return all_conflicts

    def display(self,environment):
        """Display the board."""
        print(self.queens)
        if environment.alive:
            environment.canvas.delete('piece')
            for r in range(len(self.queens)):
                for c in range(len(self.queens)):
                    if self.queens[c] == r:
                        environment.canvas.create_image(r*(500/len(self.queens)) + 250/len(self.queens),c*(500/len(self.queens))+250/len(self.queens),image=environment.canvas.img,tag='piece')
            environment.canvas.update_idletasks()
            environment.canvas.update()

class SimulatedAnnealing(object):

    def __init__(self,environment):
        self.environment = environment

    def anneal(self):

        starttemp = int(self.environment.control.params.starttemp.get())
        decayRate = float(self.environment.control.params.decayRate.get())
        maxsteps = int(self.environment.control.params.maxsteps.get())

        ## Initial random board
        x = Board(8);
        t = starttemp
        steps = 0
        self.environment.solved = False
        ## While problem is not solved  
        while x.cost() > 0 and steps < maxsteps and self.environment.alive:

            neighbour = x.neighbor(random.choice(x.actions()))

            if neighbour.cost() < x.cost():
                x = neighbour
            else:
                cost_increase = neighbour.cost() - x.cost()
                p = math.exp(-cost_increase/t)
                if random.random() < p:
                    x = neighbour
                t = t * decayRate
                if(t==0):
                    t=0.001

           ## Display best every 100 generations     
            if (steps % 100 == 0):
                x.display(self.environment)
                self.environment.message('step {}\ntemperature: {}\ncost: {}'.format(steps,t,x.cost()))
                time.sleep(0.1)
            steps = steps+1
            
        
        x.display(self.environment)
        self.environment.message('step {}\ntemperature: {}\ncost: {}'.format(steps,t,x.cost()))
        if x.cost == 0: self.environment.solved = True
        return steps


class EvolutionaryAlgorithm(object):
    """Evolve solutions to the n-queens problem"""

    def __init__(self,environment):
        self.environment = environment

    def evolve(self):
        popsize = int(self.environment.control.params.popsize.get())
        pc = float(self.environment.control.params.pc.get())
        maxsteps = int(self.environment.control.params.maxsteps.get())
        
        ## Initial population
        population = []
        for i in range(popsize):
            population.append(Board(8));

        steps = 0
        self.environment.solved = False
        ## While problem is not solved    
        #print(population)
        #print(population[0].cost())
        while population[0].cost() > 0 and steps < maxsteps and self.environment.alive:

            ## Uniform random parent selection
            x = population[random.choice(range(popsize))]

            ## Crossover with probability pc
            if random.random() < pc:
                y = population[random.choice(range(popsize))]
                x = x.crossover(y)

            ## Mutation (take a short random walk)
            for i in range(np.random.poisson()+1):                
                mlist = x.actions()
                x = x.neighbor(random.choice(mlist))            

            ## Truncation selection
            population.append(x)
          
            ## sort population by fitness, remove least fit
            population = [x for _, x in sorted(zip(map(Board.cost,population),population))]
            population.pop()

            ## Display best every 100 generations
            if (steps % 100 == 0):
                population[0].display(self.environment)
                self.environment.message('step {}\nbest cost: {}'.format(steps,population[0].cost()))
                time.sleep(0.1)
                
            steps = steps+1
        population[0].display(self.environment)
        self.environment.message('step {}\nbest cost: {}'.format(steps,population[0].cost()))
        if population[0].cost == 0: self.environment.solved == True
        return steps