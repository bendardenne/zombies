#!/usr/bin/env python3
"""
GUI interface for the Zombie game.
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
import signal
import sys
import ssl
import logging
import time
import threading
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
from optparse import OptionParser
from zombies import *
from game import Viewer, Game

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

CONFIG_MSG = 'CONFIG'
READY_MSG = 'READY'
PLAYMOVE_MSG = 'PLAY'
PAUSE_MSG = 'PAUSE'
NEXT_MSG = 'NEXT'
PREVIOUS_MSG = 'PREVIOUS'
FINISHED_MSG = 'FINISHED'
ACKNOWLEDGEMENT_MSG = 'ACKNOWLEDGEMENT'
ACTIONS_MSG = 'ACTIONS'
HASMOVED_MSG = 'MOVE'

CONFIG_HvH = 'human vs human'
CONFIG_HvA = 'human vs ai'
CONFIG_AvH = 'ai vs human'
CONFIG_AvA = 'ai vs ai'
CONFIG_R = 'replay'

connectedEvent = threading.Event()
acknowledgementEvent = threading.Event()
hasPlayedEvent = threading.Event()
lastActionPlayed = ''

class SimpleMessager(WebSocket):

  def giveViewerRef(self, viewer):
    self.viewer = viewer

  def handleMessage(self):
    if self.data is None:
      self.data = ''
    try:
      message = self.data.decode("utf-8").split('\n')
      #logging.info("Message received: " + message[0])
      if message[0] == READY_MSG:
        if message[1] == CONFIG_R:
          self.sendTraceStep()
      elif message[0] == PAUSE_MSG:
        self.server.paused = True
      elif message[0] == PLAYMOVE_MSG:
        self.server.paused = False
        self.sendTraceStep()
      elif message[0] == PREVIOUS_MSG:
        self.sendPreviousStep()
      elif message[0] == NEXT_MSG:
        self.sendNextStep()
      elif message[0] == ACKNOWLEDGEMENT_MSG:
        acknowledgementEvent.set()
      elif message[0] == HASMOVED_MSG:
        self.hasMoved(message[1:])
        hasPlayedEvent.set()

    except Exception as n:
      logging.error(n)

  def update(self, step, action, player):
    self.sendMessage(PLAYMOVE_MSG + "\n" + str(player) + "\n" + self.actionToString(action))
    self.server.step += 1

  def finished(self, steps, winner, reason=""):
    self.sendMessage(FINISHED_MSG + "\n" + self.finished_msg())

  def handleConnected(self):
    logging.info("Web client connected at " + str(self.address))
    try:
      if self.server.configuration == CONFIG_R:
        self.sendMessage(CONFIG_MSG + "\n" + CONFIG_R)
      elif self.server.configuration == CONFIG_HvH:
        self.sendMessage(CONFIG_MSG + "\n" + CONFIG_HvH)
      elif self.server.configuration == CONFIG_HvA:
        self.sendMessage(CONFIG_MSG + "\n" + CONFIG_HvA)
      elif self.server.configuration == CONFIG_AvH:
        self.sendMessage(CONFIG_MSG + "\n" + CONFIG_AvH)
      elif self.server.configuration == CONFIG_AvA:
        self.sendMessage(CONFIG_MSG + "\n" + CONFIG_AvA)
      connectedEvent.set()
    except Exception as n:
      logging.error(n)

  def handleClose(self):
    logging.info("Connection with " + str(self.address) + " closed")

  def sendPreviousStep(self):
    if self.server.step > 0:
      self.server.step -= 1
      player, action, t = self.server.trace.actions[self.server.step]
      self.sendMessage(PREVIOUS_MSG + "\n" + str(player) + "\n" + self.actionToString(action))

  def sendNextStep(self):
    if self.server.step < len(self.server.trace.actions) - 1:
      player, action, t = self.server.trace.actions[self.server.step]
      self.sendMessage(PLAYMOVE_MSG + "\n" + str(player) + "\n" + self.actionToString(action))
      self.server.step += 1
    elif self.server.step == len(self.server.trace.actions) - 1:
      player, action, t = self.server.trace.actions[self.server.step]
      self.server.step += 1
      self.sendMessage(PLAYMOVE_MSG + "\n" + str(player) + "\n" + self.actionToString(action) + "\n" + self.finished_msg())

  def sendTraceStep(self):
    def waitAndResend(waitTime, step):
      time.sleep(waitTime)
      if not self.server.paused and step == self.server.step:
        player, action, t = self.server.trace.actions[self.server.step]
        if self.server.step < len(self.server.trace.actions) - 1:
          self.sendMessage(PLAYMOVE_MSG + "\n" + str(player) + "\n" + self.actionToString(action))
          self.server.step += 1
          self.sendTraceStep()
        elif self.server.step == len(self.server.trace.actions) - 1:
          self.server.step += 1
          self.sendMessage(PLAYMOVE_MSG + "\n" + str(player) + "\n" + self.actionToString(action) + "\n" + self.finished_msg())
    
    if self.server.step <= len(self.server.trace.actions) and not self.server.paused:
      waitTime = -t / self.server.speed if self.server.speed < 0 else self.server.speed
      waitThread = threading.Thread(target=waitAndResend, args=(waitTime, self.server.step))
      waitThread.start()

  def actionToString(self, action):
    move, fromPos, toPos = action
    return str(self.server.step) + "\n" + move + "\n" + str(fromPos[0]) + " " + str(fromPos[1]) + "\n" + str(toPos[0]) + " " + str(toPos[1])

  def finished_msg(self):
    msg = ""
    try:
      if self.server.trace.winner == 0:
        msg += "Draw game\n"
      elif self.server.trace.winner > 0:
        msg += "Player 1 has won"
      else:
        msg += "Player 2 has won"
      msg += " after " + str(len(self.server.trace.actions)) + " steps.\n"
      if self.server.trace.reason:
        msg += self.server.trace.reason
    except Exception as e:
      logging.error(e)
    return msg

  def play(self, actions, player, step, time_left):
    msg = ACTIONS_MSG + "\n"
    msg += str(player) + "\n"
    msg += str(step) + "\n"
    for action in actions:
      msg += str(action[0]) + " " + str(action[1][0]) + " " + str(action[1][1]) + " " + str(action[2][0]) + " " + str(action[2][1]) + "\n"
    self.sendMessage(msg)

  def hasMoved(self, msg):
    moveType = msg[0]
    fromPos = (int(msg[1]), int(msg[2]))
    toPos = (int(msg[3]), int(msg[4]))
    global lastActionPlayed
    lastActionPlayed = (moveType, fromPos, toPos)


class WebViewer(Viewer):

  def __init__(self):
    self.running = False
    self.host_address = ''
    self.port = 8500
    self.server = SimpleWebSocketServer(self.host_address, self.port, SimpleMessager)
    self.game = None

  def init_viewer(self, board, game=None):
    self.board = board
    if not self.game:
      self.game = game
      self.server.game = self.game
    if game:
      if type(self.game.agents[0]) == WebViewer and type(self.game.agents[1]) == WebViewer:
        self.server.configuration = CONFIG_HvH
      elif type(self.game.agents[0]) == WebViewer and type(self.game.agents[1]) != WebViewer:
        self.server.configuration = CONFIG_HvA
      elif type(self.game.agents[0]) != WebViewer and type(self.game.agents[1]) == WebViewer:
        self.server.configuration = CONFIG_AvH
      elif type(self.game.agents[0]) != WebViewer and type(self.game.agents[1]) != WebViewer:
        self.server.configuration = CONFIG_AvA
    else:
      self.server.configuration = CONFIG_R
    if not connectedEvent.is_set():
      self.serverThread = threading.Thread(target=self.server.serveforever)
      self.serverThread.start()
      connectedEvent.wait()

  def run(self):
    """Launch the GUI."""
    if self.running:
      return
    self.running = True
    #self.server.serveforever()

  def replay(self, trace, speed, show_end=False):
    """Replay a game given its saved trace.

    Attributes:
    trace -- trace of the game
    speed -- speed scale of the replay
    show_end -- start with the final state instead of the initial state

    """
    self.trace = trace
    self.speed = speed
    # generate all boards to access them backwards
    self.boards = [trace.get_initial_board()]
    for step in range(len(trace.actions)):
      player, action, t = trace.actions[step]
      b = self.boards[-1].clone()
      b.play_action(action, player, step)
      self.boards.append(b)
    self.step = 0
    self.server.initialize_replay(self.trace, self.speed, self.boards)
    self.init_viewer(self.boards[0], None)

  def close_sig_handler(signal, frame):
    self.server.close()
    sys.exit()

  def playing(self, step, player):
    print("Step", step, "- Player", player, "is playing")

  def update(self, step, action, player):
    print("Step", step, "- Player", player, "has played", action)
    acknowledgementEvent.clear()
    self.server.update(step, action, player)
    acknowledgementEvent.wait()

  def play(self, percepts, player, step, time_left):
    try:
      hasPlayedEvent.clear()
      self.server.play(percepts, player, step, time_left)
      hasPlayedEvent.wait()
    except EOFError:
      exit(1)
    try:
      return lastActionPlayed
    except (ValueError, AssertionError):
      pass

  def finished(self, steps, winner, reason=""):
    if winner == 0:
      print("Draw game")
    else:
      print("Player 1" if winner > 0 else "Player 2", "has won!")
    if reason:
      print("Reason:", reason)
    self.server.initialize_replay(self.game.trace, 1.0, [])
    self.server.finished(steps, winner, reason)

  signal.signal(signal.SIGINT, close_sig_handler)
  signal.signal(signal.SIGTERM, close_sig_handler)
  #signal.signal(signal.SIGQUIT, close_sig_handler)
