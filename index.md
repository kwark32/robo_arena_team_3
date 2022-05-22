## Week 4



We started implementing the visuals of the arena with basic tile designs.

The arenas borders will be a ring of walls.

We extended our robot class for more realistic robot movement in the arena.

The robots do now have:

  - current acceleration
  - current rotataional acceleration
  - maximum acceleration
  - maximum rotational acceleration
  - speed in driving direction and turning speed

Environmental variables like the maximum acceleration and the maximum rotational acceleration might be adjustable in the game settings later.
The movement input keys remain w,a,s and d with w -> forward, s -> backward, a -> turn left, d -> turn right.

We instantiated four non-player robots and placed them at different positions in the arena.
For now they just move in circles.

![Main menu](/Arena_mit_4_Bots_und_Hintergrund.png)

## Week 3

How the game could be structured:

Main menu

  - Singleplayer
  - Multiplayer (2players on one keyboard, wasd, arrow keys,...)
  - Settings (general movement speed, robot health, damage,...)
  - Quit game

In-game

  - Full map shown on screen
  - Different textures for tiles
  - Countdown to start
  - Exit on esc

Sketch how the main menu could look:
  
![Main menu](/sketches/main-menu.png)

One style of how the arena could look:

![Map sketch 1](/sketches/map-kevin.png)

And another possible style of the arena/map:

![Map sketch 2](/sketches/map-johannes.png)

We created a class to represent the arena. (See main.py)

We added code to draw the arena. (See arena.py)

We also created a robot class and code to draw and move the robot. (See robot.py)

## Week 2

We created the repository and Github.io pages and invited all team members and the tutors.

After that we created a program with an empty window and added the flake8 test workflow.

![Empty test window](/main-window.png)

After opening a pull request, the check ran fine and another team member could comment/review, as seen in the last two screenshots.

![Empty test window](/pr-review-test-details.png)

![Empty test window](/flake8-details.png)
