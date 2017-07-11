from Tkinter import *
from Tkconstants import W, E, N, S
from tkFileDialog import askopenfilename, asksaveasfilename
from tkMessageBox import askyesnocancel, showerror
from globalconst import *
from checkers import Checkers
from boardview import BoardView
from playercontroller import PlayerController
from alphabetacontroller import AlphaBetaController
from gamepersist import SavedGame
from textserialize import Serializer
import numpy
import tcp_client
import datetime
import uuid
import random

def get_piece(letter):
    if letter == 'b':
        return BLACK | MAN
    if letter == 'B':
        return BLACK | KING
    if letter == 'w':
        return WHITE | MAN
    if letter == 'W':
        return WHITE | KING
    return FREE

def convert_in_hundreds(value, mn, mx):
    if (value < mn):
        return 0
    if (value > mx):
        return 100
    oldRange = (mx-mn)
    newRange = (100-0)
    newValue = (((value - mn)*newRange) / oldRange) + 0
    return int(newValue)

def calculate_arousal(state, model):
    list = []
    for (a, s) in model.successors(state):
        util = model.utility(BLACK, s)
        if (util < -200):
            util = -200
        if (util > 200):
            util = 200
        list.append(util)
    arr = numpy.array(list)
    arousal = numpy.std(arr, axis=0)
    arousal = convert_in_hundreds(arousal, 0, 3)
    return  arousal

ID = '1-9u3ljbalrsotjp9ah9rdr586l1'
with open(ID+'-moves.txt', 'r') as file:
    i=0
    models = []
    timestamps = []
    model = Checkers()
    skip = False
    for line in  file.readlines():
        if i == 0:
            model = Checkers()
            model.curr_state.clear()
            fields = line.split(",")
            timestamps.append(fields[0])
            if fields[1] == "'turn-start'":
                #state += fields[2]
                values = []
                for f in fields:
                    values.append(f.split(" "))
                    model.curr_state.to_move = BLACK

            else:
                skip = True
            i+=1
        else:
            if skip == False:
                values = line.strip("\n").split(" ")
                values = filter(None, values)
                if values[0] == '8':
                    model.curr_state.squares[45] = get_piece(values[1])
                    model.curr_state.squares[46] = get_piece(values[2])
                    model.curr_state.squares[47] = get_piece(values[3])
                    model.curr_state.squares[48] = get_piece(values[4])
                if values[0] == '7':
                    model.curr_state.squares[39] = get_piece(values[1])
                    model.curr_state.squares[40] = get_piece(values[2])
                    model.curr_state.squares[41] = get_piece(values[3])
                    model.curr_state.squares[42] = get_piece(values[4])
                if values[0] == '6':
                    model.curr_state.squares[34] = get_piece(values[1])
                    model.curr_state.squares[35] = get_piece(values[2])
                    model.curr_state.squares[36] = get_piece(values[3])
                    model.curr_state.squares[37] = get_piece(values[4])
                if values[0] == '5':
                    model.curr_state.squares[28] = get_piece(values[1])
                    model.curr_state.squares[29] = get_piece(values[2])
                    model.curr_state.squares[30] = get_piece(values[3])
                    model.curr_state.squares[31] = get_piece(values[4])
                if values[0] == '4':
                    model.curr_state.squares[23] = get_piece(values[1])
                    model.curr_state.squares[24] = get_piece(values[2])
                    model.curr_state.squares[25] = get_piece(values[3])
                    model.curr_state.squares[26] = get_piece(values[4])
                if values[0] == '3':
                    model.curr_state.squares[17] = get_piece(values[1])
                    model.curr_state.squares[18] = get_piece(values[2])
                    model.curr_state.squares[19] = get_piece(values[3])
                    model.curr_state.squares[20] = get_piece(values[4])
                if values[0] == '2':
                    model.curr_state.squares[12] = get_piece(values[1])
                    model.curr_state.squares[13] = get_piece(values[2])
                    model.curr_state.squares[14] = get_piece(values[3])
                    model.curr_state.squares[15] = get_piece(values[4])
                if values[0] == '1':
                    model.curr_state.squares[6] = get_piece(values[1])
                    model.curr_state.squares[7] = get_piece(values[2])
                    model.curr_state.squares[8] = get_piece(values[3])
                    model.curr_state.squares[9] = get_piece(values[4])
            if i==9:
                if skip == False:
                    models.append(model)
                else:
                    skip = False
                i = 0
            else:
                i+=1

i = 0
for m in models:
    # calculate utility value for valence
    # less than -200 is definitely bad, 0 best value
    # print("util black=", self.model.curr_state.utility(BLACK))
    # print("util white=", self.model.curr_state.utility(WHITE))
    valence = m.curr_state.utility(BLACK)
    valence = convert_in_hundreds(valence, -200, 200)
    # print("valence=", valence)

    # calculate how many moves are possible (maybe also utility variance for them)
    # capture should evaluate variance of utility as well, otherwise inconsistent
    if len(m.captures_available()) != 0:
        list = []
        for (a, s) in m.successors(m.curr_state):
            ar = calculate_arousal(s, m)
            list.append(ar)
        arousal = numpy.mean(list, axis=0)
        arousal = int(arousal)
    # a variance of 4 seems pretty high, should probably se as maximum
    else:
        list = []
        for (a, s) in m.successors(m.curr_state):
            util = m.utility(BLACK, s)
            if (util < -200):
                util = -200
            if (util > 200):
                util = 200
            list.append(util)
        arr = numpy.array(list)
        arousal = numpy.std(arr, axis=0)
        arousal = convert_in_hundreds(arousal, 0, 3)
        # print("arousal=",arousal)

    # save in log
    with open(ID+'-retrieved.txt', 'a') as file:
        file.write(
            "{},{},{}\n".format(timestamps[i], valence, arousal))
    i += 1

#model.curr_state = states[0]
#print model.curr_state
#print model.curr_state.utility(BLACK, model.curr_state)