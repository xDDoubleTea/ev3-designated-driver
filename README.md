# EV3 Designated Driver

A self-driving robot built on a LEGO MINDSTORMS EV3 brick running
[ev3dev](https://www.ev3dev.org/), programmed in Python with
[`python-ev3dev2`](https://python-ev3dev.readthedocs.io/).

## Current state

`demo.py` is a working obstacle-avoidance loop:

- Drive forward continuously on a two-motor tank chassis.
- Poll an ultrasonic sensor each cycle. When it reads under 25 cm, stop, pause,
  reverse for a second, then spin in place toward a randomly chosen direction.
- Ctrl-C stops the motors rather than leaving the robot driving.

Turn angles are derived from the chassis geometry instead of being hardcoded.
For a spin turn the wheel diameter cancels against the arc each wheel traces,
which reduces to:

```
motor_degrees = robot_degrees * axle_track / wheel_diameter
```

`turn_degrees()` implements this, so a single `AXLE_TRACK_MM` constant
calibrates every angle rather than just the 90° case.

### Hardware

| Port | Device |
| --- | --- |
| `OUTPUT_A`, `OUTPUT_B` | Large motors, left and right |
| `INPUT_1` | Ultrasonic sensor, forward facing |

Wheels are 81.6 mm in diameter.

### Calibration

`AXLE_TRACK_MM` is an *effective* track width, calibrated by watching the robot
turn — not a ruler measurement. The tires are wide, so they scrub sideways
through a spin turn and pivot inboard of the tread centre; the robot behaves as
if its track were noticeably narrower than measured. If turns start drifting,
re-tune that one constant and every derived angle follows.

## Running it

The script must run on the brick — it needs `ev3dev2` and the sysfs device
interface, so it cannot be tested on a development machine.

Copy it across and run:

```sh
rsync -avz demo.py ev3:/home/robot/ev3-designated-driver/
ssh -t ev3 'cd ev3-designated-driver && ./demo.py'
```

`ev3` here is an ssh host alias for the brick. This project develops over a
Bluetooth PAN link, but anything that gives you ssh — USB, Wi-Fi dongle,
Ethernet — works the same way.

**The recommended workflow is VS Code with the Remote-SSH extension**, which
edits files directly on the brick and gives you an integrated terminal there —
no sync step to think about at all. The `rsync` commands below exist because
this project is developed from a terminal-based setup, not because they're the
better path.

To re-sync automatically on every save, with [`entr`](https://eradman.com/entrproject/):

```sh
printf '%s\n' *.py | entr -c rsync -avz ./*.py ev3:/home/robot/ev3-designated-driver/
```

Two things that bite on this hardware:

- **Keep imports lean.** The brick is a 300 MHz ARM9 with 64 MB of RAM, and
  startup time is dominated by imports rather than execution.
  `ev3dev2.display` and `ev3dev2.fonts` pull in PIL and cost seconds — don't
  import them unless the screen is actually used.
- **The brick ships rsync 3.1.2**, so `--mkpath` fails on the remote side even
  when the local rsync supports it. Create the destination directory ahead of
  time with `ssh ev3 mkdir -p`.

## Planned: line following

The next feature is a line follower driven by **two colour sensors in
`COL-REFLECT` mode**, with motor power adjusted in real time from their
readings.

Two sensors straddling the line give a signed error from the difference between
them, rather than the single-sensor edge-following approach that can only track
one side of a line. The intended shape:

- Read both reflected-light values each cycle.
- Compute the error as the difference between them — zero when the line sits
  centred between the sensors, signed toward whichever side has drifted onto
  it.
- Apply that error as a differential to the two motor powers, steering
  continuously instead of in discrete corrections.

Both sensors will need calibrating against the actual surface first: reflected
light readings depend on the mat, the lighting, and the sensor's ride height,
so raw values should be normalised between measured white and black references
before being compared.

Port assignments for the colour sensors are not fixed yet.

## Licence

GNU General Public License v2 — see [LICENSE](LICENSE).
