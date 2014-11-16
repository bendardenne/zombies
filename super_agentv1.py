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

class Agent: #(Agent, minimax.Game):
    """This is the skeleton of an agent to play the Zombies game."""

    def __init__(self, name="Super Agent"):
        self.name = name
        self.player = zombies.PLAYER1

    """The successors function must return (or yield) a list of
    pairs (a, s) in which a is the action played to reach the
    state s; s is the new state, i.e. a triplet (b, p, st) where
    b is the new board after the action a has been played,
    p is the player to play the next move and st is the next
    step number.
    """
    def successors(self, state):
        b, p, st = state
        
        actions = b.get_actions(p, st)
        
        random.shuffle(actions)
        for a in actions:
            newboard = b.clone()
            newboard.play_action(a, p, st)
            yield (a, (newboard, -p, st + 1))


        #if type(self.pieces[former_pos]) is int:

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
        
        CircleMyNecro = 0
        CircleHisNecro = 0
        FreeRynners = 0;
        
        if state[0].unplaced_pieces[zombies.NECROMANCER * self.player] == 0 and \
            state[0].unplaced_pieces[zombies.NECROMANCER * -self.player] == 0:
            for piece in state[0].pieces:
                if (type(state[0].pieces[piece]) is int and state[0].pieces[piece] * self.player == zombies.NECROMANCER) or \
                    (type(state[0].pieces[piece]) is list and zombies.NECROMANCER * self.player in state[0].pieces[piece]):             #MyNecro
                    CircleMyNecro += len(state[0].get_non_empty_neighbours(piece))
                elif (type(state[0].pieces[piece]) is int and state[0].pieces[piece] * -self.player == zombies.NECROMANCER) or \
                    (type(state[0].pieces[piece]) is list and zombies.NECROMANCER * -self.player in state[0].pieces[piece]):             #HisNecro
                    CircleHisNecro += len(state[0].get_non_empty_neighbours(piece))
                elif (type(state[0].pieces[piece]) is int and state[0].pieces[piece] * -self.player == zombies.SPRINTER):             #MyRynners
                    if(len(state[0].get_non_empty_neighbours(piece)) >= 2):
                        FreeRynners +=1
    
        
        
        #else:
        #return -10
        
        

        if CircleHisNecro == 6:
            print("C'est FINIIIIIIII COUILLON 88888888888888888")
            return 20000

        print("Score = " + str( -CircleMyNecro + CircleHisNecro ))
        return -CircleMyNecro + CircleHisNecro #+ FreeRynners;

    def play(self, board, player, step, time_left):
        """This function is used to play a move according
        to the board, player and time left provided as input.
        It must return an action representing the move the player
        will perform.
        """
        self.player = player
        self.time_left = time_left
        state = (board, player, step)
        return minimax.search(state, self)


if __name__ == "__main__":
    zombies.agent_main(Basic_Agent())
