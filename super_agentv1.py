#!/usr/bin/env python3
"""
Zombies agent.
Author: Nicolas Van Wallendael <nicolas.vanwallendael@student.uclouvain.be>
        Benoit Dardenne <benoit.ardenne@student.uclouvain.be>
Copyright (C) 2014, Université catholique de Louvain

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.

"""

import zombies
import minimax
import random
import math 

ATTACK = 0
DEFENSE = 1

class Agent: #(Agent, minimax.Game):
    """This is the skeleton of an agent to play the Zombies game."""

    def __init__(self, name="Super Agent"):
        self.name = name
        self.player = zombies.PLAYER1
        self.strategy = ATTACK
        self.necromancers = {}

    """The successors function must return (or yield) a list of
    pairs (a, s) in which a is the action played to reach the
    state s; s is the new state, i.e. a triplet (b, p, st) where
    b is the new board after the action a has been played,
    p is the player to play the next move and st is the next
    step number.
    """
    def successors(self, state):
        board, player, step = state
        
        if step <= 2 :
            yield self.random_placement(zombies.HUGGER, state)
                         
        elif step <= 4:
            yield self.random_placement(zombies.CREEPER, state)

        elif step <= 6:
            yield self.random_placement(zombies.JUMPER, state)


        actions = board.get_actions(player, step)
        
        random.shuffle(actions)
        for a in actions:
            newboard = board.clone()
            newboard.play_action(a, player, step)
            yield (a, (newboard, -player, step + 1))

    """The cutoff function returns true if the alpha-beta/minimax
    search has to stop; false otherwise.
    """
    def cutoff(self, state, depth):
        if depth >= 2 or state[0].is_finished():
            return True

        return False

    """The evaluate function must return an integer value
    representing the utility function of the board.
    """
    def evaluate(self, state):

        b, p, step = state
        
        """ 
        if CircleHisNecro == 6:
            return 20000 - step
        """
        return b.get_score() #  -CircleMyNecro + CircleHisNecro #+ myNecroFree - hisNecroFree
        

    def play(self, board, player, step, time_left):
        self.player = player
        self.time_left = time_left

        if step > 8 and self.is_necromancer_in_danger(board): 
            self.strategy = DEFENSE

        state = (board, player, step)
        return minimax.search(state, self)

    def is_necromancer_in_danger(self, board):
        self.update_necromancer(board)
        myNecro = len(board.get_non_empty_neighbours(self.necromancers[self.player]))
        hisNecro = len(board.get_non_empty_neighbours(self.necromancers[-self.player]))

        if myNecro >= 4 and hisNecro < 5:
            return True

        return False
        

    def update_necromancer(self, board):

        for piece in board.pieces:
            if (type(board.pieces[piece]) is int and board.pieces[piece] * self.player == zombies.NECROMANCER) or \
                (type(board.pieces[piece]) is list and zombies.NECROMANCER * self.player in board.pieces[piece]):
                self.necromancers[self.player] = piece
            elif (type(board.pieces[piece]) is int and board.pieces[piece] * -self.player == zombies.NECROMANCER) or \
                (type(board.pieces[piece]) is list and zombies.NECROMANCER * -self.player in board.pieces[piece]):
                self.necromancers[-self.player] = piece
        

    def random_placement(self, piece, state) :
        board, player, step = state
        pos = board.get_possible_placements(self.player, step) 
        newboard = board.clone()
        action = ('P', (piece * self.player, board.unplaced_pieces[piece * self.player]), \
            random.choice(pos))
        newboard.play_action(action, self.player, step)
        return (action, (newboard, -player, step + 1))

if __name__ == "__main__":
    zombies.agent_main(Basic_Agent())
