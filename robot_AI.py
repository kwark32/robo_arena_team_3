# imports


class RobotAI:
    def __init__(self, robot):
        self.robot = robot
        self.world_sim = robot.world_sim
        self.first = True

    def update(self, delta_time):
        if not self.first:
            return
        self.first = False
        # find the closest player
        shortest_distance = 1000000
        closest_player = None
        for other_robot in self.world_sim.robots:
            if not other_robot.has_ai:
                current_distance = self.robot.sim_body.position.dist(other_robot.sim_body.position)
                if current_distance < shortest_distance:
                    closest_player = other_robot
                    shortest_distance = current_distance
        # get the shortest path to the closest player
        if closest_player is not None:
            arena_size = self.world_sim.arena.tile_count, self.world_sim.arena.tile_count
            start = self.robot.sim_body.position.copy()
            start.div(self.robot.world_sim.arena.tile_size)
            start.floor()
            end = closest_player.sim_body.position.copy()
            end.div(self.robot.world_sim.arena.tile_size)
            end.floor()
            # TODO: replace with vector.as_tuple
            shortest_path = astar(self.world_sim.arena.tiles, arena_size, (start.x, start.y), (end.x, end.y))
            for node in shortest_path:
                print(node)
        # take the shortest path to the closest player


class Node:
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def astar(tiles, arena_size, start, end):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""

    print((arena_size, start, end))

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1),
                             (1, 1)]:  # Adjacent squares

            # Get node position
            node_position = (
                current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (arena_size[1] - 1) or node_position[0] < 0 or node_position[1] > (
                    arena_size[0] - 1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            print(tiles[node_position[1]][node_position[0]].name)
            if tiles[node_position[1]][node_position[0]].has_collision:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + (
                    (child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.append(child)
