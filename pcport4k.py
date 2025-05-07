# test.py - Inspired by Mario 64, created with passion!
# Developed using CATSDK's tools for an authentic experience.
# Every detail is crafted to bring the essence of SM64 to life.
# No static images, all procedural generation for smooth 60 FPS gameplay.

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import random

# Initialize the Ursina app for our SM64-inspired world.
app = Ursina()

# Create a sky with a color reminiscent of SM64's skyboxes.
Sky(color=color.rgba(random.randint(50, 150), random.randint(50, 150), random.randint(150, 255), 255))

# Set up the player controller with properties inspired by Mario's movement in SM64.
player = FirstPersonController(
    collider='box',
    jump_height=2.5,  # Adjusted for a Mario-like jump feel.
    gravity=0.7,      # Gravity similar to SM64.
    speed=12,         # Speed to match the fast-paced action.
    position=(0, 10, 0)  # Starting position elevated for a vast world.
)
player.cursor.visible = False  # Hide the cursor for immersive gameplay.
player.gun = None  # No gun, staying true to Mario's character.

# Create a large ground plane inspired by Bob-omb Battlefield.
ground = Entity(
    model='quad',
    color=color.hex('8c5a2b'),  # Earthy color for a natural look.
    scale=200,
    rotation_x=90,
    collider='box',
    texture='white_cube',
    shader=lit_with_shadows_shader
)
ground.texture_scale = (ground.scale_x / 10, ground.scale_z / 10)  # Tiled texture for retro aesthetics.

# --- Power Stars ---
# Inspired by the collectible stars in SM64.
TOTAL_STARS = 7  # Number of stars to collect in this version.
stars_collected = 0
star_entities = []  # List to hold star entities.

class Star(Entity):
    def __init__(self, position=(0, 1, 0)):
        super().__init__(
            model='sphere',  # Placeholder for the actual star model.
            color=color.yellow,
            scale=0.8,
            collider='sphere',
            position=position,
            shader=lit_with_shadows_shader  # Enhanced lighting for visual appeal.
        )
        self.id = f"STAR_{random.randint(1000, 9999)}"  # Unique identifier for the star.
        self.collected = False
        self.rotation_speed = random.uniform(80, 120)  # Rotation speed for visual effect.
        print(f"Star created at {position} with ID: {self.id}")

    def update(self):
        self.rotation_y += self.rotation_speed * time.dt  # Rotate the star.
        if not self.collected and self.intersects(player).hit:
            print(f"Player collected Star {self.id}")
            self.collected = True
            self.disable()  # Remove the star from the scene.
            global stars_collected
            stars_collected += 1
            update_star_ui()
            # TODO: Add sound effect for collecting a star.

# UI for Stars - Inspired by the interface in SM64.
star_text = Text(text=f'Stars: 0/{TOTAL_STARS}', origin=(0, -18), color=color.gold, scale=2, background=True)

def update_star_ui():
    star_text.text = f'Stars: {stars_collected}/{TOTAL_STARS}'
    if stars_collected >= TOTAL_STARS:
        Text("All stars collected! Well done!", origin=(0,0), scale=3, color=color.cyan, background=True, lifetime=10)
        # Here you could trigger a "game end" or "next level" event.

# --- Platforms and Level Chunks ---
# Procedurally generated platforms inspired by SM64's level design.
num_platforms = 70  # Number of platforms to generate.
platform_list = []

# Generate platforms similar to Whomp's Fortress.
print("Generating platforms inspired by Whomp's Fortress.")
for i in range(num_platforms // 2):
    platform = Entity(
        model='cube',
        color=color.gray,  # Gray color for a stone-like appearance.
        collider='box',
        position=(
            random.uniform(-80, 80),
            random.uniform(1, 30),
            random.uniform(-80, 80)
        ),
        scale=(random.uniform(5, 15), random.uniform(1, 3), random.uniform(5, 15)),
        shader=lit_with_shadows_shader
    )
    platform_list.append(platform)
    # Add movement to some platforms for dynamic gameplay.
    if random.random() < 0.2:
        if random.random() < 0.5:
            platform.animate_position(
                platform.position + Vec3(random.uniform(-5, 5), 0, 0),
                duration=random.uniform(3, 6),
                loop=True,
                curve=curve.in_out_sine
            )
        else:
            platform.animate_position(
                platform.position + Vec3(0, random.uniform(-3, 3), 0),
                duration=random.uniform(3, 6),
                loop=True,
                curve=curve.in_out_sine
            )

# Generate platforms similar to Bob-omb Battlefield.
print("Generating platforms inspired by Bob-omb Battlefield.")
for i in range(num_platforms // 2):
    platform = Entity(
        model='cube',
        color=color.green,  # Green color for a grassy appearance.
        collider='box',
        position=(
            random.uniform(-80, 80),
            random.uniform(1, 25),
            random.uniform(-80, 80)
        ),
        scale=(random.uniform(3, 10), random.uniform(0.5, 2), random.uniform(3, 10)),
        shader=lit_with_shadows_shader
    )
    platform_list.append(platform)

# --- Coins ---
num_coins = 150  # Number of coins to spawn.
print(f"Spawning {num_coins} coins throughout the level.")
for _ in range(num_coins):
    # Place coins on platforms if available.
    chosen_platform = random.choice(platform_list) if platform_list else None
    if chosen_platform:
        coin_pos_y = chosen_platform.y + chosen_platform.scale_y / 2 + 0.5
        coin_pos_x = chosen_platform.x + random.uniform(-chosen_platform.scale_x / 2.1, chosen_platform.scale_x / 2.1)
        coin_pos_z = chosen_platform.z + random.uniform(-chosen_platform.scale_z / 2.1, chosen_platform.scale_z / 2.1)
        coin_pos = (coin_pos_x, coin_pos_y, coin_pos_z)
    else:
        coin_pos = (random.uniform(-78, 78), random.uniform(2, 32), random.uniform(-78, 78))

    coin = Entity(
        model='sphere',  # Placeholder for coin model.
        color=color.gold,
        scale=0.5,
        collider='sphere',
        position=coin_pos,
        shader=lit_with_shadows_shader
    )
    coin.rotation_speed = random.uniform(50, 150)
    def update_coin_rotation(c=coin):
        c.rotation_y += c.rotation_speed * time.dt
    coin.update = update_coin_rotation

# --- Enemies (Goombas, Bob-ombs) ---
# Inspired by the enemies in SM64.

class Goomba(Entity):
    def __init__(self, position=(0, 1, 0)):
        super().__init__(
            model='cube',  # Placeholder for Goomba model.
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
        print(f"Goomba spawned at {position}")

    def update(self):
        if self.health <= 0:
            return

        self.move_timer -= time.dt
        if self.move_timer <= 0:
            self.direction = random.choice([Vec3(1, 0, 0), Vec3(-1, 0, 0), Vec3(0, 0, 1), Vec3(0, 0, -1)])
            self.move_timer = random.uniform(2, 5)

        self.position += self.direction * self.speed * time.dt

        # Basic boundary check
        if self.x > 90 or self.x < -90 or self.z > 90 or self.z < -90:
            self.position -= self.direction * self.speed * time.dt
            self.direction = -self.direction

        # Check for player collision
        hit_info = self.intersects(player)
        if hit_info.hit:
            if player.y > self.world_y + self.scale_y * 0.7 and player.velocity.y < -0.1:
                print("Player stomped a Goomba")
                self.disable()
                self.health = 0
                # TODO: Add coin spawn or sound effect.
            else:
                print("Player hit by a Goomba")
                player.position = (random.uniform(-5, 5), 10, random.uniform(-5, 5))
                # TODO: Add damage sound effect.

class Bobomb(Entity):
    def __init__(self, position=(0, 1, 0)):
        super().__init__(
            model='sphere',  # Placeholder for Bob-omb model.
            color=color.black,
            collider='sphere',
            position=position,
            scale=0.7,
            shader=lit_with_shadows_shader
        )
        self.fuse_lit = False
        self.fuse_time = 3
        self.explosion_radius = 5
        print(f"Bob-omb spawned at {position}")

    def update(self):
        if self.disabled:
            return

        if self.fuse_lit:
            self.fuse_time -= time.dt
            # Flash redder as the fuse burns
            self.color = color.lerp(color.black, color.rgb(255, random.randint(0, 50), 0), 1 - (self.fuse_time / 3))
            if self.fuse_time <= 0:
                self.explode()
        elif not self.disabled and distance(self.world_position, player.world_position) < 4:
            print("Bob-omb fuse lit")
            self.fuse_lit = True
            # TODO: Add particle effect for fuse spark.

    def explode(self):
        if self.disabled:
            return
        print("Bob-omb exploded")
        # Create explosion effect
        explosion_effect = Entity(
            model='sphere',
            color=color.rgba(255, 100, 0, 200),
            scale=self.explosion_radius,
            lifetime=0.5,
            shader=lit_with_shadows_shader
        )
        explosion_effect.animate_scale(self.explosion_radius * 1.5, duration=0.5, curve=curve.out_expo)
        explosion_effect.fade_out(duration=0.5)

        # Check if player is within explosion radius
        if distance(self.world_position, player.world_position) < self.explosion_radius:
            print("Player caught in Bob-omb blast")
            player.position = (random.uniform(-5, 5), 10, random.uniform(-5, 5))
            # TODO: Add explosion sound effect.

        # Check other entities
        for e in scene.entities:
            if isinstance(e, Goomba) and e.enabled and distance(self.world_position, e.world_position) < self.explosion_radius:
                print("Goomba caught in blast")
                e.disable()
                e.health = 0
            if isinstance(e, Bobomb) and e.enabled and e != self and distance(self.world_position, e.world_position) < self.explosion_radius:
                if not e.fuse_lit:
                    print("Another Bob-omb caught in blast, lighting its fuse")
                    e.fuse_lit = True

        self.disable()

# --- Spawn Entities ---
# Spawn stars in reachable locations.
star_positions = []
print("Calculating star positions.")
for _ in range(TOTAL_STARS):
    if platform_list:
        p = random.choice(platform_list)
        pos = (
            p.x + random.uniform(-p.scale_x / 2, p.scale_x / 2),
            p.y + p.scale_y / 2 + 1.5,
            p.z + random.uniform(-p.scale_z / 2, p.scale_z / 2)
        )
        star_positions.append(pos)
    else:
        star_positions.append((random.uniform(-30, 30), random.uniform(5, 15), random.uniform(-30, 30)))

for pos in star_positions:
    star_entities.append(Star(position=pos))

update_star_ui()  # Initialize UI

# Spawn Goombas
num_goombas = 10
print(f"Spawning {num_goombas} Goombas.")
for _ in range(num_goombas):
    if platform_list:
        p = random.choice(platform_list)
        pos = (
            p.x + random.uniform(-p.scale_x / 2.1, p.scale_x / 2.1),
            p.y + p.scale_y / 2 + 0.51,
            p.z + random.uniform(-p.scale_z / 2.1, p.scale_z / 2.1)
        )
        Goomba(position=pos)
    else:
        Goomba(position=(random.uniform(-30, 30), 1, random.uniform(-30, 30)))

# Spawn Bob-ombs
num_bobombs = 5
print(f"Spawning {num_bobombs} Bob-ombs.")
for _ in range(num_bobombs):
    if platform_list:
        p = random.choice(platform_list)
        pos = (
            p.x + random.uniform(-p.scale_x / 2.1, p.scale_x / 2.1),
            p.y + p.scale_y / 2 + 0.36,
            p.z + random.uniform(-p.scale_z / 2.1, p.scale_z / 2.1)
        )
        Bobomb(position=pos)
    else:
        Bobomb(position=(random.uniform(-30, 30), 0.7, random.uniform(-30, 30)))

# Enable FPS counter and set window title
window.fps_counter.enabled = True
window.title = 'SM64-Inspired Python Port'
window.borderless = False

# Enable shadows for better visuals
sun = DirectionalLight(shadows=True)
sun.look_at(Vec3(1, -1, -1))

# Input handling
def input(key):
    if key == 'escape':
        application.quit()

# Run the game
print("Starting the game. Enjoy!")
app.run()
