# graphicsGridworldDisplay.py
# ---------------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import functools
from collections import defaultdict
from mdp.blockworld.displayutils import *


class User:
    def __init__(self, actionFunction):
        self.action = None
        self.__func = actionFunction

    def getUserAction(self, state):
        """
        Get an action from the user (rather than the agent).

        Used for debugging and lecture demos.
        """
        from mdp.blockworld import displayutils
        self.action = None
        while True:
            keys = displayutils.wait_for_keys()
            if 'Up' in keys: self.action = 'up'
            if 'Down' in keys: self.action = 'down'
            if 'Left' in keys: self.action = 'left'
            if 'Right' in keys: self.action = 'right'
            if 'q' in keys: sys.exit(0)
            if self.action is None: continue
            break
        actions = self.__func[state.get_state()]
        if self.action not in actions:
            self.action = actions[0]

    def act(self, state):
        self.getUserAction(state)
        return self.action


class GridworldDisplay:
    def __init__(self, gridworld, size=120, speed=1.0):
        self.blockworld = gridworld
        self.size = size
        self.speed = speed

    def start(self):
        setup(self.blockworld, size=self.size)

    def pause(self):
        wait_for_keys()

    def displayValues(self, agent, currentState=None, message='Agent Values'):
        values = defaultdict(float)
        policy = {}
        states = self.blockworld.get_states()
        for state in states:
            values[state.get_state()] = agent.get_value(state.get_state())
            policy[state.get_state()] = agent.get_policy(state.get_state())
        drawValues(self.blockworld, values, policy, currentState, message)
        sleep(0.05 / self.speed)

    def displayNullValues(self, currentState=None, message=''):
        values = defaultdict(float)
        # policy = {}
        states = self.blockworld.get_states()
        for state in states:
            values[state] = 0.0
            # policy[state] = agent.getPolicy(state)
        drawNullValues(self.blockworld, currentState, '')
        # drawValues(self.gridworld, values, policy, currentState, message)
        sleep(0.05 / self.speed)

    def displayQValues(self, agent, currentState=None, message='Agent Q-Values'):
        qValues = defaultdict(float)
        states = self.blockworld.get_states()
        for state in states:
            for action in self.blockworld.get_actions():
                qValues[(state, action)] = agent.get_q_val(state, action)
        drawQValues(self.blockworld, qValues, currentState, message)
        sleep(0.05 / self.speed)


BACKGROUND_COLOR = format_color(0, 0, 0)
EDGE_COLOR = format_color(1, 1, 1)
OBSTACLE_COLOR = format_color(0.5, 0.5, 0.5)
TEXT_COLOR = format_color(1, 1, 1)
MUTED_TEXT_COLOR = format_color(0.7, 0.7, 0.7)
LOCATION_COLOR = format_color(0, 0, 1)

WINDOW_SIZE = -1
GRID_SIZE = -1
GRID_HEIGHT = -1
MARGIN = -1


def setup(blockworld, title="Blockworld Display", size=120):
    global GRID_SIZE, MARGIN, GRID_HEIGHT
    block = blockworld.blocks
    WINDOW_SIZE = size
    GRID_SIZE = size
    GRID_HEIGHT = blockworld.height
    MARGIN = GRID_SIZE * 0.75
    screen_width = (blockworld.width - 1) * GRID_SIZE + MARGIN * 2
    screen_height = (blockworld.height - 0.5) * GRID_SIZE + MARGIN * 2

    begin_graphics(screen_width,
                   screen_height,
                   BACKGROUND_COLOR, title=title)


def drawNullValues(gridworld, currentState=None, message=''):
    grid = gridworld.grid
    blank()
    for x in range(grid.width):
        for y in range(grid.height):
            state = (x, y)
            gridType = grid[x][y]
            isExit = (str(gridType) != gridType)
            isCurrent = (currentState == state)
            if gridType == '#':
                drawSquare(x, y, 0, 0, 0, None, None, True, False, isCurrent)
            else:
                drawNullSquare(gridworld.grid, x, y, False, isExit, isCurrent)
    pos = to_screen(((grid.width - 1.0) / 2.0, - 0.8))
    text(pos, TEXT_COLOR, message, "Courier", -32, "bold", "c")


def drawValues(gridworld, values, policy, currentState=None, message='State Values'):
    grid = gridworld.grid
    blank()
    valueList = [values[state.get_state()] for state in gridworld.get_states()] + [0.0]
    minValue = min(valueList)
    maxValue = max(valueList)
    for x in range(gridworld.width):
        for y in range(gridworld.height):
            state = gridworld.get_state(x, y)
            gridType = grid[x][y][0]
            isExit = state.is_terminal()
            if currentState is not None:
                isCurrent = (currentState == state)
            else:
                isCurrent = None
            if gridType == '#':
                drawSquare(x, y, 0, 0, 0, None, None, True, False, isCurrent)
            else:
                if isExit:
                    if (x, y) == gridworld.goal_loc:
                        value = gridworld.get_goal_reward()
                    elif (x, y) in gridworld.holes:
                        value = -gridworld.get_hole_cost()
                    else:
                        value = 0 - gridworld.get_step_cost()
                    action = 'exit'
                    valString = '%.2f' % value
                    drawSquare(x, y, value, minValue, maxValue, valString, action, False, isExit, isCurrent)
                else:
                    value = values[state.get_state()]
                    action = policy[state.get_state()]
                    valString = '%.2f' % value
                    drawSquare(x, y, value, minValue, maxValue, valString, action, False, isExit, isCurrent)
    pos = to_screen(((gridworld.width - 1.0) / 2.0, - 0.8))
    text(pos, TEXT_COLOR, message, "Courier", -32, "bold", "c")


def drawQValues(blockworld, qValues, currentState=None, message='State-Action Q-Values'):
    block = blockworld.blocks
    blank()
    stateCrossActions = [[(state, action) for action in blockworld.get_actions()] for state in
                         blockworld.get_states()]
    qStates = functools.reduce(lambda x, y: x + y, stateCrossActions, [])
    qValueList = [qValues[(state, action)] for state, action in qStates] + [0.0]
    minValue = min(qValueList)
    maxValue = max(qValueList)
    for x in range(blockworld.width):
        for y in range(blockworld.height):
            state = blockworld.get_state(x, y)
            gridType = block[x][y]
            isExit = state.is_terminal()
            # print(currentState, state)
            if currentState is not None:
                isCurrent = (currentState == state)
            else:
                isCurrent = None
            actions = blockworld.get_actions()
            if actions is None or len(actions) == 0:
                actions = [None]
            bestQ = max([qValues[(state, action)] for action in actions])
            bestActions = [action for action in actions if qValues[(state, action)] == bestQ]

            q = defaultdict(float)
            valStrings = {}
            for action in actions:
                v = qValues[(state, action)]
                q[action] += v
                valStrings[action] = '%.2f' % v
            if gridType == '#':
                drawSquare(x, y, 0, 0, 0, None, None, True, False, isCurrent)
            elif isExit:
                if (x, y) == blockworld.goal_loc:
                    value = blockworld.get_goal_reward()
                elif (x, y) in blockworld.holes:
                    value = -blockworld.get_hole_cost()
                else:
                    value = 0 - blockworld.get_step_cost()
                action = 'exit'
                valString = '%.2f' % value
                # print(type(value))
                drawSquare(x, y, maxValue, minValue, maxValue, valString, action, False, isExit, isCurrent)
            else:
                drawSquareQ(x, y, q, minValue, maxValue, valStrings, actions, isCurrent)
            # print("'", gridType, "'", end="")
        # print()
    pos = to_screen(((blockworld.width - 1.0) / 2.0, - 0.8))
    text(pos, TEXT_COLOR, message, "Courier", -32, "bold", "c")


def blank():
    clear_screen()


def drawNullSquare(grid, x, y, isObstacle, isTerminal, isCurrent):
    square_color = getColor(0, -1, 1)

    if isObstacle:
        square_color = OBSTACLE_COLOR

    (screen_x, screen_y) = to_screen((x, y))
    square((screen_x, screen_y),
           0.5 * GRID_SIZE,
           color=square_color,
           filled=1,
           width=1)

    square((screen_x, screen_y),
           0.5 * GRID_SIZE,
           color=EDGE_COLOR,
           filled=0,
           width=3)

    if isTerminal and not isObstacle:
        square((screen_x, screen_y),
               0.4 * GRID_SIZE,
               color=EDGE_COLOR,
               filled=0,
               width=2)
        text((screen_x, screen_y),
             TEXT_COLOR,
             str(grid[x][y]),
             "Courier", -24, "bold", "c")

    text_color = TEXT_COLOR

    if not isObstacle and isCurrent:
        circle((screen_x, screen_y), 0.1 * GRID_SIZE, LOCATION_COLOR, fillColor=LOCATION_COLOR)

    # if not isObstacle:
    #   text( (screen_x, screen_y), text_color, valStr, "Courier", 24, "bold", "c")


def drawSquare(x, y, val, min, max, valStr, action, isObstacle, isTerminal, isCurrent):
    square_color = getColor(val, min, max)

    if isObstacle:
        square_color = OBSTACLE_COLOR

    (screen_x, screen_y) = to_screen((x, y))
    square((screen_x, screen_y),
           0.5 * GRID_SIZE,
           color=square_color,
           filled=1,
           width=1)
    square((screen_x, screen_y),
           0.5 * GRID_SIZE,
           color=EDGE_COLOR,
           filled=0,
           width=3)
    if isTerminal and not isObstacle:
        square((screen_x, screen_y),
               0.4 * GRID_SIZE,
               color=EDGE_COLOR,
               filled=0,
               width=2)

    if action == 'up':
        polygon([(screen_x, screen_y - 0.45 * GRID_SIZE), (screen_x + 0.05 * GRID_SIZE, screen_y - 0.40 * GRID_SIZE),
                 (screen_x - 0.05 * GRID_SIZE, screen_y - 0.40 * GRID_SIZE)], EDGE_COLOR, filled=1, smoothed=False)
    if action == 'down':
        polygon([(screen_x, screen_y + 0.45 * GRID_SIZE), (screen_x + 0.05 * GRID_SIZE, screen_y + 0.40 * GRID_SIZE),
                 (screen_x - 0.05 * GRID_SIZE, screen_y + 0.40 * GRID_SIZE)], EDGE_COLOR, filled=1, smoothed=False)
    if action == 'left':
        polygon([(screen_x - 0.45 * GRID_SIZE, screen_y), (screen_x - 0.4 * GRID_SIZE, screen_y + 0.05 * GRID_SIZE),
                 (screen_x - 0.4 * GRID_SIZE, screen_y - 0.05 * GRID_SIZE)], EDGE_COLOR, filled=1, smoothed=False)
    if action == 'right':
        polygon([(screen_x + 0.45 * GRID_SIZE, screen_y), (screen_x + 0.4 * GRID_SIZE, screen_y + 0.05 * GRID_SIZE),
                 (screen_x + 0.4 * GRID_SIZE, screen_y - 0.05 * GRID_SIZE)], EDGE_COLOR, filled=1, smoothed=False)

    text_color = TEXT_COLOR

    if not isObstacle and isCurrent:
        circle((screen_x, screen_y), 0.1 * GRID_SIZE, outlineColor=LOCATION_COLOR, fillColor=LOCATION_COLOR)

    if not isObstacle:
        text((screen_x, screen_y), text_color, valStr, "Courier", -30, "bold", "c")


def drawSquareQ(x, y, qVals, minVal, maxVal, valStrs, bestActions, isCurrent):
    (screen_x, screen_y) = to_screen((x, y))

    center = (screen_x, screen_y)
    nw = (screen_x - 0.5 * GRID_SIZE, screen_y - 0.5 * GRID_SIZE)
    ne = (screen_x + 0.5 * GRID_SIZE, screen_y - 0.5 * GRID_SIZE)
    se = (screen_x + 0.5 * GRID_SIZE, screen_y + 0.5 * GRID_SIZE)
    sw = (screen_x - 0.5 * GRID_SIZE, screen_y + 0.5 * GRID_SIZE)
    n = (screen_x, screen_y - 0.5 * GRID_SIZE + 5)
    s = (screen_x, screen_y + 0.5 * GRID_SIZE - 5)
    w = (screen_x - 0.5 * GRID_SIZE + 5, screen_y)
    e = (screen_x + 0.5 * GRID_SIZE - 5, screen_y)

    actions = qVals.keys()
    for action in actions:

        wedge_color = getColor(qVals[action], minVal, maxVal)

        if action == 'up':
            polygon((center, nw, ne), wedge_color, filled=1, smoothed=False)
            # text(n, text_color, valStr, "Courier", 8, "bold", "n")
        if action == 'down':
            polygon((center, sw, se), wedge_color, filled=1, smoothed=False)
            # text(s, text_color, valStr, "Courier", 8, "bold", "s")
        if action == 'right':
            polygon((center, ne, se), wedge_color, filled=1, smoothed=False)
            # text(e, text_color, valStr, "Courier", 8, "bold", "e")
        if action == 'left':
            polygon((center, nw, sw), wedge_color, filled=1, smoothed=False)
            # text(w, text_color, valStr, "Courier", 8, "bold", "w")

    square((screen_x, screen_y),
           0.5 * GRID_SIZE,
           color=EDGE_COLOR,
           filled=0,
           width=3)
    line(ne, sw, color=EDGE_COLOR)
    line(nw, se, color=EDGE_COLOR)

    if isCurrent:
        circle((screen_x, screen_y), 0.1 * GRID_SIZE, LOCATION_COLOR, fillColor=LOCATION_COLOR)

    for action in actions:
        text_color = TEXT_COLOR
        if qVals[action] < max(qVals.values()):
            text_color = MUTED_TEXT_COLOR
        valStr = ""
        if action in valStrs:
            valStr = valStrs[action]
        h = -20
        if action == 'up':
            # polygon( (center, nw, ne), wedge_color, filled = 1, smooth = 0)
            text(n, text_color, valStr, "Courier", h, "bold", "n")
        if action == 'down':
            # polygon( (center, sw, se), wedge_color, filled = 1, smooth = 0)
            text(s, text_color, valStr, "Courier", h, "bold", "s")
        if action == 'right':
            # polygon( (center, ne, se), wedge_color, filled = 1, smooth = 0)
            text(e, text_color, valStr, "Courier", h, "bold", "e")
        if action == 'left':
            # polygon( (center, nw, sw), wedge_color, filled = 1, smooth = 0)
            text(w, text_color, valStr, "Courier", h, "bold", "w")


def getColor(val, minVal, maxVal):
    red, green = 0.0, 0.0
    if val < 0 and minVal < 0:
        red = val * 0.65 / minVal
    if val > 0 and maxVal > 0:
        green = val * 0.65 / maxVal
    return format_color(red, green, 0.0)


def square(pos, size, color, filled, width):
    x, y = pos
    dx, dy = size, size
    return polygon([(x - dx, y - dy), (x - dx, y + dy), (x + dx, y + dy), (x + dx, y - dy)], outlineColor=color,
                   fillColor=color, filled=filled, width=width, smoothed=False)


def to_screen(point):
    (game_x, game_y) = point
    x = game_x * GRID_SIZE + MARGIN
    y = (GRID_HEIGHT - game_y - 1) * GRID_SIZE + MARGIN
    return x, y


def to_grid(point):
    (x, y) = point
    x = int((y - MARGIN + GRID_SIZE * 0.5) / GRID_SIZE)
    y = int((x - MARGIN + GRID_SIZE * 0.5) / GRID_SIZE)
    print(point, "-->", (x, y))
    return x, y
