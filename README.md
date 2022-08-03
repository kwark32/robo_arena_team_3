# Robo Arena Team 3 (Die luftigen Kwarkbällchen und der UI Designer)

Python 3.9 + PyQt5 project

#### Requirements:
  - Python3.8+ (maybe lower can work too)
  - PyQt5
  - PyBox2D: `pip3 install box2d-py`

#### Project agreements:

We have a maximum line length of 120 chars.<br>
To test your current files on flake8, type<br>
`flake8 . --count --max-line-length=120`<br>
(on Linux & Mac).

Commit messages start with a big letter and are in past tense.

Tasks are assigned and decisions tracked via the Task Project under "Projects"

## Game Design:

### Arena:
    
- Terrain types:
  
  - Ground: metal arena, no modifiers
  
  - Wall: made of tires, impenetrable barrier
  
  - Lava: causes low fire damage, decreases movement speed
  
  - Fire: causes higher fire damage, increases movement speed
  
  - Water: the more a robot is damaged, the more short circuit damage it gets, decreases movement speed
  
  - Earth: decreases movement speed
  
  - Hole: causes fall damage, immobilizes for a few seconds
  
  - Portal: teleports robot to another portal randomly, random damage or healing and power up
  
  - Health tower: slowly regenerates health (team specific)
  
- General:
  
  - 1000x1000px arena and window size
  
  - 40x40px per tile
  
  - different textures for tiles
  
  - origin (0, 0) upper left corner

### Upcoming tasks & Decisions:

See our Task Project page.


Contributions:

kwark32 (Matts):

kweiss1 (Kevin):
- Soundtrack
- Sound Effects
- Main Menu & Settings Graphics
- Menu Layout
- Tiles and Sprites Graphics
- Animations
- UML Class Diagram

airzocker (Felix):
- The Rest (general aspects:)
- Code design/model
- Arena loading
- Robots, Weapons, Bullets
- Physics
- Most drawing
- UI code (not using QT elements)
- Multiplayer (all networking) & Headless server
- Settings with save & load
- Singleplayer game mode ("survival mode", score/highcore etc)
- Health/Name overlay & Multiplayer scoreboard
- Sounds
- Animation code
- Big/Scrolling arena, follow cam & fullscreen/dynamic resolution
