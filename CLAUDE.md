# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-script robot control program for a LEGO MINDSTORMS EV3 brick running
[ev3dev](https://www.ev3dev.org/). `demo.py` drives a two-motor tank chassis
forward until an ultrasonic sensor sees an obstacle, then backs up and turns a
random direction.

Hardware wiring is encoded in the constants at the top of `demo.py`: large
motors on `OUTPUT_A`/`OUTPUT_B`, ultrasonic sensor on `INPUT_1`.

## The code does not run on the development machine

There is no `ev3dev2` module and no `/sys/class/tacho-motor` here. Anything
beyond a syntax check has to happen on the brick. Do not claim a change is
tested unless it was run there.

Local verification is limited to:

```sh
python3 -c "import ast; ast.parse(open('demo.py').read())"
```

There is no build, no linter config, and no test suite in this repository.

## Deploying to the brick

The brick is reachable over a Bluetooth PAN link as the ssh alias `ev3`
(defined in `~/.ssh/config`, not in this repo). Deploy target is
`/home/robot/ev3-designated-driver/`.

VS Code with Remote-SSH is the recommended workflow for this project and edits
files on the brick directly. The `rsync` loop below is what this particular
setup uses because it is terminal-based — treat it as one option, not the
prescribed one.

```sh
# sync on every save
printf '%s\n' *.py | entr -c rsync -avz ./*.py ev3:/home/robot/ev3-designated-driver/

# run it
ssh -t ev3 'cd ev3-designated-driver && ./demo.py'
```

Two constraints worth knowing before writing sync commands:

- Use a shell glob with `printf`, not `ls`, to feed `entr`. The `ls` alias on
  this machine forces colour even when piped, and the ANSI escapes end up
  inside the filenames `entr` tries to stat.
- The brick runs rsync **3.1.2**, so `--mkpath` (3.2.3+) fails on the remote
  side even though the local rsync accepts it. Create destination directories
  with a separate `ssh ev3 mkdir -p`.

`cmd.txt` is a gitignored scratch file holding these commands.

## Startup cost dominates

The brick is a 300 MHz ARM9 with 64 MB of RAM. Import time, not execution
speed, is what makes the script feel slow — `ev3dev2.display` and
`ev3dev2.fonts` pull in PIL and cost seconds. Do not import them unless the
display is genuinely used. Profile with `python3 -X importtime demo.py` on the
brick, not locally.

For the same reason, rewriting in C is not the lever it looks like: the loop
sleeps 50 ms per iteration and the ultrasonic sensor only samples every
~30–60 ms, so the bottleneck is hardware and sysfs I/O rather than language.

## Turn geometry

`turn_degrees()` converts a desired robot rotation into motor degrees for a
spin turn. The wheel diameter cancels against the arc length, leaving:

```
motor_degrees = robot_degrees * axle_track / wheel_diameter
```

`AXLE_TRACK_MM` is an **effective** value calibrated by watching the robot, not
a ruler measurement. The wide tires scrub and pivot inboard of the tread
centre, so the robot turns as if the track were meaningfully smaller than
measured. When turns drift, re-tune `AXLE_TRACK_MM` — every derived angle then
stays consistent. Editing `TURN_DEGREES` directly only fixes the 90° case.
