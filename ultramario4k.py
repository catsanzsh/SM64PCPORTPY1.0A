from ursina import *

app = Ursina()
window.fps_counter.enabled = True
window.title = 'SM64-Inspired Game'
window.borderless = False
window.vsync = True
application.development_mode = False

# Player
player = FirstPersonController(
    collider='box',
    jump_height=2.5,
    gravity=0.7,
    speed=12,
    position=(0, 10, 0)
)
player.cursor.visible = False
player.can_fly = False
player.jump_count = 0
player.on_ground_last_frame = False
player.is_swimming = False

# Terrains
ground = Entity(model='quad', color=color.green, scale=200, rotation_x=90, collider='box')
water_area = Entity(model='cube', color=color.blue, collider='box', position=(50, -5, 50), scale=(50, 10, 50), alpha=0.5)
snow_area = Entity(model='cube', color=color.white, collider='box', position=(-50, 5, -50), scale=(50, 1, 50))

# Wing Cap
class WingCap(Entity):
    def __init__(self, position):
        super().__init__(model='cube', color=color.red, position=position, collider='box', scale=1)
        self.rotation_speed = 50

    def update(self):
        self.rotation_y += self.rotation_speed * time.dt
        if self.intersects(player).hit and not player.can_fly:
            player.can_fly = True
            print_on_screen("Wing Cap Activated!", position=(-0.5, 0.4), scale=2, duration=3)
            invoke(self.remove_wing_cap, delay=15)
            self.disable()

    def remove_wing_cap(self):
        player.can_fly = False
        print_on_screen("Wing Cap Wore Off!", position=(-0.5, 0.4), scale=2, duration=3)

wing_cap = WingCap(position=(10, ground.y + 6, 10))

# Collectibles
TOTAL_STARS = 7
stars_collected = 0

class Star(Entity):
    def __init__(self, position):
        super().__init__(model='sphere', color=color.yellow, scale=0.8, collider='sphere', position=position)
        self.rotation_speed = random.uniform(80, 120)

    def update(self):
        self.rotation_y += self.rotation_speed * time.dt
        if self.intersects(player).hit:
            global stars_collected
            stars_collected += 1
            update_star_ui()
            self.disable()

star_text = Text(text=f'Stars: 0/{TOTAL_STARS}', origin=(0, -18), color=color.gold, scale=2, background=True)

def update_star_ui():
    star_text.text = f'Stars: {stars_collected}/{TOTAL_STARS}'
    if stars_collected >= TOTAL_STARS:
        Text("All stars collected!", origin=(0, 0), scale=3, color=color.cyan, background=True, duration=10)

for _ in range(TOTAL_STARS):
    Star(position=(random.uniform(-70, 70), random.uniform(5, 20), random.uniform(-70, 70)))

for _ in range(150):
    coin = Entity(model='sphere', color=color.gold, scale=0.5, collider='sphere',
                  position=(random.uniform(-78, 78), random.uniform(2, 32), random.uniform(-78, 78)))
    coin.rotation_speed = random.uniform(50, 150)
    def coin_update(self=coin):
        self.rotation_y += self.rotation_speed * time.dt
        if self.intersects(player).hit:
            self.disable()
    coin.update = coin_update

# Enemies
class Goomba(Entity):
    def __init__(self, position):
        super().__init__(model='cube', color=color.brown, collider='box', position=position, scale=(1, 1, 1))
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
            self.direction *= -1
        if self.intersects(player).hit:
            if player.y > self.world_y + self.scale_y * 0.6 and player.velocity.y < -0.05:
                self.disable()
                player.jump()
            else:
                player.position = (0, 10, 0)
                print_on_screen("You got hurt!", position=(-0.5, 0.4), scale=2, duration=2)

for _ in range(10):
    Goomba(position=(random.uniform(-70, 70), 1, random.uniform(-70, 70)))

# NPC
class NPC(Entity):
    def __init__(self, position, message="Find all the stars!"):
        super().__init__(model='cube', color=color.white, position=position, collider='box', scale=1.5)
        self.message = message
        self.talk_cooldown = 0

    def update(self):
        if self.talk_cooldown > 0:
            self.talk_cooldown -= time.dt
        if distance(self, player) < 3 and self.talk_cooldown <= 0:
            print_on_screen(self.message, position=(-0.5, 0.3), scale=1.5, duration=4)
            self.talk_cooldown = 5

npc = NPC(position=(20, ground.y + 5, 20))

# Update function
def update():
    if player.y < water_area.y + water_area.scale_y / 2 and water_area.intersects(player).hit:
        if not player.is_swimming:
            player.is_swimming = True
        player.gravity = 0.05
        player.velocity.y = clamp(player.velocity.y, -0.1, 0.1)
        if held_keys['space']:
            player.y += 2 * time.dt
        if held_keys['control'] or held_keys['c']:
            player.y -= 2 * time.dt
    else:
        if player.is_swimming:
            player.is_swimming = False
            player.gravity = 0.7

    if player.can_fly:
        player.gravity = 0
        if held_keys['space']:
            player.y += 6 * time.dt
        if held_keys['control'] or held_keys['c']:
            player.y -= 6 * time.dt
    elif not player.is_swimming:
        player.gravity = 0.7

# Input handling
def input(key):
    if key == 'space':
        if player.is_swimming or player.can_fly:
            return
        if player.grounded:
            player.jump()
            player.jump_count = 1
        elif player.jump_count < 3:
            player.jump()
            player.jump_count += 1
            if player.jump_count == 3:
                player.velocity.y *= 1.2
    if key == 'space down' and held_keys['left shift'] and player.grounded and player.velocity.xz.length() > 3:
        player.velocity = player.forward * player.speed * 1.2 + Vec3(0, player.jump_height * 0.8, 0)
        player.jump_count = 1
        print_on_screen("Long Jump!", position=(-0.5, 0.4), scale=2, duration=1)

app.run()
