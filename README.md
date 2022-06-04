# Robo Arena Team 3 (Die luftigen Kwarkschafe u. der UI Designer)

Python 3.9 + PyQt5 project

#### Requirements:
  - Python3.9 (so far 3.8 & 3.10 work too)
  - PyQt5
  - PyBox2D: `pip3 install box2d box2d-kengz box2d-py`

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
