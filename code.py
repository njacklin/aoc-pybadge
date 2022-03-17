# Advent of Code "Trophy"

# IMPORTS --------------------------------------------------------------------
import board
import displayio
import time

from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

# SETUP ----------------------------------------------------------------------

# load font
font = bitmap_font.load_font("fonts/SourceCodePro-subset_32_126-10pt.bdf", 
                             displayio.Bitmap)

# display group setup
disp_group = list()
disp_group.append(displayio.Group()) # disp_group[0] for main leaderboard
disp_group.append(displayio.Group()) # disp_group[1] for first-to-50 stars
disp_group.append(displayio.Group()) # disp_group[2] for 2021 day11 demo
DGROUP_MAIN = 0
DGROUP_50STARS = 1
DGROUP_2021DAY11 = 2

# build common display group assets - DOES NOT WORK
#label_aoc = label.Label(font, text="Advent of Code\n  int y=2021;", color=0x009900)
#label_aoc.anchor_point = (0.0,0.0) # upper left
#label_aoc.anchored_position = (0,0)

# build disp_group[DGROUP_MAIN] --------------------------

# AOC label at top
label_aoc = label.Label(font, text="Advent of Code\n  int y=2021;", color=0x009900)
label_aoc.anchor_point = (0.0,0.0) # upper left
label_aoc.anchored_position = (0,0)
disp_group[DGROUP_MAIN].append(label_aoc)

# "VTS Leaderboard"
label_leaderboard = label.Label(font,text=" VTS Leaderboard:")
label_leaderboard.anchor_point = (0.0,0.0) # upper left
label_leaderboard.anchored_position = (0,30)
disp_group[DGROUP_MAIN].append(label_leaderboard)

# build disp_group[DGROUP_50STARS] -----------------------

# AOC label at top
label_aoc = label.Label(font, text="Advent of Code\n  int y=2021;", color=0x009900)
label_aoc.anchor_point = (0.0,0.0) # upper left
label_aoc.anchored_position = (0,0)
disp_group[DGROUP_50STARS].append(label_aoc)

# "First to 50*"
label_firstto50 = label.Label(font,text=" First to 50*:")
label_firstto50.anchor_point = (0.0,0.0) # upper left
label_firstto50.anchored_position = (0,30)
disp_group[DGROUP_50STARS].append(label_firstto50)

# build disp_group[DGROUP_2021DAY11] ---------------------

# AOC label at top
label_aoc = label.Label(font, text="Advent of Code\n  int y=2021;", color=0x009900)
label_aoc.anchor_point = (0.0,0.0) # upper left
label_aoc.anchored_position = (0,0)
disp_group[DGROUP_2021DAY11].append(label_aoc)

# "Day 11 Demo"
label_demo = label.Label(font,text="2021 Day 11 Demo:")
label_demo.anchor_point = (0.0,0.0) # upper left
label_demo.anchored_position = (0,30)
disp_group[DGROUP_2021DAY11].append(label_demo)

# init display
board.DISPLAY.show(disp_group[DGROUP_MAIN])

print("DEBUG: END OF SETUP")

# LOOP -----------------------------------------------------------------------

print("DEBUG: STARTING LOOP...")

dgroup_show = 0

while True:
    
    time.sleep(5.0)
    dgroup_show = (dgroup_show+1)%len(disp_group)
    board.DISPLAY.show(disp_group[dgroup_show])

    print("DEBUG: ...BOTTOM OF LOOP")
