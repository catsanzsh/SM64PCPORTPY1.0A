from ursina import *
from ursina.shaders import basic_lighting_shader
import math

app = Ursina()

# Constants
GRAVITY = 1.5
WALK_SPEED = 4
RUN_SPEED = 8
JUMP_FORCE = 12
AIR_CONTROL = 0.8
CAM_DISTANCE = 6

# Game State
stars_collected = 0
coins = 0
health = 8

class Mario(Entity):
    def __init__(self):
        super().__init__(
            model='sphere',
            color=color.red,
            scale=(1,2,1),
            collider='box',
            position=(0, 10, 0),
            shader=basic_lighting_shader
        )
        self.velocity = Vec3(0)
        self.speed = WALK_SPEED
        self.jump_height = JUMP_FORCE
        self.grounded = False
        self.can_double_jump = True
        self.rotation_speed = 150

    def update(self):
        self.rotation_y += held_keys['d'] * self.rotation_speed * time.dt
        self.rotation_y -= held_keys['a'] * self.rotation_speed * time.dt
        
        move_dir = self.forward * held_keys['w'] + self.back * held_keys['s']
        move_dir += self.right * held_keys['d'] + self.left * held_keys['a']
        
        if self.grounded:
            self.velocity = move_dir * self.speed
        else:
            self.velocity += move_dir * self.speed * AIR_CONTROL * time.dt

        self.velocity.y -= GRAVITY * time.dt
        self.position += self.velocity * time.dt

        ray = raycast(self.position, self.down, distance=2.1)
        self.grounded = ray.hit
        if self.grounded:
            self.can_double_jump = True

    def jump(self):
        if self.grounded:
            self.velocity.y = self.jump_height
            self.grounded = False
        elif self.can_double_jump:
            self.velocity.y = self.jump_height * 0.8
            self.can_double_jump = False

# Setup
player = Mario()
camera.position = (0, 6, -CAM_DISTANCE)
camera.rotation_x = 20

# Lighting
DirectionalLight(color=color.white, direction=(1,-1,1))
AmbientLight(color=color.gray.tint(-0.5))

# Level Geometry
ground = Entity(
    model='plane',
    texture='white_cube',
    color=color.green,
    scale=(100,1,100),
    collider='mesh'
)

castle = Entity(
    model='cube',
    color=color.gray,
    scale=(10,20,10),
    position=(0,10,50),
    collider='box'
)

platforms = [
    Entity(model='cube', color=color.blue, scale=(5,1,5), position=(15,5,20), collider='box'),
    Entity(model='cube', color=color.blue, scale=(5,1,5), position=(-15,10,30), collider='box'),
    Entity(model='cube', color=color.blue, scale=(5,1,5), position=(0,15,40), collider='box'),
]

# Collectibles
class Star(Entity):
    def __init__(self, position):
        super().__init__(
            model='sphere',
            color=color.yellow,
            scale=2,
            position=position,
            collider='sphere',
            shader=basic_lighting_shader
        )
        
stars = [
    Star((0, 20, 50)),
    Star((15, 10, 20)),
    Star((-15, 15, 30))
]

class Coin(Entity):
    def __init__(self, position):
        super().__init__(
            model='sphere',
            color=color.gold,
            scale=1,
            position=position,
            collider='sphere',
            shader=basic_lighting_shader
        )

coins = [Coin((x*2, 3, z*2)) for x in range(-10,10) for z in range(-10,10)]

# UI
health_text = Text(text=f"Health: {health}", origin=(-0.85, 0.45), scale=2)
coin_text = Text(text=f"Coins: {coins}", origin=(-0.85, 0.4), scale=2)
star_text = Text(text=f"Stars: {stars_collected}", origin=(-0.85, 0.35), scale=2)

# Physics
def update():
    camera.position = lerp(camera.position, player.position + (0,6,-CAM_DISTANCE), 5*time.dt)
    camera.rotation_x = lerp(camera.rotation_x, 20, 5*time.dt)
    
    if held_keys['shift']:
        player.speed = RUN_SPEED
    else:
        player.speed = WALK_SPEED

def input(key):
    if key == 'space':
        player.jump()

# Collisions
def on_collision(e1, e2):
    global stars_collected, coins
    if e1 == player:
        if isinstance(e2, Star):
            stars_collected += 1
            destroy(e2)
        elif isinstance(e2, Coin):
            coins += 1
            destroy(e2)

app.run()
