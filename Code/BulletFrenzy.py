from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

HEIGHT, WIDTH = 800, 800
life_line = 5
missing_bullets = 0 
score = 0
game_over = False

player_pos = [0.0, 0.0, 0.0]
gun_pos = 90 
GRID_LENGTH = 500
bullet_speed = 5
enemy_pos = 30.0
enemy_speed = 0.03
missed_bulcount = 10
bullets = []  
enemies = []


cam_rad =  500
cam_angle = math.pi / 2
cam_pos = 500.0
cam_mode = False 
free_move = False
cheat_mode = False

# Draw Shapes

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(0,0,0)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_zone():
    grid_size = 100
    for x in range(-GRID_LENGTH, GRID_LENGTH, grid_size):
        for y in range(-GRID_LENGTH, GRID_LENGTH, grid_size):
            glColor3f(1, 1, 1) if (x // grid_size + y // grid_size) % 2 == 0 else glColor3f(0.95, 0.67, 0.81)
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0)
            glVertex3f(x + grid_size, y, 0)
            glVertex3f(x + grid_size, y + grid_size, 0)
            glVertex3f(x, y + grid_size, 0)
            glEnd()

 
    def draw_wall(x, y, sx, sy, sz, color):
        glPushMatrix()
        glColor3f(*color)
        glTranslatef(x, y, sz/2)
        glScalef(sx, sy, sz)
        glutSolidCube(1)
        glPopMatrix()

    wall_width = 20
    wall_height = 100
    zone_length = GRID_LENGTH

    walls = [
        ( zone_length, 0, wall_width, zone_length * 2, wall_height, (0, 0, 1)),# Right Wall
        (-zone_length, 0, wall_width, zone_length * 2, wall_height, (0, 1, 0)), #Left Wall
        (0,  zone_length, zone_length * 2, wall_width, wall_height, (1, 1, 1)), # Top Wall
        (0, -zone_length, zone_length * 2, wall_width, wall_height, (0, 1, 1)), # Bottom Wall
    ]

    for x, y, sx, sy, sz, color in walls:
        draw_wall(x, y, sx, sy, sz, color)


def draw_player():
    glPushMatrix()
    glTranslatef(*player_pos)
    glRotatef(gun_pos-90, 0, 0, 1)
    player_body(0, 0, 0)
    glPopMatrix()

def player_body(x, y, z):
    body_parts = [
        (0, 0, 100, (0, 0, 0), lambda: gluSphere(gluNewQuadric(), 25, 10, 10)),  # Head
        (0, 0, 50, (0.24, 0.98, 0.25), lambda: (glScalef(1, 1, 2), glutSolidCube(30))),   # Body
        (20, 0, 70, (1, 0.6, 0.55), lambda: (glRotatef(-90, 1, 0, 0), gluCylinder(gluNewQuadric(), 10, 2, 50, 10, 10))),  # Left Hand
        (-20, 0, 70, (1, 0.6, 0.55), lambda: (glRotatef(-90, 1, 0, 0), gluCylinder(gluNewQuadric(), 10, 2, 50, 10, 10))), # Right Hand
        (0, 0, 70, (0.3, 0.3, 0.3), lambda: (glRotatef(-90, 1, 0, 0), gluCylinder(gluNewQuadric(), 10, 2, 60, 10, 10))),         # Gun
        (10, 0, 30, (0, 0, 1), lambda: (glRotatef(-180, 1, 0, 0), gluCylinder(gluNewQuadric(), 10, 2, 50, 10, 10))),        # Left Leg
        (-10, 0, 30, (0, 0, 1), lambda: (glRotatef(-180, 1, 0, 0), gluCylinder(gluNewQuadric(), 10, 2, 50, 10, 10)))        # Right Leg
    ]

    for dx, dy, dz, color, shape in body_parts:
        glPushMatrix()
        glColor3f(*color)
        glTranslatef(x + dx, y + dy, z + dz)
        shape()
        glPopMatrix()

def draw_enemy(enemy):
    if not game_over:
        s = 1.0 + 0.2 * math.sin(time.time() * 2 )
        glPushMatrix()
        glTranslatef(enemy['x'], enemy['y'], enemy['z'])
        glScalef(s, s, s)
        glColor3f(1, 0, 0)
        glutSolidSphere(enemy_pos, 20, 20)
        glPushMatrix()
        glTranslatef(0, 0, enemy_pos + 10)  
        glColor3f(0, 0, 0)
        glutSolidSphere(enemy_pos / 1.5, 15, 15)
        glPopMatrix()

        glPopMatrix()

    else:
        enemies.clear()

def enemy_gen():
    edge = random.choice(['top', 'bottom', 'left', 'right'])
    margin = 50
    if edge == 'top':
        x = random.uniform(-GRID_LENGTH + margin, GRID_LENGTH - margin)
        y = GRID_LENGTH - margin
    elif edge == 'bottom':
        x = random.uniform(-GRID_LENGTH + margin, GRID_LENGTH - margin)
        y = -GRID_LENGTH + margin
    elif edge == 'left':
        x = -GRID_LENGTH + margin
        y = random.uniform(-GRID_LENGTH + margin, GRID_LENGTH - margin)
    else:  # right
        x = GRID_LENGTH - margin
        y = random.uniform(-GRID_LENGTH + margin, GRID_LENGTH - margin)
    return {'x': x, 'y': y, 'z': 20.0}
  

def init_enemies():
    global enemies
    enemies = [enemy_gen() for i in range(5)]

def draw_bullet(bullet):
    if not game_over:
        glPushMatrix()
        glTranslatef(bullet['x'], bullet['y'], bullet['z'])
        glColor3f(1, 0, 0)
        glutSolidCube(20)
        glPopMatrix()
    else:
        bullets.clear()   


def fire_bullet():
    rad = math.radians(gun_pos)
    x = player_pos[0] + math.cos(rad) * 1
    y = player_pos[1] + math.sin(rad) * 1
    bullets.append({'x': x, 'y': y, 'z': player_pos[2], 'angle': gun_pos})

def update_game():
    global missing_bullets, life_line, score, gun_pos, game_over, cheat_mode

    if cheat_mode:
        gun_pos = (gun_pos + 2) % 360
        for e in enemies:
            dx, dy = e['x'] - player_pos[0], e['y'] - player_pos[1]
            angle_to_enemy = (math.degrees(math.atan2(dy, dx)) + 360) % 360
            if abs(angle_to_enemy - gun_pos) < 1:
                fire_bullet()
                break

    # moving bullets
    new_bullets = []
    for bullet in bullets:
        rad = math.radians(bullet['angle'])
        bullet['x'] += bullet_speed * math.cos(rad)
        bullet['y'] += bullet_speed * math.sin(rad)

        
        if abs(bullet['x']) < GRID_LENGTH and abs(bullet['y']) < GRID_LENGTH:
            new_bullets.append(bullet)
        elif not cheat_mode:
            missing_bullets += 1
    bullets[:] = new_bullets

    
    if life_line <= 0 or missing_bullets >= missed_bulcount:
        game_over = True
        return  

    # Moving enemy
    for enemy in enemies:
        dx = player_pos[0] - enemy['x']
        dy = player_pos[1] - enemy['y']
        dist = math.hypot(dx, dy)
        if dist:
            enemy['x'] += enemy_speed * dx / dist
            enemy['y'] += enemy_speed * dy / dist

    # Killing enemy
    for bullet in bullets[:]:
        for enemy in enemies:
            if math.hypot(bullet['x'] - enemy['x'], bullet['y'] - enemy['y']) < enemy_pos + 10:
                bullets.remove(bullet)
                enemies.remove(enemy)
                enemies.append(enemy_gen())
                score += 1
                break  

    #Killing player
    for enemy in enemies[:]:
        if math.hypot(enemy['x'] - player_pos[0], enemy['y'] - player_pos[1]) < enemy_pos + 15:
            life_line -= 1
            enemies.remove(enemy)
            enemies.append(enemy_gen())


   

def reset_game():
    global bullets, life_line, missing_bullets, score, gun_pos, cam_mode, game_over, free_move, cheat_mode
    bullets.clear()
    life_line = 5
    missing_bullets = 0
    score = 0
    gun_pos = 90
    cam_mode = False
    free_move = False
    cheat_mode = False
    game_over = False
    init_enemies()


    if life_line <= 0 or missing_bullets >= missed_bulcount:
        game_over = True

    


def setup_camera():
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
    """

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(120, WIDTH / HEIGHT, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    rad = math.radians(gun_pos)

    # first person view- free roaming
    if cam_mode or (cheat_mode and free_move):

        eye_x = player_pos[0] - math.cos(rad) * 10
        eye_y = player_pos[1] - math.sin(rad) * 10 + 40
        eye_z = player_pos[2] + 90

        center_x = player_pos[0] + math.cos(rad) * 100
        center_y = player_pos[1] + math.sin(rad) * 100
        center_z = eye_z

        gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0, 0, 1)

    # third person view-free roaming 
    else:
        cam_x = cam_rad * math.cos(cam_angle)
        cam_y = cam_rad * math.sin(cam_angle) - 100
        cam_z = cam_pos

        gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 0, 1)

def show_screen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, WIDTH, HEIGHT)
    setup_camera()


    if not game_over:
        update_game()

    draw_zone()
    for i in enemies:
        draw_enemy(i)
    for j in bullets:
        draw_bullet(j)

    if game_over:
        draw_text(WIDTH-500, HEIGHT-250, "!!! GAME OVER !!!")
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        draw_player()
        glPopMatrix()
    else:
        draw_player()
    display_game_info()

    glutSwapBuffers()

def idle():
    """
    Idle function that runs continuously:
    - Triggers screen redraw for real-time updates.
    """
    update_game()
    # Ensure the screen updates with the latest changes
    glutPostRedisplay()

def key_boards(key, x, y):
    global gun_pos, free_move, cheat_mode
    if key == b'w':
        rad = math.radians(gun_pos)
        player_pos[0] += 5 * math.cos(rad)
        player_pos[1] += 5 * math.sin(rad)
    if key == b's':
        rad = math.radians(gun_pos)
        player_pos[0] -= 5 * math.cos(rad)
        player_pos[1] -= 5 * math.sin(rad)
    if key == b'a':
        gun_pos = (gun_pos + 5) % 360
    if key == b'd':
        gun_pos = (gun_pos - 5) % 360
    if key == b'c':
        cheat_mode = not cheat_mode
    if key == b'v' and cheat_mode==True:
        free_move = not free_move
    if key == b'r':
        reset_game()

def special_key(key, x, y):
    global cam_angle, cam_pos
    if key == GLUT_KEY_UP:#cam_up
        cam_pos += 20
    if key == GLUT_KEY_DOWN:#cam_down
        cam_pos-= 20 
    if key == GLUT_KEY_LEFT:#cam_left
        cam_angle -= 0.05
    if key == GLUT_KEY_RIGHT:#can_right
        cam_angle += 0.05

def mouse_key(button, state, x, y):
    global cam_mode
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not game_over:
        fire_bullet()
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if cam_mode == False:
            cam_mode = True
        else:
            cam_mode = False

def display_game_info():
    
    glColor3f(1.0, 1.0, 1.0)
    screen_height = glutGet(GLUT_WINDOW_HEIGHT)

    lines = [
        f"Player Life Remaining: {life_line}",
        f"Game Score: {score}",
        f"Missing Bullets: {missing_bullets}/{missed_bulcount}"
    ]

    for i, line in enumerate(lines):
        draw_text(10, screen_height - 20 - i * 20, line)


def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Bullet Frenzy - OpenGL Game")

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.2, 0.2, 0.2, 1)
    
    glutDisplayFunc(show_screen)
    glutIdleFunc(show_screen)
    glutKeyboardFunc(key_boards)
    glutSpecialFunc(special_key)
    glutMouseFunc(mouse_key)
    glutIdleFunc(idle)
    reset_game()
    
    
    glutMainLoop()

if __name__ == "__main__":
    main()

