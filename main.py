import pygame
import random
import sys
import tkinter as tk
import threading
import time


# =====================================================
#              FUNCIÓN PARA INICIAR PYGAME
# =====================================================
def iniciar_juego():
    pygame.init()

    WIDTH, HEIGHT = 800, 500
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PlaneFlying")  # Título actualizado

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 30)

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)  # Color para letras de Game Over

    # =====================================================
    #                CARGAR ASSETS
    # =====================================================

    background_raw = pygame.image.load("fondo.png").convert()
    background_raw = pygame.transform.scale(background_raw, (WIDTH, HEIGHT))

    # Fondo de Game Over
    game_over_bg_raw = pygame.image.load("game_over_fondo.png").convert()
    game_over_bg_raw = pygame.transform.scale(game_over_bg_raw, (WIDTH, HEIGHT))

    bg_x1 = 0
    bg_x2 = WIDTH
    bg_speed = 3

    plane_img_raw = pygame.image.load("avion.png").convert_alpha()

    # ---------------- OBSTÁCULOS ANIMADOS (2 FRAMES) ----------------
    obst_frame1 = pygame.image.load("obst1.png").convert_alpha()
    obst_frame2 = pygame.image.load("obst2.png").convert_alpha()
    obstacle_frames = [obst_frame1, obst_frame2]

    obstacle_anim_index = 0
    obstacle_anim_speed = 0.15

    plane_width = 90
    plane_height = 45
    plane_img_base = pygame.transform.scale(plane_img_raw, (plane_width, plane_height))

    # -------- EXPLOSIÓN --------
    explosion_frames = []
    for i in range(5):
        img = pygame.image.load(f"explosion_{i}.png").convert_alpha()
        img = pygame.transform.scale(img, (120, 120))
        explosion_frames.append(img)

    explosion_frame_index = 0
    explosion_active = False
    explosion_x = 0
    explosion_y = 0
    explosion_finished_time = 0

    # -------- VARIABLES DEL AVIÓN --------
    plane_x = 100
    plane_y = HEIGHT // 2
    y_velocity = 0

    gravity = 0.8
    lift = -1
    glide = -0.1

    obstacle_list = []
    obstacle_speed = 6
    spawn_time = 130
    timer = 0
    obstacle_width = 50

    obstacles_passed = 0
    game_over = False

    # ---------------- FUNCIONES ----------------
    def spawn_obstacle():
        height = random.randint(40, 160)
        y = random.randint(0, HEIGHT - height)
        rect = pygame.Rect(WIDTH, y, obstacle_width, height)
        obstacle_list.append({"rect": rect, "counted": False})

    def reset_game():
        nonlocal plane_y, obstacle_list, timer, obstacles_passed, y_velocity, explosion_active, game_over, explosion_finished_time
        plane_y = HEIGHT // 2
        obstacle_list = []
        timer = 0
        obstacles_passed = 0
        y_velocity = 0
        explosion_active = False
        game_over = False
        explosion_finished_time = 0

    reset_game()

    # =====================================================
    #                LOOP PRINCIPAL
    # =====================================================
    while True:

        # -------- EVENTOS --------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Revisar teclas solo cuando la pantalla de GAME OVER ya se muestra
            if game_over and not explosion_active and time.time() - explosion_finished_time >= 2:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        reset_game()
                    elif event.key == pygame.K_n:
                        pygame.quit()
                        sys.exit()

        keys = pygame.key.get_pressed()

        # -------- MOVER FONDO --------
        if not game_over:
            bg_x1 -= bg_speed
            bg_x2 -= bg_speed

        if bg_x1 <= -WIDTH:
            bg_x1 = WIDTH
        if bg_x2 <= -WIDTH:
            bg_x2 = WIDTH

        # -------- DIBUJAR FONDO --------
        if not (game_over and not explosion_active and time.time() - explosion_finished_time >= 2):
            screen.blit(background_raw, (bg_x1, 0))
            screen.blit(background_raw, (bg_x2, 0))

        # -------- LÓGICA DEL JUEGO --------
        if not game_over and not explosion_active:

            # Movimiento del avión
            if keys[pygame.K_UP]:
                y_velocity += lift
            else:
                y_velocity += gravity + glide

            plane_y += y_velocity

            # Limitar al techo y piso
            if plane_y < 0:
                plane_y = 0
                y_velocity = 0
                explosion_active = True
                explosion_frame_index = 0
                explosion_x = plane_x - 30
                explosion_y = plane_y - 30
                game_over = True
                explosion_finished_time = time.time()
            elif plane_y > HEIGHT - plane_height:
                plane_y = HEIGHT - plane_height
                y_velocity = 0
                explosion_active = True
                explosion_frame_index = 0
                explosion_x = plane_x - 30
                explosion_y = plane_y - 30
                game_over = True
                explosion_finished_time = time.time()

            plane_rect = pygame.Rect(plane_x, plane_y, plane_width, plane_height)

            # Rotación del avión
            angle = max(min(-y_velocity * 4, 25), -25)
            plane_img = pygame.transform.rotate(plane_img_base, angle)

            # Generar obstáculos
            timer += 1
            if timer >= spawn_time:
                spawn_obstacle()
                timer = 0

            # Animación de obstáculos
            obstacle_anim_index += obstacle_anim_speed
            if obstacle_anim_index >= len(obstacle_frames):
                obstacle_anim_index = 0
            current_obstacle_img = obstacle_frames[int(obstacle_anim_index)]

            # Mover y dibujar obstáculos
            for obs in obstacle_list:
                obs["rect"].x -= obstacle_speed
            obstacle_list = [o for o in obstacle_list if o["rect"].x > -60]

            for obs in obstacle_list:
                rect = obs["rect"]
                img = pygame.transform.scale(current_obstacle_img, (obstacle_width, rect.height))
                screen.blit(img, (rect.x, rect.y))

                # Contar obstáculos pasados
                if rect.x + rect.width < plane_x and not obs["counted"]:
                    obs["counted"] = True
                    obstacles_passed += 1

                # Colisión
                if plane_rect.colliderect(rect):
                    explosion_active = True
                    explosion_frame_index = 0
                    explosion_x = plane_x - 30
                    explosion_y = plane_y - 30
                    game_over = True
                    explosion_finished_time = time.time()

            # Dibujar puntaje
            counter_text = font.render(f"Obstáculos pasados: {obstacles_passed}", True, WHITE)
            screen.blit(counter_text, (20, 20))

            # Dibujar avión
            screen.blit(plane_img, (plane_x, plane_y))

        # -------- EXPLOSIÓN --------
        if explosion_active:
            if explosion_frame_index < len(explosion_frames):
                screen.blit(explosion_frames[int(explosion_frame_index)], (explosion_x, explosion_y))
                explosion_frame_index += 0.20
            else:
                explosion_active = False

        # -------- PANTALLA GAME OVER --------
        if game_over and not explosion_active and time.time() - explosion_finished_time >= 2:
            screen.blit(game_over_bg_raw, (0, 0))
            text1 = font.render("GAME OVER", True, BLACK)
            text2 = font.render("¿Reiniciar? (Y / N)", True, BLACK)
            screen.blit(text1, (WIDTH // 2 - 100, HEIGHT // 2 - 40))
            screen.blit(text2, (WIDTH // 2 - 140, HEIGHT // 2 + 10))

        pygame.display.update()
        clock.tick(60)


# =====================================================
#     VENTANA EMERGENTE (Tkinter) EN OTRO HILO
# =====================================================
def abrir_juego():
    root.destroy()
    hilo = threading.Thread(target=iniciar_juego)
    hilo.start()


root = tk.Tk()
root.title("Iniciar Juego")
root.geometry("300x150")

label = tk.Label(root, text="PlaneFlying", font=("Arial", 18))
label.pack(pady=10)

btn = tk.Button(root, text="Iniciar juego", font=("Arial", 14), command=abrir_juego)
btn.pack(pady=20)

root.mainloop()
