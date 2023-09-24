import time
from curses import wrapper, curs_set
import random
from collections import defaultdict


class Maze:

    empty_spaces = [" ","S","G"]

    def __init__(self, sleep_time = 0.1) -> None:
        self.sleep_time = sleep_time

    def load(self, filename):
        maze = []
        with open(filename, "r") as mfile:
            lines = mfile.readlines()
            for line in lines:
                #line = line.replace('G','🧀')
                maze.append([char for char in line])
        self.maze =  maze
        self.start = self.starting_location()
        self.move_count = 0
        self.quit = False
        self.won = False

    def starting_location(self):
        for row in range(len(self.maze)):
            for col in range(len(self.maze[row])):
                if self.maze[row][col] == "S":
                    return (row, col)
        raise ValueError("Bad maze. No starting S found.")
    
    def __repr__(self) -> str:
        str = ""
        for line in self.maze:
            str += "".join(line)
        return str
    def can_move_up(self, step=1):
        return self.mouse.y > step and self.maze[self.mouse.y-step][self.mouse.x] in Maze.empty_spaces and self.maze[self.mouse.y-(step-1)][self.mouse.x] in Maze.empty_spaces
    def can_move_down(self, step=1):
        return self.mouse.y < len(self.maze) - step and self.maze[self.mouse.y+step][self.mouse.x] in Maze.empty_spaces and self.maze[self.mouse.y+step-1][self.mouse.x] in Maze.empty_spaces
    def can_move_left(self, step=2):
        return self.mouse.x > step and self.maze[self.mouse.y][self.mouse.x-step] in Maze.empty_spaces and self.maze[self.mouse.y][self.mouse.x-(step-1)] in Maze.empty_spaces
    def can_move_right(self, step=2):
        return self.mouse.x < len(self.maze[self.mouse.y]) - step and self.maze[self.mouse.y][self.mouse.x+step] in Maze.empty_spaces and self.maze[self.mouse.y][self.mouse.x+step-1] in Maze.empty_spaces

    def make_move(self, y_step=0, x_step=0, dir=None):
        self.mouse.old_y = self.mouse.y
        self.mouse.old_x = self.mouse.x
        self.mouse.y += y_step
        self.mouse.x += x_step
        self.mouse.direction = dir
        self.move_count += 1
        self.draw_mouse()
        
    def move_up(self, step=1):
        if self.can_move_up(step):
            self.make_move(0-step,0,'up')
    def move_down(self, step=1):
        if self.can_move_down(step):
            self.make_move(step,0,'down')
    def move_left(self, step=2):
        if self.can_move_left(step):
            self.make_move(0,0-step,'left')
    def move_right(self, step=2):
        if self.can_move_right(step):
            self.make_move(0,step,'right')

    def draw_mouse(self):
        #if self.mouse.old_x != self.mouse.x or self.mouse.old_y != self.mouse.y :
        self.stdscr.addch(self.mouse.old_y, self.mouse.old_x, self.mouse.save_char)
        self.stdscr.refresh()
        self.mouse.save_char = chr(self.stdscr.inch(self.mouse.y, self.mouse.x))
        if self.mouse.save_char == "G":
            self.won = True
        self.stdscr.addch(self.mouse.y, self.mouse.x, self.mouse.character)
        self.stdscr.refresh()


    def play_internal(self, stdscr, mouse):
        # Clear screen
        self.stdscr = stdscr
        mouse.get_key_func = stdscr.getkey
        stdscr.clear()
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
                mouse.record_map() # record where the cheese is
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
        if self.won:
            print(f"You won in {self.move_count} moves.")
        else:
            print("You did not find the cheese.")

        self.mouse.print_map()



class BaseMouse:
    def __init__(self, maze) -> None:
        self.maze = maze
        self.direction = "up"
        self.position = (0,0)
        temp = ['?'] * (((len(maze.maze[0])-2)//4) * 4 + 1)
        self.map = []
        for i in range(((len(maze.maze)-1)//2 * 4 + 1)):
            self.map.append(temp.copy())
        self.map_x_offset = ((len(maze.maze[0])-2)//4) * 2
        self.map_y_offset = ((len(maze.maze)-1)//2) * 2
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
        for line in self.map[self.min_y_position + self.map_y_offset -1 : self.max_y_position+ self.map_y_offset + 2]:
            print("\r" + "".join(line[self.min_x_position + self.map_x_offset -1 : self.max_x_position+ self.map_x_offset + 2]))
        

    @property
    def character(self):
        if self.direction == "up":
            return "↑"
        elif self.direction == "right":
            return "→"
        elif self.direction == "left":
            return "←"
        else :
            return "↓"
        
class RandomMouse(BaseMouse):
    def __init__(self, maze) -> None:
        super().__init__(maze)
    
    def move(self):
        if self.direction == "up":
            if self.maze.can_move_up():
                self.maze.move_up()
            else:
                self.direction = random.choices(population=["down", "left", "right"], weights=[0.1,0.45,0.45],k=1)[0]
        elif self.direction == "down":
            if self.maze.can_move_down():
                self.maze.move_down()
            else:
                self.direction = random.choices(population=["up", "left", "right"], weights=[0.1,0.45,0.45],k=1)[0]
        elif self.direction == "left":
            if self.maze.can_move_left():
                self.maze.move_left()
            else:
                self.direction = random.choices(population=["right", "up", "down"], weights=[0.1,0.45,0.45],k=1)[0]
        elif self.direction == "right":
            if self.maze.can_move_right():
                self.maze.move_right()
            else:
                self.direction = random.choices(population=["left", "up", "down"], weights=[0.1,0.45,0.45],k=1)[0]


class SlamDfs(BaseMouse):
    def __init__(self, maze) -> None:
        super().__init__(maze)
        self.visited = set()
        self.position = (0,0)
        self.stack = [self.position]
        self.graph = defaultdict(set)


    def move(self):
        row, col = self.position
        self.record_map()
        
        while self.stack:
            vertex = self.stack.pop()
            if vertex not in self.visited:
                self.visited.add(vertex)
            for neighbor in self.graph[vertex]:
                if neighbor not in self.visited:
                    self.stack.append(neighbor)
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
        
        self.position = vertex
        row, col = self.position
        # create map

        if self.maze.can_move_up():
            if (row-1, col) not in self.visited:
                self.graph[self.position].add((row-1, col))
                self.graph[(row-1, col)].add(self.position)
                self.stack.append(vertex)
                self.stack.append((row-1, col))
                self.map[row - 1 + self.map_y_offset][col + self.map_x_offset] = " "
        else:
            self.map[row - 1 + self.map_y_offset][col + self.map_x_offset] = "*"

        if self.maze.can_move_down():
            if (row+1, col) not in self.visited:
                self.graph[self.position].add((row+1, col))
                self.graph[(row+1, col)].add(self.position)
                self.stack.append(vertex)
                self.stack.append((row+1, col))
                self.map[row + 1 + self.map_y_offset][col + self.map_x_offset] = " "
        else:
            self.map[row + 1 + self.map_y_offset][col + self.map_x_offset] = "*"

        if self.maze.can_move_right():
            if (row, col+1) not in self.visited:
                self.graph[self.position].add((row, col+1))
                self.graph[(row, col+1)].add(self.position)
                self.stack.append(vertex)
                self.stack.append((row, col+1))
                self.map[row + self.map_y_offset][col + 1 + self.map_x_offset] = " "
        else:
            self.map[row + self.map_y_offset][col + 1 + self.map_x_offset] = "*"

        if self.maze.can_move_left():
            if (row, col-1) not in self.visited:
                self.graph[self.position].add((row, col-1))
                self.graph[(row, col-1)].add(self.position)
                self.stack.append(vertex)
                self.stack.append((row, col-1))
                self.map[row + self.map_y_offset][col - 1 + self.map_x_offset] = " "
        else:
            self.map[row + self.map_y_offset][col - 1 + self.map_x_offset] = "*"

        

class HumanMouse(BaseMouse):
    def __init__(self, maze) -> None:
        super().__init__(maze)
    
    def move(self):
        key = self.get_key_func()
        if key == 'KEY_UP':
            self.maze.move_up()
        elif key == 'KEY_DOWN':
            self.maze.move_down()
        if key == 'KEY_LEFT':
            self.maze.move_left()
        elif key == 'KEY_RIGHT':
            self.maze.move_right()
        elif key == 'q' or key == "Q":
            self.maze.quit = True

    
if __name__ == "__main__":
    maze = Maze()    
    maze.load("mazefiles/classic/13ye.txt")
    m1 = HumanMouse(maze)
    m2 = RandomMouse(maze)
    m3 = SlamDfs(maze)
    maze.play(m3)