import pygame
import math

pygame.init()

WIDTH = HEIGHT = 800

timestep_font = pygame.font.SysFont('comicsans', 20)
planet_data = pygame.font.SysFont('comicsans', 20)

G = 6.67e-11
AU = (149.6e6 * 1000)  # 149.6 million km, in meters.
SCALE = 250 / AU  # 1 AU = 100 pixels
TIMESTEP = 1
active = 'sun'

time_elapsed = 0
seconds_elapsed = 0
minutes_elapsed = 0
hours_elapsed = 0
days_elapsed = 0
years_elapsed = 0

time_step_preset = [-100_000, -10000, -100, 1, 2, 3, 5, 10, 25, 50, 100, 250, 500, 1000,
                    5000, 10000, 25000, 100_000, 200_000, 350_000, 500_000, 1_000_000]
time_step_preset_index = 3


WHITE = (255, 255, 255)


class Planet:
    def __init__(self, name, x, y, mass, radius, color):
        self.name = name
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = radius
        self.color = color
        self.centre_x = 0
        self.centre_y = 0
        self.distance_from_sun = 0
        self.sun = False
        self.scale = SCALE
        self.x_vel = 0
        self.y_vel = 0
        self.orbit = []
        self.active = False
        self.hitbox = pygame.Rect(
            self.x * self.scale + WIDTH//2-self.radius, self.y * self.scale + HEIGHT//2-self.radius, self.radius*2, self.radius*2)

    def draw(self, win):
        if not self.active and active == 'sun':
            if len(self.orbit) > 2:
                pygame.draw.lines(win, WHITE, False, self.orbit)

            x = self.x * self.scale + WIDTH//2
            y = self.y * self.scale + HEIGHT//2
            pygame.draw.circle(win, self.color, (x, y), self.radius)
            #pygame.draw.rect(win, 'red', self.hitbox, 2)

            fps_label = timestep_font.render(
                "FPS: "+str(round(clock.get_fps(), 2)), 1, WHITE)
            win.blit(fps_label, (WIDTH - 110, 0))

        elif self.active:
            self.centre_x, self.centre_y = 0, 0
            x = self.centre_x * self.scale + WIDTH//2
            y = self.centre_y * self.scale + HEIGHT//2
            pygame.draw.circle(win, self.color, (x, y), self.radius)

            if self.name != 'sun':
                name_label = planet_data.render(
                    "name: "+str(self.name), 1, WHITE)
                win.blit(name_label, (0, 35))

                dist_from_sun_label = planet_data.render(
                    "current distance from sun(m): "+str(self.distance_from_sun), 1, WHITE)
                win.blit(dist_from_sun_label, (0, 55))

                vel_label = planet_data.render("current orbital velocity(m/s): "+str(
                    round(math.sqrt(self.x_vel**2 + self.y_vel**2), 3)), 1, WHITE)
                win.blit(vel_label, (0, 75))

                time_warning_label = planet_data.render(
                    "time(relative to start of simulation):", 1, WHITE)
                win.blit(time_warning_label, (0, 95))

                years_label = planet_data.render(
                    "years: "+str(years_elapsed), 1, WHITE)
                win.blit(years_label, (0, 115))
                days_label = planet_data.render(
                    "days: "+str(days_elapsed), 1, WHITE)
                win.blit(days_label, (0, 135))
                hours_label = planet_data.render(
                    "hours: "+str(hours_elapsed), 1, WHITE)
                win.blit(hours_label, (0, 155))
                minutes_label = planet_data.render(
                    "minutes: "+str(minutes_elapsed), 1, WHITE)
                win.blit(minutes_label, (0, 175))
                seconds_label = planet_data.render(
                    "seconds: "+str(seconds_elapsed), 1, WHITE)
                win.blit(seconds_label, (0, 195))

                moons_label = planet_data.render(
                    "moons: "+','.join(self.moons), 1, WHITE)
                win.blit(moons_label, (0, 215))

    def attraction(self, planet):
        dx = planet.x - self.x
        dy = planet.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if planet.name == 'sun':
            self.distance_from_sun = distance

        angle = math.atan2(dy, dx)

        F = (G * planet.mass * self.mass) / (distance ** 2)

        f_x = math.cos(angle) * F
        f_y = math.sin(angle) * F
        return distance, f_x, f_y

    def update_pos(self, planets):
        fx_total = fy_total = 0
        for planet in planets:
            if planet == self:
                continue
            F, fx, fy = self.attraction(planet)
            fx_total += fx
            fy_total += fy

        # F = ma  => a = F/m
        # a = v/t => v = at
        # F = mv/t => v = Ft/m

        self.x_vel += (fx_total * TIMESTEP) / self.mass
        self.y_vel += (fy_total * TIMESTEP) / self.mass

        # v = x/t
        # x = vt

        self.x += self.x_vel * TIMESTEP
        self.y += self.y_vel * TIMESTEP
        self.hitbox = pygame.Rect(self.x * self.scale + WIDTH//2-self.radius,
                                  self.y * self.scale + HEIGHT//2-self.radius, self.radius*2, self.radius*2)
        self.orbit.append((self.x*self.scale + WIDTH//2,
                          self.y*self.scale + HEIGHT//2))

        return F, fx_total, fy_total

    def activate_planet(self):
        self.active = True
        global active
        active = self.name

    def find_moons(self, moons):
        self.moons = []
        for moon in moons:
            if self == moon.parent:
                self.moons.append(moon.name)
        if len(self.moons) == 0:
            self.moons.append("none")

        return self.moons


class Moon(Planet):
    def __init__(self, name, x, y, mass, radius, color, parent_planet):
        Planet.__init__(self, name, x, y, mass, radius, color)
        self.parent = parent_planet
        self.scale = SCALE * 100

    def draw(self, win):
        if self.parent.active:
            if len(self.orbit) > 2:
                pygame.draw.lines(win, WHITE, False, self.orbit)
            x = self.x * self.scale + WIDTH//2
            y = self.y * self.scale + HEIGHT//2
            pygame.draw.circle(win, self.color, (x, y), self.radius)

    def attraction(self):
        dx = self.parent.centre_x - self.x
        dy = self.parent.centre_y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        angle = math.atan2(dy, dx)

        F = (G * self.parent.mass * self.mass) / (distance ** 2)

        f_x = math.cos(angle) * F
        f_y = math.sin(angle) * F
        return distance, f_x, f_y

    def update_pos(self):
        dist, fx_total, fy_total = self.attraction()

        self.x_vel += (fx_total * TIMESTEP) / self.mass
        self.y_vel += (fy_total * TIMESTEP) / self.mass

        self.x += self.x_vel * TIMESTEP
        self.y += self.y_vel * TIMESTEP
        self.hitbox = pygame.Rect(self.x * self.scale + WIDTH//2-self.radius,
                                  self.y * self.scale + HEIGHT//2-self.radius, self.radius*2, self.radius*2)
        self.orbit.append((self.x*self.scale + WIDTH//2,
                          self.y*self.scale + HEIGHT//2))

        return dist, fx_total, fy_total


def orbital_velocity(dist, mass):
    return ((G * mass)/dist)**0.5


def collision(planets):
    for planet in planets:
        for planet2 in planets:
            if planet == planet2:
                continue
            if planet.hitbox.colliderect(planet2.hitbox):
                if planet.mass > planet2.mass:
                    planet.mass += planet2.mass
                    planets.remove(planet2)

    return planets


# Sun
sun = Planet('sun', 0, 0, 1.98e30, 30, 'yellow')
sun.sun = True

# Planets
earth = Planet('earth', -AU, 0, 5.97e24, 15, 'light blue')
earth.y_vel = -29.78e3
earth.y_vel = -orbital_velocity(-earth.x, sun.mass)

mars = Planet('mars', -1.5 * AU, 0, 6.39e23, 13, 'red')
mars.y_vel = -24.07e3

venus = Planet('venus', -0.72 * AU, 0, 4.86e24, 14, 'beige')
venus.y_vel = -35.02e3

mercury = Planet('mercury', -0.38 * AU, 0, 3.30e23, 10, 'light grey')
mercury.y_vel = -47.36e3

fat_man = Planet('little boy', -0.35 * AU, 0, 1.9e27, 20, (170, 140, 120))
fat_man.y_vel = -orbital_velocity(-fat_man.x, sun.mass)

planets = [sun, mercury, venus, earth, mars]
# planets = [sun, fat_man, venus, earth, mars]

# Moons
luna = Moon('luna', -0.0025*AU, 0, 7.34e22, 5, 'white', earth)
luna.y_vel = -orbital_velocity(-luna.x, earth.mass)

phobos = Moon('phobos', -0.001 * AU, 0, 1.06e16, 5, (160, 130, 110), mars)
phobos.y_vel = -orbital_velocity(-phobos.x, mars.mass)

deimos = Moon('deimos', -0.0045 * AU, 0, 1.06e15, 3, (185, 185, 170), mars)
deimos.y_vel = -orbital_velocity(-deimos.x, mars.mass)

pain = Moon('earth', -0.0045 * AU, 0, earth.mass, earth.radius, earth.color, fat_man)
pain.y_vel = -orbital_velocity(-pain.x, fat_man.mass)


moons = [luna, phobos, deimos, pain]

win = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()
run = True
while run:
    clock.tick(60)
    win.fill((0, 0, 0))
    timestep_label = timestep_font.render(
        "Timestep: x"+str(TIMESTEP), 1, 'white')
    win.blit(timestep_label, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if time_step_preset_index > 0:
                    time_step_preset_index -= 1
                    TIMESTEP = time_step_preset[time_step_preset_index]
            if event.key == pygame.K_RIGHT:
                if time_step_preset_index + 1 < len(time_step_preset):
                    time_step_preset_index += 1
                    TIMESTEP = time_step_preset[time_step_preset_index]
            if event.key == pygame.K_LSHIFT:
                for planet in planets:
                    planet.active = False
                sun.activate_planet()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if active == 'sun':
                for planet in planets:
                    if planet.hitbox.collidepoint(*pygame.mouse.get_pos()):
                        selected = planet
                        for planet in planets:
                            planet.active = False
                        selected.activate_planet()
                        break

    for planet in planets:
        planet.update_pos(planets)
        planet.moons = planet.find_moons(moons)
        planet.draw(win)

    for moon in moons:
        moon.update_pos()
        moon.draw(win)

    time_elapsed += TIMESTEP

    seconds_elapsed = time_elapsed

    # only 360 days | 3.154e7 == 365 days
    years_elapsed = round(seconds_elapsed // (3600*24*30*12))
    seconds_elapsed %= (3600*24*30*12)

    days_elapsed = round(seconds_elapsed // (3600*24))
    seconds_elapsed %= (3600*24)

    hours_elapsed = round(seconds_elapsed // 3600)
    seconds_elapsed %= 3600

    minutes_elapsed = round(seconds_elapsed // 60)

    seconds_elapsed = round(seconds_elapsed % 60)

##    planets = collision(planets)

    pygame.display.update()

pygame.quit()
