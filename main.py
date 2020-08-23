import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH,WIDTH))
pygame.display.set_caption("A* Path finding algorithm")
## Colors Constants:
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
PURPLE = (128,0,128)
ORANGE = (255,165,0)
GREY = (128,128,128)
TURQUOISE = (64,224,208)

class Node:
    def __init__(self,row,col,width,total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
    ## ---------------------- ##
    ##    Getters functions   ##
    ## ---------------------- ##
    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED
    def is_open(self):
        return self.color == GREEN
    def is_barrier(self):
        return self.color == BLACK
    def is_start(self):
        return self.color == ORANGE
    def is_end(self):
        return self.color == TURQUOISE
    ## ---------------------- ##
    ## Change state functions ##
    ## ---------------------- ##
    def reset(self):
        self.color = WHITE
    def make_close(self):
        self.color = RED
    def make_open(self):
        self.color = GREEN
    def make_barrier(self):
        self.color = BLACK
    def make_start(self):
        self.color = ORANGE
    def make_end(self):
        self.color = TURQUOISE
    def make_path(self):
        self.color = PURPLE
    ## ---------------------- ##
    ##  The drawing function  ##
    ## ---------------------- ##
    def draw(self,win):
        pygame.draw.rect(win,self.color,(self.x,self.y,self.width,self.width))

    def update_neighbors(self,grid):
        self.neighbors = []
        ## DOWN neighbor
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        ## UP neighbor
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        ## RIGHT neighbor
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        ## LEFT neighbor
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def h(p1,p2):
    """
    Heuristic function for Point1, Point2
    :param p1: an (x1,y1) point
    :param p2: an (x2,y2) point
    :return: heuristic distance
    """
    x1,y1 = p1
    x2,y2 = p2
    return abs(x1-x2) + abs(y1-y2)

def make_grid(rows,width):
    """
    Making the grid with rox*width Nodes
    :param rows:
    :param width:
    :return: the newly created grid
    """
    grid = []
    cell_width = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i,j,cell_width,rows)
            grid[i].append(node)
    return grid

def draw_grid(win,rows,width):
    """
    Draw the grid lines
    :param win:
    :param rows:
    :param width:
    :return:
    """
    cell_width = width//rows
    for i in range(rows):
        pygame.draw.line(win,GREY,(0,i*cell_width),(width,i*cell_width))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * cell_width,0), (j * cell_width, width))

def draw(win,grid,rows,width):
    """
    Draw the nodes in the given grid, and the grid line on top
    :param win:
    :param grid:
    :param rows:
    :param width:
    :return:
    """
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win,rows,width)
    pygame.display.update()

def get_clicked_pos(pos,rows,width):
    """
    Helper function to get the mouse clicked position
    :param pos:
    :param rows:
    :param width:
    :return:
    """
    cell_width = width//rows
    y,x = pos
    row = y//cell_width
    col = x//cell_width
    return row,col

def reconstruct_path(came_from, current, draw_func):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw_func()

def algorithm(draw_func,grid,start,end):
    ## Initializing
    count = 0
    open_set = PriorityQueue() #Get the smallest element efficiently
    open_set.put((0,count,start))
    open_set_hash = {start} #For lookup
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(),end.get_pos())
    ## Algorithm
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = open_set.get()[2] # get the node with minimal f_score
        open_set_hash.remove(current) # sync
        # If we've done-
        if current == end:
            reconstruct_path(came_from, end, draw_func)
            end.make_end()
            start.make_start()
            return True
        # Else:
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]: # better path
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(),end.get_pos())
                if neighbor not in open_set_hash:
                    count+=1
                    open_set.put((f_score[neighbor],count,neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw_func()
        if current != start:
            current.make_close()
    return False


def main_loop(win,width):
    ROWS = 50
    grid = make_grid(ROWS,width)
    start = None
    end = None
    run = True
    while run:
        draw(win,grid,ROWS,WIDTH)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            ## Left mouse clicked:
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row,col = get_clicked_pos(pos,ROWS,width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    end.make_end()
                elif node != end and node != start:
                    node.make_barrier()

            ## Right mouse clicked:
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            ## Run the algorithm after hitting space
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    algorithm(lambda: draw(win,grid,ROWS,width),grid,start,end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS,width)
    pygame.quit()

main_loop(WIN,WIDTH)