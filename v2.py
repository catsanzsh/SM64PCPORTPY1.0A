from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import random

# Initialize Ursina app
app = Ursina()

# SM64-inspired sky
Sky(color=color.rgba(random.randint(50, 150), random.randint(50, 150), random.randint(150, 255), 255))

# Player with SM64-like movement
player = FirstPersonController(
    collider='box',
    jump_height=2.5,
    gravity=0.7,
    speed=12,
    position=(0, 10, 0)
)
player.cursor.visible = False
player.gun = None
player.can_fly = False  # For Wing Cap
player.jump_count = 0   # For triple jump

# Ground plane (Bob-omb Battlefield-inspired)
ground = Entity(
    model='quad',
    color=color.hex('8c5a2b'),
    scale=200,
    rotation_x=90,
    collider='box',
    texture='white_cube',
    shader=lit_with_shadows_shader
)
ground.texture_scale = (ground.scale_x / 10, ground.scale_z / 10)

# Themed areas
water_area = Entity(
    model='cube',
    color=color.blue,
    collider='box',
    position=(50, -5, 50),
    scale=(50, 1, 50)
)

snow_area = Entity(
    model='cube',
    color=color.white,
    collider='box',
    position=(-50, 5, -50),
    scale=(50, 1, 50)
)

# Power-Ups (Wing Cap)
class WingCap(Entity):
    def __init__(self, position):
        super().__init__(
            model='cube',
            color=color.red,
            position=position,
            collider='box',
            scale=1
        )

    def update(self):
        if self.intersects(player).hit:
            player.can_fly = True
            invoke(lambda: setattr(player, 'can_fly', False), delay=10)  # 10-second duration
            self.disable()

wing_cap = WingCap(position=(10, 5, 10))

# Stars
TOTAL_STARS = 7
stars_collected = 0
star_entities = []

class Star(Entity):
    def __init__(self, position=(0, 1, 0)):
        super().__init__(
            model='sphere',
            color=color.yellow,
            scale=0.8,
            collider='sphere',
            position=position,
            shader=lit_with_shadows_shader
        )
        self.id = f"STAR_{random.randint(1000, 9999)}"
        self.collected = False
        self.rotation_speed = random.uniform(80, 120)

    def update(self):
        self.rotation_y += self.rotation_speed * time.dt
        if not self.collected and self.intersects(player).hit:
            self.collected = True
            self.disable()
            global stars_collected
            stars_collected += 1
            update_star_ui()

# Star UI
star_text = Text(text=f'Stars: 0/{TOTAL_STARS}', origin=(0, -18), color=color.gold, scale=2, background=True)

def update_star_ui():
    star_text.text = f'Stars: {stars_collected}/{TOTAL_STARS}'
    if stars_collected >= TOTAL_STARS:
        Text("All stars collected! Well done!", origin=(0,0), scale=3, color=color.cyan, background=True, lifetime=10)

# Platforms
num_platforms = 70
platform_list = []

for i in range(num_platforms // 2):  # Whomp's Fortress style
    platform = Entity(
        model='cube',
        color=color.gray,
        collider='box',
        position=(random.uniform(-80, 80), random.uniform(1, 30), random.uniform(-80, 80)),
        scale=(random.uniform(5, 15), random.uniform(1, 3), random.uniform(5, 15)),
        shader=lit_with_shadows_shader
    )
    platform_list.append(platform)
    if random.random() < 0.2:
        direction = random.choice([Vec3(random.uniform(-5, 5), 0, 0), Vec3(0, random.uniform(-3, 3), 0)])
        platform.animate_position(platform.position + direction, duration=random.uniform(3, 6), loop=True, curve=curve.in_out_sine)

for i in range(num_platforms // 2):  # Bob-omb Battlefield style
    platform = Entity(
        model='cube',
        color=color.green,
        collider='box',
        position=(random.uniform(-80, 80), random.uniform(1, 25), random.uniform(-80, 80)),
        scale=(random.uniform(3, 10), random.uniform(0.5, 2), random.uniform(3, 10)),
        shader=lit_with_shadows_shader
    )
    platform_list.append(platform)

# Coins
num_coins = 150
for _ in range(num_coins):
    chosen_platform = random.choice(platform_list) if platform_list else None
    if chosen_platform:
        coin_pos = (
            chosen_platform.x + random.uniform(-chosen_platform.scale_x / 2.1, chosen_platform.scale_x / 2.1),
            chosen_platform.y + chosen_platform.scale_y / 2 + 0.5,
            chosen_platform.z + random.uniform(-chosen_platform.scale_z / 2.1, chosen_platform.scale_z / 2.1)
        )
    else:
        coin_pos = (random.uniform(-78, 78), random.uniform(2, 32), random.uniform(-78, 78))
    coin = Entity(
        model='sphere',
        color=color.gold,
        scale=0.5,
        collider='sphere',
        position=coin_pos,
        shader=lit_with_shadows_shader
    )
    coin.rotation_speed = random.uniform(50, 150)
    coin.update = lambda: setattr(coin, 'rotation_y', coin.rotation_y + coin.rotation_speed * time.dt)

# Enemies
class Goomba(Entity):
    def __init__(self, position=(0, 1, 0)):
        super().__init__(
            model='cube',
            color=color.brown,
            collider='box',
            position=position,
            scale=(1, 1, 1),
            shader=lit_with_shadows_shader
        )
        self.speed = random.uniform(1, 3)
        self.direction = random.choice([Vec3(1, 0, 0), Vec3(-1, 0, 0), Vec3(0, 0, 1), Vec3(0, 0, -1)])
        self.move_timer = random.uniform(2, 5)
        self.health = 1

    def update(self):
        if self.health <= 0:
            return
        self.move_timer -= time.dt
        if self.move_timer <= 0:
            self.direction = random.choice([Vec3(1, 0, 0), Vec3(-1, 0, 0), Vec3(0, 0, 1), Vec3(0, 0, -1)])
            self.move_timer = random.uniform(2, 5)
        self.position += self.direction * self.speed * time.dt
        if self.x > 90 or self.x < -90 or self.z > 90 or self.z < -90:
            self.direction = -self.direction
        if self.intersects(player).hit:
            if player.y > self.world_y + self.scale_y * 0.7 and player.velocity.y < -0.1:
                self.disable()
                self.health = 0
            else:
                player.position = (random.uniform(-5, 5), 10, random.uniform(-5, 5))

class Bobomb(Entity):
    def __init__(self, position=(0, 1, 0)):
        super().__init__(
            model='sphere',
            color=color.black,
            collider='sphere',
            position=position,
            scale=0.7,
            shader=lit_with_shadows_shader
        )
        self.fuse_lit = False
        self.fuse_time = 3
        self.explosion_radius = 5

    def update(self):
        if self.disabled:
            return
        if self.fuse_lit:
            self.fuse_time -= time.dt
            self.color = color.lerp(color.black, color.rgb(255, random.randint(0, 50), 0), 1 - (self.fuse_time / 3))
            if self.fuse_time <= 0:
                self.explode()
        elif distance(self.world_position, player.world_position) < 4:
            self.fuse_lit = True

    def explode(self):
        if self.disabled:
            return
        explosion_effect = Entity(
            model='sphere',
            color=color.rgba(255, 100, 0, 200),
            scale=self.explosion_radius,
            lifetime=0.5,
            shader=lit_with_shadows_shader
        )
        explosion_effect.animate_scale(self.explosion_radius * 1.5, duration=0.5, curve=curve.out_expo)
        explosion_effect.fade_out(duration=0.5)
        if distance(self.world_position, player.world_position) < self.explosion_radius:
            player.position = (random.uniform(-5, 5), 10, random.uniform(-5, 5))
        self.disable()

class Koopa(Entity):
    def __init__(self, position):
        super().__init__(
            model='cube',
            color=color.green,
            position=position,
            collider='box',
            scale=(1, 1, 1)
        )
        self.speed = 2

    def update(self):
        direction = (player.position - self.position).normalized()
        self.position += direction * self.speed * time.dt
        if self.intersects(player).hit:
            player.position = (0, 10, 0)

# NPC
class NPC(Entity):
    def __init__(self, position):
        super().__init__(
            model='cube',
            color=color.white,
            position=position,
            collider='box',
            scale=1
        )
        self.message = "Find all the stars!"

    def update(self):
        if distance(self, player) < 2:
            print(self.message)

# Spawn entities
for pos in [(p.x + random.uniform(-p.scale_x / 2, p.scale_x / 2), p.y + p.scale_y / 2 + 1.5, p.z + random.uniform(-p.scale_z / 2, p.scale_z / 2)) for p in random.sample(platform_list, min(TOTAL_STARS, len(platform_list)))]:
    star_entities.append(Star(position=pos))

for _ in range(10):  # Goombas
    p = random.choice(platform_list)
    Goomba(position=(p.x, p.y + p.scale_y / 2 + 0.51, p.z))

for _ in range(5):  # Bob-ombs
    p = random.choice(platform_list)
    Bobomb(position=(p.x, p.y + p.scale_y / 2 + 0.36, p.z))

for _ in range(3):  # Koopas
    p = random.choice(platform_list)
    Koopa(position=(p.x, p.y + p.scale_y / 2 + 0.5, p.z))

npc = NPC(position=(20, 5, 20))

# Camera system
camera.parent = player
camera.position = (0, 5, -10)
camera.rotation_x = 20

# Player update for swimming and flying
def update():
    if player.y < water_area.y + water_area.scale_y / 2:
        player.gravity = 0.1  # Swimming
    else:
        player.gravity = 0.7
    if player.can_fly and held_keys['space']:
        player.y += 0.1
    # Long jump
    if held_keys['shift'] and player.grounded:
        player.velocity.x *= 1.5
        player.velocity.z *= 1.5

# Input handling
def input(key):
    if key == 'escape':
        application.quit()

# Setup
window.fps_counter.enabled = True
window.title = 'SM64-Inspired Python Port'
window.borderless = False
sun = DirectionalLight(shadows=True)
sun.look_at(Vec3(1, -1, -1))
update_star_ui()

app.run()
