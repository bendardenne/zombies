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

Inf = float("inf")

class Agent: #(Agent, minimax.Game):
    """This is the skeleton of an agent to play the Zombies game."""

    def __init__(self, name="Super Agent"):
        self.name = name
        self.player = zombies.PLAYER1
        self.positions = {}

    """The successors function must return (or yield) a list of
    pairs (a, s) in which a is the action played to reach the
    state s; s is the new state, i.e. a triplet (b, p, st) where
    b is the new board after the action a has been played,
    p is the player to play the next move and st is the next
    step number.
    """
    def successors(self, state):
        board, player, step = state
        
        if player == self.player : 
            if step <= 2 :
                yield self.random_placement(zombies.HUGGER, state)

            else:
                actions = board.get_actions(player, step)
                random.shuffle(actions)
                for a in actions:
                    newboard = board.clone()
                    newboard.play_action(a, player, step)
                    yield (a, (newboard, -player, step + 1))


        else : 
            actions = board.get_actions(player, step)
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
        b, player, step = state
        
        circleMyNecro = 0 
        circleHisNecro = 0
        hisFreeNecro = 0
        sumDistance = 0
        totalPieces = 0
        emptyAccessible = 0
        huggerOn = 0
        creeperReachable = 0
        jumperReachable = 0
       
        self.update_necromancer(b)
        
        if self.positions[self.player * zombies.NECROMANCER] :
            circleMyNecro = len(b.get_non_empty_neighbours(self.positions[self.player * zombies.NECROMANCER][0]))
        
        if self.positions[-self.player * zombies.NECROMANCER] :
            circleHisNecro = len(b.get_non_empty_neighbours(self.positions[-self.player * zombies.NECROMANCER][0]))
            hisFreeNecro = len(b.get_necromancer_moves(self.positions[-self.player * zombies.NECROMANCER][0]))
            if self.positions[self.player * zombies.CREEPER] :
                for creeper in self.positions[self.player * zombies.CREEPER]:
                    creeper_pos = b.get_creeper_moves(creeper)
                    tiles = b.get_neighbouring_tiles(self.positions[-self.player * zombies.NECROMANCER][0])
                    empty = [x for x in tiles if b.pieces[x] == zombies.EMPTY]
                    creeperReachable = len([x for x in empty if x in creeper_pos])
            
            if self.positions[self.player * zombies.JUMPER] :
                for jumper in self.positions[self.player * zombies.JUMPER]:
                    jumper_pos = b.get_creeper_moves(jumper)
                    tiles = b.get_neighbouring_tiles(self.positions[-self.player * zombies.NECROMANCER][0])
                    empty = [x for x in tiles if b.pieces[x] == zombies.EMPTY]
                    jumperReachable = len([x for x in empty if x in jumper_pos])
         
        if self.positions[-self.player * zombies.NECROMANCER]:
            if type(b.pieces[self.positions[-self.player * zombies.NECROMANCER][0]]) is list and hisFreeNecro > 0 :
                huggerOn = 1
            for kind in self.positions:
                if kind * self.player < 0 or kind == zombies.NECROMANCER:
                    continue
                else:
                    for pos in self.positions[kind]:
                        totalPieces += 1
                        dist = b.hex_distance(pos, self.positions[-self.player * zombies.NECROMANCER][0])
                        sumDistance += dist
                if totalPieces != 0 : sumDistance /= totalPieces
        
        
        if circleHisNecro == 6:
            return Inf

        if circleMyNecro == 6:
            return -Inf
        
        if circleHisNecro == 5:
            tiles = b.get_neighbouring_tiles(self.positions[-self.player * zombies.NECROMANCER][0])
            empty = [x for x in tiles if b.pieces[x] == zombies.EMPTY][0]
            tiles = b.get_neighbouring_tiles(empty)
            emptyAccessible = len([x for x in tiles if x in b.pieces and b.pieces[x] == zombies.EMPTY])
       

        return ( -8*circleMyNecro + 20*circleHisNecro - 2.5*sumDistance - 15 * hisFreeNecro +  10 * emptyAccessible + huggerOn * 18 +  2 * totalPieces  + 12 * creeperReachable ) #+ 12 * jumperReachable)
        

    def play(self, board, player, step, time_left):
        self.player = player
        self.time_left = time_left
        
        state = (board, player, step)
        return minimax.search(state, self)

    def is_necromancer_in_danger(self, board):
        self.update_necromancer(board)
        myNecro = len(board.get_non_empty_neighbours(self.positions[self.player * zombies.NECROMANCER][0]))
        hisNecro = len(board.get_non_empty_neighbours(self.positions[-self.player * zombies.NECROMANCER][0]))

        if myNecro > 4 and hisNecro < 5:
            return True

        return False
        

    def update_necromancer(self, board):
        self.positions = {}
        
        for pos in board.pieces:
            for kind in range(1,5):
                self.positions.setdefault(kind, [])
                self.positions.setdefault(-kind, [])
                if self.check_tile(board, pos, self.player * kind):
                    self.positions[kind * self.player].append(pos)
                elif self.check_tile(board, pos, -self.player * kind):
                    self.positions[kind * -self.player].append(pos)
        

    def check_tile(self, board, pos, piece):
        return (type(board.pieces[pos]) is int and board.pieces[pos] == piece) or \
                (type(board.pieces[pos]) is list and piece in board.pieces[pos])


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
