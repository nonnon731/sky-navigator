import pygame
import random
import math
import json
import asyncio
from datetime import datetime

# Pygame-Web用の初期化
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ANA SKY NAVIGATOR - Web版")
clock = pygame.time.Clock()

# ANA風カラーパレット
ANA_BLUE = (0, 51, 153)
ANA_LIGHT_BLUE = (102, 153, 255)
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (255, 69, 0)
GREEN = (50, 205, 50)
GOLD = (255, 215, 0)
PINK = (255, 105, 180)
ORANGE = (255, 165, 0)
PURPLE = (138, 43, 226)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)

# Web版用スコア管理（localStorage代替）
web_scores = []

def save_web_score(name, score, time_survived):
    global web_scores
    new_score = {
        "name": name,
        "score": score,
        "time": time_survived,
        "date": datetime.now().strftime("%m-%d %H:%M")
    }
    web_scores.append(new_score)
    web_scores.sort(key=lambda x: x["score"], reverse=True)
    web_scores = web_scores[:10]  # トップ10のみ保持

def get_web_ranking():
    return web_scores

# アイテムタイプ定義
ITEM_TYPES = {
    "coin": {"points": 10, "color": GOLD, "size": 15},
    "gem": {"points": 50, "color": CYAN, "size": 18},
    "star": {"points": 100, "color": PINK, "size": 20},
    "diamond": {"points": 200, "color": WHITE, "size": 22}
}

# ゲーム状態
game_state = "menu"
player_name = ""
input_active = False
score_saved = False

# 飛行機
plane_x, plane_y = WIDTH // 2, HEIGHT - 100
plane_speed = 6

# ゲーム要素
obstacles = []
items = []
particles = []
game_time = 0
start_time = 0
score = 0

# フォント設定（Web版用）
try:
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 28)
    tiny_font = pygame.font.Font(None, 20)
except:
    font = pygame.font.SysFont("arial", 48)
    small_font = pygame.font.SysFont("arial", 28)
    tiny_font = pygame.font.SysFont("arial", 20)

def get_difficulty_settings(time_elapsed):
    base_obstacle_freq = max(30 - time_elapsed // 10, 10)
    base_obstacle_speed = min(3 + time_elapsed // 15, 8)
    base_scroll_speed = min(2 + time_elapsed // 20, 5)
    
    return {
        "obstacle_freq": base_obstacle_freq,
        "obstacle_speed": base_obstacle_speed,
        "scroll_speed": base_scroll_speed
    }

def draw_gradient_bg():
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(135 + (200 - 135) * ratio)
        g = int(206 + (220 - 206) * ratio)
        b = int(235 + (255 - 235) * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

def draw_rounded_rect(surface, color, rect, radius):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def create_obstacle():
    x = random.randint(50, WIDTH - 50)
    y = -50
    obstacles.append([x, y, 60, 40])

def draw_obstacle(obs):
    pygame.draw.ellipse(screen, WHITE, obs)
    pygame.draw.ellipse(screen, GRAY, [obs[0]+5, obs[1]+5, obs[2]-10, obs[3]-10])

def create_item():
    x = random.randint(50, WIDTH - 50)
    y = -30
    
    if game_time > 60:
        item_type = random.choices(
            ["coin", "gem", "star", "diamond"],
            weights=[40, 30, 20, 10]
        )[0]
    elif game_time > 30:
        item_type = random.choices(
            ["coin", "gem", "star"],
            weights=[50, 30, 20]
        )[0]
    else:
        item_type = random.choices(
            ["coin", "gem"],
            weights=[70, 30]
        )[0]
    
    items.append([x, y, ITEM_TYPES[item_type]["size"], ITEM_TYPES[item_type]["size"], item_type])

def draw_item(item):
    item_type = item[4]
    item_data = ITEM_TYPES[item_type]
    center_x = item[0] + item[2] // 2
    center_y = item[1] + item[3] // 2
    
    pygame.draw.circle(screen, item_data["color"], (center_x, center_y), item_data["size"]//2)
    
    # ポイント表示
    points_text = tiny_font.render(str(item_data["points"]), True, BLACK)
    text_rect = points_text.get_rect(center=(center_x, center_y))
    screen.blit(points_text, text_rect)

def draw_plane(x, y):
    # 簡単な飛行機の描画
    pygame.draw.polygon(screen, ANA_BLUE, [(x, y), (x-12, y+30), (x+12, y+30)])
    pygame.draw.polygon(screen, WHITE, [(x, y+10), (x-8, y+25), (x+8, y+25)])

def check_collision(px, py, obstacles):
    plane_rect = pygame.Rect(px-12, py, 24, 50)
    for obs in obstacles:
        obs_rect = pygame.Rect(obs[0], obs[1], obs[2], obs[3])
        if plane_rect.colliderect(obs_rect):
            return True
    return False

def check_item_collision(px, py, items):
    plane_rect = pygame.Rect(px-12, py, 24, 50)
    collected_items = []
    for i, item in enumerate(items):
        item_rect = pygame.Rect(item[0], item[1], item[2], item[3])
        if plane_rect.colliderect(item_rect):
            collected_items.append((i, item[4]))
    return collected_items

def add_particle(x, y, color):
    particles.append([x, y, random.uniform(-2, 2), random.uniform(-3, -1), color, 30])

def update_particles():
    for particle in particles[:]:
        particle[0] += particle[2]
        particle[1] += particle[3]
        particle[5] -= 1
        if particle[5] <= 0:
            particles.remove(particle)

def draw_particles():
    for particle in particles:
        pygame.draw.circle(screen, particle[4], (int(particle[0]), int(particle[1])), 3)

def draw_menu():
    draw_gradient_bg()
    
    title = font.render("ANA SKY NAVIGATOR", True, WHITE)
    screen.blit(title, (WIDTH//2 - 200, 100))
    
    subtitle = small_font.render("Web版", True, GOLD)
    screen.blit(subtitle, (WIDTH//2 - 30, 150))
    
    if player_name:
        name_display = tiny_font.render(f"パイロット: {player_name}", True, ANA_BLUE)
        screen.blit(name_display, (WIDTH//2 - 60, 200))
    
    start_button = pygame.Rect(WIDTH//2 - 80, 300, 160, 50)
    draw_rounded_rect(screen, PINK, start_button, 15)
    start_text = small_font.render("ゲーム開始", True, WHITE)
    screen.blit(start_text, (WIDTH//2 - 50, 320))
    
    name_button = pygame.Rect(WIDTH//2 - 80, 370, 160, 40)
    draw_rounded_rect(screen, CYAN, name_button, 10)
    name_text = tiny_font.render("名前設定 (N)", True, WHITE)
    screen.blit(name_text, (WIDTH//2 - 45, 385))
    
    rank_button = pygame.Rect(WIDTH//2 - 80, 420, 160, 40)
    draw_rounded_rect(screen, GOLD, rank_button, 10)
    rank_text = tiny_font.render("ランキング (R)", True, WHITE)
    screen.blit(rank_text, (WIDTH//2 - 50, 435))

def draw_name_input():
    draw_gradient_bg()
    
    title = font.render("名前入力", True, WHITE)
    screen.blit(title, (WIDTH//2 - 80, 150))
    
    input_rect = pygame.Rect(WIDTH//2 - 150, 250, 300, 40)
    color = CYAN if input_active else GRAY
    draw_rounded_rect(screen, WHITE, input_rect, 10)
    pygame.draw.rect(screen, color, input_rect, 3, border_radius=10)
    
    name_text = small_font.render(player_name, True, BLACK)
    screen.blit(name_text, (WIDTH//2 - 140, 265))
    
    help_text = tiny_font.render("Enter: 決定 / Escape: キャンセル", True, WHITE)
    screen.blit(help_text, (WIDTH//2 - 100, 350))

def draw_ranking():
    draw_gradient_bg()
    
    title = font.render("トップ10ランキング", True, WHITE)
    screen.blit(title, (WIDTH//2 - 120, 80))
    
    ranking = get_web_ranking()
    
    if not ranking:
        no_data_text = small_font.render("まだ記録がありません", True, GRAY)
        screen.blit(no_data_text, (WIDTH//2 - 80, HEIGHT//2))
    else:
        y_start = 150
        for i, score_data in enumerate(ranking):
            y_pos = y_start + i * 35
            rank_color = [GOLD, GRAY, ORANGE][i] if i < 3 else BLACK
            
            rank_text = f"{i+1}. {score_data['name'][:8]} - {score_data['score']}点"
            minutes = score_data["time"] // 60
            seconds = score_data["time"] % 60
            time_text = f" ({minutes:02d}:{seconds:02d})"
            
            rank_surface = tiny_font.render(rank_text + time_text, True, rank_color)
            screen.blit(rank_surface, (WIDTH//2 - 150, y_pos))
    
    back_text = tiny_font.render("Escapeキーで戻る", True, WHITE)
    screen.blit(back_text, (WIDTH//2 - 60, 520))

async def main():
    global game_state, player_name, input_active, score_saved
    global plane_x, plane_y, obstacles, items, game_time, start_time, score
    
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if game_state == "menu":
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        game_state = "playing"
                        plane_x, plane_y = WIDTH // 2, HEIGHT - 100
                        obstacles.clear()
                        items.clear()
                        score = 0
                        game_time = 0
                        start_time = 0
                        score_saved = False
                    elif event.key == pygame.K_n:
                        game_state = "name_input"
                        input_active = True
                    elif event.key == pygame.K_r:
                        game_state = "ranking"
                
                elif game_state == "name_input":
                    if event.key == pygame.K_RETURN and len(player_name) > 0:
                        game_state = "menu"
                        input_active = False
                    elif event.key == pygame.K_ESCAPE:
                        game_state = "menu"
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        if len(player_name) < 10 and event.unicode.isprintable():
                            player_name += event.unicode
                
                elif game_state == "ranking":
                    if event.key == pygame.K_ESCAPE:
                        game_state = "menu"
                
                elif game_state == "game_over":
                    if event.key == pygame.K_r or event.key == pygame.K_SPACE:
                        game_state = "playing"
                        plane_x, plane_y = WIDTH // 2, HEIGHT - 100
                        obstacles.clear()
                        items.clear()
                        score = 0
                        game_time = 0
                        start_time = 0
                        score_saved = False
                    elif event.key == pygame.K_m or event.key == pygame.K_ESCAPE:
                        game_state = "menu"
        
        # ゲーム画面の処理
        if game_state == "menu":
            draw_menu()
        
        elif game_state == "name_input":
            draw_name_input()
        
        elif game_state == "ranking":
            draw_ranking()
        
        elif game_state == "playing":
            # 時間更新
            if start_time == 0:
                start_time = pygame.time.get_ticks()
            game_time = (pygame.time.get_ticks() - start_time) // 1000
            
            current_settings = get_difficulty_settings(game_time)
            
            # キー入力
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and plane_x > 25:
                plane_x -= plane_speed
            if keys[pygame.K_RIGHT] and plane_x < WIDTH - 25:
                plane_x += plane_speed
            
            # 障害物生成
            if random.randint(1, current_settings["obstacle_freq"]) == 1:
                create_obstacle()
            
            # アイテム生成
            if random.randint(1, current_settings["obstacle_freq"] * 2) == 1:
                create_item()
            
            # 障害物移動
            for obs in obstacles[:]:
                obs[1] += current_settings["obstacle_speed"] + current_settings["scroll_speed"]
                if obs[1] > HEIGHT:
                    obstacles.remove(obs)
                    score += 10
            
            # アイテム移動
            for item in items[:]:
                item[1] += current_settings["obstacle_speed"] + current_settings["scroll_speed"]
                if item[1] > HEIGHT:
                    items.remove(item)
            
            # 衝突判定
            if check_collision(plane_x, plane_y, obstacles):
                for _ in range(15):
                    add_particle(plane_x, plane_y, random.choice([RED, GOLD, WHITE]))
                game_state = "game_over"
            
            # アイテム取得
            collected = check_item_collision(plane_x, plane_y, items)
            for i, item_type in reversed(collected):
                items.pop(i)
                points = ITEM_TYPES[item_type]["points"]
                score += points
                effect_color = ITEM_TYPES[item_type]["color"]
                for _ in range(10):
                    add_particle(plane_x, plane_y, random.choice([effect_color, WHITE, GOLD]))
            
            update_particles()
            
            # 描画
            draw_gradient_bg()
            
            for obs in obstacles:
                draw_obstacle(obs)
            
            for item in items:
                draw_item(item)
            
            draw_plane(plane_x, plane_y)
            draw_particles()
            
            # UI
            ui_panel = pygame.Rect(10, 10, 250, 100)
            draw_rounded_rect(screen, (255, 255, 255, 150), ui_panel, 15)
            
            if player_name:
                name_text = tiny_font.render(f"パイロット: {player_name}", True, ANA_BLUE)
                screen.blit(name_text, (20, 20))
                y_start = 40
            else:
                y_start = 25
            
            minutes = game_time // 60
            seconds = game_time % 60
            time_text = small_font.render(f"時間 {minutes:02d}:{seconds:02d}", True, PURPLE)
            screen.blit(time_text, (20, y_start))
            
            score_text = tiny_font.render(f"得点: {score}", True, ORANGE)
            screen.blit(score_text, (20, y_start + 25))
            
            difficulty_level = min(game_time // 15 + 1, 10)
            diff_text = tiny_font.render(f"難易度: Lv.{difficulty_level}", True, GREEN)
            screen.blit(diff_text, (20, y_start + 45))
        
        elif game_state == "game_over":
            draw_gradient_bg()
            update_particles()
            draw_particles()
            
            if not score_saved:
                if player_name:
                    save_web_score(player_name, score, game_time)
                score_saved = True
            
            panel_rect = pygame.Rect(WIDTH//2 - 160, HEIGHT//2 - 100, 320, 200)
            draw_rounded_rect(screen, (255, 255, 255, 200), panel_rect, 25)
            pygame.draw.rect(screen, RED, panel_rect, 4, border_radius=25)
            
            text = font.render("ゲーム終了", True, RED)
            screen.blit(text, (WIDTH//2 - 80, HEIGHT//2 - 80))
            
            if player_name:
                name_text = tiny_font.render(f"{player_name} さん", True, ANA_BLUE)
                screen.blit(name_text, (WIDTH//2 - 30, HEIGHT//2 - 50))
            
            minutes = game_time // 60
            seconds = game_time % 60
            time_text = small_font.render(f"生存時間: {minutes:02d}:{seconds:02d}", True, GREEN)
            screen.blit(time_text, (WIDTH//2 - 70, HEIGHT//2 - 20))
            
            score_text = small_font.render(f"最終得点: {score}", True, PURPLE)
            screen.blit(score_text, (WIDTH//2 - 60, HEIGHT//2 + 10))
            
            restart_text = tiny_font.render("Space: 再開 / Escape: メニュー", True, ORANGE)
            screen.blit(restart_text, (WIDTH//2 - 80, HEIGHT//2 + 50))
        
        pygame.display.flip()
        await asyncio.sleep(0)  # Pygame-Web用の非同期処理
        clock.tick(60)

if __name__ == "__main__":
    asyncio.run(main())
