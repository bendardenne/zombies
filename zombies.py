"""
Common definitions for the Zombie players.
Author: Cyrille Dejemeppe <cyrille.dejemeppe@uclouvain.be>
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

import random
import itertools
import operator

PLAYER1 = 1
PLAYER2 = -1
# The empty available (reachable) tile
EMPTY = 0
# The necromancer tile
NECROMANCER = 1
# The zombie huger tile
HUGGER = 2
# The zombie jumper tile
JUMPER = 3
# The zombie creeper tile
CREEPER = 4
# The zombie sprinter tile
SPRINTER = 5

PIECE_NAMES = ["EMPTY", "NECROMANCER", "HUGGER", "JUMPER", "CREEPER", "SPRINTER"]


class InvalidAction(Exception):

  """Raised when an invalid action is played."""

  def __init__(self, action=None, player=PLAYER1):
    self.action = action
    self.player = player
    playerStr = "1" if self.player == PLAYER1 else "2"
    print("Player " + playerStr + " has performed an invalid action: " + str(action))


class NonExistingTile(Exception):

  """Raised when an invalid action is played."""

  def __init__(self, pos=None):
    self.pos = pos

class NoPath(Exception):
    """Raised when a player puts a wall such that no path exists
    between a player and its goal row"""
    def __repr__(self):
        return "Exception: no path respecting move liberty\
        between these two positions"


class Board:
  """
  Representation of a Zombie Board.

  """

  def __init__(self, percepts=None):
    """
    Constructor of the representation for a Zombies game.
    The representation can be initialized by a percepts
    If percepts==None:
        The board is empty and each player has the starting
        11 zombie pieces.
    """
    self.pieces = {}
    self.unplaced_pieces = {}
    if percepts is not None:
      for piece in percepts.unplaced_pieces:
        self.unplaced_pieces[piece] = percepts.unplaced_pieces[piece]
      for (q_coord, r_coord) in percepts.pieces:
        if type(percepts.pieces[q_coord, r_coord]) is list:
          tmp_lst = []
          for piece in percepts.pieces[q_coord, r_coord]:
            tmp_lst.append(piece)
          self.pieces[(q_coord, r_coord)] = tmp_lst
        else:
          self.pieces[(q_coord, r_coord)] = percepts.pieces[(q_coord, r_coord)]
    else:
      self.unplaced_pieces[NECROMANCER] = 1
      self.unplaced_pieces[HUGGER] = 2
      self.unplaced_pieces[JUMPER] = 3
      self.unplaced_pieces[CREEPER] = 2
      self.unplaced_pieces[SPRINTER] = 3
      self.unplaced_pieces[-NECROMANCER] = 1
      self.unplaced_pieces[-HUGGER] = 2
      self.unplaced_pieces[-JUMPER] = 3
      self.unplaced_pieces[-CREEPER] = 2
      self.unplaced_pieces[-SPRINTER] = 3
      self.pieces[(0, 0)] = EMPTY

  def pretty_print(self):
    """Print of the representation"""
    pretty_str = "Pieces on the board:"
    for (q_coord, r_coord) in self.pieces:
      pretty_str += "(" + str(q_coord) + ", " + str(r_coord) + "): "
      pretty_str += self.tile_str(q_coord, r_coord) + "\n"
    print(pretty_str)

  def __str__(self):
    """String representation of the board"""
    board_str = "UNPLACED P1: "
    for piece in self.unplaced_pieces:
      if piece > 0:
        board_str += "(" + str(PIECE_NAMES[piece]) + ": " + str(self.unplaced_pieces[piece]) + "); "
    board_str += "\nUNPLACED P2: "
    for piece in self.unplaced_pieces:
      if piece < 0:
        board_str += "(" + str(PIECE_NAMES[-piece]) + ": " + str(self.unplaced_pieces[piece]) + "); "
    board_str += "\nPLACED PIECES"
    for (q_coord, r_coord) in self.pieces:
      board_str += "(" + str(q_coord) + ", " + str(r_coord) + "): " + self.tile_str(q_coord, r_coord) + "\n"
    return board_str

  def tile_str(self, q, r):
    """String representation of a tile on the board"""
    tile_repr = ""
    if type(self.pieces[(q, r)]) is int:
      tile_repr += PIECE_NAMES[abs(self.pieces[(q, r)])]
      if self.pieces[q, r] < 0:
        tile_repr += " (P2)"
      elif self.pieces[q, r] > 0:
        tile_repr += " (P1)"
    else:
      tile_repr += "["
      for i in range(len(self.pieces[(q, r)]) - 1):
        tile_repr += PIECE_NAMES[abs(self.pieces[(q, r)][i])]
        if self.pieces[q, r][i] < 0:
          tile_repr += " (P2), "
        else:
          tile_repr += " (P1), "
      tile_repr += PIECE_NAMES[abs(self.pieces[(q, r)][-1])]
      if self.pieces[q, r][-1] < 0:
        tile_repr += " (P2)]"
      else:
        tile_repr += " (P1)]"
    return tile_repr

  def clone(self):
    """Return a clone of this object."""
    clone_board = Board()
    for piece in self.unplaced_pieces:
      clone_board.unplaced_pieces[piece] = self.unplaced_pieces[piece]
    for (q_coord, r_coord) in self.pieces:
      if type(self.pieces[q_coord, r_coord]) is list:
        tmp_lst = []
        for piece in self.pieces[q_coord, r_coord]:
          tmp_lst.append(piece)
        clone_board.pieces[(q_coord, r_coord)] = tmp_lst
      else:
        clone_board.pieces[(q_coord, r_coord)] = self.pieces[(q_coord, r_coord)]
    return clone_board

  def is_move_valid(self, former_pos, new_pos, player):
    """Returns true if the player can move piece from
    former_pos to new_pos"""
    former_q, former_r = former_pos
    new_q, new_r = new_pos

    #Checks whether the necromancer is already placed
    if self.unplaced_pieces[player * NECROMANCER] != 0:
      return False

    #Checks whether the coordinates are known
    if not (former_pos in self.pieces and new_pos in self.pieces):
      return False

    #If the move makes the pieces not connected, or if the piece
    #moving is isolated, it is not valid
    if not self.pieces_are_connected_without(former_pos) or \
      (type(self.pieces[former_pos]) is int and self.is_position_isolated(new_pos, former_pos)):
      return False

    #Get the upper piece in case there is a stack of pieces at position 
    former_piece = self.pieces[former_pos] if not type(self.pieces[former_pos]) is list else self.pieces[former_pos][-1]
    new_piece = self.pieces[new_pos] if not type(self.pieces[new_pos]) is list else self.pieces[new_pos][-1]
    
    if former_piece * player <= 0:
      return False
    if former_piece * player == NECROMANCER:
      return (new_q != former_q or new_r != former_r) and abs(new_q - former_q) <= 1 and \
        abs(new_r - former_r) <= 1 and self.pieces[new_pos] == EMPTY and \
        self.respects_move_liberty(former_pos, new_pos)
    if former_piece * player == HUGGER:
      return former_pos != new_pos and abs(new_q - former_q) <= 1 and \
        abs(new_r - former_r) <= 1
    if former_piece * player == JUMPER:
      return self.jumps_in_line(former_pos, new_pos)
    if former_piece * player == CREEPER:
      return self.is_triple_move_correct(former_pos, new_pos)
    if former_piece * player == SPRINTER:
      return self.is_multi_tile_move_correct(former_pos, new_pos)

  def get_necromancer_moves(self, necro_pos):
    """Returns a list of the new positions that can be attained
    by the necromancer currently placed at necro_pos"""
    necro_moves = []
    if self.pieces_are_connected_without(necro_pos):
      neighbour_tiles = self.get_neighbouring_tiles(necro_pos)
      for new_pos in neighbour_tiles:
        if self.pieces[new_pos] == EMPTY and \
          self.respects_move_liberty(necro_pos, new_pos) and \
          not self.is_position_isolated(new_pos, necro_pos):
          necro_moves.append(new_pos)
    return necro_moves

  def get_hugger_moves(self, hugger_pos):
    """Returns a list of the new positions that can be attained
    by the hugger zombie currently placed at hugger_pos"""
    hugger_moves = []
    if self.pieces_are_connected_without(hugger_pos):
      neighbour_tiles = self.get_neighbouring_tiles(hugger_pos)
      if (type(self.pieces[hugger_pos]) is list):
        hugger_moves += neighbour_tiles
      else:
        for new_pos in neighbour_tiles:
          if not self.is_position_isolated(new_pos, hugger_pos):
            hugger_moves.append(new_pos)
    return hugger_moves

  def get_jumper_moves(self, jumper_pos):
    """Returns a list of the new positions that can be attained
    by the jumper zombie currently placed at jumper_pos"""
    jumper_moves = []
    if self.pieces_are_connected_without(jumper_pos):
      line_unit_vectors = [(1,  0), (1, -1), (0, -1), (-1,  0), (-1, 1), (0, 1)]
      for dir_q, dir_r in line_unit_vectors:
        jump_length = 1
        potential_pos = (jumper_pos[0] + dir_q, jumper_pos[1] + dir_r)
        while potential_pos in self.pieces and self.pieces[potential_pos] != EMPTY:
          potential_pos = (potential_pos[0] + dir_q, potential_pos[1] + dir_r)
          jump_length += 1
        if jump_length > 1:
          jumper_moves.append(potential_pos)
    return jumper_moves

  def get_creeper_moves(self, creeper_pos):
    """Returns a list of the new positions that can be attained
    by the creeper zombie currently placed at creeper_pos"""
    creeper_moves = []
    if self.pieces_are_connected_without(creeper_pos):
      paths = self.find_all_paths_of_size(creeper_pos, 3, creeper_pos)
      for path in paths:
        creeper_moves.append(path[-1])
    return creeper_moves

  def get_sprinter_moves(self, sprinter_pos):
    """Returns a list of the new positions that can be attained
    by the sprinter zombie currently placed at sprinter_pos"""
    sprinter_moves = []
    if self.pieces_are_connected_without(sprinter_pos):
      empty_tiles = self.get_empty_tiles()
      sprinter_moves.append(sprinter_pos)
      new_component_found = True
      while(new_component_found):
        new_component_found = False
        for empty_tile in empty_tiles:
          for attainable_tile in sprinter_moves:
            if self.respects_move_liberty(attainable_tile, empty_tile) and \
              not self.is_position_isolated(empty_tile, sprinter_pos):
              empty_tiles.remove(empty_tile)
              sprinter_moves.append(empty_tile)
              new_component_found = True
              break
      sprinter_moves.remove(sprinter_pos)
    return sprinter_moves

  def jumps_in_line(self, from_pos, to_pos):
    """Returns True if the line between from_pos and to_pos
    intersects perpendicularly the tile edges and only
    crosses non-empty tiles; False otherwise"""
    line_unit_vectors = [(1,  0), (1, -1), (0, -1), (-1,  0), (-1, 1), (0, 1)]
    from_q, from_r = from_pos
    to_q, to_r = to_pos
    delta_q = to_q - from_q
    delta_r = to_r - from_r
    mult_factor = max(abs(delta_q), abs(delta_r))
    for dir_q, dir_r in line_unit_vectors:
      if mult_factor * dir_q == delta_q and \
        mult_factor * dir_r == delta_r:
        for i in range(1, mult_factor):
          if not (from_q + i * dir_q, from_r + i * dir_r) in self.pieces:
            return False
        return True
    return False

  def is_triple_move_correct(self, from_pos, to_pos):
    """Returns True if there exists a path of empty tiles
    of length 3 between from_pos and to_pos such that it
    respects move liberty and doesn't go back on its own step;
    False otherwise"""
    if not to_pos in self.pieces or self.pieces[to_pos] != EMPTY:
      return False
    for path in self.find_all_paths_of_size(from_pos, 3, from_pos):
      if path[-1] == to_pos:
        return True
    return False
    
  def find_all_paths_of_size(self, start_pos, size, orig_pos, path=[]):
    """Returns a list containing all the paths of the given size
    between start_pos and any position such that they respect
    move liberty and don't go back on their own step"""
    path = path + [start_pos]
    if len(path) == size + 1:
      return [path]
    paths = []
    potential_positions = [coord for coord in
      self.get_neighbouring_tiles(start_pos) \
      if coord in self.pieces and \
      self.respects_move_liberty(start_pos, coord)]
    for new_pos in potential_positions:
      if new_pos not in path and not self.is_position_isolated(new_pos, orig_pos):
        new_paths = self.find_all_paths_of_size(new_pos, size, orig_pos, path)
        for new_path in new_paths:
          paths.append(new_path)
    paths_of_correct_size = []
    for path in paths:
      if len(path) == size + 1:
        paths_of_correct_size.append(path)
    return paths_of_correct_size

  def find_all_paths(self, start_pos, end_pos, orig_pos, path=[]):
    """Returns a list containing all the paths between
    start_pos and end_pos such that they respect move liberty
    and don't go back on their own step"""
    path = path + [start_pos]
    if start_pos == end_pos:
      return [path]
    paths = []
    potential_positions = [coord for coord in
      self.get_neighbouring_tiles(start_pos) \
      if coord in self.pieces and \
      self.respects_move_liberty(start_pos, coord) and \
      not self.is_position_isolated(coord, orig_pos)]
    for new_pos in potential_positions:
      if new_pos not in path:
        new_paths = find_all_paths(new_pos, end_pos, orig_pos, path)
        for new_path in new_paths:
          paths.append(new_path)
    return paths

  def is_multi_tile_move_correct(self, from_pos, to_pos):
    """Returns True if there exists a path of empty tiles
    between from_pos and to_pos such that it respects move
    liberty and doesn't go back on its own step;
    False otherwise"""
    if not from_pos in self.pieces:
      raise NonExistingTile(from_pos)
    if not to_pos in self.pieces:
      raise NonExistingTile(to_pos)
    if self.pieces[to_pos] != EMPTY or \
      not self.pieces_are_connected_without(from_pos):
      return False
    try:
      self.get_shortest_path(from_pos, to_pos)
      return True
    except NoPath:
      return False

  def get_shortest_path(self, start_pos, end_pos):
    """Returns a shortest path between start_pos and end_pos
    such that every move performed respects the move liberty."""
    if start_pos == end_pos:
      return []
    visited = {}
    # Predecessor matrix in the BFS
    prede = {}
    prede[start_pos] = None

    for empty_tile in self.get_empty_tiles():
      visited[empty_tile] = False
      prede[empty_tile] = None
    
    neighbours = [start_pos]

    while len(neighbours) > 0:
      neighbour = neighbours.pop(0)
      visited[neighbour] = True
      
      if neighbour == end_pos:
        succ = [neighbour]
        curr = prede[neighbour]
        while curr is not None and curr != start_pos:
          succ.append(curr)
          curr = prede[curr]
        succ.reverse()
        return succ
      
      unvisited_succ = [coord for coord in
        self.get_neighbouring_tiles(neighbour) \
        if coord in self.pieces and \
        self.respects_move_liberty(neighbour, coord) and \
        not visited[coord]]
      for coord in unvisited_succ:
        if not coord in neighbours:
          neighbours.append(coord)
          prede[coord] = neighbour
    raise NoPath()

  def pieces_are_connected_without(self, piece_pos_moving):
    """Returns True if the pieces are still connected without
    the (top) piece positioned at piece_pos_moving"""
    if not piece_pos_moving in self.pieces:
      raise NonExistingTile(piece_pos_moving)
    if type(self.pieces[piece_pos_moving]) is list:
      return True
    piece_coords = []
    for piece_pos in self.pieces:
      if piece_pos != piece_pos_moving and self.pieces[piece_pos] != EMPTY:
        piece_coords.append(piece_pos)
    l = [piece_coords[-1]]
    k = [piece_coords[-1]]
    while k:
      x = k.pop(-1)
      for new_pos in piece_coords:
        if self.are_neighbours(x, new_pos) and not new_pos in l:
          l.append(new_pos)
          k.append(new_pos)
    return len(l) == len(piece_coords)

  def is_position_isolated(self, new_pos, orig_pos):
    """Returns True if new_pos has no non-empty neighbour or
    that its only neighbour is orig_pos; False otherwise"""
    non_empty_neighbours = self.get_non_empty_neighbours(new_pos)
    return len(non_empty_neighbours) == 1 and \
      non_empty_neighbours[0] == orig_pos

  def respects_move_liberty(self, pos1, pos2):
    """Returns True if moving a piece from pos1 to pos2 respects
    the move liberty; False otherwise"""
    if not pos1 in self.pieces:
      raise NonExistingTile(pos1)
    if not pos2 in self.pieces:
      raise NonExistingTile(pos2)
    if self.pieces[pos2] != EMPTY:
      return False
    q1, r1 = pos1
    q2, r2 = pos2
    q_dist = q2 - q1
    r_dist = r2 - r1
    if q_dist == 1 and r_dist == -1:
      return (not (q1, r1 - 1) in self.pieces) or (not (q1 + 1, r1) in self.pieces) or \
        (self.pieces[(q1, r1 - 1)] == EMPTY) or (self.pieces[(q1 + 1, r1)] == EMPTY)
    elif q_dist == 1 and r_dist == 0:
      return (not (q1 + 1, r1 - 1) in self.pieces) or (not (q1, r1 + 1) in self.pieces) or \
        (self.pieces[(q1 + 1, r1 - 1)] == EMPTY) or (self.pieces[(q1, r1 + 1)] == EMPTY)
    elif q_dist == 0 and r_dist == 1:
      return (not (q1 + 1, r1) in self.pieces) or (not (q1 - 1, r1 + 1) in self.pieces) or \
        (self.pieces[(q1 + 1, r1)] == EMPTY) or (self.pieces[(q1 - 1, r1 + 1)] == EMPTY)
    elif q_dist == -1 and r_dist == 1:
      return (not (q1, r1 + 1) in self.pieces) or (not (q1 - 1, r1) in self.pieces) or \
        (self.pieces[(q1, r1 + 1)] == EMPTY) or (self.pieces[(q1 - 1, r1)] == EMPTY)
    elif q_dist == -1 and r_dist == 0:
      return (not (q1, r1 - 1) in self.pieces) or (not (q1 - 1, r1 + 1) in self.pieces) or \
        (self.pieces[(q1, r1 - 1)] == EMPTY) or (self.pieces[(q1 - 1, r1 + 1)] == EMPTY)
    elif q_dist == 0 and r_dist == -1:
      return (not (q1 + 1, r1 - 1) in self.pieces) or (not (q1 - 1, r1) in self.pieces) or \
        (self.pieces[(q1 + 1, r1 - 1)] == EMPTY) or (self.pieces[(q1 - 1, r1)] == EMPTY)
    else:
      return False

  def are_neighbours(self, pos1, pos2):
    """Returns True if the two positions are neighbour hex,
    False otherwise"""
    return self.hex_distance(pos1, pos2) == 1

  def hex_distance(self, pos1, pos2):
    """Returns the distance between two hex positions"""
    q1, r1 = pos1
    q2, r2 = pos2
    return (abs(q1 - q2) + abs(r1 - r2) + abs(q1 + r1 - q2 - r2)) / 2

  def get_neighbouring_tiles(self, pos):
    """Returns all hex positions which are adjacent to pos"""
    q, r = pos
    neighbour_deltas = [(1,  0), (1, -1), (0, -1), (-1,  0), (-1, 1), (0, 1)]
    neighbour_tiles = []
    for (delta_q, delta_r) in neighbour_deltas:
      neighbour_tiles.append((q + delta_q, r + delta_r))
    return neighbour_tiles

  def get_non_empty_neighbours(self, pos):
    """Returns a list of all the non-empty hex positions
    adjacent to pos"""
    non_empty_neighbours = []
    for neighbour_pos in self.get_neighbouring_tiles(pos):
      if neighbour_pos in self.pieces and \
        self.pieces[neighbour_pos] != EMPTY:
        non_empty_neighbours.append(neighbour_pos)
    return non_empty_neighbours

  def get_empty_tiles(self):
    """Returns all hex positions of the empty tiles"""
    empty_positions = []
    for pos in self.pieces:
      if self.pieces[pos] == EMPTY:
        empty_positions.append(pos)
    return empty_positions

  def is_placement_valid(self, piece_desc, position, player, step):
    """Returns True if the unplaced piece described by piece_desc
    can be placed at position; False otherwise"""
    (piece, qty) = piece_desc
    if piece * player < 0 or qty < 1 or \
      not piece in self.unplaced_pieces or \
      self.unplaced_pieces[piece] != qty or \
      not position in self.pieces:
      return False
    #The two first steps must allow to put a piece
    #on empty board or adjacent to an opponent piece
    if step <= 2:
      return True
    non_empty_neighbours = self.get_non_empty_neighbours(position)
    for neighbour in non_empty_neighbours:
      if neighbour in self.pieces:
        if type(self.pieces[neighbour]) is int:
          if self.pieces[neighbour] * player < 0:
            return False
        else:
          for piece in self.pieces[neighbour]:
            if piece * player < 0:
              return False
    return len(non_empty_neighbours) > 0

  def get_possible_placements(self, player, step):
    """Returns all hex positions at which player can place a piece"""
    empty_tiles = self.get_empty_tiles()
    if step <= 2:
      return empty_tiles
    possible_placements = []
    for empty_tile in empty_tiles:
      neighbours = self.get_neighbouring_tiles(empty_tile)
      neighbour_index = 0
      is_connected = False
      no_opponent_adjacent = True
      while neighbour_index < len(neighbours) and \
        no_opponent_adjacent:
        if neighbours[neighbour_index] in self.pieces:
          if type(self.pieces[neighbours[neighbour_index]]) is int:
            if self.pieces[neighbours[neighbour_index]] * player > 0:
              is_connected = True
            elif self.pieces[neighbours[neighbour_index]] * player < 0:
              no_opponent_adjacent = False
          else:
            for i in range(len(self.pieces[neighbours[neighbour_index]])):
              if self.pieces[neighbours[neighbour_index]][i] * player < 0:
                no_opponent_adjacent = False
            if no_opponent_adjacent:
              is_connected = True
        neighbour_index += 1
      if is_connected and no_opponent_adjacent:
        possible_placements.append(empty_tile)
    return possible_placements

  def get_actions(self, player, step):
    """ Returns all the possible actions for player."""
    possible_placements = self.get_possible_placements(player, step)
    placement_actions = []
    move_actions = []
    #Each player must play its necromancer before its fourth turn
    if (step == 7 or step == 8) and \
      self.unplaced_pieces[player * NECROMANCER] > 0:
      for pos in possible_placements:
        placement_actions.append(('P', (player * NECROMANCER, self.unplaced_pieces[player * NECROMANCER]), pos))
    else:
      for piece in self.unplaced_pieces:
        if piece * player > 0 and self.unplaced_pieces[piece] > 0:
          for (q_coord, r_coord) in possible_placements:
            placement_actions.append(('P', (piece, self.unplaced_pieces[piece]), (q_coord, r_coord)))
      if self.unplaced_pieces[player * NECROMANCER] == 0:
        for former_pos in self.pieces:
          if type(self.pieces[former_pos]) is int:
            piece_type = self.pieces[former_pos] * player
          else:
            piece_type = self.pieces[former_pos][-1] * player
          if piece_type > 0:
            new_positions = []
            if piece_type == NECROMANCER:
              new_positions = self.get_necromancer_moves(former_pos)
            elif piece_type == HUGGER:
              new_positions = self.get_hugger_moves(former_pos)
            elif piece_type == JUMPER:
              new_positions = self.get_jumper_moves(former_pos)
            elif piece_type == CREEPER:
              new_positions = self.get_creeper_moves(former_pos)
            elif piece_type == SPRINTER:
              new_positions = self.get_sprinter_moves(former_pos)
            for new_pos in new_positions:
              move_actions.append(('M', former_pos, new_pos))
    possible_moves = placement_actions + move_actions
    if possible_moves:
      return possible_moves
    else:
      return [('S', (0, 0), (0, 0))]

  def is_action_valid(self, action, player, step):
    """Returns True if the action played by player
    is valid; False otherwise.
    """
    kind, (q1, r1), (q2, r2) = action
    #Each player must play its necromancer before its fourth turn
    if (step == 7 or step == 8) and \
      self.unplaced_pieces[player * NECROMANCER] > 0 and \
      (kind != 'P' or q1 != player * NECROMANCER):
      return False
    if kind == 'P':
      return self.is_placement_valid((q1, r1), (q2, r2), player, step)
    elif kind == 'M':
      return self.is_move_valid((q1, r1), (q2, r2), player)
    elif kind == 'S':
      possible_actions = self.get_actions(player, step)
      if len(possible_actions) == 1 and possible_actions[0][0] == 'S':
        return True
      else:
        return False
    else:
      return False

  def place_piece(self, piece_desc, to_pos, player):
    """Changes the board by placing the unplaced piece
    described by piece_desc at position to_pos.
    """
    (piece, qty) = piece_desc
    self.unplaced_pieces[piece] = qty - 1
    self.pieces[to_pos] = piece
    for neighbour_pos in self.get_neighbouring_tiles(to_pos):
      if not neighbour_pos in self.pieces:
        self.pieces[neighbour_pos] = EMPTY

  def move_piece(self, from_pos, to_pos, player):
    """Changes the board by placing the unplaced piece
    described by piece_desc at position to_pos.
    """
    if type(self.pieces[from_pos]) is list:
      moving_piece = self.pieces[from_pos].pop()
      if len(self.pieces[from_pos]) == 1:
        self.pieces[from_pos] = self.pieces[from_pos][0]
      if type(self.pieces[to_pos]) is list:
        self.pieces[to_pos].append(moving_piece)
      else:
        if self.pieces[to_pos] == EMPTY:
          self.pieces[to_pos] = moving_piece
        else:
          self.pieces[to_pos] = [self.pieces[to_pos], moving_piece]
        for neighbour_pos in self.get_neighbouring_tiles(to_pos):
          if not neighbour_pos in self.pieces:
            self.pieces[neighbour_pos] = EMPTY
    else:
      moving_piece = self.pieces[from_pos]
      self.pieces[from_pos] = EMPTY
      if type(self.pieces[to_pos]) is list:
        self.pieces[to_pos].append(moving_piece)
      else:
        if self.pieces[to_pos] == EMPTY:
          self.pieces[to_pos] = moving_piece
        else:
          self.pieces[to_pos] = [self.pieces[to_pos], moving_piece]
        for neighbour_pos in self.get_neighbouring_tiles(to_pos):
          if not neighbour_pos in self.pieces:
            self.pieces[neighbour_pos] = EMPTY
      for neighbour_pos in self.get_neighbouring_tiles(from_pos):
        if len(self.get_non_empty_neighbours(neighbour_pos)) == 0:
          del self.pieces[neighbour_pos]

  def play_action(self, action, player, step):
    """Play an action if it is valid.

    If the action is invalid, raise an InvalidAction exception.
    Return self.

    Arguments:
    action -- the action to be played
    player -- the player who is playing
    step -- the step at which the action occurs

    """
    if not self.is_action_valid(action, player, step):
      raise InvalidAction(action, player)
    kind, (q1, r1), (q2, r2) = action
    if kind == 'P':
      self.place_piece((q1, r1), (q2, r2), player)
    elif kind == 'M':
      self.move_piece((q1, r1), (q2, r2), player)
    elif kind == 'S':
      pass
    else:
      raise InvalidAction(action, player)
    return self

  def is_finished(self):
    """Return whether one or both of the necromancers
    are surrounded (i.e. the game is finished).
    """
    for piece in self.pieces:
      if (type(self.pieces[piece]) is int and abs(self.pieces[piece]) == NECROMANCER) or \
        (type(self.pieces[piece]) is list and \
        (NECROMANCER in self.pieces[piece] or -NECROMANCER in self.pieces[piece])):
        if len(self.get_non_empty_neighbours(piece)) == 6:
          return True
    return False 

  def get_score(self, player=PLAYER1):
    """Return a score for this board for the given player.

    The score is the difference between the number of adjacent pieces
    to the necromancer opponent and those adjacent to the necromancer
    of player.
    """
    score = 0
    if self.unplaced_pieces[NECROMANCER * player] == 0 and \
      self.unplaced_pieces[NECROMANCER * -player] == 0:
      for piece in self.pieces:
        if (type(self.pieces[piece]) is int and self.pieces[piece] * player == NECROMANCER) or \
           (type(self.pieces[piece]) is list and NECROMANCER * player in self.pieces[piece]):
          score -= len(self.get_non_empty_neighbours(piece))
        elif (type(self.pieces[piece]) is int and self.pieces[piece] * -player == NECROMANCER) or \
           (type(self.pieces[piece]) is list and NECROMANCER * -player in self.pieces[piece]):
          score += len(self.get_non_empty_neighbours(piece))
    return score

def load_percepts(csvfile):
  """Load percepts from a CSV file.
  """
  if isinstance(csvfile, str):
    with open(csvfile, "r") as f:
      return load_percepts(f)
  else:
    import csv
    percepts = []
    for row in csv.reader(csvfile):
      if not row:
        continue
        row = [int(c.strip(), 16) for c in row]
        percepts.append(row)
        assert len(row) == len(percepts[0]), \
          "rows must have the same length"
    return percepts


class Agent:

  """Interface for a Zombies agent"""

  def initialize(self, percepts, players, time_left):
    """Begin a new game.

    The computation done here also counts in the time credit.

    Arguments:
    percepts -- the initial board in a form that can be fed to the Board
        constructor.
    players -- sequence of players this agent controls
    time_left -- a float giving the number of seconds left from the time
        credit for this agent (all players taken together). If the game is
        not time-limited, time_left is None.

    """
    pass

  def play(self, percepts, player, step, time_left):
    """Play and return an action.

    Arguments:
    percepts -- the current board in a form that can be fed to the Board
        constructor.
    player -- the player to control in this step
    step -- the current step number, starting from 1
    time_left -- a float giving the number of seconds left from the time
        credit. If the game is not time-limited, time_left is None.

    """
    pass

def agent_main(agent, args_cb=None, setup_cb=None):
  """Launch agent server depending on arguments.

  Arguments:
  agent -- an Agent instance
  args_cb -- function taking two arguments: the agent and an
      ArgumentParser. It can add custom options to the parser.
      (None to disable)
  setup_cb -- function taking three arguments: the agent, the
      ArgumentParser and the options dictionary. It can be used to
      configure the agent based on the custom options. (None to
      disable)

  """
  pass
