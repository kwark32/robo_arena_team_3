## Robo Arena Overview and Summary

Idea:

Our game was inspired by retro pixelated games.<br>
The sprites and tiles are all pixel art and the soundtrack and sound effects are also 8-bit. 



Main Menu:

The main menu has our Robo Arena logo and 5 buttons: Single Player, Online, Local, Settings and Exit. 

![Summary](/Summary/main_menu.png)

The single player, online and local buttons start an offline, online and local game respectively.<br>
The settings include sliders for the master, sound effects and music volume.

![Summary](/Summary/settings.png)



Gameplay:

The player controls a tank with a turret on top.<br>
The tank is moved with the WASD keys and the mouse is used to aim and shoot the turrets.<br>
On the map there are several enemy tanks which will find and shoot the player.<br>
The enemies use an A*-algorithm to locate and follow the player and avoid different tiles based on their priority.<br>
All robots in the arena (players and AI robots) have 1000HP maximum health and deal 250dmg with a bullet from their tank cannon so it usually takes 4 hits to destroy a robot.<br>
However the health and damage of the robots in the arena can not only be influenced by other robots, but by the tile effects and the power up effects of the arena as well.<br>
The current health of a player is always visually availible to them by the healthbar displayed over their robot.

![Summary](/Summary/gameplay_healthbar.png)

Arena -> Tiles:

There are several different tiles scattered across the map, with the most common being the basic metal ground tile and the wall tile (tires). 

![Summary](/Summary/gameplay.gif)

The metal tile has no effect on the player and can be driven over. 

![Summary](/Summary/metal_tile.png)

The wall tile (tires) block the player from passing over them, which gives the map a border that the tanks cannot pass through and also some cover to hide behind. Bullets cannot pass through the wall tiles (tires) and they cannot be destroyed. 

![Summary](/Summary/tires.png)

There are 6 special tiles on the map. The fire tile inflicts rather low damage and increases the movement speed of a robot while driven over. 

![Summary](/Summary/fire.gif)

The water tile inflicts short circuit damage to robots when their health is below 50% of the maximium health (=500). It also decreases movement speed by 50%. 

![Summary](/Summary/water_tile.png)

The lava tile causes high melting damage and greatly decreases movement speed by 75%. 

![Summary](/Summary/lava_tile.png)

The earth tile decreases movement speed by 25% and has no damage effect. 

![Summary](/Summary/dirt_tile.png)

The hole tile gives the tanks fall damage wich results in immobilisation and an instant destruct after a short "falling animation". 

![Summary](/Summary/hole_tile.png)

The portal tile teleports the robots to a random portal of the other colour and inflicts rather low damage of 100 so the player cant just keep teleporting around to get away and survive. 

![Summary](/Summary/portal_blue.gif)

![Summary](/Summary/portal_purple.gif)

Arena -> Power ups:

In the arena 4 different types of collectable power ups spawn that apply the following effects to a robot when picked up.

![Main menu](/power_ups_in_arena.png)

The speed power up (lightning) increases the robots movement speed by 100% for 5 seconds (additive).<br>
The health power up (heart) restores 250HP.<br>
The damage reduction power up (shield) makes the robot take 50% less damage for 10 seconds (multipicative).<br>
The increased damage power up (Bullet) makes the robot inflict 100% more damage for 10 seconds (multiplicative).<br>
Power ups will only spawn on ground tiles and their effects are stackable.

Arena -> Animations:

When a robot loses all its health, it explodes (short animation). In singleplayer mode this means game over, the score is saved. In multiplayer mode the players respawn after a few seconds.

![Summary](/Summary/explosion.gif)

As seen further up in the report fire and portal tiles have constant animations.

Arena -> Generation:

The arena was generated using our png-to-arena converter.<br>
It allowed us to easily design arenas in image editors like gimp and have them translated to actual arenas.<br>
The png file we used to generate the latest version of the arena for example looks like this:

![Main menu](/latest_arena_png.png)

General Class Diagram:

![Summary](/Summary/class.png)




## Weeks 11 & 12

We created a better robot-AI.

The robots do now have pathfinding to their target (closest player) using an A*-Algorithm.

The pathfinding avoids different types of tiles based on their priority and looks for alternate paths.

The robots do also shoot now.

![Main menu](/Pathfinding.png)

We also added new fire and portal textures.

![Main menu](/new_tile_textures.png)

## Soundtrack and Textures Tutorial

In this little excursion the creation of the soundtrack, sound effects and textures will be explained. For the sounds the software Ableton Live 11 was used. For the sound effects, the sample library Titanomachy was used, which is a cinematic sound effects library. To fit it better to our game, the built-in Ableton effect Redux was used, which degrades the sound and gives it that 8-Bit feel with the right settings. 

![Tutorial](/TutorialPictures/redux.png)

The tank driving sound also uses the spectral resonator effect, which gives it a cold metallic sound.

![Tutorial](/TutorialPictures/spectral.png)

For the soundtrack, the songs use basic drums, synths, basses and arpeggios. 

![Tutorial](/TutorialPictures/soundtrack_1.png)

![Tutorial](/TutorialPictures/soundtrack_2.png)

On most of the sound channels, the redux effect was utilized again to better fit it to the atmosphere of the game.

For the textures, the website pixilart.com was used. It is a website specifically for making pixel art, which is the art direction we wanted to go in. For some of the textures, a simple real life or similar reference was used to visualize the texture and to give a starting point. 

![Tutorial](/TutorialPictures/pixilart.png)

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

We implemented local and online multiplayer mode for the game so now players are able to host and join game sessions.

![Main menu](/local_multiplayer.png)

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
