# Future plans #
Most checkers or chess programs go the route of deep search combined with perfect opening and endgame databases. These techniques are well-explored and not really all that interesting to me. I plan on making a big change in future versions of Raven by relying more on planning than brute-force search.

Here's what I'm thinking:

  * Implement a planning AI. These plans will be based on tactics and strategies from Richard Pask's books [Starting Out in Checkers](http://www.jimloy.com/checkers/pask.htm) and [Play Better Checkers & Draughts](http://www.bobnewell.net/checkers/bookorders/getpbcd1.html), which I use in my own checkers study.
  * Parse training files in order to inform the AI about best moves and positions, whether for openings or endgames. As the user adds more training information, the AI should automatically get better. I will be  switching the file format to XML to make it easier for Raven to parse the information.
  * Represent potential formations (short dyke, long dyke, phalanx, pyramid, echelon) as constraint satisfaction problems (CSPs) and use a quick search to evaluate whether each formation can still be achieved (after each turn) as part of the planning process. The WHITE\_MAP and BLACK\_MAP dictionaries can be used to populate the domain for the CSP variables (each checker used in a formation). CSP search can be long if the problems are too constrained, but this should be a representation with fairly loose constraints and few conflicts. Once I evaluate the goal with a CSP, I will resort to a standard backtracking search (with make\_move and undo\_move) for then determining whether a moving a particular checker gets me closer to the goal formation.
  * Make the undo and redo work completely correct with the background AI processing.
  * Begin documenting my design choices with UML. I've been doing a fair amount of exploratory programming up to this point, but I need to illustrate my design if anyone has a hope of understanding it now.
  * Release a new version that contains the planner code. Probably will use [PyInstaller](http://www.pyinstaller.org). Would like to make an OS X release as well as a Windows release this time around.

# Version 0.4 #
  * Just released! -- finished up the new annotation feature, along with new training files from Richard Pask's Starting Out In Checkers. I made a new Windows executable to share all the new fixes/features I've been working on. Eventually I hope I can generate a similar one for Ubuntu using [PyInstaller](http://www.pyinstaller.org/). Sorry, at this point the Linux version doesn't run.
# Version 0.3.5 #
  * Fixed [issue #2](https://code.google.com/p/raven-checkers/issues/detail?id=#2), [issue #4](https://code.google.com/p/raven-checkers/issues/detail?id=#4), [issue #15](https://code.google.com/p/raven-checkers/issues/detail?id=#15): All related to the fix that the last move by a human player generated a crash in games.py (because there was no available move for the other player). There was also a need for a `terminal_test` check inside `alphabetacontroller`'s `start_move` method to properly respond to a lack of available moves.
  * This version is not available as a Windows executable, but the source code has been checked in to the Mercurial repo and can be run at the command line by typing `python mainframe.py`.
# Version 0.3.4 #
  * Fixed [issue #10](https://code.google.com/p/raven-checkers/issues/detail?id=#10): All dialogs now derive from `tkSimpleDialog.Dialog`
  * Fixed [issue #11](https://code.google.com/p/raven-checkers/issues/detail?id=#11): Multiple undo/redo now works again. Still have issues with undo/redo while the computer is calculating a move, however.
  * Corrected unit tests for optional diamond jumps (for both black and white).
  * Correctly handled `StopIteration` in `argmin_random_tie` (inside utils.py).
  * Modified `find_more_captures` in checkers.py to store a `set` of old moves to detect cycles.
  * If a capture is available, `calc_move` (in alphabetacontroller.py) will now pick the longest available capture. If a term\_event is received, `calc_move` will send `None` to `get_move` (instead of returning `None`, which caused the program to hang). `get_move` will now always call `self._before_turn_event()` instead of checking `state.ok_to_move` first.
  * This version is not available as a Windows executable, but the source code has been checked in to the Mercurial repo and can be run at the command line by typing `python mainframe.py`.
# Version 0.3.3 #
  * Fixed [issue #8](https://code.google.com/p/raven-checkers/issues/detail?id=#8): This was the result of `Checkers._get_captures` not generating all the appropriate moves. I fixed this and added an additional unit test to `test_cb.py` to check for a known faulty case.
  * Some initial attempts to solve [issue #5](https://code.google.com/p/raven-checkers/issues/detail?id=#5), [issue #6](https://code.google.com/p/raven-checkers/issues/detail?id=#6), [issue #7](https://code.google.com/p/raven-checkers/issues/detail?id=#7) and [issue #10](https://code.google.com/p/raven-checkers/issues/detail?id=#10).
  * This version is not available as a Windows executable, but the source code has been checked in to the Mercurial repo and can be run at the command line by typing `python mainframe.py`.
# Version 0.3.1 #
  * One or two player mode, plus an "autoplay" feature that pits the AI engine against itself.
  * AI opponent uses a standard alpha-beta search algorithm which runs in a background process and has a customizable "think time".
  * Tkinter GUI has a Model-View-Controller (MVC) architecture.
  * Basic undo and redo functionality implemented.
  * Board setup allows you to configure the pieces on the checkerboard, set the number of players, and select which player goes next.
  * Flip board allows you to rotate the board 180 degrees to view pieces from either Black or White's perspective.