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

class GameManager(object):
    def __init__(self, **props):
        self.model = Checkers()
        self._root = props['root']
        self.parent = props['parent']
        statusbar = Label(self._root, relief=SUNKEN, font=('Helvetica',7),
                          anchor=NW)
        statusbar.pack(side='bottom', fill='x')
        self.view = BoardView(self._root, model=self.model, parent=self,
                              statusbar=statusbar)
        self.player_color = BLACK
        self.num_players = 1
        self.set_controllers()
        self._controller1.start_turn()
        self.filename = None

        #this gets argument, going to use it to set up experiment type
        global experiment
        global id
        if len(sys.argv) > 1:
            id = sys.argv.pop()
            experiment = sys.argv.pop()
        else:
            experiment = "1"
            # create UUID for log saving
            id = str(uuid.uuid4())
        print experiment
        print id

        #metacompose start
        tcp_client.metacompose_start()
        #tcp_client.metacompose_change_composition("checkers0")
        tcp_client.metacompose_change_composition(id)
        tcp_client.metacompose_change_mood(100,0)


    def set_controllers(self):
        think_time = self.parent.thinkTime.get()
        if self.num_players == 0:
            self._controller1 = AlphaBetaController(model=self.model,
                                                    view=self.view,
                                                    searchtime=think_time,
                                                    end_turn_event=self.turn_finished)
            self._controller2 = AlphaBetaController(model=self.model,
                                                    view=self.view,
                                                    searchtime=think_time,
                                                    end_turn_event=self.turn_finished)
        elif self.num_players == 1:
            # assumption here is that Black is the player
            self._controller1 = PlayerController(model=self.model,
                                                 view=self.view,
                                                 end_turn_event=self.turn_finished)
            self._controller2 = AlphaBetaController(model=self.model,
                                                    view=self.view,
                                                    searchtime=think_time,
                                                    end_turn_event=self.turn_finished)
            # swap controllers if White is selected as the player
            if self.player_color == WHITE:
                self._controller1, self._controller2 = self._controller2, self._controller1
        elif self.num_players == 2:
            self._controller1 = PlayerController(model=self.model,
                                                 view=self.view,
                                                 end_turn_event=self.turn_finished)
            self._controller2 = PlayerController(model=self.model,
                                                 view=self.view,
                                                 end_turn_event=self.turn_finished)
        self._controller1.set_before_turn_event(self._controller2.remove_highlights)
        self._controller2.set_before_turn_event(self._controller1.remove_highlights)

    def _stop_updates(self):
        # stop alphabeta threads from making any moves
        self.model.curr_state.ok_to_move = False
        self._controller1.stop_process()
        self._controller2.stop_process()

    def _save_curr_game_if_needed(self):
        if self.view.is_dirty():
            msg = 'Do you want to save your changes'
            if self.filename:
                msg += ' to %s?' % self.filename
            else:
                msg += '?'
            result = askyesnocancel(TITLE, msg)
            if result == True:
                self.save_game()
            return result
        else:
            return False

    def new_game(self):
        self._stop_updates()
        self._save_curr_game_if_needed()
        self.filename = None
        self._root.title('Raven ' + VERSION)
        self.model = Checkers()
        self.player_color = BLACK
        self.view.reset_view(self.model)
        self.think_time = self.parent.thinkTime.get()
        self.set_controllers()
        self.view.update_statusbar()
        self.view.reset_toolbar_buttons()
        self.view.curr_annotation = ''
        self._controller1.start_turn()

    def load_game(self, filename):
        self._stop_updates()
        try:
            saved_game = SavedGame()
            saved_game.read(filename)
            self.model.curr_state.clear()
            self.model.curr_state.to_move = saved_game.to_move
            self.num_players = saved_game.num_players
            squares = self.model.curr_state.squares
            for i in saved_game.black_men:
                squares[squaremap[i]] = BLACK | MAN
            for i in saved_game.black_kings:
                squares[squaremap[i]] = BLACK | KING
            for i in saved_game.white_men:
                squares[squaremap[i]] = WHITE | MAN
            for i in saved_game.white_kings:
                squares[squaremap[i]] = WHITE | KING
            self.model.curr_state.reset_undo()
            self.model.curr_state.redo_list = saved_game.moves
            self.model.curr_state.update_piece_count()
            self.view.reset_view(self.model)
            self.view.serializer.restore(saved_game.description)
            self.view.curr_annotation = self.view.get_annotation()
            self.view.flip_board(saved_game.flip_board)
            self.view.update_statusbar()
            self.parent.set_title_bar_filename(filename)
            self.filename = filename
        except IOError as (err):
            showerror(PROGRAM_TITLE, 'Invalid file. ' + str(err))

    def open_game(self):
        self._stop_updates()
        self._save_curr_game_if_needed()
        f = askopenfilename(filetypes=(('Raven Checkers files','*.rcf'),
                                       ('All files','*.*')),
                            initialdir=TRAINING_DIR)
        if not f:
            return
        self.load_game(f)

    def save_game_as(self):
        self._stop_updates()
        filename = asksaveasfilename(filetypes=(('Raven Checkers files','*.rcf'),
                                                ('All files','*.*')),
                                     initialdir=TRAINING_DIR,
                                     defaultextension='.rcf')
        if filename == '':
            return
        self._write_file(filename)

    def save_game(self):
        self._stop_updates()
        filename = self.filename
        if not self.filename:
            filename = asksaveasfilename(filetypes=(('Raven Checkers files','*.rcf'),
                                                    ('All files','*.*')),
                                         initialdir=TRAINING_DIR,
                                         defaultextension='.rcf')
            if filename == '':
                return
        self._write_file(filename)

    def _write_file(self, filename):
        try:
            saved_game = SavedGame()
            # undo moves back to the beginning of play
            undo_steps = 0
            while self.model.curr_state.undo_list:
                undo_steps += 1
                self.model.curr_state.undo_move(None, True, True,
                                                self.view.get_annotation())
            # save the state of the board
            saved_game.to_move = self.model.curr_state.to_move
            saved_game.num_players = self.num_players
            saved_game.black_men = []
            saved_game.black_kings = []
            saved_game.white_men = []
            saved_game.white_kings = []
            for i, sq in enumerate(self.model.curr_state.squares):
                if sq == BLACK | MAN:
                    saved_game.black_men.append(keymap[i])
                elif sq == BLACK | KING:
                    saved_game.black_kings.append(keymap[i])
                elif sq == WHITE | MAN:
                    saved_game.white_men.append(keymap[i])
                elif sq == WHITE | KING:
                    saved_game.white_kings.append(keymap[i])
            saved_game.description = self.view.serializer.dump()
            saved_game.moves = self.model.curr_state.redo_list
            saved_game.flip_board = self.view.flip_view
            saved_game.write(filename)
            # redo moves forward to the previous state
            for i in range(undo_steps):
                annotation = self.view.get_annotation()
                self.model.curr_state.redo_move(None, annotation)
            # record current filename in title bar
            self.parent.set_title_bar_filename(filename)
            self.filename = filename
        except IOError:
            showerror(PROGRAM_TITLE, 'Could not save file.')

    def convert_in_hundreds(self, value, mn, mx):
        if (value < mn):
            return 0
        if (value > mx):
            return 100
        oldRange = (mx-mn)
        newRange = (100-0)
        newValue = (((value - mn)*newRange) / oldRange) + 0
        return int(newValue)

    def calculate_arousal(self, state):
        list = []
        for (a, s) in self.model.successors(state):
            util = self.model.utility(BLACK, s)
            if (util < -200):
                util = -200
            if (util > 200):
                util = 200
            list.append(util)
        arr = numpy.array(list)
        arousal = numpy.std(arr, axis=0)
        arousal = self.convert_in_hundreds(arousal, 0, 3)
        return  arousal

    def turn_finished(self):
        if self.model.curr_state.to_move == BLACK:
            self._controller2.end_turn() # end White's turn
            self._root.update()
            self.view.update_statusbar()

            #Check experiment code
            #0: control group, static music
            #1: supporting group
            global experiment
            global id
            if (experiment != "0"):
                # calculate utility value for valence
                #less than -200 is definitely bad, 0 best value
                print("util black=", self.model.curr_state.utility(BLACK))
                print("util white=", self.model.curr_state.utility(WHITE))
                valence = self.model.curr_state.utility(BLACK)
                valence = self.convert_in_hundreds(valence, -200, 200)
                print("valence=", valence)

                #calculate how many moves are possible (maybe also utility variance for them)
                #capture should evaluate variance of utility as well, otherwise inconsistent
                if len(self.model.captures_available()) != 0:
                    list = []
                    for (a, s) in self.model.successors(self.model.curr_state):
                        ar = self.calculate_arousal(s)
                        list.append(ar)
                    arousal = numpy.mean(list, axis=0)
                    arousal = int(arousal)
                #a variance of 4 seems pretty high, should probably se as maximum
                else:
                    list = []
                    for (a, s) in self.model.successors(self.model.curr_state):
                        util = self.model.utility(BLACK, s)
                        if (util < -200):
                            util = -200
                        if (util > 200):
                            util = 200
                        list.append(util)
                    arr = numpy.array(list)
                    arousal = numpy.std(arr, axis=0)
                    arousal = self.convert_in_hundreds(arousal, 0, 3)
                print("arousal=",arousal)

                #send new mood to metacompose
                tcp_client.metacompose_change_mood(valence,arousal)

                #save in log
                with open(experiment+'-'+id+'.txt', 'a') as file:
                    file.write("'{}',{},{}\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), valence,arousal,self.model.curr_state))

            #regrdless of experiment save state
            with open(experiment+'-'+id+'-moves.txt', 'a') as file:
                file.write("'{}','{}',{}\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'turn-start', self.model.curr_state))

            self._controller1.start_turn() # begin Black's turn
        else:
            self._controller1.end_turn() # end Black's turn
            self._root.update()
            self.view.update_statusbar()

            # regrdless of experiment save moves
            with open(experiment+'-'+id+'-moves.txt', 'a') as file:
                file.write("'{}','{}',{}\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'turn-end', self.model.curr_state))

            self._controller2.start_turn() # begin White's turn

