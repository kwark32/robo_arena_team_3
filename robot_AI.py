import math

from util import Vector


class RobotAI:
    def __init__(self, robot):
        self.robot = robot
        self.world_sim = robot.world_sim
        self.shortest_path = None
        self.walkable_check = DrivableTileCheck(self.world_sim.arena)

    def update(self, delta_time):
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
            self.shortest_path = astar(self.world_sim.arena.tiles, arena_size,
                                       (start.x, start.y), (end.x, end.y), self.walkable_check)
        # take the shortest path to the closest player
        bearing = 0
        if self.shortest_path is not None:
            target = closest_player.sim_body.position.copy()
            if len(self.shortest_path) >= 2:
                target = Vector(self.shortest_path[1][0], self.shortest_path[1][1])
                target.mult(self.world_sim.arena.tile_size)
                target.add_scalar(self.world_sim.arena.tile_size / 2)
            diff = self.robot.sim_body.position.diff(target)
            bearing = diff.signed_angle() - self.robot.sim_body.rotation
            if bearing <= -math.pi:
                bearing += 2 * math.pi
            robot_stop_dist = ((self.robot.sim_body.ang_velocity ** 2) / self.robot.sim_body.max_ang_accel) / 2
            should_rotate_right = bearing > 0
            if robot_stop_dist >= abs(bearing):
                self.robot.input.right = not should_rotate_right
                self.robot.input.left = should_rotate_right
            else:
                self.robot.input.right = should_rotate_right
                self.robot.input.left = not should_rotate_right
        if bearing < 0.2:
            self.robot.input.up = True
        else:
            self.robot.input.up = False


class WalkableTerrainCheck:
    def is_walkable(self, x, y):
        return False


class DrivableTileCheck(WalkableTerrainCheck):
    def __init__(self, arena):
        self.arena = arena

    def is_walkable(self, x, y):
        tile = self.arena.tiles[y][x]
        blocked = tile.has_collision or tile.name == "lava"
        return not blocked


class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def astar(tiles, arena_size, start, end, walkable_check):

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize open and closed list
    open_list = []
    closed_list = []

    # Add start node
    open_list.append(start_node)

    # check for progress possibility
    progress_possible = True
    last_node = Node()

    # Loop until end found
    while len(open_list) > 0 and progress_possible:

        # Get current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # save current node to track progress
        last_node = Node(current_node.parent, last_node.position)
        last_node.g = current_node.g
        last_node.h = current_node.h
        last_node.f = current_node.f

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found destination
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # Adjacent squares

            # Get node position
            node_position = (
                current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (arena_size[1] - 1) or node_position[0] < 0 or node_position[1] > (
                    arena_size[0] - 1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if not walkable_check.is_walkable(node_position[0], node_position[1]):
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

            # Create f, g, and h values
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

            # check progress
            if current_node == last_node:
                progress_possible = False
