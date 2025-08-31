from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time
import random

# Game state variables  (sakura)
car = {
    'x': 0.0, 'y': 0.5, 'z': 0.0,
    'lane': 1,  # 0=left, 1=middle, 2=right
    'speed': 5.0,  # Start with baseline speed
    'rotation': 0.0,
    'health': 10,
    'flying': False,
    'fly_timer': 0.0
}
# Baseline speed (minimum continuous speed)  (sakura)
BASELINE_SPEED = 5.0
MAX_SPEED = 50.0

# Camera modes: 0=third-person, 1=first-person, 2=overview  
camera_mode = 0

# Lane positions (3 lanes) (sakura)
LANE_POSITIONS = [-5.0, 0.0, 5.0]  # Left, Middle, Right
ROAD_LENGTH = 100.0


# Game objects rodo
obstacles = []
items = []
powerups = []
enemies = []


# Game stats rodo
score = 0
coins_collected = 0  # Track coins separately
game_over = False

#Rehnuma
#Special abilities
cheat_mode = False
cheat_timer = 0.0
magnet_mode = False
magnet_timer = 0.0


# Input state
keys_pressed = set()
special_keys_pressed = set()

# Timing variables for spawning rodo
last_obstacle_spawn = 0.0
last_enemy_spawn = 0.0
obstacle_spawn_interval = 10.0  # 10 seconds
enemy_spawn_interval = 20.0  # 20 seconds
game_start_time= 0.0  # Track when game started
first_enemy_delay = 25.0  # First enemy after 25 seconds



def reset_game():
    """Reset game to initial state"""
    global score, coins_collected, game_over, cheat_mode, cheat_timer, magnet_mode, magnet_timer
    global last_obstacle_spawn, last_enemy_spawn, game_start_time

    car['x'] = 0.0
    car['y'] = 0.5
    car['z'] = 0.0
    car['lane'] = 1
    car['speed'] = BASELINE_SPEED  # Start with baseline speed
    car['rotation'] = 0.0
    car['health'] = 10
    car['flying'] = False
    car['fly_timer'] = 0.0

    #rodo
    score = 0
    coins_collected = 0
    game_over = False

    #rehnuma
    cheat_mode = False
    cheat_timer = 0.0
    magnet_mode = False
    magnet_timer = 0.0

    # Reset spawn timers rodo
    last_obstacle_spawn = time.time()
    last_enemy_spawn = time.time()

    init_game_objects()
    print("Game reset! Ready to race!")

def init_game_objects():
   """Initialize obstacles, items, powerups, and enemies for 3-lane road"""
   global obstacles, items, powerups, enemies


   # Start with fewer initial obstacles - they'll spawn over time rodo
   obstacles.clear()
   for i in range(3):  # Start with only 3 obstacles
       lane = random.randint(0, 2)
       z_pos = random.uniform(10, 30)
       x_pos = LANE_POSITIONS[lane]
       obstacle_type = random.choice(["barrier", "cone", "rock"])
       obstacles.append([x_pos, 1.0, z_pos, obstacle_type])


   # Generate coins only across lanes rodo
   items.clear()
   for i in range(30):
       lane = random.randint(0, 2)
       z_pos = random.uniform(5, 60)
       x_pos = LANE_POSITIONS[lane] + random.uniform(-1, 1)
       item_type = "coin"  # Only coins
       rotation = 0.0
       collected = False
       items.append([x_pos, 2.0, z_pos, item_type, rotation, collected])


   # No power-ups - remove them completely
   powerups.clear()


   # Start with fewer enemy cars - they'll spawn over time rodo
   enemies.clear()
   for i in range(1):  # Start with only 1 enemy
       lane = random.randint(0, 2)
       z_pos = random.uniform(15, 30)
       x_pos = LANE_POSITIONS[lane]
       vel_x = 0.0
       vel_z = -random.uniform(15, 25)  # Negative for opposite direction
       rotation = 180.0  # Face opposite direction
       last_hit = 0.0
       enemies.append([x_pos, 0.5, z_pos, vel_x, vel_z, rotation, last_hit])



#rodo
def spawn_obstacle():
   """Spawn a new obstacle in a random lane"""
   global obstacles
   lane = random.randint(0, 2)
   z_pos = car['z'] + random.uniform(20, 40)  # Spawn ahead of player
   x_pos = LANE_POSITIONS[lane]
   obstacle_type = random.choice(["barrier", "cone", "rock"])
   obstacles.append([x_pos, 1.0, z_pos, obstacle_type])
   print(f"Spawned {obstacle_type} in lane {lane + 1} at position {x_pos}")



#rodo
def spawn_enemy():
   """Spawn a new enemy car in a random lane from far ahead"""
   global enemies
   lane = random.randint(0, 2)
   z_pos = car['z'] + random.uniform(50, 80)  # Spawn far ahead of player
   x_pos = LANE_POSITIONS[lane]
   vel_x = 0.0
   vel_z = -random.uniform(15, 25)  # Negative velocity for opposite direction
   rotation = 180.0  # Face opposite direction
   last_hit = 0.0
   enemies.append([x_pos, 0.5, z_pos, vel_x, vel_z, rotation, last_hit])



#rodo
def update_spawning():
   """Update obstacle and enemy spawning based on time"""
   global last_obstacle_spawn, last_enemy_spawn


   current_time = time.time()


   # Spawn obstacle every 10 seconds
   if current_time - last_obstacle_spawn >= obstacle_spawn_interval:
       spawn_obstacle()
       last_obstacle_spawn = current_time


   # Spawn enemy every 20 seconds (but not in first 25 seconds)
   time_since_start = current_time - game_start_time
   if time_since_start >= first_enemy_delay and current_time - last_enemy_spawn >= enemy_spawn_interval:
       spawn_enemy()
       last_enemy_spawn = current_time



def setupCamera():
    """Set up camera with multiple modes"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.25, 0.1, 1500)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == 0:  # Third-person
        cam_x = car['x']
        cam_y = car['y'] + 8.0
        cam_z = car['z'] - 15.0
        look_x = car['x']
        look_y = car['y']
        look_z = car['z'] + 10.0
    elif camera_mode == 1:  # First-person
        cam_x = car['x']
        cam_y = car['y'] + 1.5
        cam_z = car['z']
        look_x = car['x']
        look_y = car['y'] + 1.5
        look_z = car['z'] + 10.0
    else:  # Overview
        cam_x = 0.0
        cam_y = 50.0
        cam_z = car['z'] - 5.0
        look_x = 0.0
        look_y = 0.0
        look_z = car['z']

    gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 1, 0)


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """Draw text on screen"""
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def render_cube():
    """Render a cube"""
    glutSolidCube(1.0)

def render_3_lane_road():
   """Render 3-lane road with visible lane markers"""
   # Road base (light gray) - infinite road based on car position
   glColor3f(0.7, 0.7, 0.7)
   glBegin(GL_QUADS)
   road_width = 15.0  # Total width for 3 lanes
   # Render road segments around the player's position
   start_z = int(car['z']) - 30
   end_z = int(car['z']) + 100
   for z in range(start_z, end_z, 2):
       glVertex3f(-road_width / 2, 0.0, z)
       glVertex3f(road_width / 2, 0.0, z)
       glVertex3f(road_width / 2, 0.0, z + 2)
       glVertex3f(-road_width / 2, 0.0, z + 2)
   glEnd()


   # Lane divider lines (white)
   glColor3f(1.0, 1.0, 1.0)
   glLineWidth(3.0)
   glBegin(GL_LINES)


   # Left lane divider
   left_divider = LANE_POSITIONS[0] + 2.5
   for z in range(start_z, end_z, 4):
       glVertex3f(left_divider, 0.1, z)
       glVertex3f(left_divider, 0.1, z + 2)


   # Right lane divider
   right_divider = LANE_POSITIONS[1] + 2.5
   for z in range(start_z, end_z, 4):
       glVertex3f(right_divider, 0.1, z)
       glVertex3f(right_divider, 0.1, z + 2)


   glEnd()


   # Road barriers (red walls on sides)
   glColor3f(0.8, 0.0, 0.0)
   glBegin(GL_QUADS)
   barrier_height = 2.0
   for z in range(start_z, end_z, 2):
       # Left barrier
       glVertex3f(-road_width / 2 - 1, 0, z)
       glVertex3f(-road_width / 2 - 1, barrier_height, z)
       glVertex3f(-road_width / 2 - 1, barrier_height, z + 2)
       glVertex3f(-road_width / 2 - 1, 0, z + 2)


       # Right barrier
       glVertex3f(road_width / 2 + 1, 0, z)
       glVertex3f(road_width / 2 + 1, barrier_height, z)
       glVertex3f(road_width / 2 + 1, barrier_height, z + 2)
       glVertex3f(road_width / 2 + 1, 0, z + 2)
   glEnd()




def render_obstacles():
   """Render obstacles in lanes"""
   for obstacle in obstacles:
       glPushMatrix()
       glTranslatef(obstacle[0], obstacle[1], obstacle[2])


       if obstacle[3] == "barrier":
           glColor3f(1.0, 0.5, 0.0)  # Orange
       elif obstacle[3] == "cone":
           glColor3f(1.0, 0.3, 0.0)  # Orange-red
       else:  # rock
           glColor3f(0.4, 0.4, 0.4)  # Gray


       # Use spheres for obstacles instead of cubes
       glutSolidSphere(1.0, 12, 12)
       glPopMatrix()




def render_items():
   """Render collectible items"""
   for item in items:
       if not item[5]:  # If not collected
           glPushMatrix()
           glTranslatef(item[0], item[1], item[2])
           glRotatef(item[4], 0, 1, 0)


           # Only coins now
           glColor3f(1.0, 1.0, 0.0)  # Gold
           glutSolidSphere(0.3, 8, 8)  # Circular coin
           glPopMatrix()


           # Update rotation
           item[4] += 2.0




def render_enemies():
   """Render enemy cars"""
   for enemy in enemies:
       glPushMatrix()
       glTranslatef(enemy[0], enemy[1], enemy[2])
       glRotatef(enemy[5], 0, 1, 0)


       # Enemy car body (red)
       glColor3f(0.8, 0.0, 0.0)
       glScalef(2.0, 1.0, 4.0)
       render_cube()
       glPopMatrix()



def render_player_car():     #Sakura
    """Render the player car with 4 wheels"""
    glPushMatrix()
    glTranslatef(car['x'], car['y'], car['z'])
    glRotatef(car['rotation'], 0, 1, 0)

    # Car body color (Rehnuma)
    if cheat_mode:
        glColor3f(1.0, 1.0, 0.0)  # Yellow when invincible
    elif magnet_mode:
        glColor3f(1.0, 0.0, 1.0)  # Magenta when magnet active
    else:
        glColor3f(0.0, 0.5, 1.0)  # Normal blue

    # Car body
    glScalef(2.0, 1.0, 4.0)
    render_cube()
    glPopMatrix()

    # Render 4 wheels (black spheres)
    glColor3f(0.1, 0.1, 0.1)  # Dark color for wheels
    wheel_radius = 0.3

    # Front left wheel
    glPushMatrix()
    glTranslatef(car['x'] - 1.2, car['y'] - 0.3, car['z'] + 1.5)
    glutSolidSphere(wheel_radius, 8, 8)
    glPopMatrix()

    # Front right wheel
    glPushMatrix()
    glTranslatef(car['x'] + 1.2, car['y'] - 0.3, car['z'] + 1.5)
    glutSolidSphere(wheel_radius, 8, 8)
    glPopMatrix()

    # Rear left wheel
    glPushMatrix()
    glTranslatef(car['x'] - 1.2, car['y'] - 0.3, car['z'] - 1.5)
    glutSolidSphere(wheel_radius, 8, 8)
    glPopMatrix()

    # Rear right wheel
    glPushMatrix()
    glTranslatef(car['x'] + 1.2, car['y'] - 0.3, car['z'] - 1.5)
    glutSolidSphere(wheel_radius, 8, 8)
    glPopMatrix()

def update_player_car():
    global cheat_mode, cheat_timer, magnet_mode, magnet_timer
    dt = 0.016
    # Special ability timers (Rehnuma)
    if cheat_mode:
        cheat_timer -= dt
        if cheat_timer <= 0:
            cheat_mode = False
            print("Cheat mode ended")

    if magnet_mode:
        magnet_timer -= dt
        if magnet_timer <= 0:
            magnet_mode = False
            print("Magnet mode ended")

    if car['flying']:
        car['fly_timer'] -= dt
        if car['fly_timer'] <= 0:
            car['flying'] = False
            car['y'] = 0.5
            print("Flying mode ended")

    # Speed control (UP/DOWN arrows) - fine control  (SAKURA)
    if GLUT_KEY_UP in special_keys_pressed:
        car['speed'] = min(car['speed'] + 25.0 * dt, MAX_SPEED)
    if GLUT_KEY_DOWN in special_keys_pressed:
        car['speed'] = max(car['speed'] - 30.0 * dt, BASELINE_SPEED)

    # Lane changing (A/D)    (SAKURA)
    if ord('a') in keys_pressed or ord('A') in keys_pressed:
        if car['lane'] > 0:
            car['lane'] -= 1
            keys_pressed.discard(ord('a'))
            keys_pressed.discard(ord('A'))
            print(f"Changed to lane {car['lane'] + 1}")

    if ord('d') in keys_pressed or ord('D') in keys_pressed:
        if car['lane'] < 2:
            car['lane'] += 1
            keys_pressed.discard(ord('d'))
            keys_pressed.discard(ord('D'))
            print(f"Changed to lane {car['lane'] + 1}")

    # Apply gentle drift back to baseline speed when no input   (SAKURA)
    if not (GLUT_KEY_UP in special_keys_pressed or GLUT_KEY_DOWN in special_keys_pressed):
        if car['speed'] > BASELINE_SPEED:
            car['speed'] = max(car['speed'] - 10.0 * dt, BASELINE_SPEED)
        elif car['speed'] < BASELINE_SPEED:
            car['speed'] = min(car['speed'] + 10.0 * dt, BASELINE_SPEED)

    # Update position based on speed and lane   (SAKURA)
    car['z'] += car['speed'] * dt
    target_x = LANE_POSITIONS[car['lane']]
    car['x'] += (target_x - car['x']) * 5.0 * dt  # Smooth lane transition

    # Update flying height (Rehnuma)
    if car['flying']:
        car['y'] = 8.0  # Much higher for visible flying
    else:
        car['y'] = 0.5

 # Infinite road - move objects back when player advances
    if car['z'] > 50:
       # Move all objects back relative to player
       for obstacle in obstacles:
           if obstacle[2] < car['z'] - 30:
               obstacle[2] += 80
       for item in items:
           if item[2] < car['z'] - 30:
               item[2] += 80
               item[5] = False  # Make uncollected again
       # No powerups to move
def update_enemies():
   """Update enemy AI cars moving in opposite direction"""
   dt = 0.016
   for enemy in enemies[:]:
       # Move in opposite direction (towards player)
       enemy[2] += enemy[4] * dt  # z position (vel_z is negative)


       # Remove enemies that passed behind player
       if enemy[2] < car['z'] - 50:
           enemies.remove(enemy)



def check_collisions():
    """Handle all collision detection"""
    global score, coins_collected, game_over

    if game_over:
        return

    player_size = 2.0

    # Check obstacle collisions (only if not in cheat mode and not flying)
    if not cheat_mode and not car['flying']:
        for obstacle in obstacles:
            if abs(obstacle[2] - car['z']) < 10:  # Only check nearby obstacles
                dx = car['x'] - obstacle[0]
                dz = car['z'] - obstacle[2]
                distance = math.sqrt(dx * dx + dz * dz)
                if distance < player_size:
                    obstacles.remove(obstacle)
                    car['health'] -= 1
                    print(f"Obstacle collision! Health: {car['health']}")
                    if car['health'] <= 0:
                        game_over = True
                        print("GAME OVER!")


    # Check coin collection in Magnet Mode (REHNUMA)
    if magnet_mode:
        # In magnet mode, collect coins across all lanes at same z position as car
        for item in items:
            if not item[5] and item[3] == "coin":  # If not collected and is a coin
                # Check if coin is at similar z position (same x-axis as car)
                if abs(item[2] - car['z']) < 3.0:  # Within 3 units of car's z position
                    item[5] = True  # Mark as collected
                    score += 10
                    coins_collected += 1
                    print(f"Magnet collected coin from lane! Coins: {coins_collected}")

    else:
        # Normal collection range
        collection_range = 2.0
        for item in items:
            if not item[5]:  # If not collected
                dx = car['x'] - item[0]
                dz = car['z'] - item[2]
                distance = math.sqrt(dx * dx + dz * dz)
                if distance < collection_range:
                    item[5] = True  # Mark as collected
                    # Only coins now
                    score += 10
                    coins_collected += 1
                    print(f"Item collected! Coins: {coins_collected}, Score: {score}")

    # No power-ups anymore

    # Check enemy collisions (only if not in cheat mode and not flying)
    if not cheat_mode and not car['flying']:
        current_time = time.time()
        for enemy in enemies:
            if abs(enemy[2] - car['z']) < 10:  # Only check nearby enemies
                dx = car['x'] - enemy[0]
                dz = car['z'] - enemy[2]
                distance = math.sqrt(dx * dx + dz * dz)
                if distance < 3.0:
                    if current_time - enemy[6] > 1.0:  # Limit collision frequency
                        enemy[6] = current_time
                        game_over = True
                        print("Enemy collision! GAME OVER!")


def showScreen():
    """Main display function"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()


    if not game_over:
        # Update game logic
        update_player_car()
        update_enemies()
        update_spawning()  # Add timed spawning
        check_collisions()

    # Render all objects rodo
    render_3_lane_road()
    render_obstacles()
    render_items()
    # No powerups to render rodo
    render_enemies()
    render_player_car()

    # Display game info
    draw_text(10, 770, "Fast & Furious Car Chase")
    draw_text(10, 740, f"Health: {car['health']}")
    draw_text(10, 710, f"Coins: {coins_collected}")
    draw_text(10, 680, f"Score: {score}")
    draw_text(10, 650, f"Speed: {car['speed']:.1f}")
    draw_text(10, 620, f"Lane: {car['lane'] + 1}")

    # Camera info
    camera_names = ["Third Person", "First Person", "Overview"]
    draw_text(10, 590, f"Camera: {camera_names[camera_mode]}")

    # Controls
    draw_text(10, 580, "A/D: Change Lane, UP/DOWN: Speed Control")
    draw_text(10, 550, "C: Cheat, J: Flying, M: Magnet, F: 1st Person, T: 3rd Person")

       # Special modes
    if cheat_mode:
        draw_text(10, 500, f"CHEAT MODE: {cheat_timer:.1f}s")
    if car['flying']:
        draw_text(10, 470, f"FLYING MODE: {car['fly_timer']:.1f}s")
    if magnet_mode:
        draw_text(10, 440, f"MAGNET MODE: {magnet_timer:.1f}s") 

    if game_over:
        draw_text(350, 450, "GAME OVER!")
        draw_text(300, 400, f"Final Score: {coins_collected} coins")
        draw_text(290, 350, f"Total Points: {score}")
        draw_text(320, 300, "Press R to restart")

    glutSwapBuffers()


def idle():
    """Idle function"""
    glutPostRedisplay()

def keyboard(key, x, y):
    """Handle key press"""
    global camera_mode, cheat_mode, cheat_timer, magnet_mode, magnet_timer, score, coins_collected
  
    keys_pressed.add(ord(key))

    # Game restart
    if key == b'r' or key == b'R':
        reset_game()
      
    # First-person camera  (sakura)
    elif key == b'f' or key == b'F':
        camera_mode = 1
        print("First-person camera")

    # Third-person camera   (SAKURA)
    elif key == b't' or key == b'T':
        camera_mode = 0
        print("Third-person camera")
        
    # Cheat mode (20 seconds invincibility) (Rehnuma)
    elif key == b'c' or key == b'C':
        cheat_mode = True
        cheat_timer = 20.0
        print("Cheat mode activated! 20 seconds of invincibility")
    # Flying mode (20 seconds above road) (Rehnuma)
    elif key == b'j' or key == b'J':
        car['flying'] = True
        car['fly_timer'] = 20.0
        print("Flying mode activated! 20 seconds in the air")

    # Magnet mode - collect all coins for 20 seconds (Rehnuma)
    elif key == b'm' or key == b'M':
        magnet_mode = True
        magnet_timer = 20.0  # 20 seconds of enhanced collection
        print("Magnet mode activated! 20 seconds of enhanced coin collection")

def keyboardUp(key, x, y):
    """Handle key release"""
    if ord(key) in keys_pressed:
        keys_pressed.remove(ord(key))


def specialKey(key, x, y):
    """Handle special keys (arrows)"""
    special_keys_pressed.add(key)


def specialKeyUp(key, x, y):
    """Handle special key release"""
    if key in special_keys_pressed:
        special_keys_pressed.remove(key)


def main():
    """Main function"""
    print("Fast & Furious Car Chase Game!")
    print("Controls:")
    print("A - Move to Left Lane")
    print("D - Move to Right Lane")
    print("UP Arrow - Increase Speed")
    print("DOWN Arrow - Decrease Speed")
    print("C - Cheat Mode (20s invincibility)")
    print("J - Flying Mode (20s above road)")
    print("M - Magnet Mode (collect all coins)")
    print("F - First Person Camera")
    print("T - Third Person Camera")
    print("R - Restart Game")

    # Initialize game objects
    init_game_objects()

    # Initialize spawn timers
    global last_obstacle_spawn, last_enemy_spawn
    last_obstacle_spawn = time.time()
    last_enemy_spawn = time.time()

    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutCreateWindow(b"Fast & Furious Car Chase")

    # Enable depth testing and lighting
    glEnable(GL_DEPTH_TEST)

    # Set clear color
    glClearColor(0.5, 0.8, 1.0, 1.0)

    # Set callback functions
    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboardUp)
    glutSpecialFunc(specialKey)
    glutSpecialUpFunc(specialKeyUp)

    # Start main loop
    glutMainLoop()


if __name__ == "__main__":
    main()


