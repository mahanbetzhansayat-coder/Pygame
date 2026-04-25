import pygame, sys

pygame.init()

w, h = 800, 600 
screen = pygame.display.set_mode((w, h))
pygame.display.set_caption("lab11_paint_geometry")
clk = pygame.time.Clock()
fnt = pygame.font.SysFont("Verdana", 14)

surf = pygame.Surface((w, h))
surf.fill((255, 255, 255)) 

cc = (0, 0, 0)
tool = "brush" 
size = 5
flag = False 
x1, y1 = 0, 0 

colors_gui = [
    (pygame.Rect(10, 10, 30, 30), (0, 0, 0)),
    (pygame.Rect(50, 10, 30, 30), (255, 0, 0)),
    (pygame.Rect(90, 10, 30, 30), (0, 255, 0)),
    (pygame.Rect(130, 10, 30, 30), (0, 0, 255))
]

# добавил новые фигуры в два ряда
tools_gui = [
    (pygame.Rect(200, 10, 60, 25), "brush"),
    (pygame.Rect(270, 10, 60, 25), "eraser"),
    (pygame.Rect(340, 10, 60, 25), "rect"),
    (pygame.Rect(410, 10, 60, 25), "circle"),
    
    # второй ряд для лабы 11
    (pygame.Rect(200, 40, 60, 25), "square"),
    (pygame.Rect(270, 40, 60, 25), "r_tri"),
    (pygame.Rect(340, 40, 60, 25), "eq_tri"),
    (pygame.Rect(410, 40, 60, 25), "rhomb")
]

def render_ui():
    pygame.draw.rect(screen, (200, 200, 200), (0, 0, w, 75)) # шапку сделал повыше
    
    for r, c in colors_gui:
        pygame.draw.rect(screen, c, r)
        if c == cc and tool != "eraser":
            pygame.draw.rect(screen, (255, 255, 255), r, 3) 

    for r, t in tools_gui:
        bg = (150, 150, 150) if t == tool else (100, 100, 100)
        pygame.draw.rect(screen, bg, r)
        txt = fnt.render(t, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=r.center))

def draw_shape(surface, t, c, start_x, start_y, end_x, end_y, s):
    # универсальная функция отрисовки шоб не дублировать код
    if t == "rect":
        pygame.draw.rect(surface, c, (start_x, start_y, end_x - start_x, end_y - start_y), s)
    elif t == "circle":
        r = int(((end_x - start_x)**2 + (end_y - start_y)**2)**0.5)
        pygame.draw.circle(surface, c, (start_x, start_y), r, s)
    elif t == "square":
        # квадрат - это прямоугольник с равными сторонами
        side = max(abs(end_x - start_x), abs(end_y - start_y))
        sx = 1 if end_x > start_x else -1
        sy = 1 if end_y > start_y else -1
        pygame.draw.rect(surface, c, (start_x, start_y, side * sx, side * sy), s)
    elif t == "r_tri":
        # прямоугольный треугольник
        pygame.draw.polygon(surface, c, [(start_x, start_y), (start_x, end_y), (end_x, end_y)], s)
    elif t == "eq_tri":
        # равносторонний (ну почти, равнобедренный)
        mid_x = start_x + (end_x - start_x) // 2
        pygame.draw.polygon(surface, c, [(mid_x, start_y), (start_x, end_y), (end_x, end_y)], s)
    elif t == "rhomb":
        # ромб
        mid_x = start_x + (end_x - start_x) // 2
        mid_y = start_y + (end_y - start_y) // 2
        pygame.draw.polygon(surface, c, [(mid_x, start_y), (end_x, mid_y), (mid_x, end_y), (start_x, mid_y)], s)

while 1: 
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            sys.exit() 
            
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1: 
                if e.pos[1] < 75: 
                    for r, c in colors_gui:
                        if r.collidepoint(e.pos):
                            cc = c
                            if tool == "eraser": tool = "brush" 
                                
                    for r, t in tools_gui:
                        if r.collidepoint(e.pos):
                            tool = t
                else:
                    flag = True
                    x1, y1 = e.pos

        elif e.type == pygame.MOUSEBUTTONUP:
            if e.button == 1 and flag:
                flag = False
                draw_shape(surf, tool, cc, x1, y1, e.pos[0], e.pos[1], size)

        elif e.type == pygame.MOUSEMOTION:
            if flag:
                if tool == "brush":
                    pygame.draw.circle(surf, cc, e.pos, size)
                elif tool == "eraser":
                    pygame.draw.circle(surf, (255, 255, 255), e.pos, size * 4)

    screen.blit(surf, (0, 0))

    if flag:
        mx, my = pygame.mouse.get_pos()
        draw_shape(screen, tool, cc, x1, y1, mx, my, size)

    render_ui()
    pygame.display.update()
    clk.tick(120)