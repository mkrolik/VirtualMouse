import time
import glob
from curses import wrapper, curs_set, newwin, echo, nocbreak, endwin
import random
from collections import defaultdict
from ConsoleColor import gradient, set_bg_color


class Maze:
    empty_spaces = [" ", "S", "G"]

    def __init__(self, sleep_time=0.1) -> None:
        self.sleep_time = sleep_time

    def load(self, filename):
        self.maze_filename = filename
        maze = []
        with open(filename, "r") as mfile:
            lines = mfile.readlines()
            for line in lines:
                # line = line.replace('G','🧀')
                maze.append([char for char in line])
        self.maze = maze
        self.start = self.starting_location()
        self.goals = self.goal_locations()
        self.move_count = 0
        self.turn_count = 0
        self.quit = False
        self.won = False
        self.run_number = 1
        self.max_run_number = 2

    def starting_location(self):
        for row in range(len(self.maze)):
            for col in range(len(self.maze[row])):
                if self.maze[row][col] == "S":
                    return (row, col)
        print(
            "Bad/training maze. No starting S found. Probably no cheese either. Defaulting 31,2 as starting position."
        )
        return (31, 2)

    def goal_locations(self):
        goals = []
        for row in range(len(self.maze)):
            for col in range(len(self.maze[row])):
                if self.maze[row][col] == "G":
                    goals.append((row, col))
        if len(goals) == 0:
            print(
                "Bad/training maze. No goals G found. Probably no cheese either. Defaulting goal positions."
            )
            return [(15, 30), (15, 34), (17, 30), (17, 34)]
        return goals

    def __repr__(self) -> str:
        str = ""
        for line in self.maze:
            str += "".join(line)
        return str

    def can_move_up(self, step=1):
        return (
            self.mouse.y > step
            and self.maze[self.mouse.y - step][self.mouse.x] in Maze.empty_spaces
            and self.maze[self.mouse.y - (step - 1)][self.mouse.x] in Maze.empty_spaces
        )

    def can_move_down(self, step=1):
        return (
            self.mouse.y < len(self.maze) - step
            and self.maze[self.mouse.y + step][self.mouse.x] in Maze.empty_spaces
            and self.maze[self.mouse.y + step - 1][self.mouse.x] in Maze.empty_spaces
        )

    def can_move_left(self, step=2):
        return (
            self.mouse.x > step
            and self.maze[self.mouse.y][self.mouse.x - step] in Maze.empty_spaces
            and self.maze[self.mouse.y][self.mouse.x - (step - 1)] in Maze.empty_spaces
        )

    def can_move_right(self, step=2):
        return (
            self.mouse.x < len(self.maze[self.mouse.y]) - step
            and self.maze[self.mouse.y][self.mouse.x + step] in Maze.empty_spaces
            and self.maze[self.mouse.y][self.mouse.x + step - 1] in Maze.empty_spaces
        )

    def make_move(self, y_step=0, x_step=0, dir=None):
        self.mouse.old_y = self.mouse.y
        self.mouse.old_x = self.mouse.x
        self.mouse.old_direction = self.mouse.direction
        self.mouse.y += y_step
        self.mouse.x += x_step
        self.mouse.direction = dir
        self.move_count += 1
        if self.mouse.direction != self.mouse.old_direction:
            self.turn_count += 1
        self.mouse.position = (self.mouse.y - self.start[0], self.mouse.x // 2 - self.start[1])
        self.draw_mouse()

    def move_up(self, step=1):
        if self.can_move_up(step):
            self.make_move(0 - step, 0, "up")

    def move_down(self, step=1):
        if self.can_move_down(step):
            self.make_move(step, 0, "down")

    def move_left(self, step=2):
        if self.can_move_left(step):
            self.make_move(0, 0 - step, "left")

    def move_right(self, step=2):
        if self.can_move_right(step):
            self.make_move(0, step, "right")

    def draw_mouse(self):
        # if self.mouse.old_x != self.mouse.x or self.mouse.old_y != self.mouse.y :
        self.stdscr.addch(self.mouse.old_y, self.mouse.old_x, self.mouse.save_char)
        self.stdscr.refresh()
        self.mouse.save_char = chr(self.stdscr.inch(self.mouse.y, self.mouse.x))
        if self.mouse.save_char == "G":
            self.won = True
        self.stdscr.addch(self.mouse.y, self.mouse.x, self.mouse.character)
        self.stdscr.refresh()
        self.diagwin.clear()
        self.diagwin.addstr(self.maze_filename + "\n")
        self.diagwin.addstr(
            f"x = {self.mouse.x}, y = {self.mouse.y}, pos = {self.mouse.position}  \n"
        )
        if "stack" in self.mouse.__dict__:
            self.diagwin.addstr(f"ss = {len(self.mouse.stack)}\n")
        self.diagwin.addstr(self.mouse.get_map())
        self.diagwin.refresh()

    def reset(self):
        self.stdscr.addch(self.mouse.y, self.mouse.x, self.mouse.save_char)
        self.mouse.y = self.start[0]
        self.mouse.x = self.start[1]
        self.mouse.old_y = self.start[0]
        self.mouse.old_x = self.start[1]
        self.mouse.save_char = "S"
        self.won = False
        self.run_number += 1 
        self.move_count = 0
        self.turn_count = 0
        self.stdscr.refresh()

    def play_internal(self, stdscr, mouse):
        # Clear screen

        mouse.get_key_func = stdscr.getkey
        stdscr.clear()
        self.stdscr = stdscr  # newwin(len(self.maze), len(self.maze[0]))
        self.diagwin = newwin(0, 0, 1, len(self.maze[0]) + 2)
        curs_set(0)
        try:
            stdscr.addstr(0, 0, str(maze))
        except Exception:
            print("Your terminal size may be to small. Make the window bigger and try again.")
            time.sleep(2)
            exit()
        self.draw_mouse()
        stdscr.refresh()

        while not maze.quit:
            mouse.move()

            if maze.won:
                mouse.record_map()  # record where the cheese is
                if self.run_number < self.max_run_number:
                    self.reset()
                else:
                    maze.quit = True
            time.sleep(self.sleep_time)

    def play(self, mouse):
        self.mouse = mouse
        self.mouse.y = self.start[0]
        self.mouse.x = self.start[1]
        self.mouse.old_y = self.start[0]
        self.mouse.old_x = self.start[1]
        self.mouse.save_char = "S"

        wrapper(maze.play_internal, mouse)
        echo()
        nocbreak()
        endwin()
        print(self.maze_filename)
        if self.won:
            print(f"You won in {self.move_count} moves, and {self.turn_count} turns. 🐭+🧀=😊")
        else:
            print("You did not find the cheese. 🧀")

        self.mouse.print_map()


class BaseMouse:
    def __init__(self, maze) -> None:
        self.maze = maze
        self.direction = "up"
        self.position = (0, 0)
        temp = ["?"] * (((len(maze.maze[0]) - 2) // 4) * 4 + 1)
        self.map = []
        for i in range(((len(maze.maze) - 1) // 2 * 4 + 1) + 1):
            self.map.append(temp.copy())
        self.map_x_offset = ((len(maze.maze[0]) - 2) // 4) * 2
        self.map_y_offset = ((len(maze.maze) - 1) // 2) * 2
        self.min_x_position = 0
        self.min_y_position = 0
        self.max_x_position = 0
        self.max_y_position = 0

    def record_map(self):
        row, col = self.position
        if col < self.min_x_position:
            self.min_x_position = col
        if col > self.max_x_position:
            self.max_x_position = col
        if row < self.min_y_position:
            self.min_y_position = row
        if row > self.max_y_position:
            self.max_y_position = row
        self.map[row + self.map_y_offset][col + self.map_x_offset] = self.save_char

    def print_map(self):
        print(self.get_map())

    def get_map(self):
        s = ""
        for line in self.map[
            self.min_y_position
            + self.map_y_offset
            - 1 : self.max_y_position
            + self.map_y_offset
            + 2
        ]:
            s = (
                s
                + ""
                + "".join(
                    line[
                        self.min_x_position
                        + self.map_x_offset
                        - 1 : self.max_x_position
                        + self.map_x_offset
                        + 2
                    ]
                )
                + "\n"
            )
        return s

    @property
    def character(self):
        if self.direction == "up":
            return "↑"
        elif self.direction == "right":
            return "→"
        elif self.direction == "left":
            return "←"
        else:
            return "↓"


class RandomMouse(BaseMouse):
    def __init__(self, maze) -> None:
        super().__init__(maze)

    def move(self):
        # self.position = (self.y, self.x//2)
        self.record_map()

        if self.direction == "up":
            if self.maze.can_move_up():
                self.maze.move_up()
            else:
                self.direction = random.choices(
                    population=["down", "left", "right"], weights=[0.1, 0.45, 0.45], k=1
                )[0]
        elif self.direction == "down":
            if self.maze.can_move_down():
                self.maze.move_down()
            else:
                self.direction = random.choices(
                    population=["up", "left", "right"], weights=[0.1, 0.45, 0.45], k=1
                )[0]
        elif self.direction == "left":
            if self.maze.can_move_left():
                self.maze.move_left()
            else:
                self.direction = random.choices(
                    population=["right", "up", "down"], weights=[0.1, 0.45, 0.45], k=1
                )[0]
        elif self.direction == "right":
            if self.maze.can_move_right():
                self.maze.move_right()
            else:
                self.direction = random.choices(
                    population=["left", "up", "down"], weights=[0.1, 0.45, 0.45], k=1
                )[0]


class SlamDfs(BaseMouse):
    def __init__(self, maze) -> None:
        super().__init__(maze)
        self.visited = set()
        self.position = (0, 0)
        self.stack = [self.position]
        self.graph = defaultdict(set)

    def move(self):
        row, col = self.position
        self.record_map()
        vertex = None

        while self.stack:
            vertex = self.stack.pop()
            if vertex not in self.visited:
                self.visited.add(vertex)
            for neighbor in self.graph[vertex]:
                if neighbor not in self.visited:
                    pass
                    # self.stack.append(neighbor)
            v_row, v_col = vertex
            if v_row == row and v_col == col:
                continue
            elif v_col > col:
                self.maze.move_right()
                break
            elif v_row < row:
                self.maze.move_up()
                break
            elif v_col < col:
                self.maze.move_left()
                break
            elif v_row > row:
                self.maze.move_down()
                break
            else:
                pass

        if vertex:
            # self.position = vertex
            row, col = self.position
            # create map
            # self.stack.append(vertex)

            if self.maze.can_move_up():
                if (row - 1, col) not in self.visited:
                    self.graph[self.position].add((row - 1, col))
                    self.graph[(row - 1, col)].add(self.position)
                    self.stack.append(vertex)
                    self.stack.append((row - 1, col))
                    self.map[row - 1 + self.map_y_offset][col + self.map_x_offset] = " "
            else:
                self.map[row - 1 + self.map_y_offset][col + self.map_x_offset] = "*"

            if self.maze.can_move_down():
                if (row + 1, col) not in self.visited:
                    self.graph[self.position].add((row + 1, col))
                    self.graph[(row + 1, col)].add(self.position)
                    self.stack.append(vertex)
                    self.stack.append((row + 1, col))
                    self.map[row + 1 + self.map_y_offset][col + self.map_x_offset] = " "
            else:
                self.map[row + 1 + self.map_y_offset][col + self.map_x_offset] = "*"

            if self.maze.can_move_right():
                if (row, col + 1) not in self.visited:
                    self.graph[self.position].add((row, col + 1))
                    self.graph[(row, col + 1)].add(self.position)
                    self.stack.append(vertex)
                    self.stack.append((row, col + 1))
                    self.map[row + self.map_y_offset][col + 1 + self.map_x_offset] = " "
            else:
                self.map[row + self.map_y_offset][col + 1 + self.map_x_offset] = "*"

            if self.maze.can_move_left():
                if (row, col - 1) not in self.visited:
                    self.graph[self.position].add((row, col - 1))
                    self.graph[(row, col - 1)].add(self.position)
                    self.stack.append(vertex)
                    self.stack.append((row, col - 1))
                    self.map[row + self.map_y_offset][col - 1 + self.map_x_offset] = " "
            else:
                self.map[row + self.map_y_offset][col - 1 + self.map_x_offset] = "*"
        else:
            self.maze.quit = True


class FloodFillMouse(BaseMouse):
    def __init__(self, maze) -> None:
        super().__init__(maze)
        self.map = [
            [0 for x in range(len(self.maze.maze[0]) // 2)] for y in range(len(self.maze.maze))
        ]
        self.fillmap = self.map.copy()
        self.max_dist = 5

    def record_map(self):
        if not self.maze.can_move_up():
            self.map[self.y - 1][self.x // 2] = -1

        if not self.maze.can_move_down():
            self.map[self.y + 1][self.x // 2] = -1

        if not self.maze.can_move_right():
            self.map[self.y][self.x // 2 + 1] = -1

        if not self.maze.can_move_left():
            self.map[self.y][self.x // 2 - 1] = -1

    def print_map(self):
        print(self.get_map(show_color=True))

    def get_map(self, show_color=False):
        s = ""
        black_color_code = ""
        for row in self.fillmap:
            for item in row:
                if item == -1:
                    s += "*"
                else:
                    color = gradient(255, 0, 0, 0, 0, 255, self.max_dist, item)
                    color_code = ""
                    if show_color:
                        color_code = set_bg_color(color[0], color[1], color[2])
                        black_color_code = set_bg_color(0, 0, 0)
                    s += f"{color_code} {black_color_code}"
            s += "\n"
        return s

    def update_flood(self):
        self.fillmap = [row.copy() for row in self.map.copy()]
        queue = [(y, x // 2, 1) for y, x in self.maze.goals]
        while queue:
            row, col, dist = queue.pop(0)
            if col < 0 or row < 0 or row >= len(self.fillmap) or col >= len(self.fillmap[0]):
                continue
            if self.fillmap[row][col] != 0:
                continue
            self.fillmap[row][col] = dist
            queue.append((row + 1, col, dist + 1))
            queue.append((row - 1, col, dist + 1))
            queue.append((row, col + 1, dist + 1))
            queue.append((row, col - 1, dist + 1))
            self.max_dist = dist

    def move(self):
        self.record_map()
        self.update_flood()
        cur_val = self.fillmap[self.y][self.x // 2]
        if self.fillmap[self.y - 1][self.x // 2] == cur_val - 1:
            self.maze.move_up()
        elif self.fillmap[self.y + 1][self.x // 2] == cur_val - 1:
            self.maze.move_down()
        elif self.fillmap[self.y][self.x // 2 + 1] == cur_val - 1:
            self.maze.move_right()
        elif self.fillmap[self.y][self.x // 2 - 1] == cur_val - 1:
            self.maze.move_left()


class HumanMouse(BaseMouse):
    def __init__(self, maze) -> None:
        super().__init__(maze)

    def move(self):
        self.record_map()
        key = self.get_key_func()
        if key == "KEY_UP":
            self.maze.move_up()
        elif key == "KEY_DOWN":
            self.maze.move_down()
        if key == "KEY_LEFT":
            self.maze.move_left()
        elif key == "KEY_RIGHT":
            self.maze.move_right()
        elif key == "q" or key == "Q":
            self.maze.quit = True


if __name__ == "__main__":
    # maze_files = glob.glob("./mazefiles/[!training]*/*.txt", recursive=True)
    maze_files = glob.glob("./mazefiles/**/*.txt", recursive=True)
    maze_file = random.choice(maze_files)
    maze = Maze()
    # maze.load("./mazefiles/classic/uk2016q.txt")
    maze.load(maze_file)
    m1 = HumanMouse(maze)
    m2 = RandomMouse(maze)
    m3 = SlamDfs(maze)
    m4 = FloodFillMouse(maze)
    maze.play(m4)
