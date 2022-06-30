## Weeks 7, 8, 9 & 10

We added basic effects to the tiles of the arena such as increased/decreased movement speed and inflicted damage as well as a provisional falling animatien for the hole tile.

We created a provisional arena design. We might implement a world generator later.

In the design the tile types are representet by the following colours for now.

    - brown -> dirt
    - white -> hole
    - black -> wall
    - blue -> water
    - yellow -> fire
    - purple -> portal
    - red -> lava

![Main menu](/robo_arena_arena_design.png)

We created soundtracks for the main menu and settings as well as for the arena.

We implemented online multiplayer mode for the game so now players are able to host and join game sessions.

We added a projectile weapon to the robots so now projectiles can be shot tapping or holding the spacebar.

The robot health is indicated by a healthbar below the player name above the robot.

## Weeks 5 & 6

We have better textures for almost anything now, including the robots (tanks).

With our new scene system, switching between different scenes is very easy, but there is still only the world scene so far.

We also have a basic physics system now, for detecting and solving collisions. For now, it works between robots and walls and also between multiple robots.

For this, PyBox2D is required, which can be installed with pip3 like this:

`pip3 install box2d box2d-kengz`

At this point, our game looks like this (in debug mode all colliders are shown with red outlines):

![Main menu](/neue-textures-und-collision.png)

## Week 4

Maps can now be loaded from a json file, currently automatically loading the default map.

The json format works like this:

- *version*: version of the map protocol, to avoid errors
- *size*: size of the map in tiles (now 25x25)
- *tiles*:
    - *row*:
        - *tile*: type of the tile
        - *count*: number of same tiles at this position in the row
        - ... (more tiles with their count, until the row has reached a length of *size*)
    - *count*: number of the same rows at this position in the columns
    - ... (more rows with their count, until the number of rows has reached *size*)

We started implementing the visuals of the arena with basic tile designs and changed the tile size from 10x10px to 40x40 pixel
(so 25x25 tiles total), because they were so small, we only made textures with 40x40px and had no intent to make anything smaller related to tiles.
It also greatly improves rendering performance

The arenas border will be a ring of walls.

We extended our robot class for more realistic robot movement in the arena.

The robots do now have:

  - current acceleration
  - current rotational acceleration
  - maximum acceleration
  - maximum rotational acceleration
  - speed in driving direction and turning speed

Environmental variables like the maximum acceleration and the maximum rotational acceleration might be adjustable in the game settings later.
The movement input keys remain w, a, s and d with w -> forward, s -> backward, a -> turn left, d -> turn right.

We instantiated four non-player robots and placed them at different positions in the arena.
For now, they just move in circles.

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
