# Advent of Code "Trophy"

# IMPORTS --------------------------------------------------------------------
import board
import displayio
import keypad 
import random
import time
import ulab.numpy as np

from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle

# HELPER FUNCTIONS -----------------------------------------------------------

# convenience function to convert (r,c) coords to linear index for circle array
def cir_lindex(r,c):
    return int( 10*c + r )

# set step count label
def update_label_stepval(sv): # takes in an int
    global label_stepval
    label_stepval.text = "%04d"%sv

# set flash count label
def update_label_flashval(fv): # takes in an int
    global label_flashval
    label_flashval.text = "%06d"%fv

# init demo
# there's not going to be a lot of error handling here...
def init_demo():
    global energy
    global flash_count
    global disp_circles
    global step
    
    # set global variables to initial values
    energy = np.zeros((10,10))
    step = 0
    flash_count = 0

    update_label_stepval(step)
    update_label_flashval(flash_count)

    # read input file or generate random input
    try:
        f = open("aoc2021_day11_init.txt")
        bInitFile = True
        print("reading init file")
    except:
        bInitFile = False
        print("generating random init")

    for ir in range(10):
        if bInitFile:
            line = f.readline()

        for ic in range(10):
            if bInitFile: 
                v = int(line[ic])
            else:
                v = random.randint(0,8)

            energy[ir][ic] = v
            disp_circles[cir_lindex(ir,ic)].fill = colormap[v]
            disp_circles[cir_lindex(ir,ic)].outline = colormap[v]

    if bInitFile:
        f.close()

# find (r,c) indices of "flashing" energy values 
# from AoC 2021 day 11 solution
def find_flashers(octomap):
    (nrows,ncols) = octomap.shape
    
    flashers = set()
    
    for i in range(nrows):
        for j in range(ncols):
            if octomap[i][j] > 9:
                flashers |= {(i,j)}
                
    return flashers


# find "neighbors" and increment energy values 
# from AoC 2021 day 11 solution
def increment_neighbors(octomap,i,j):
    (nrows,ncols) = octomap.shape
    
    if i == 0 and j == 0 : # upper left corner
        octomap[i][j+1] += 1
        octomap[i+1][j] += 1 
        octomap[i+1][j+1] += 1
    elif i == 0 and j == ncols-1: # upper right corner
        octomap[i][j-1] += 1 
        octomap[i+1][j] += 1 
        octomap[i+1][j-1] += 1
    elif i == 0: # top row middle
        octomap[i][j-1] += 1  
        octomap[i][j+1] += 1  
        octomap[i+1][j] += 1
        octomap[i+1][j-1] += 1  
        octomap[i+1][j+1] += 1   
    elif i == nrows-1 and j == 0: # lower left corner
        octomap[i-1][j] += 1 
        octomap[i][j+1] += 1 
        octomap[i-1][j+1] += 1  
    elif i == nrows-1 and j == ncols-1: # lower right corner
        octomap[i-1][j] += 1
        octomap[i][j-1] += 1 
        octomap[i-1][j-1] += 1  
    elif i == nrows-1: # bottom row middle
        octomap[i-1][j] += 1 
        octomap[i][j-1] += 1 
        octomap[i][j+1] += 1 
        octomap[i-1][j-1] += 1  
        octomap[i-1][j+1] += 1  
    elif j == 0: # left middle
        octomap[i-1][j] += 1 
        octomap[i][j+1] += 1 
        octomap[i+1][j] += 1 
        octomap[i-1][j+1] += 1  
        octomap[i+1][j+1] += 1  
    elif j == ncols-1: # right middle
        octomap[i-1][j] += 1 
        octomap[i][j-1] += 1 
        octomap[i+1][j] += 1 
        octomap[i-1][j-1] += 1  
        octomap[i+1][j-1] += 1  
    else: # middle
        octomap[i-1][j] += 1 
        octomap[i][j-1] += 1 
        octomap[i][j+1] += 1 
        octomap[i+1][j] += 1 
        octomap[i-1][j-1] += 1  
        octomap[i-1][j+1] += 1  
        octomap[i+1][j-1] += 1  
        octomap[i+1][j+1] += 1  
    
    return octomap

# copy set function (should work like copy.deepcopy, but for a set)
def copy_set(inset):
    outset = set()

    for e in inset:
        outset.add(e)

    return outset

# SETUP ----------------------------------------------------------------------

# set up some global constants
MAX_CHAR = 20 # max number of text chars that can fit, based on observation

# load font
font = bitmap_font.load_font("fonts/SourceCodePro-subset_32_126-10pt.bdf", 
                             displayio.Bitmap)

# display group setup
disp_group = list()
disp_group.append(displayio.Group()) # disp_group[0] for main leaderboard
disp_group.append(displayio.Group()) # disp_group[1] for first-to-50 stars
disp_group.append(displayio.Group()) # disp_group[2] for 2021 day11 demo
DGROUP_MAIN      = const(0)
DGROUP_50STARS   = const(1)
DGROUP_2021DAY11 = const(2)

# build common display group assets - DOES NOT WORK, CANNOT ADD OBJECTS TO MULTIPLE DISPLAY GROUPS
#label_aoc = label.Label(font, text="Advent of Code\n  int y=2021;", color=0x009900)
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
# bg = Rect(0, 0, board.DISPLAY.width, board.DISPLAY.height, fill=0x0f0f23)
# disp_group[DGROUP_MAIN].append(bg)

# AOC label at top
label_aoc = label.Label(font, text="Advent of Code\n   int y=2021;", color=0x009900)
label_aoc.anchor_point = (0.0,0.0) # upper left
label_aoc.anchored_position = (0,0)
disp_group[DGROUP_MAIN].append(label_aoc)

# "VTS Leaderboard"
label_leaderboard = label.Label(font,text="~ VTS Leaderboard ~")
label_leaderboard.anchor_point = (0.5,0.0) # middle top
label_leaderboard.anchored_position = (board.DISPLAY.width/2,45)
disp_group[DGROUP_MAIN].append(label_leaderboard)

# first place
label_first = label.Label(font,text="1st:38* John Moon",scale=1)
label_first.anchor_point = (0.0,0.0) # left top
label_first.anchored_position = (0,60)
disp_group[DGROUP_MAIN].append(label_first)

# second place
label_2nd = label.Label(font,text="2nd:36* Neil Jacklin")
label_2nd.anchor_point = (0.0,0.0) # left top
label_2nd.anchored_position = (0,75)
disp_group[DGROUP_MAIN].append(label_2nd)

# third place
label_3rd = label.Label(font,text="3rd:31*DaveBuscaglia")
label_3rd.anchor_point = (0.0,0.0) # left top
label_3rd.anchored_position = (0,90)
disp_group[DGROUP_MAIN].append(label_3rd)

# build disp_group[DGROUP_50STARS] -----------------------

# # background
# bg = Rect(0, 0, board.DISPLAY.width, board.DISPLAY.height, fill=0x0f0f23)
# disp_group[DGROUP_50STARS].append(bg)

# AOC label at top
label_aoc = label.Label(font, text="Advent of Code\n   int y=2021;", color=0x009900)
label_aoc.anchor_point = (0.0,0.0) # left top
label_aoc.anchored_position = (0,0)
disp_group[DGROUP_50STARS].append(label_aoc)

# "First to 50*"
label_firstto50 = label.Label(font,text="First to 50*")
label_firstto50.anchor_point = (0.5,0.0) # middle top
label_firstto50.anchored_position = (board.DISPLAY.width/2,45)
disp_group[DGROUP_50STARS].append(label_firstto50)

# Name
label_firstto50name = label.Label(font,text="Dave Buscaglia")
label_firstto50name.anchor_point = (0.5,0.0) # middle top
label_firstto50name.anchored_position = (board.DISPLAY.width/2,60)
disp_group[DGROUP_50STARS].append(label_firstto50name)

# Date
label_firstto50date = label.Label(font,text="7 MAR 2022")
label_firstto50date.anchor_point = (0.5,0.0) # middle top
label_firstto50date.anchored_position = (board.DISPLAY.width/2,75)
disp_group[DGROUP_50STARS].append(label_firstto50date)

# stars
# label_stars = label.Label(font,text="0123456789012345678901234",color=0xffff66) # only 20 chars show
label_stars = label.Label(font,text=("*"*MAX_CHAR),color=0xffff66)
label_stars.anchor_point = (0.0,0.0) # middle top
label_stars.anchored_position = (0,100)
disp_group[DGROUP_50STARS].append(label_stars)


# build disp_group[DGROUP_2021DAY11] ---------------------

# # background -- looks bad when display is viewed from the side
# bg = Rect(0, 0, board.DISPLAY.width, board.DISPLAY.height, fill=0x0f0f23)
# disp_group[DGROUP_2021DAY11].append(bg)

# AOC label at top
# label_aoc = label.Label(font, text="Advent of Code\n   int y=2021;", color=0x009900)
label_aoc = label.Label(font, text="AoC 2021      Day 11", color=0x009900)
label_aoc.anchor_point = (0.0,0.0) # left top
label_aoc.anchored_position = (0,0)
disp_group[DGROUP_2021DAY11].append(label_aoc)

# "Step" label
label_step = label.Label(font, text="Step")
label_step.anchor_point = (0.0,0.0) # left top
label_step.anchored_position = (0,27)
disp_group[DGROUP_2021DAY11].append(label_step)

# Step value label
label_stepval = label.Label(font, text="0000")
label_stepval.anchor_point = (0.0,0.0) # left top
label_stepval.anchored_position = (0,42)
disp_group[DGROUP_2021DAY11].append(label_stepval)

# "Flashes" label
labl_flash = label.Label(font, text="Flashes")
labl_flash.anchor_point = (0.0,0.0) # left top
labl_flash.anchored_position = (0,100)
disp_group[DGROUP_2021DAY11].append(labl_flash)

# Flash value label
label_flashval = label.Label(font, text="000000")
label_flashval.anchor_point = (0.0,0.0) # left top
label_flashval.anchored_position = (0,115)
disp_group[DGROUP_2021DAY11].append(label_flashval)

# # "Day 11 Demo" label at the bottom
# label_demo = label.Label(font,text="2021 DAY 11")
# label_demo.anchor_point = (0.5,1.0) # middle bottom
# label_demo.anchored_position = (board.DISPLAY.width/2,board.DISPLAY.height)
# disp_group[DGROUP_2021DAY11].append(label_demo)

# circles (dumbo ocotopi)
# TODO?: replace with sprites?
radius = const(4)
cir_start_x = const(57)
cir_start_y = const(25) 
disp_circles = list()
for ir in range(10):
    for ic in range(10):
        disp_circles.append( Circle( cir_start_x+radius+1+(2*radius+2)*ir,
                                     cir_start_y+radius+1+(2*radius+2)*ic, 
                                     radius,
                                     fill=0x000000, # 0xFFFFFF
                                     stroke=1,
                                     outline=0x000000) )

        disp_group[DGROUP_2021DAY11].append(disp_circles[-1])

# colormap
# need to colors for energy levels 0 - 10 (11 total), 
# and 0 should be dark gray but not black; 10 is the "flashing" color
colormap = list()
colormap.append(0x171717) # 0
colormap.append(0x2E2E2E) # 1
colormap.append(0x464646) # 2
colormap.append(0x5D5D5D) # 3
colormap.append(0x747474) # 4
colormap.append(0x8B8B8B) # 5
colormap.append(0xA2A2A2) # 6
colormap.append(0xB9B9B9) # 7
colormap.append(0xD1D1D1) # 8
colormap.append(0xE8E8E8) # 9
colormap.append(0xFFFFFF) # 10+

# establish global variables for demo and initialize
step = 0
flash_count = 0
step_delay_sec = 1.0
MAX_STEP = const(9999)
init_demo()

# init display
board.DISPLAY.show(disp_group[DGROUP_MAIN])

print("DEBUG: END OF SETUP")

# LOOP -----------------------------------------------------------------------

print("DEBUG: STARTING LOOP...")

dgroup_show = 0

while True:

    # do state actions
    if dgroup_show == DGROUP_MAIN:
        pass
    elif dgroup_show == DGROUP_50STARS:
        pass
    elif dgroup_show == DGROUP_2021DAY11:
        if time.monotonic() >= next_step_time and step <= MAX_STEP:

            # inc step
            step += 1
            update_label_stepval(step)
                    
            # increase energy and update display
            for ir in range(10):
                for ic in range(10):
                    energy[ir][ic] += 1
                    disp_circles[cir_lindex(ir,ic)].fill = colormap[int(min(energy[ir][ic],10))]
                    disp_circles[cir_lindex(ir,ic)].outline = colormap[int(min(energy[ir][ic],10))]
                    if energy[ir][ic] >= 10:
                        disp_circles[cir_lindex(ir,ic)].outline = 0xFFFF66

            time.sleep(0.1) # not ideal, but want some visual delay
            
            # find inital flashers
            flashers = find_flashers(energy)
            
            # propogate flashes and update display
            new_flashers = copy_set(flashers)
            while len(new_flashers) > 0:
                for (ir,ic) in new_flashers:
                    energy = increment_neighbors(energy,ir,ic) 
                    disp_circles[cir_lindex(ir,ic)].fill = colormap[10]
                    disp_circles[cir_lindex(ir,ic)].outline = 0xFFFF66
                time.sleep(0.1) #  not ideal, but want some visual delay
                flashers |= new_flashers
                new_flashers = find_flashers(energy) - flashers 
                    
            # reset energy levels of flashers
            flashed = find_flashers(energy)
            
            if len(flashed) == (100):
                print("ALL FLASHED at step = %d"%(step+1))
                #break
            
            flash_count += len(flashed)

            if len(flashed) > 0:
                time.sleep(0.1) #  not ideal, but want some visual delay

            for (ir,ic) in flashed:
                energy[ir][ic] = 0
                disp_circles[cir_lindex(ir,ic)].fill = colormap[0]
                disp_circles[cir_lindex(ir,ic)].outline = colormap[0]

            update_label_flashval(flash_count)

            # set time for next step increment
            next_step_time = time.monotonic() + step_delay_sec
    else:
        print("undefined state: %d"%dgroup_show)

    # detect button presses
    ke = event = keys.events.get()
    if ke: # if any key press event is happening
        print("detected key press = %d"%ke.key_number)
        dgroup_show = (dgroup_show+1)%len(disp_group)
        board.DISPLAY.show(disp_group[dgroup_show])

        # do state transition stuff, if necessary
        if dgroup_show == DGROUP_MAIN:
            pass
        elif dgroup_show == DGROUP_50STARS:
            pass
        elif dgroup_show == DGROUP_2021DAY11:
            init_demo()
            next_step_time = time.monotonic() + 2*step_delay_sec
        else:
            print("undefined state transition: %d"%dgroup_show)

        time.sleep(0.5) # pause to ignore registering too many clicks
        keys.events.clear()   
        keys.reset()           

    # print("DEBUG: ...BOTTOM OF LOOP")
