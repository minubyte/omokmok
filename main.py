import pygame
import sys
import time

pygame.init()

screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))

clock = pygame.time.Clock()

UNIT = 40

MX = (1, 1, 0, -1, -1, -1, 0, 1)
MY = (0, 1, 1, 1, 0, -1, -1, -1)

INF = 10**8

AI = 2
PLAYER = 1

DEPTH_LIMIT = 4

cam_x = UNIT
cam_y = UNIT

board = [[0]*(15+1) for _ in range(15+1)]
stones = set()

last_x = -1
last_y = -1

base_patterns = {
    "oooo": 1200,
    "ooo": 900,
    "oo": 400,
}

win_patterns = {
    ".ooooo",
    "ooooo.",
    "xooooo",
    "ooooox",
}

patterns = {}

def add_pattern(pattern, point):
    if len(pattern) >= 6:
        patterns[pattern] = point
    else:
        pattern = pattern+"."*(6-len(pattern))
        patterns[pattern] = point

def init_patterns():
    for pattern, point in base_patterns.items():
        for i in range(5):
            add_pattern(pattern, point)
            temp = pattern[:i]+"."+pattern[i:]
            add_pattern(temp, point-100)

        add_pattern(pattern+"x", point-200)
        add_pattern("x"+pattern, point-200)
        add_pattern(".x"+pattern, point-200)

    # for pattern, point in PATTERNS.items():
    #     print(pattern, point)

init_patterns()

def timer(function):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = function(*args, **kwargs)
        end_time = time.time()
        print(f"걸린 시간: {round(end_time-start_time, 3)}")
        return result
    return wrapper

def make_move(x, y, side):
    board[y][x] = side
    stones.add((x, y))

def unmake_move(x, y):
    board[y][x] = 0
    stones.discard((x, y))

def draw_board():
    pygame.draw.rect(screen, "#b0813e", [cam_x-UNIT/2, cam_y-UNIT/2, UNIT+15*UNIT, UNIT+15*UNIT])
    for y in range(15+1):
        pygame.draw.line(screen, "#222222", [cam_x, cam_y+y*UNIT], [cam_x+15*UNIT, cam_y+y*UNIT], 1)
    for x in range(15+1):
        pygame.draw.line(screen, "#222222", [cam_x+x*UNIT, cam_y], [cam_x+x*UNIT, cam_y+15*UNIT], 1)
    for y in range(15+1):
        for x in range(15+1):
            if board[y][x] == PLAYER:
                pygame.draw.circle(screen, "#d1dfe8", [cam_x+x*UNIT, cam_y+y*UNIT], UNIT//2)
            elif board[y][x] == AI:
                pygame.draw.circle(screen, "#0e1626", [cam_x+x*UNIT, cam_y+y*UNIT], UNIT//2)

def inside_board(x, y):
    return x >= 0 and x <= 15 and y >= 0 and y <= 15

def get_moves():
    moves = set()
    for x, y in stones:
        for i in range(8):
            nx = x+MX[i]
            ny = y+MY[i]
            if inside_board(nx, ny) and board[ny][nx] == 0:
                moves.add((nx, ny))
    return moves

def get_pattern(x, y, side, dir):
    pattern = ""
    for i in range(-1, 5):
        tx, ty = x+MX[dir]*i, y+MY[dir]*i
        if inside_board(tx, ty):
            if board[ty][tx] == side:
                pattern += "o"
            elif board[ty][tx] != 0:
                pattern += "x"
            else:
                pattern += "."
    return pattern

def evaluate_board():
    scores = {1: 0, 2: 0}
    for x, y in stones:
        side = board[y][x]
        score = 0
        # 4방향만 해도 됨 (역방향 제외)
        for i in range(4):
            pattern = get_pattern(x, y, side, i)
            if pattern in patterns:
                score = max(score, patterns[pattern])
            if pattern in win_patterns:
                score = INF
                break
        scores[side] += score

    return scores[1], scores[2]

def alphabeta(depth, alpha, beta, maximizing_player):
    if depth == 0:
        return evaluate(), None

    if maximizing_player:
        best_score = -INF
        best_move = None
        for x, y in get_moves():
            make_move(x, y, AI)
            score, _ = alphabeta(depth-1, alpha, beta, False)
            unmake_move(x, y)
            if score > best_score:
                best_score = score
                best_move = x, y
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break
        return best_score, best_move
    else:
        best_score = INF
        best_move = None
        for x, y in get_moves():
            make_move(x, y, PLAYER)
            score, _ = alphabeta(depth-1, alpha, beta, True)
            unmake_move(x, y)
            if score < best_score:
                best_score = score
                best_move = x, y
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score, best_move

@timer
def find_move():
    _, best_move = alphabeta(DEPTH_LIMIT, -INF, INF, True)
    return best_move

def evaluate():
    player_score, ai_score = evaluate_board()
    return ai_score-player_score*1.5

while True:
    mouse_pos = pygame.mouse.get_pos()
    mouse_x = round((mouse_pos[0]-cam_x)/UNIT)
    mouse_y = round((mouse_pos[1]-cam_y)/UNIT)
        
    screen.fill("#d1dfe8")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if inside_board(mouse_x, mouse_y):
                if event.button == 1:
                    if board[mouse_y][mouse_x] == 0:
                        make_move(mouse_x, mouse_y, PLAYER)
                        x, y = find_move()
                        make_move(x, y, AI)
                        last_x, last_y = x, y

    dt = clock.tick(60)/(1000/60)

    draw_board()

    if inside_board(mouse_x, mouse_y):
        pygame.draw.circle(screen, "#222222", [UNIT+mouse_x*UNIT, UNIT+mouse_y*UNIT], UNIT//2, 2)

    if last_x != -1 and last_y != -1:
        pygame.draw.circle(screen, "#ffb330", [UNIT+last_x*UNIT, UNIT+last_y*UNIT], UNIT//2, 2)

    pygame.display.update()