import pygame
import sys
import math
import random
import configparser
from pygame.locals import *

config_parser = configparser.RawConfigParser()
config_file_path = r'./data/config.ini'
config_parser.read(config_file_path)

player_name = config_parser.get("general", "PlayerName")
fps = int(config_parser.get("general", "FPS"))
scr_width_list = config_parser.get("general", "ScreenWidth")
scr_height_list = config_parser.get("general", "ScreenHeight")
scr_width_list = scr_width_list.split(" ")
scr_height_list = scr_height_list.split(" ")
cur_screen_size = int(config_parser.get("general", "StartingScreenSize"))
no_of_stripes_list = config_parser.get("general", "NumberOfStripes")
no_of_stripes_list = no_of_stripes_list.split(" ")
font_type = config_parser.get("general", "Font")
stripe_height = 65
bg_color = eval(config_parser.get("color", "BackgroundColor"))
help_bg_color = (255, 255, 153)
menu_bg_color = (153, 255, 204)
stripe_color = eval(config_parser.get("color", "StripeColor"))
font_color = eval(config_parser.get("color", "FontColor"))
help_font_color = (204, 0, 102)
menu_font_color = (204, 102, 0)
pause_color = eval(
    config_parser.get("color", "PauseScreenColor"))
img_height = 60
img_width = 40
zombie_speed = int(config_parser.get("speed", "ZombieBaseSpeed"))
player_speed = int(config_parser.get("speed", "PlayerSpeed"))
speed_factor = int(
    config_parser.get("speed", "ZombieSpeedFactor"))
next_level_text = config_parser.get("message",
                                    "NextLevelText")
failed_level_text = config_parser.get("message",
                                      "FailedLevelText")
pygame.init()
fps_clock = pygame.time.Clock()

no_of_stripes = int(no_of_stripes_list[cur_screen_size])
scr_width = int(scr_width_list[cur_screen_size])
scr_height = int(scr_height_list[cur_screen_size])
screen = pygame.display.set_mode((scr_width, scr_height))
pygame.display.set_caption("Assignment 3")

font = list()
font.append(pygame.font.Font(font_type, 3 * stripe_height // 5))
font.append(pygame.font.Font(font_type, scr_height // 12))

frame_count = 0
river_size = (scr_height - no_of_stripes * stripe_height) / (no_of_stripes - 1)

st_obs_x = []
mv_obs_x = []
mv_obs_type = []
mv_obs_dir = []

spr_char_left = [[], []]
spr_char_right = [[], []]
spr_char_left_dead = [[], []]
spr_char_right_dead = [[], []]
spr_char = [[], []]
spr_zombie_left = [[], []]
spr_zombie_right = [[], []]
spr_monster = []

play_box = "Click this box to start playing"
help_box = "Click this box for help"
quit_box = "Click this to quit game"

pass_string = ""
pass_last_frame = 0
pass_message = ""
monster_enable = True

pause = False
pause_heading = ""
menu = True
playing = False
help_status = False
help_lines_remaining = 0
help_lines_done = 0

die = 0
dying = 0


def load_image(img_src, width, append_to, append_flipped_to="null"):
    img = pygame.image.load("./data/Resources/img/" + img_src)
    img = pygame.transform.scale(img, (width, img_height))
    eval(append_to).append(img)
    if append_flipped_to != "null":
        img = pygame.transform.flip(img, True, False)
        eval(append_flipped_to).append(img)


def load_text(string, font_size, font_color, prop1, val1, prop2, val2):
    text = font[font_size].render(string, True, font_color)
    rect = text.get_rect()
    setattr(rect, prop1, val1)
    setattr(rect, prop2, val2)
    screen.blit(text, rect)
    return text


def wrap_text(string, start_y):
    words = string.split()
    to_print = ""
    prev_text_size = 0
    temp = scr_width - 2 * stripe_height
    for word in words:
        next_word = font[0].render(word, True, font_color)
        if prev_text_size + next_word.get_width() <= temp:
            prev_text_size += next_word.get_width()
            to_print += " " + word
        else:
            load_text(to_print, 0, help_font_color, "centerx", scr_width / 2,
                      "centery", start_y)
            start_y += 3 * stripe_height // 5
            to_print = word
            prev_text_size = next_word.get_width()
    load_text(to_print, 0, help_font_color, "centerx", scr_width / 2,
              "centery",
              start_y)
    return start_y + 3 * stripe_height // 5


def setup_help(lineno):
    global help_status, help_lines_remaining, help_lines_done
    help_status = True
    screen.fill(help_bg_color)
    if lineno == 1:
        help_lines_remaining = 0
        help_lines_done = 0
    with open("./data/help.txt", "r") as help_file:
        help_text = help_file.readlines()
        start_y = stripe_height
        i = 0
        printed = 0
        help_lines_remaining = 0
        for line in help_text:
            i += 1
            if i >= lineno:
                if start_y >= scr_height - 2 * stripe_height:
                    help_lines_remaining += 1
                else:
                    start_y = wrap_text(line, start_y)
                    printed += 1
    help_lines_done += printed


def setup_menu():
    global play_box, help_box, quit_box, menu
    menu = True
    screen.fill(menu_bg_color)
    load_text("Hello " + player_name, 1, (0, 102, 51), "centery",
              scr_height / 8,
              "centerx", scr_width / 2)
    play_box = pygame.Rect(0, 0, scr_width / 4, scr_height / 8)
    play_box.centery = scr_height / 3
    play_box.centerx = scr_width / 2
    pygame.draw.rect(screen, (255, 255, 255), play_box)
    load_text("Play", 1, menu_font_color, "centerx", play_box.centerx,
              "centery",
              play_box.centery)
    help_box = pygame.Rect(0, 0, scr_width / 4, scr_height / 8)
    help_box.centery = play_box.bottom + scr_height / 6
    help_box.centerx = scr_width / 2
    pygame.draw.rect(screen, (255, 255, 255), help_box)
    load_text("Help", 1, menu_font_color, "centerx", help_box.centerx,
              "centery",
              help_box.centery)
    quit_box = pygame.Rect(0, 0, scr_width / 4, scr_height / 8)
    quit_box.centery = help_box.bottom + scr_height / 6
    quit_box.centerx = scr_width / 2
    pygame.draw.rect(screen, (255, 255, 255), quit_box)
    load_text("Quit", 1, menu_font_color, "centerx", quit_box.centerx,
              "centery",
              quit_box.centery)


def start_play():
    global die, cur_player, p_x, p_y, mv_obs_crossed
    global st_obs_crossed, score, level
    global dying, playing
    playing = True
    die = 0
    cur_player = 0
    p_x = scr_width / 2
    p_y = scr_height - img_height / 2
    mv_obs_crossed = 0
    st_obs_crossed = 0
    score = [3, 3]
    level = [1, 1]
    dying = 0
    generate_obs()
    draw_everything()
    display_pause("Starting")


def generate_obs():
    global st_obs_x, mv_obs_x, mv_obs_type, mv_obs_dir
    st_obs_x = []
    mv_obs_x = []
    mv_obs_type = []
    mv_obs_dir = []
    for i in range(no_of_stripes):
        st_obs_x.append([])
        st_obs_x[i].append(
            img_width + (scr_width / 3 - 2 * img_width) * random.random())
        st_obs_x[i].append(img_width + scr_width / 3 + (
                scr_width / 3 - 2 * img_width) * random.random())
        st_obs_x[i].append(img_width + 2 * scr_width / 3 + (
                scr_width / 3 - 2 * img_width) * random.random())
    for i in range(no_of_stripes - 1):
        mv_obs_x.append(
            img_width + (scr_width - 2 * img_width) * random.random())
        mv_obs_type.append(int(2 * random.random()) % 2)
        mv_obs_dir.append(int(2 * random.random()) % 2)


def display_details():
    load_text("P1: " + str(int(score[0])), 0, font_color, "left",
              stripe_height / 2, "centery", stripe_height / 2)
    load_text("P2: " + str(int(score[1])), 0, font_color, "right",
              scr_width - stripe_height / 2, "centery",
              stripe_height / 2)
    load_text("Player " + str(cur_player + 1), 0, font_color, "centery",
              scr_height - stripe_height / 2, "left",
              stripe_height / 2)
    load_text("Level " + str(level[cur_player]), 0, font_color, "centery",
              scr_height - stripe_height / 2, "right",
              scr_width - stripe_height / 2)
    if cur_player == 0:
        load_text("END", 0, font_color, "centerx", scr_width / 2, "centery",
                  stripe_height / 2)
    else:
        load_text("END", 0, font_color, "centerx", scr_width / 2, "centery",
                  scr_height - stripe_height / 2)


def text_bg(top, bottom):
    top -= stripe_height / 2
    bottom += stripe_height / 2
    h = bottom - top
    s = pygame.Surface((scr_width, h))
    s.set_alpha(150)
    s.fill((0, 0, 0))
    screen.blit(s, (0, top))


def display_pause(s):
    global pause, pause_heading
    pause = True
    if s != "":
        pause_heading = s
    text_bg(scr_height / 4, 3 * scr_height / 4)
    load_text(pause_heading, 1, pause_color, "centery", scr_height / 3,
              "centerx",
              scr_width / 2)
    load_text("Press Space to Continue", 0, pause_color, "centery",
              2 * scr_height / 3, "centerx", scr_width / 2)
    load_text("Player " + str(cur_player + 1) + " turn", 0, pause_color,
              "centery", scr_height / 2, "centerx", scr_width / 2)


def check_collision():
    if not monster_enable:
        return False
    global p_x, p_y, st_obs_x, mv_obs_x
    for i in range(1, no_of_stripes - 1):
        for j in range(3):
            x = st_obs_x[i][j]
            y = i * (stripe_height + river_size) + stripe_height / 2
            if abs(x - p_x) < img_width and abs(y - p_y) < img_height - 5:
                return True
    for i in range(no_of_stripes - 1):
        x = mv_obs_x[i]
        y = (i + 1) * stripe_height + i * river_size + river_size / 2
        if abs(x - p_x) < img_width and abs(y - p_y) < img_height - 5:
            return True
    return False


def move():
    global p_x, p_y
    keys = pygame.key.get_pressed()
    if keys[K_DOWN] and p_y + img_height / 2 + player_speed <= scr_height:
        p_y += player_speed
    if keys[K_UP] and p_y - img_height / 2 - player_speed >= 0:
        p_y -= player_speed
    if keys[K_LEFT] and p_x - img_width / 2 - player_speed >= 0:
        p_x -= player_speed
    if keys[K_RIGHT] and p_x + img_width / 2 + player_speed <= scr_width:
        p_x += player_speed


def cur_stripe():
    p0 = (scr_height - p_y - img_height / 2) // (
            (scr_height - stripe_height) / (no_of_stripes - 1))
    p1 = (p_y - img_height / 2) // (
            (scr_height - stripe_height) / (no_of_stripes - 1))
    return cur_player * p1 + (1 - cur_player) * p0


def cur_river():
    p0 = (scr_height - p_y - stripe_height - river_size / 2) // (
            (scr_height - stripe_height) / (no_of_stripes - 1))
    p1 = (p_y - stripe_height - river_size / 2) // (
            (scr_height - stripe_height) / (no_of_stripes - 1))
    return cur_player * p1 + (1 - cur_player) * p0


def change_player():
    global cur_player, mv_obs_crossed, st_obs_crossed, p_x, p_y, die
    die = 0
    generate_obs()
    if cur_player == 1:
        p_y = scr_height - img_height / 2
    else:
        p_y = img_height / 2
    p_x = scr_width / 2
    cur_player = 1 - cur_player
    mv_obs_crossed = 0
    st_obs_crossed = 0


def change_score():
    global score, mv_obs_crossed, st_obs_crossed, dying
    score[cur_player] -= 1 / fps
    if score[cur_player] <= 0 or check_collision():
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            dying = -1
        else:
            dying = 1
    if cur_stripe() > mv_obs_crossed:
        mv_obs_crossed += 1
        score[cur_player] += 4
    if cur_river() > st_obs_crossed:
        st_obs_crossed += 1
        score[cur_player] += 2


def draw_player():
    global die, dying
    x = p_x - img_width / 2
    y = p_y - img_height / 2
    img_per_sprite = 15
    if cur_player == 1:
        img_per_sprite = 20
    keys = pygame.key.get_pressed()
    if not dying:
        if keys[K_LEFT]:
            screen.blit(
                spr_char_left[cur_player][frame_count % img_per_sprite],
                (x, y))
        elif keys[K_RIGHT] or keys[K_UP] or keys[K_DOWN]:
            screen.blit(
                spr_char_right[cur_player][frame_count % img_per_sprite],
                (x, y))
        else:
            screen.blit(spr_char[cur_player][frame_count % img_per_sprite],
                        (x, y))
    else:
        if dying == -1:
            screen.blit(spr_char_left_dead[cur_player][die // 2], (x, y))
        else:
            screen.blit(spr_char_right_dead[cur_player][die // 2], (x, y))
        die += 1
        if die == 2 * img_per_sprite:
            change_player()
            display_pause(
                failed_level_text.replace("%level%",
                                          str(level[1 - cur_player])))
            dying = 0


def draw_stripes():
    for y in range(0, no_of_stripes):
        pygame.draw.rect(screen, stripe_color, (
            0, y * (river_size + stripe_height), scr_width, stripe_height))


def draw_st_obs():
    temp = stripe_height / 2 - img_height / 2
    for i in range(1, no_of_stripes - 1):
        y = i * (river_size + stripe_height) + temp
        for j in range(3):
            screen.blit(spr_monster[frame_count % 6],
                        (st_obs_x[i][j] - img_width / 2, y))


def draw_mv_obs():
    global mv_obs_x, mv_obs_dir, mv_obs_dead
    for i in range(no_of_stripes - 1):
        temp = img_height / 2
        y = (i + 1) * stripe_height + i * river_size + river_size / 2 - temp
        if mv_obs_dir[i] == 1:
            if mv_obs_x[i] + img_width / 2 + zombie_speed <= scr_width:
                mv_obs_x[i] += zombie_speed + speed_factor * level[cur_player]
            else:
                mv_obs_dir[i] = 0
            screen.blit(spr_zombie_right[mv_obs_type[i]][frame_count % 10],
                        (mv_obs_x[i] - img_width / 2, y))
        else:
            if mv_obs_x[i] - img_width / 2 - zombie_speed >= 0:
                mv_obs_x[i] -= zombie_speed + speed_factor * level[cur_player]
            else:
                mv_obs_dir[i] = 1
            screen.blit(spr_zombie_left[mv_obs_type[i]][frame_count % 10],
                        (mv_obs_x[i] - img_width / 2, y))


def end_detect():
    global level, score
    if score[0] <= 0 and score[1] <= 0:
        declare_winner()
    if cur_player == 0 and p_y <= player_speed + img_height / 2 + 1:
        change_player()
        display_pause(next_level_text.replace("%level%", str(level[0])))
        score[0] += 5 * level[0]
        level[0] += 1
    elif cur_player == 1 and \
            p_y >= scr_height - player_speed - img_height / 2 - 1:
        change_player()
        display_pause(next_level_text.replace("%level%", str(level[1])))
        score[1] += 5 * level[1]
        level[1] += 1


def change_screen_size():
    global screen, scr_width, scr_height, cur_screen_size, font, river_size
    global no_of_stripes, p_y, p_x, help_lines_done, help_lines_remaining
    if playing:
        cur_stripe_no = cur_stripe()
    cur_screen_size = 1 - cur_screen_size
    scr_width = int(scr_width_list[cur_screen_size])
    scr_height = int(scr_height_list[cur_screen_size])
    no_of_stripes = int(no_of_stripes_list[cur_screen_size])
    screen = pygame.display.set_mode((scr_width, scr_height))
    font[1] = pygame.font.Font(font_type, scr_height // 12)
    font[0] = pygame.font.Font(font_type, 3 * stripe_height // 5)
    river_size = (scr_height - no_of_stripes * stripe_height) / (
                no_of_stripes - 1)
    if menu:
        setup_menu()
    elif help_status:
        setup_help(1)
    elif playing:
        if cur_player == 0:
            p_y = scr_height - cur_stripe_no * (
                    stripe_height + river_size) - stripe_height / 2
        else:
            p_y = cur_stripe_no * (
                        stripe_height + river_size) + stripe_height / 2
        generate_obs()
        p_x = img_width
        while check_collision() and p_x < scr_width - img_width:
            p_x += img_width / 2
        draw_everything()
        if pause:
            display_pause("")


def pass_check():
    global pass_message, monster_enable
    if pass_string == "tichnas" and pass_message == "":
        if monster_enable:
            pass_message = chr(0) + "Monsters Disabled"
            monster_enable = False
        else:
            pass_message = chr(0) + "Monsters Enabled"
            monster_enable = True
    if pass_message != "":
        text_bg(scr_height - stripe_height / 2, scr_height)
        load_text(pass_message[1:], 0, (255, 255, 255), "centerx",
                  scr_width / 2,
                  "centery", scr_height - stripe_height / 2)
        ch = pass_message[0]
        ch = chr(ord(ch) + 1)
        pass_message = ch + pass_message[1:]
        if ord(ch) == 3 * fps:
            pass_message = ""


def draw_everything():
    screen.fill(bg_color)
    draw_stripes()
    draw_st_obs()
    draw_mv_obs()
    display_details()
    draw_player()


def declare_winner():
    global playing
    screen.fill((0, 0, 0))
    string = "Draw!"
    if level[1] > level[0] or (level[1] == level[0] and score[1] > score[0]):
        string = "Player 2 Won"
    if level[0] > level[1] or (level[1] == level[0] and score[0] > score[1]):
        string = "Player 2 Won"
    load_text(string, 1, (255, 255, 255), "centery", scr_height / 2, "centerx",
              scr_width / 2)
    pygame.display.update()
    fps_clock.tick(1)
    playing = False
    setup_menu()


for i in range(1, 16):
    load_image("character/male/Run (" + str(i) + ").png", img_width,
               "spr_char_right[0]", "spr_char_left[0]")
    load_image("character/male/Idle (" + str(i) + ").png", img_width,
               "spr_char[0]")
    load_image("character/male/Dead (" + str(i) + ").png", img_height,
               "spr_char_right_dead[0]", "spr_char_left_dead[0]")
for i in range(1, 21):
    load_image("character/female/Run (" + str(i) + ").png", img_width,
               "spr_char_right[1]", "spr_char_left[1]")
    load_image("character/female/Idle (" + str(1 + i % 16) + ").png",
               img_width,
               "spr_char[1]")
    load_image("character/female/Dead (" + str(i) + ").png", img_height,
               "spr_char_right_dead[1]", "spr_char_left_dead[1]")
for i in range(1, 11):
    load_image("zombie/male/Walk (" + str(i) + ").png", img_width,
               "spr_zombie_right[0]", "spr_zombie_left[0]")
    load_image("zombie/female/Walk (" + str(i) + ").png", img_width,
               "spr_zombie_right[1]", "spr_zombie_left[1]")
for i in range(1, 7):
    load_image("monster/standing/frame-" + str(i) + ".png", img_width,
               "spr_monster")

setup_menu()
while True:
    if fps + pass_last_frame < frame_count:
        pass_string = ""
    if playing and not pause:
        draw_everything()
        pass_check()
        if not dying:
            move()
            end_detect()
            change_score()
    for event in pygame.event.get():
        if menu and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            if play_box.collidepoint(pos):
                menu = False
                start_play()
            if help_box.collidepoint(pos):
                menu = False
                setup_help(1)
            if quit_box.collidepoint(pos):
                pygame.quit()
                sys.exit()
        if event.type == pygame.KEYDOWN:
            pass_string += event.unicode
            pass_last_frame = frame_count
            if help_status and event.key == K_SPACE:
                if help_lines_remaining != 0:
                    setup_help(help_lines_done + 1)
                else:
                    help_status = False
                    setup_menu()
            if playing and event.key == K_SPACE:
                if not pause:
                    display_pause("PAUSE")
                else:
                    pause = False
            if event.key == K_f:
                change_screen_size()
            if event.key == K_m:
                if playing:
                    declare_winner()
                setup_menu()
                playing = False
                help_status = False
        if event.type == QUIT or (
                event.type == pygame.KEYDOWN and event.key == K_ESCAPE):
            if playing:
                declare_winner()
            pygame.quit()
            sys.exit()
    frame_count += 1
    pygame.display.update()
    fps_clock.tick(fps)
