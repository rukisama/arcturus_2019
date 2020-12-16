import tcod
import tcod.event
from random import randint, choice

width = 96
height = 54
title = "Test"
vsync = True
order = "F"
renderer = tcod.RENDERER_OPENGL2


class Particle:
    def __init__(self, xo, yo, xd, yd):
        self.step = 0
        path = list(tcod.line_iter(xo, yo, xd, yd))

        if randint(0, 1) == 0:  # "Close" star
            self.glyph = ord('.')
            self.color = (255, 255, 255)  # choice([(128, 128, 255), (255, 255, 0), (255, 128, 128), (255, 255, 255)])
            slow_path = [point for point in path[0:len(path)//4] for _ in (0, 1)]
            fast_path = path[len(path)//4:]

            full_path = slow_path + fast_path

            self.path = full_path[randint(0,4):]
        else:  # "Far" star
            self.glyph = ord('.')
            self.color = (191, 191, 191)  # choice([(64, 64, 128), (128, 128, 0), (128, 64, 64), (128, 128, 128)])
            path = path[len(path)//randint(3, 4):]
            self.path = [point for point in path for _ in (0, 1)]

    def next(self):
        self.step += 1
        if self.step >= len(self.path):
            raise StopIteration

        return self.path[self.step-1]

    def print_path(self):
        print(self.path)


def main():

    tcod.console_set_custom_font("potash_10x10.png", tcod.FONT_LAYOUT_ASCII_INROW | tcod.FONT_TYPE_GREYSCALE)
    root_console = tcod.console_init_root(width, height, title, renderer=renderer, order=order, vsync=vsync)
    tcod.sys_set_fps(30)

    num_particles = randint(35, 100)

    edges = []
    for x in range(0, width):
        edges.append((x, 0))
        edges.append((x, height-1))
    for y in range(0, height):
        edges.append((0, y))
        edges.append((width-1, y))

    p_list = []
    for i in range(num_particles):
        xo = width // 2
        yo = height // 2
        xd, yd = choice(edges)
        p_list.append(Particle(xo, yo, xd, yd))

    # for p in p_list:
    #     p.print_path()

    while True:
        for event in tcod.event.get():
            if event.type == "QUIT" or (event.type == "KEYDOWN" and event.sym == tcod.event.K_ESCAPE):
                raise SystemExit()

        # Test code here

        for particle in p_list:
            try:
                x, y = particle.next()
                root_console.ch[x, y] = particle.glyph
                root_console.fg[x, y] = particle.color
            except StopIteration:
                p_list.remove(particle)
                xo = width // 2
                yo = height // 2
                xd, yd = choice(edges)
                p_list.append(Particle(xo, yo, xd, yd))
                if len(p_list) > 100:
                    p_list = p_list[0:100]

        root_console.ch[width // 2, height // 2] = 0
        root_console.ch[width // 2 - 3:width // 2 + 3, height // 2] = 0
        root_console.ch[width // 2, height // 2 - 3:height // 2 + 3] = 0
        root_console.ch[width // 2 - 2:width // 2 + 3, height // 2 - 2:height // 2 + 3] = 0

        tcod.console_flush()
        root_console.clear()


if __name__ == '__main__':
    main()
