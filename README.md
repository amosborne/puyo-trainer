# Just tell me the controls:
1. Press the *spacebar* to proceed to the next test.
2. Use the *arrow keys* and *X/Z* to move and rotate.
3. Use the *mouse (right and left click)* for everything else.

# I'd prefer to see it in video format:

https://www.youtube.com/watch?v=rWmMWvFeG8M

# OK, I'll read the (short) manual:

## How to Download

Download the latest release (look to the sidebar on the right). Packaged as a Windows (64-bit) executable. Do not separate the executable from the other directories (*modules/* and *ppvs2_skins/*) contained within the zip file.

## How to Use

Puzzles are organized into modules. Modules should generally contain puzzles that are similar in the technique they are applying. Use a descriptive README to tell the user what to do.

### New Module

Create a new module. 2-by-1 (Tsu) pieces or 2-by-2 (Fever) pieces may be used. The board, color limit, and pop limit may also take some non-standard values.

### New Puzzle

First you must define the **initial board** and the **drawpile**. Left-click on the puzzle board to rotate between puyos. Right-click will clear that puyo. Initial boards may not have floating puyos, more puyos colors than the module allows for, or any puyos already grouped above the pop limit.

Click start to input the **solution**. Use the arrow keys (shift left, shift right, apply move, revert move) and X/Z (rotate right/left). Save when you're done. If you close the window, nothing is saved.

### Review Puzzle

The selected puzzle may be reviewed to see what the solution is. Only the up and down arrow keys are active on this interface. Notice that multiple review windows may be open simultaneously.

### Test Module

Testing a module is a cycle of **test** and **review**. The test period is how many tests are performed in a row, followed by the corresponding reviews. A single test is chosen at random from the puzzles within the module. The colors are randomized. The number of moves tested will be no more than what was selected. So if your module has puzzles with typically 6 moves, perhaps you start practicing by only testing the final 2 and then working your way up to 6.

The same keyboard controls are used in the test window. During a test, the up arrow revert move key is disabled. At the end of a test or review, **press the spacebar to move on to the next screen** (whether that be a test or review). Spacebar can actually skip a review entirely, because the up arrow revert move key is enabled in this case.

### Self-compatibility

This is an experimental bonus feature. It tests whether all the puzzles within a module are self-compatible, i.e. if both puzzles have the same board state and the puyos to be drawn look the same, then the move made in both puzzles must also be the same. This calculation can take a lot of time to run if there are many puzzle in the module. The output of the self-compatibility calculation is written to file in the relevant *modules/* subdirectory.

### Skins

PuyoPuyoVs2 skin PNG files may be used, simply drop the file into the *ppvs2_skins/* directory.

### Editing files by hand

Module and puzzle metadata are stored in plain text in the relevant *modules/* subdirecty. I do not recommend performing any manual manipulation of these files except for deleting individual puzzles or deleting entire modules. When modules (and their puzzles) are loaded by the software, there is error checking of all the metadata that will prevent a module from loading if a file has become "broken". Of course you can edit these files by hand at your own risk.
