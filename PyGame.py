import pygame
import random
from minesweeper import sprites

tile_size = 30
padding_top = 80
res = width, height = 600, 600 + padding_top
screen = pygame.display.set_mode(res)

# Tiles
tiles_style = sprites.TileSheets(sprites.TileSheets.two_thousand)
builder = sprites.TileBuilder(tiles_style)
builder.unopened(tiles_style).empty(tiles_style).flag(tiles_style)
tile1 = builder.build()
blit = lambda img, idx, row: screen.blit(pygame.transform.scale(img, (tile_size, tile_size)),
                                         (tile_size * idx, padding_top + row * tile_size))

# Score
score_style = sprites.ScoreSheets(sprites.ScoreSheets.two_thousand)
score_builder = sprites.ScoreBuilder()
score = score_builder.zero(score_style).one(score_style).two(score_style).three(score_style).four(score_style).five(
    score_style).six(score_style).seven(score_style).eight(score_style).nine(score_style).build()
blitScore = lambda img, idx: screen.blit(pygame.transform.scale(img, (20, 40)),
                                         (10 + 20 * idx, padding_top / 2 - 20))
blitTime = lambda img, idx: screen.blit(pygame.transform.scale(img, (20, 40)),
                                        (width - 70 + 20 * idx, padding_top / 2 - 20))

# Face
face_style = sprites.FaceSheets(sprites.FaceSheets.two_thousand)
face_builder = sprites.FaceBuilder()
face = face_builder.excited(face_style).dead(face_style).smile(face_style).build()
blitFace = lambda img: screen.blit(pygame.transform.scale(img, (50, 50)),
                                   (width / 2 - 25, padding_top / 2 - 25))


def translate(n):
    if n == 0:
        return score.zero
    elif n == 1:
        return score.one
    elif n == 2:
        return score.two
    elif n == 3:
        return score.three
    elif n == 4:
        return score.four
    elif n == 5:
        return score.five
    elif n == 6:
        return score.six
    elif n == 7:
        return score.seven
    elif n == 8:
        return score.eight
    elif n == 9:
        return score.nine


class Board:
    def __init__(self, widthB, heightB, mines_count):
        self.top = padding_top
        self.tile_size = 30
        self.width = widthB
        self.height = heightB
        self.opened = []
        self.flags = []
        self.mines = []
        screen.fill((200, 200, 200))
        self.draw_board(widthB, heightB)
        self.mines_count = mines_count
        self.make_mines(mines_count)
        self.flags_count = mines_count
        self.draw_score(mines_count)
        self.status = 0  # 0 - игра не начата, 1 - игра, 2 - победа, 3 - проигрыш
        self.draw_face()
        self.draw_time(0)

    def make_mines(self, count):
        while len(self.mines) < count:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in self.mines:
                self.mines.append((x, y))

    def show_mines(self):
        for x, y in self.mines:
            blit(tile1.mine, x, y)
        self.status = 3

    def around(self, tile, type):
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= tile[0] + i < self.width and 0 <= tile[1] + j < self.height:
                    if (tile[0] + i, tile[1] + j) in type:
                        count += 1
        return count

    def get_zone(self, mouse_pos):
        if res[0] / 2 - 25 < mouse_pos[0] < res[0] / 2 + 25 and self.top / 2 - 25 < mouse_pos[1] < self.top / 2 + 25:
            return 0
        elif mouse_pos[1] >= self.top:
            return 1
        else:
            return 2

    def get_tile(self, mouse_pos):
        x = mouse_pos[0] // self.tile_size
        y = (mouse_pos[1] - self.top) // self.tile_size
        return (x, y)

    def on_click_left(self, tile):
        count_mines = self.around(tile, self.mines)
        count_flags = self.around(tile, self.flags)
        if tile not in self.opened and tile not in self.flags:
            if tile in self.mines:
                self.show_mines()
            else:
                if count_mines > 0:
                    blit(tile1[count_mines], int(tile[0]), int(tile[1]))
                    self.opened.append(tile)
                else:
                    blit(tile1.empty, int(tile[0]), int(tile[1]))
                    self.opened.append(tile)
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if 0 <= tile[0] + i < self.width and 0 <= tile[1] + j < self.height:
                                self.on_click_left((tile[0] + i, tile[1] + j))
        if tile in self.opened and 0 < count_mines == count_flags:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 <= tile[0] + i < self.width and 0 <= tile[1] + j < self.height:
                        if (tile[0] + i, tile[1] + j) not in self.flags and (
                                tile[0] + i, tile[1] + j) not in self.opened:
                            self.on_click_left((tile[0] + i, tile[1] + j))

    def on_click_right(self, tile):
        if tile not in self.opened and tile not in self.flags and self.flags_count > 0:
            blit(tile1.flag, tile[0], tile[1])
            self.flags.append(tile)
            self.flags_count -= 1
        elif tile in self.flags:
            blit(tile1.unopened, tile[0], tile[1])
            self.flags.remove(tile)
            self.flags_count += 1

    def get_click(self, mouse_pos, mouse_button):
        if self.status == 2 or self.status == 3:
            self.__init__(self.width, self.height, self.mines_count)
        else:
            if self.get_zone(mouse_pos) == 0:
                if self.status == 1:
                    self.status = 3
                    self.show_mines()
            if self.get_zone(mouse_pos) == 1:
                if self.status == 0:
                    self.status = 1
                tile = self.get_tile(mouse_pos)
                if mouse_button == 1:
                    self.on_click_left(tile)
                elif mouse_button == 3:
                    self.on_click_right(tile)

    def draw_score(self, number):
        hundred = number // 100
        ten = (number - hundred * 100) // 10
        one = number - hundred * 100 - ten * 10
        blitScore(translate(hundred), 0)
        blitScore(translate(ten), 1)
        blitScore(translate(one), 2)

    def draw_time(self, number):
        if number >= 999:
            number = 999
        hundred = number // 100
        ten = (number - hundred * 100) // 10
        one = number - hundred * 100 - ten * 10
        blitTime(translate(hundred), 0)
        blitTime(translate(ten), 1)
        blitTime(translate(one), 2)

    def draw_face(self):
        if self.status == 0 or self.status == 1:
            blitFace(face.smile)
        elif self.status == 2:
            blitFace(face.excited)
        elif self.status == 3:
            blitFace(face.dead)

    def draw_board(self, w, h):
        for i in range(w):
            for j in range(h):
                blit(tile1.unopened, i, j)

    def draw_inerface(self):
        self.draw_score(self.flags_count)
        self.draw_face()


board = Board(20, 20, 40)
pygame.init()
clock = pygame.time.Clock()
seconds = 0
pygame.time.set_timer(pygame.USEREVENT, 1000)

running = True
while running:
    if board.status == 0:
        seconds = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.USEREVENT:
            if board.status == 1:
                seconds += 1
            board.draw_time(seconds)
        if event.type == pygame.MOUSEBUTTONDOWN:
            board.get_click(event.pos, event.button)
    if sorted(board.mines) == sorted(board.flags):
        board.status = 2
    board.draw_inerface()
    pygame.display.flip()