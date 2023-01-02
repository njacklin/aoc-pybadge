# Advent of Code "Trophy"
# 2022 Edition


# PARAMETERS AND CONSTANTS ----------------------------------------------------

USE_NEOPIXELS = False # set to True or False... one board is defective :-(

MAX_CHAR = 20 # max number of text chars that can fit, based on observation

COLOR_AOCGREEN  = 0x009900 # from AoC website stylesheet
COLOR_AOCYELLOW = 0xFFFF66 # from AoC website stylesheet
COLOR_AOCBGBLUE = 0x0F0F23 # from AoC website stylesheet (background) -- not used
COLOR_WHITE  = 0xFFFFFF
COLOR_BLACK  = 0x000000
COLOR_GRAY   = 0x888888
COLOR_YELLOW = 0xFFFF00

COLOR_ROCK   = COLOR_GRAY
COLOR_SAND   = COLOR_YELLOW

# IMPORTS --------------------------------------------------------------------
import board
import displayio
import keypad 
from math import floor
import neopixel
import random
import re 
# note limitations of circuitpython re module here: 
    # https://docs.circuitpython.org/en/latest/docs/library/re.html
import time
import ulab.numpy as np 
# note limitations of circuitpython ulab.numpy module here: 
    # https://micropython-ulab.readthedocs.io/en/latest/ulab-intro.html
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle

# HELPER FUNCTIONS -----------------------------------------------------------

# convenience function to convert (r,c) coords to linear index for occ{Rock,Sand} array
def occ_lindex(r,c):
    global demo_size_width
    return int( demo_size_width*c + r )

def occ_lindext(coordtuple):
    global demo_size_width
    return int( demo_size_width*coordtuple[1] + coordtuple[0] )

# set stars label 
def update_label_stars(star_count): 
    global label_stars
    label_stars.text = ("*"*star_count) + (" "*(MAX_CHAR-star_count))

# init demo
# there's not going to be a lot of error handling here...
def init_demo():
    global demo_energy
    global demo_flash_count
    global disp_circles
    global demo_step
    
    # set global variables to initial values


# copy set function (should work like copy.deepcopy, but for a set)
def copy_set(inset):
    outset = set()

    for e in inset:
        outset.add(e)

    return outset

# SETUP ----------------------------------------------------------------------

# load font
font = bitmap_font.load_font("fonts/SourceCodePro-subset_32_126-10pt.bdf", 
                             displayio.Bitmap)

# display group setup
disp_group = list()
disp_group.append(displayio.Group()) # disp_group[0] for main leaderboard
disp_group.append(displayio.Group()) # disp_group[1] for first-to-50 stars
disp_group.append(displayio.Group()) # disp_group[2] for 2022 day14 demo
DGROUP_MAIN      = const(0)
DGROUP_50STARS   = const(1)
DGROUP_2022DAY14 = const(2)

# build common display group assets - DOES NOT WORK, CANNOT ADD OBJECTS TO MULTIPLE DISPLAY GROUPS
#label_aoc = label.Label(font, text="Advent of Code\n  int y=202x;", color=0x009900)
#label_aoc.anchor_point = (0.0,0.0) # upper left
#label_aoc.anchored_position = (0,0)

# button stuff
BUTTON_LEFT   = const(128)
BUTTON_UP     = const(64)
BUTTON_DOWN   = const(32)
BUTTON_RIGHT  = const(16)
BUTTON_SELECT = const(8)
BUTTON_START  = const(4)
BUTTON_A      = const(2)
BUTTON_B      = const(1)

keys = keypad.ShiftRegisterKeys(
    clock=board.BUTTON_CLOCK,
    data=board.BUTTON_OUT,
    latch=board.BUTTON_LATCH,
    key_count=8,
    value_when_pressed=True,
)

# build disp_group[DGROUP_MAIN] --------------------------

# # background
# bg = Rect(0, 0, board.DISPLAY.width, board.DISPLAY.height, fill=COLOR_BGBLUE)
# disp_group[DGROUP_MAIN].append(bg)

# AOC label at top
label_aoc = label.Label(font, text="Advent of Code\n   int y=2022;", color=COLOR_AOCGREEN)
label_aoc.anchor_point = (0.0,0.0) # upper left
label_aoc.anchored_position = (0,0)
disp_group[DGROUP_MAIN].append(label_aoc)

# "VTS Leaderboard"
label_leaderboard = label.Label(font,text="~ VTS Leaderboard ~")
label_leaderboard.anchor_point = (0.5,0.0) # middle top
label_leaderboard.anchored_position = (board.DISPLAY.width/2,45)
disp_group[DGROUP_MAIN].append(label_leaderboard)

# first place
label_1st = label.Label(font,text="1st:   Sean McCarthy")
label_1st.anchor_point = (0.0,0.0) # left top
label_1st.anchored_position = (0,60)
disp_group[DGROUP_MAIN].append(label_1st)

label_1st_stars = label.Label(font,text="    41*",color=COLOR_AOCYELLOW)
label_1st_stars.anchor_point = (0.0,0.0) # left top
label_1st_stars.anchored_position = (-1,60+1)
disp_group[DGROUP_MAIN].append(label_1st_stars)

# second place
label_2nd = label.Label(font,text="2nd:   DaveBuscaglia")
label_2nd.anchor_point = (0.0,0.0) # left top
label_2nd.anchored_position = (0,75)
disp_group[DGROUP_MAIN].append(label_2nd)

label_2nd_stars = label.Label(font,text="    39*",color=COLOR_AOCYELLOW)
label_2nd_stars.anchor_point = (0.0,0.0) # left top
label_2nd_stars.anchored_position = (-1,75+1)
disp_group[DGROUP_MAIN].append(label_2nd_stars)

# third place
label_3rd = label.Label(font,text="3rd:    Ash Evans")
label_3rd.anchor_point = (0.0,0.0) # left top
label_3rd.anchored_position = (0,90)
disp_group[DGROUP_MAIN].append(label_3rd)

label_3rd_stars = label.Label(font,text="    34*",color=COLOR_AOCYELLOW)
label_3rd_stars.anchor_point = (0.0,0.0) # left top
label_3rd_stars.anchored_position = (-1,90+1)
disp_group[DGROUP_MAIN].append(label_3rd_stars)

# push button for more...
label_more = label.Label(font,text="push button for more",color=COLOR_BLACK)
label_more.anchor_point = (0.5,1.0) # middle bottom
label_more.anchored_position = (board.DISPLAY.width/2,board.DISPLAY.height)
disp_group[DGROUP_MAIN].append(label_more)

# build disp_group[DGROUP_50STARS] -----------------------

# # background
# bg = Rect(0, 0, board.DISPLAY.width, board.DISPLAY.height, fill=0x0f0f23)
# disp_group[DGROUP_50STARS].append(bg)

# AOC label at top
label_aoc = label.Label(font, text="Advent of Code\n   int y=2022;", color=COLOR_AOCGREEN)
label_aoc.anchor_point = (0.0,0.0) # left top
label_aoc.anchored_position = (0,0)
disp_group[DGROUP_50STARS].append(label_aoc)

# "First to 50*"
label_firstto50 = label.Label(font,text="First to 50*")
label_firstto50.anchor_point = (0.5,0.0) # middle top
label_firstto50.anchored_position = (board.DISPLAY.width/2,45)
disp_group[DGROUP_50STARS].append(label_firstto50)

# Name
label_firstto50name = label.Label(font,text="~ UNCLAIMED ~")
label_firstto50name.anchor_point = (0.5,0.0) # middle top
label_firstto50name.anchored_position = (board.DISPLAY.width/2,60)
disp_group[DGROUP_50STARS].append(label_firstto50name)

# Date
label_firstto50date = label.Label(font,text="   TBD   ")
label_firstto50date.anchor_point = (0.5,0.0) # middle top
label_firstto50date.anchored_position = (board.DISPLAY.width/2,75)
disp_group[DGROUP_50STARS].append(label_firstto50date)

# stars
# label_stars = label.Label(font,text="0123456789012345678901234",color=0xffff66) # only 20 chars show
#label_stars = label.Label(font,text=("*"*MAX_CHAR),color=COLOR_YELLOW)
label_stars = label.Label(font,text=(" "*MAX_CHAR),color=COLOR_AOCYELLOW)
label_stars.anchor_point = (0.0,0.0) # middle top
label_stars.anchored_position = (0,100)
disp_group[DGROUP_50STARS].append(label_stars)


# build disp_group[DGROUP_2022DAY14] ---------------------

# # background -- looks bad when display is viewed from the side
# bg = Rect(0, 0, board.DISPLAY.width, board.DISPLAY.height, fill=0x0f0f23)
# disp_group[DGROUP_2022DAY14].append(bg)

# AOC label at top
# label_aoc = label.Label(font, text="Advent of Code\n   int y=2022;", color=0x009900)
label_aoc = label.Label(font, text="AoC 2022      Day 14", color=COLOR_AOCGREEN)
label_aoc.anchor_point = (0.0,0.0) # left top
label_aoc.anchored_position = (0,0)
disp_group[DGROUP_2022DAY14].append(label_aoc)

# neopixel init ------------------------------------------
if USE_NEOPIXELS:
    pin_neopixel = board.NEOPIXEL
    num_neopixel = 5
    neopixels = neopixel.NeoPixel(pin_neopixel, num_neopixel, pixel_order=neopixel.GRB,
                                brightness=0.01, auto_write=False)
    neopixels.fill(COLOR_BLACK) # turn off
    neopixels.show()

# establish global variables for all states ---------------

main_more_delay_sec = 2.0
main_more_delay_on = False
main_more_change_time = time.monotonic() + 2.0*main_more_delay_sec 
# delay a little extra the first time

fiftystar_stars = 0
fiftystar_count_delay_sec = 1.0
fiftystar_flash_on = True
fiftystar_flash_count = 0
fiftystar_flash_delay_sec = 1.0
fiftystar_change_time = 0.0
FIFTYSTAR_FLASHES = const(4)

# demo global vars 
demo_voffset = const(28)  # offset for start of demo view
demo_hoffset = const(0)   # offset for start of demo view

demo_size_height = int(board.DISPLAY.height-demo_voffset)
demo_size_width  = int(board.DISPLAY.width-demo_hoffset)

print('DEBUG: size of occ* is (%d,%d)'%(demo_size_height,demo_size_width))

# change to occupied array, and record ROCK or SAND
# this will conserve RAM, because arrays of bools don't work in circuitpython
# (specifically, you can't index into them properly for some reason)
demo_occ = np.zeros((demo_size_width,demo_size_height),dtype=np.int8) # bool does not work properly
ROCK = const(1)
SAND = const(2)

demo_sand_startpos = (0,int(demo_size_width/2))

demo_step_delay_sec = 1.0


# one-time setup for demo screen ----------------------------
# for 2022 day 14 demo, this means drawing the "rocks"

# read input file or use default input
try:
    f = open("aoc2022_day14_init.txt")
    print("reading init file")
except:
    f = open("aoc2022_day14_ex.txt")
    print("using default init") 
    

regex_space = re.compile(" ")
regex_comma = re.compile(",")

for line in f.readlines():
    # skip short lines
    if len(line) <= 1:
        next 
        
    print("DEBUG: processing line: %s"%line)
        
    # add rocks
    ipair = 0
    current = (0,0)
    for s in regex_space.split(line):
        # skip short segments and arrows
        if len(s) < 3:
            continue 
            
        # print("DEBUG: processing coords = '%s' of len = %d"%(s,len(s)))
            
        # parse coordinates
        coord = [0,0]
        for (iscm,scm) in enumerate(regex_comma.split(s)):
            coord[iscm] = int(scm) 
            
        # print("DEBUG: coord parsed is (%d,%d)"%(coord[0],coord[1]))
            
        # fill in demo_occ and draw rocks as rectangles
        if ipair == 0:
            current = tuple(coord) 
            demo_occ[current] = ROCK 
        else: 
            if coord[0] > current[0]: # fill towards right
                # draw rect
                this_rect = Rect( current[0] + demo_hoffset, 
                                  current[1] + demo_voffset, 
                                  coord[0] - current[0] + 1, 
                                  1, 
                                  fill = COLOR_ROCK )
                disp_group[DGROUP_2022DAY14].append(this_rect)
                # fill in demo_occ 
                for i in range(coord[0]-current[0]):
                    current = (current[0]+1, current[1]) 
                    demo_occ[current] = ROCK 
            elif coord[0] < current[0]: # fill towards left
                # draw rect
                this_rect = Rect( coord[0] + demo_hoffset, 
                                  current[1] + demo_voffset, 
                                  current[0] - coord[0] + 1, 
                                  1, 
                                  fill = COLOR_ROCK )
                disp_group[DGROUP_2022DAY14].append(this_rect)
                # fill in demo_occ 
                for i in range(current[0]-coord[0]):
                    current = (current[0]-1, current[1]) 
                    demo_occ[current] = ROCK 
            elif coord[1] > current[1]: # fill downward
                # draw rect
                this_rect = Rect( current[0] + demo_hoffset, 
                                  current[1] + demo_voffset, 
                                  1, 
                                  coord[1] - current[1] + 1, 
                                  fill = COLOR_ROCK )
                disp_group[DGROUP_2022DAY14].append(this_rect)
                # fill in demo_occ 
                for i in range(coord[1]-current[1]):
                    current = (current[0], current[1]+1) 
                    demo_occ[current] = ROCK 
            elif coord[1] < current[1]: # fill upward
                # draw rect
                this_rect = Rect( current[0] + demo_hoffset, 
                                  coord[1] + demo_voffset, 
                                  1, 
                                  current[1] - coord[1] + 1, 
                                  fill = COLOR_ROCK )
                disp_group[DGROUP_2022DAY14].append(this_rect)
                # fill in demo_occ 
                for i in range(current[1]-coord[1]):
                    current = (current[0], current[1]-1) 
                    demo_occ[current] = ROCK 
            else: # this should only happen if a repeated point is given
                # draw rect
                this_rect = Rect( current[0] + demo_hoffset, 
                                  current[1] + demo_voffset, 
                                  1, 
                                  1, 
                                  fill = COLOR_ROCK )
                disp_group[DGROUP_2022DAY14].append(this_rect)
                # fill in demo_occ 
                demo_occ[current] = ROCK 
                
            # print("DEBUG: coord   = (%d,%d)"%(coord[0],coord[1]))
            # print("DEBUG: current = (%d,%d)"%(current[0],current[1]))
            # assert(current==coord) # fails incorrectly
            
        ipair += 1

f.close()
    


# init display ----------------------------------------------
board.DISPLAY.show(disp_group[DGROUP_MAIN])

print("INFO: END OF SETUP")

# LOOP -----------------------------------------------------------------------

print("INFO: STARTING LOOP...")

dgroup_show = 0

while True:

    # do state actions
    if dgroup_show == DGROUP_MAIN:
        if time.monotonic() >= main_more_change_time:
            if main_more_delay_on:
                label_more.color = COLOR_BLACK # turn "off" text
                main_more_delay_on = False
            else: 
                label_more.color = COLOR_GRAY # turn "on" text
                main_more_delay_on = True

            main_more_change_time = time.monotonic() + main_more_delay_sec

    elif dgroup_show == DGROUP_50STARS:
        if time.monotonic() >= fiftystar_change_time:
            if fiftystar_stars < MAX_CHAR:
                fiftystar_stars += 1
                update_label_stars(fiftystar_stars)
                if USE_NEOPIXELS:
                    for i in range(num_neopixel):
                        neopixels[i] = COLOR_BLACK
                    for i in range(floor(fiftystar_stars/(MAX_CHAR/num_neopixel))):
                        neopixels[i] = COLOR_YELLOW
                    neopixels.show()
                
                if fiftystar_stars == MAX_CHAR:
                    fiftystar_flash_on = True
                    fiftystar_change_time = time.monotonic() + fiftystar_flash_delay_sec
                else:
                    fiftystar_change_time = time.monotonic() + fiftystar_count_delay_sec

            else: # on max stars
                if fiftystar_flash_count < FIFTYSTAR_FLASHES:
                    if fiftystar_flash_on: # if they were on, now turn off
                        update_label_stars(0)
                        if USE_NEOPIXELS:
                            neopixels.fill(COLOR_BLACK)
                            neopixels.show()
                        fiftystar_flash_on = False
                        fiftystar_flash_count += 1
                        
                    else: # if they were off, now turn on
                        update_label_stars(MAX_CHAR)
                        if USE_NEOPIXELS:
                            neopixels.fill(COLOR_YELLOW)
                            neopixels.show()
                        fiftystar_flash_on = True

                    fiftystar_change_time = time.monotonic() + fiftystar_flash_delay_sec

                else: # last flash
                    fiftystar_flash_on = True 
                    fiftystar_flash_count = 0
                    fiftystar_stars = 0
                    update_label_stars(0)
                    fiftystar_change_time = time.monotonic() + fiftystar_count_delay_sec


    elif dgroup_show == DGROUP_2022DAY14:
        if time.monotonic() >= demo_next_step_time:
            
            # move sand # TODO
            pass
                    
            # set time for next step increment
            demo_next_step_time = time.monotonic() + demo_step_delay_sec
    else:
        print("ERROR: undefined state: %d"%dgroup_show)

    # detect button presses
    ke = event = keys.events.get()
    if ke: # if any key press event is happening
        print("INFO: detected key press = %d"%ke.key_number)
        dgroup_show = (dgroup_show+1)%len(disp_group)
        board.DISPLAY.show(disp_group[dgroup_show])

        # do state transition stuff, if necessary
        if USE_NEOPIXELS:
            neopixels.fill(COLOR_BLACK) # turn off all neopixels on any state transition
            neopixels.show()

        if dgroup_show == DGROUP_MAIN:
            print("INFO: transitioning to MAIN/LEADERBOARD screen")
            main_more_delay_on = False
            label_more.color = COLOR_BLACK
            main_more_change_time = time.monotonic() + 2.0*main_more_delay_sec

        elif dgroup_show == DGROUP_50STARS:
            print("INFO: transitioning to 50* screen")
            fiftystar_stars = 0
            update_label_stars(0)
            fiftystar_flash_count = 0
            fiftystar_time_change = time.monotonic() + 2.0*fiftystar_flash_delay_sec

        elif dgroup_show == DGROUP_2022DAY14:
            print("INFO: transitioning to DEMO screen")
            init_demo()
            demo_next_step_time = time.monotonic() + 2.0*demo_step_delay_sec# TODO update

        else:
            print("ERROR: undefined state transition: %d"%dgroup_show)

        time.sleep(0.5) # pause to ignore registering too many clicks
        keys.events.clear()   
        keys.reset()           

    # print("DEBUG: ...BOTTOM OF LOOP")
