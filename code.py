# Advent of Code "Trophy"
# 2023 Edition
# Demo of Day 14 (rocks falling) for visualization
#   initialized from aoc2023_day14_init.txt, backup aoc2023_day14_ex.txt
#   note, must be a 10x10 grid of "O" for rocks, "#" for immovable cubes, or "." for empty

# PARAMETERS AND CONSTANTS ----------------------------------------------------

USE_NEOPIXELS = True # set to True or False... one board is defective :-(

USE_ACCEL = True # set to True or False... PyBadge LC does not have device.

MAX_CHAR = const(20) # max number of text chars that can fit, based on observation

COLOR_AOCGREEN  = 0x009900 # from AoC website stylesheet
COLOR_AOCYELLOW = 0xFFFF66 # from AoC website stylesheet
COLOR_AOCBGBLUE = 0x0F0F23 # from AoC website stylesheet (background) -- not used
COLOR_WHITE  = 0xFFFFFF
COLOR_BLACK  = 0x000000
COLOR_GRAY   = 0x888888
COLOR_LTGRAY = 0xAAAAAA
COLOR_YELLOW = 0xFFFF00
COLOR_BROWN  = 0xCD7F32

COLOR_ROCK   = COLOR_GRAY
COLOR_CUBE   = COLOR_BROWN

# IMPORTS --------------------------------------------------------------------
import board
import displayio
import gc
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
import adafruit_lis3dh # accelerometer library, see 
   # https://learn.adafruit.com/adafruit-lis3dh-triple-axis-accelerometer-breakout/python-circuitpython
   # from experimentation, as you look at the board, +x is to the right, 
   # +y is down, and -z is into the board (+z is out of the board towards viewer)
import digitalio # needed for accelerometer

# HELPER FUNCTIONS -----------------------------------------------------------

# set stars label 
def update_label_stars(star_count): 
    global label_stars
    label_stars.text = ("*"*star_count) + (" "*(MAX_CHAR-star_count))

# set flash count label
def update_label_loadval(): # takes in an int
    global label_loadval
    global demo_loadval 
    global demo_map

    # update demo_loadval by reading demo_map
    demo_loadval = 0
    for irow in range(demo_N_ROWS):
        for icol in range(demo_N_COLS):
            if demo_map[irow,icol] == DEMO_V_ROCK:
                if   demo_falldir == DEMO_FALL_UP:
                    demo_loadval += (demo_N_ROWS - irow) 
                elif demo_falldir == DEMO_FALL_DOWN: 
                    demo_loadval += (irow + 1)
                elif demo_falldir == DEMO_FALL_RIGHT: 
                    demo_loadval += (demo_N_COLS - icol)
                elif demo_falldir == DEMO_FALL_LEFT: 
                    demo_loadval += (icol + 1)
                else: 
                    raise ValueError("Invalid demo_falldir = %s"%demo_falldir)    

    # update label asset 
    label_loadval.text = "%4d" % demo_loadval

# demo_convert_rowcol_to_circlecoords
#  be very careful of row/col and x/y directions.  rows go down y and cols go down x.
def demo_convert_rowcol_to_circlecoord(c_row,c_col):

    global DEMO_CIR_RADIUS
    global DEMO_CIR_START_X
    global DEMO_CIR_START_Y

    cir_x = DEMO_CIR_START_X+DEMO_CIR_RADIUS+1+(2*DEMO_CIR_RADIUS+2)*c_col # x along col

    cir_y = DEMO_CIR_START_Y+DEMO_CIR_RADIUS+1+(2*DEMO_CIR_RADIUS+2)*c_row # y along rows

    return (cir_x,cir_y)

# init demo
# there's not going to be a lot of error handling here...
def demo_init(): 
    global disp_group 
    global demo_disp_circles
    global demo_display_group_init_size
    global demo_map 
    global demo_stop

    global DEMO_CIR_RADIUS
    global DEMO_CIR_START_X
    global DEMO_CIR_START_Y
    
    # set global variables to initial values
    demo_stop = False 

    demo_disp_circles = list()

    # remove all rock and cube objects (anything drawn after initial init)
    while len(disp_group[DGROUP_2023DAY14]) > demo_display_group_init_size:
        disp_group[DGROUP_2023DAY14].pop() 
        
    # send out garbage collector 
    gc.collect()

    # read input file or use default input
    try:
        f = open("aoc2023_day14_init.txt")
        print("INFO: reading init file")
    except:
        f = open("aoc2023_day14_ex.txt")
        print("INFO: using default init") 
        
    # fill in map and draw objects
    irow = 0
    for line in f.readlines():
        if len(line) < 2:
            continue 
        
        for (icol,c) in enumerate(line.strip()):
            if c == '.':
                demo_map[irow,icol] = DEMO_V_EMPTY

            elif c == 'O':
                demo_map[irow,icol] = DEMO_V_ROCK 

                (cir_x,cir_y) = demo_convert_rowcol_to_circlecoord(irow,icol)

                demo_disp_circles.append( Circle( cir_x, cir_y,                                                 
                                                  DEMO_CIR_RADIUS,
                                                  fill=COLOR_GRAY, 
                                                  stroke=1,
                                                  outline=COLOR_LTGRAY) )
                
                # print("DEBUG: creating rock at map index (%d,%d) with coords (%d,%d)"%(irow,icol,cir_x,cir_y))
                
                disp_group[DGROUP_2023DAY14].append(demo_disp_circles[-1])

            elif c == '#':
                demo_map[irow,icol] = DEMO_V_CUBE 

                disp_group[DGROUP_2023DAY14].append( Rect( DEMO_CIR_START_X+(2*DEMO_CIR_RADIUS+2)*icol, 
                                                           DEMO_CIR_START_Y+(2*DEMO_CIR_RADIUS+2)*irow,
                                                           2*DEMO_CIR_RADIUS+2, # height
                                                           2*DEMO_CIR_RADIUS+2, # width
                                                           fill=COLOR_BROWN ) )

            else:
                raise Exception("Unrecognized symbol: %s"%c)
                
        irow += 1

    f.close()

    print("INFO: demo_init() complete")
    
    
# demo-related function: check for rotation
#   updates demo_falldir and reset demo_stop
def demo_check_rotation():
    global demo_falldir 
    global demo_stop 
    
    init_demo_falldir = demo_falldir 
    
    # read accelerometer
    (a_x,a_y,a_z) = accel.acceleration 
    
    # print('DEBUG: check_rotation a_x = %0.2f, a_y = %0.2f, a_z = %0.2f'%(a_x,a_y,a_z))
    
    if a_y > 0 and abs(a_y) > abs(a_x): 
        demo_falldir = DEMO_FALL_DOWN
    elif a_y < 0 and abs(a_y) > abs(a_x): 
        demo_falldir = DEMO_FALL_UP
    elif a_x > 0 and abs(a_x) > abs(a_y):
        demo_falldir = DEMO_FALL_RIGHT
    elif a_x < 0 and abs(a_x) > abs(a_y):
        demo_falldir = DEMO_FALL_LEFT
    else:
        demo_falldir = DEMO_FALL_DOWN
        print('WARN: could not detect direction, so setting demo_falldir = DEMO_FALL_DOWN')
        
    if init_demo_falldir != demo_falldir:
        if demo_falldir == DEMO_FALL_DOWN:
            print('INFO: changing rotation direction to DOWN')
        elif demo_falldir == DEMO_FALL_UP:
            print('INFO: changing rotation direction to UP')
        elif demo_falldir == DEMO_FALL_RIGHT:
            print('INFO: changing rotation direction to RIGHT')
        elif demo_falldir == DEMO_FALL_LEFT:
            print('INFO: changing rotation direction to LEFT')

        demo_stop = False # restart demo if it was stopped
    
# return rock (Circle) object in  disp_group[DGROUP_2023DAY14] which corresponds to coordinates given
#   or None for failure
def demo_find_rock_in_disp_group(c_row,c_col):

    global demo_disp_circles

    (cir_x,cir_y) = demo_convert_rowcol_to_circlecoord(c_row,c_col)
    # print("DEBUG: in find_rock searching for rock at map index (%d,%d) with coords (%d,%d)"%(c_row,c_col,cir_x,cir_y))

    for Rock in demo_disp_circles:
        # print("DEBUG: (Rock.x,Rock.y)=(%d,%d)"%(Rock.x,Rock.y))
        if Rock.x + DEMO_CIR_RADIUS == cir_x and Rock.y + DEMO_CIR_RADIUS == cir_y : # constructor is a convenience function(?), x/y are shifted by CIR_RADIUS on read back
           return Rock 

    print("ERROR: did not find a match in find_rock")
    time.sleep(1.0) # DEBUG

    return None 
    
# demo-related function: try to move the rocks 
def demo_rocks_fall() :
    global demo_stop 
    global demo_map
    global demo_N_ROWS
    global demo_N_COLS
    
    fall_x = 0 # amount to "fall" in x direction
    fall_y = 0 # amount to "fall" in y direction
    
    if demo_falldir == DEMO_FALL_DOWN:
        fall_y = 1
    elif demo_falldir == DEMO_FALL_UP:
        fall_y = -1
    elif demo_falldir ==  DEMO_FALL_LEFT:
        fall_x = -1
    elif demo_falldir ==  DEMO_FALL_RIGHT:
        fall_x = 1
    else:
        raise ValueError(demo_falldir)
    
    # print("DEBUG: inside demo_rocks_fall()") # debug
    
    # scan map and try to move each rock.  if one moves, bail out (this will make "falling" visible)
    for irow in range(demo_N_ROWS):
        for icol in range(demo_N_COLS):
            # print("DEBUG: checking map at (%d,%d), value found = %d"%(irow,icol,demo_map[irow,icol]))
            if demo_map[irow,icol] == DEMO_V_ROCK:

                # print("DEBUG: rock found at (%d,%d)"%(irow,icol))
                # DANGEROUS - reading beyond indices doesn't always fail?? extends array!
                #   DO NOT DO: # print("DEBUG: value where we want to move to is %d (EMPTY = %d)"%(demo_map[irow+fall_y,icol+fall_x],DEMO_V_EMPTY))
                # print("DEBUG: irow = %d, fall_y = %d, demo_N_ROWS = %d, icol = %d, fall_x= %d, demo_N_COLS = %d"%(irow,fall_y,demo_N_ROWS,icol,fall_x,demo_N_COLS))
                # print("DEBUG: 0 <= irow+fall_y < demo_N_ROWS is %s and 0 <= icol+fall_x < demo_N_COLS is %s"%(0 <= irow+fall_y < demo_N_ROWS, 0 <= icol+fall_x < demo_N_COLS ))
                if 0 <= irow+fall_y < demo_N_ROWS and 0 <= icol+fall_x < demo_N_COLS and demo_map[irow+fall_y,icol+fall_x] == DEMO_V_EMPTY:
                    # update position in demo_map
                    demo_map[irow+fall_y,icol+fall_x] = DEMO_V_ROCK 
                    demo_map[irow,icol] = DEMO_V_EMPTY 

                    # update position in display_group drawing
                    Rock = demo_find_rock_in_disp_group(irow,icol)
                    if not Rock:
                        # unroll changes to demo_map to avoid state corruption
                        demo_map[irow+fall_y,icol+fall_x] = DEMO_V_EMPTY 
                        demo_map[irow,icol] = DEMO_V_ROCK 
                        raise Exception("*** find_rock failed !!!") # fucks up state in demo_map... not atomic
                    
                    (new_cir_x,new_cir_y) = demo_convert_rowcol_to_circlecoord(irow+fall_y,icol+fall_x)
                    Rock.x = new_cir_x - DEMO_CIR_RADIUS
                    Rock.y = new_cir_y - DEMO_CIR_RADIUS 

                    # if we successfully moved a rock, return early
                    # print("DEBUG: *** moved a rock ***") # debug
                    return 

    # if we get here, then no rocks were moved
    demo_stop = False # was True here... this basically makes demo_stop always False 
    # NOTE: the CPU has to be doing something, so no point of demo_stop = True. 

    # print("DEBUG: hit bottom of demo_rocks_fall() with no rock moved") # debug
    update_label_loadval()    
    

# SETUP ----------------------------------------------------------------------

# load font
font = bitmap_font.load_font("fonts/SourceCodePro-subset_32_126-10pt.bdf", 
                             displayio.Bitmap)

# display group setup
disp_group = list()
disp_group.append(displayio.Group()) # disp_group[0] for main leaderboard
disp_group.append(displayio.Group()) # disp_group[1] for first-to-50 stars
disp_group.append(displayio.Group()) # disp_group[2] for 2023 day14 demo
DGROUP_MAIN      = const(0)
DGROUP_50STARS   = const(1)
DGROUP_2023DAY14 = const(2)

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

# accelerometer setup ------------------------------------
# read by pulling (x,y,z) = accel.acceleration
# normalize by dividing by adafruit_lis3dh.STANDARD_GRAVITY
# to check for shaking, use "accel.shake(shake_threshold=30)" (lower = easier to detect, try 15-60)
if USE_ACCEL: 
    accel = adafruit_lis3dh.LIS3DH_I2C(board.I2C(), int1=digitalio.DigitalInOut(board.ACCELEROMETER_INTERRUPT))
    accel.range = adafruit_lis3dh.RANGE_2_G

# print('DEBUG: initial accelerometer reading (normalized): ')
# (a_x,a_y,a_z) = accel.acceleration 
# print('       a_x = %0.2f g, a_y = %0.2f g, a_z = %0.2f g'%
#       (a_x/adafruit_lis3dh.STANDARD_GRAVITY,a_y/adafruit_lis3dh.STANDARD_GRAVITY,a_z/adafruit_lis3dh.STANDARD_GRAVITY))

# build disp_group[DGROUP_MAIN] --------------------------

# # background
# bg = Rect(0, 0, board.DISPLAY.width, board.DISPLAY.height, fill=COLOR_BGBLUE)
# disp_group[DGROUP_MAIN].append(bg)

# AOC label at top
label_aoc = label.Label(font, text="Advent of Code\n   int y=2023;", color=COLOR_AOCGREEN)
label_aoc.anchor_point = (0.0,0.0) # upper left
label_aoc.anchored_position = (0,0)
disp_group[DGROUP_MAIN].append(label_aoc)

# "VTS Leaderboard"
label_leaderboard = label.Label(font,text="~ VTS Leaderboard ~")
label_leaderboard.anchor_point = (0.5,0.0) # middle top
label_leaderboard.anchored_position = (board.DISPLAY.width/2,45)
disp_group[DGROUP_MAIN].append(label_leaderboard)

# first place                             NNNNNNNNNNNNN
label_1st = label.Label(font,text="1st:   DominickBeamn")
label_1st.anchor_point = (0.0,0.0) # left top
label_1st.anchored_position = (0,60)
disp_group[DGROUP_MAIN].append(label_1st)

label_1st_stars = label.Label(font,text="    50*",color=COLOR_AOCYELLOW)
label_1st_stars.anchor_point = (0.0,0.0) # left top
label_1st_stars.anchored_position = (-1,60+1)
disp_group[DGROUP_MAIN].append(label_1st_stars)

# second place                            NNNNNNNNNNNNN
label_2nd = label.Label(font,text="2nd:   Sean McCarthy")
label_2nd.anchor_point = (0.0,0.0) # left top
label_2nd.anchored_position = (0,75)
disp_group[DGROUP_MAIN].append(label_2nd)

label_2nd_stars = label.Label(font,text="    42*",color=COLOR_AOCYELLOW)
label_2nd_stars.anchor_point = (0.0,0.0) # left top
label_2nd_stars.anchored_position = (-1,75+1)
disp_group[DGROUP_MAIN].append(label_2nd_stars)

# third place                             NNNNNNNNNNNNN
label_3rd = label.Label(font,text="3rd:   DaveBuscaglia")
label_3rd.anchor_point = (0.0,0.0) # left top
label_3rd.anchored_position = (0,90)
disp_group[DGROUP_MAIN].append(label_3rd)

label_3rd_stars = label.Label(font,text="    41*",color=COLOR_AOCYELLOW)
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
label_aoc = label.Label(font, text="Advent of Code\n   int y=2023;", color=COLOR_AOCGREEN)
label_aoc.anchor_point = (0.0,0.0) # left top
label_aoc.anchored_position = (0,0)
disp_group[DGROUP_50STARS].append(label_aoc)

# "First to 50*"
label_firstto50 = label.Label(font,text="First to 50*")
label_firstto50.anchor_point = (0.5,0.0) # middle top
label_firstto50.anchored_position = (board.DISPLAY.width/2,45)
disp_group[DGROUP_50STARS].append(label_firstto50)

# Name
label_firstto50name = label.Label(font,text="Dominick Beaman", color=COLOR_AOCYELLOW)
label_firstto50name.anchor_point = (0.5,0.0) # middle top
label_firstto50name.anchored_position = (board.DISPLAY.width/2,60)
disp_group[DGROUP_50STARS].append(label_firstto50name)

# Date
label_firstto50date = label.Label(font,text="before 12/31/2023!")
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


# build disp_group[DGROUP_2023DAY14] ---------------------

# # background -- looks bad when display is viewed from the side
# bg = Rect(0, 0, board.DISPLAY.width, board.DISPLAY.height, fill=0x0f0f23)
# disp_group[DGROUP_2023DAY14].append(bg)

# AOC label at top
label_aoc = label.Label(font, text="AoC 2023      Day 14", color=COLOR_AOCGREEN)
label_aoc.anchor_point = (0.0,0.0) # left top
label_aoc.anchored_position = (0,0)
disp_group[DGROUP_2023DAY14].append(label_aoc)

# "Load" label
label_load = label.Label(font, text="Load")
label_load.anchor_point = (0.0,0.0) # left top
label_load.anchored_position = (0,100)
disp_group[DGROUP_2023DAY14].append(label_load)

# "Load" value label
label_loadval = label.Label(font, text="   0")
label_loadval.anchor_point = (0.0,0.0) # left top
label_loadval.anchored_position = (0,115)
disp_group[DGROUP_2023DAY14].append(label_loadval)


# neopixel init ------------------------------------------
# if USE_NEOPIXELS: # always init... just never turn on if not using
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

demo_N_ROWS = 10
demo_N_COLS = 10

demo_loadval = 0

demo_stop = False 
demo_process_rotate = False 

DEMO_CIR_RADIUS = const(4)
DEMO_CIR_START_X = const(57) # note, starts in upper left and goes to right
DEMO_CIR_START_Y = const(25) # note, starts in upper left and goes down

DEMO_FALL_DOWN  = const(1)
DEMO_FALL_LEFT  = const(2)
DEMO_FALL_RIGHT = const(3)
DEMO_FALL_UP    = const(4)
demo_falldir = DEMO_FALL_DOWN # provision for accelerometer direction reading

# MAIN ANIMATION SPEED KNOB
demo_step_delay_sec = 0.010 # 0.030 # 100 ms (0.100) looks good # TODO set

demo_map = np.zeros((demo_N_ROWS,demo_N_COLS),dtype=np.int8)
# this is a demo_N_ROWS x demo_N_COLS matrix, mapping locations of grid
#  values are one of the three below, where DEMO_V_EMPTY = 0

DEMO_V_EMPTY = const(0)
DEMO_V_ROCK  = const(1)
DEMO_V_CUBE  = const(2)

demo_disp_circles = list()

demo_display_group_init_size = len(disp_group[DGROUP_2023DAY14])

demo_init()
    
# report free memory ----------------------------------------
print("INFO: Free memory = %d bytes."%gc.mem_free())

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


    elif dgroup_show == DGROUP_2023DAY14:
        if time.monotonic() >= demo_next_step_time:
            
            if USE_ACCEL: 
                # check rotation
                demo_check_rotation()
            
            if not demo_stop: 
                demo_rocks_fall() 
            
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

        elif dgroup_show == DGROUP_2023DAY14:
            print("INFO: transitioning to DEMO screen")
            demo_init()
            demo_next_step_time = time.monotonic() + 2.0*demo_step_delay_sec 

        else:
            print("ERROR: undefined state transition: %d"%dgroup_show)

        time.sleep(0.5) # pause to ignore registering too many clicks
        keys.events.clear()   
        keys.reset()           

    # print("DEBUG: ...BOTTOM OF LOOP")
