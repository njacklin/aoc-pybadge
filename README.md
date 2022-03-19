# aoc-pybadge

This is CircuitPython code for making an Advent of Code "trophy" out of an 
[Adafruit PyBadge](https://www.adafruit.com/product/4623).  

For more information on the Advent of Code, visit the website [https://adventofcode.com](https://adventofcode.com).

## code.py
__This file must be present on the root of the CIRCUITPY drive of the PyBadge for it to function properly.__

This is main python code.  This file is automatically executed on startup.

To understand this file, you will have to be familiar with CircuitPython, which
is an Adafruit adaptation of MicroPython.  Basically, this code creates three
screens (display groups) and rotates through them when a hardware button is 
pressed. The three screens are (1) leaderboard, (2) first-to-50 stars, and 
(3) a demo of the AoC 2021 day 11 challenge (dumbo octopus).

## fonts
__This folder must be present on the root of the CIRCUITPY drive of the PyBadge for it to function properly.__

Contains a custom bitmapped font file.  The font is based on Google Fonts 
["Source Code Pro"](https://fonts.google.com/specimen/Source+Code+Pro).
The command-line tool otf2bdf was used to create this font.  A version for 
Mac OS is included in the "font-making" folder of this repo, and  the tool is
also available for most other operating systems.

## font-making
Tools for making bitmapped fonts.  See above.

This folder does not need to be copied to the PyBadge.  In fact it is discouraged because space is very limited.

## lib
__This folder must be present on the root of the CIRCUITPY drive of the PyBadge for it to function properly.__

This folder contains the runtime libraries needed by code.py which are not in 
the standard CircuitPython distribution.

## updates
This folder contains the binary UF2 images for CircuitPython and the bootloader
which was used for this project.  Any version of CircuitPython >= 7.0.0 should 
work.  Refer to the CircuitPython documentation for a description of the boot
loader, but for most users it is recommended to update the boot loader to the 
latest version availble.

These files must be loaded when the PyBadge is in bootloader mode.  It is strongly recommended
to read the CircuitPython documentation to avoid bricking your board.  TLDR: push the RESET
button on the of the PyBadge quickly twice to enter bootloader mode.

