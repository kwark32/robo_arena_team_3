# Robo Arena Team 3 (Die luftigen Kwarkschafe u. der UI Designer)

Python 3.9 + pyqt5 project

Requirements:

    - `pip3 install box2d box2d-kengz`

Game design ideas:
  
  Game Design:
    
    
  
  Arena:
    
    Terrain types:
      
      - normal: metal ground, no modifiers
      
      - wall: made of tyres, impenetrable barrier
      
      - fire: causes fire damage, increases movement speed
      
      - water: if robot is heavily damaged, might cause short circuit damage, greatly reduces movement speed
      
      - earth: reduces movement speed
      
      - hole: causes fall damage, immobilizes for a few seconds
      
      - portal: teleports robot to another portal randomly, random damage or healing and power up
      
      - health tower: slowly regenerates health (team specific)
      
    General:
      
      - 1000x1000px
      
      - 40x40px per tile
      
      - different textures for tiles
      
      - origin (0, 0) upper left corner



Upcoming tasks:

    - design main menu and settings visuals

    - implement main menu and settings

    - add tile effects for fire, water, earth, air and portal tiles

    - implement robot AI for single player mode

To be decided:

    - designing a single map or implementing a map genetrator?

    - robot weapons and their effects?

    - multiplayer on one keyboard or multiple devices with networking?
