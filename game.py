import asyncio
import pygame
import random
import math

# 初期化
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ANA Sky Navigator")
clock = pygame.time.Clock()

# 色定義
BLUE = (0, 51, 153)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
CYAN = (0, 255, 255)
PINK = (255, 105, 180)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# ゲーム変数
plane_x = WIDTH // 2
plane_y = HEIGHT - 100
obstacles = []
items = []
score = 0
game_time = 0
start_time = 0
game_over = False

# アイテムタイプ
ITEMS = {
    "coin": {"points": 10, "color": GOLD},
    "gem": {"points": 50, "color": CYAN},
    "star": {"points": 100, "color": PINK}
}

def reset_game():
    global plane_x, plane_y, obstacles, items, score, game_time, start_time, game_over
    plane_x = WIDTH // 2
    plane_y = HEIGHT - 100
    obstacles.clear()
    items.clear()
    score = 0
    game_time = 0
    start_time = pygame.time.get_ticks()
    game_over = False

def create_obstacle():
    x = random.randint(50, WIDTH - 50)
    obstacles.append([x, -50, 60, 40])

def create_item():
    x = random.randint(50, WIDTH - 50)
    item_type = random.choice(list(ITEMS.keys()))
    items.append([x, -30, 20, 20, item_type])

def draw_background():
    screen.fill((135, 206, 235))

def draw_plane():
    pygame.draw.polygon(screen, BLUE, [(plane_x, plane_y), (plane_x-15, plane_y+40), (plane_x+15, plane_y+40)])
    pygame.draw.polygon(screen, WHITE, [(plane_x, plane_y+10), (plane_x-10, plane_y+30), (plane_x+10, plane_y+30)])

def draw_obstacles():
    for obs in obstacles:
        pygame.draw.ellipse(screen, WHITE, obs)

def draw_items():
    for item in items:
        item_type = item[4]
        color = ITEMS[item_type]["color"]
        pygame.draw.circle(screen, color, (item[0] + 10, item[1] + 10), 10)

def check_collisions():
    global game_over, score
    
    # 障害物との衝突
    plane_rect = pygame.Rect(plane_x - 15, plane_y, 30, 40)
    for obs in obstacles[:]:
        obs_rect = pygame.Rect(obs[0], obs[1], obs[2], obs[3])
        if plane_rect.colliderect(obs_rect):
            game_over = True
    
    # アイテムとの衝突
    for item in items[:]:
        item_rect = pygame.Rect(item[0], item[1], item[2], item[3])
        if plane_rect.colliderect(item_rect):
            item_type = item[4]
            score += ITEMS[item_type]["points"]
            items.remove(item)

def update_game():
    global game_time
    
    if not game_over:
        game_time = (pygame.time.get_ticks() - start_time) // 1000
        
        # 障害物移動
        for obs in obstacles[:]:
            obs[1] += 5
            if obs[1] > HEIGHT:
                obstacles.remove(obs)
                score += 10
        
        # アイテム移動
        for item in items[:]:
            item[1] += 5
            if item[1] > HEIGHT:
                items.remove(item)
        
        # 新しい障害物とアイテム生成
        if random.randint(1, 60) == 1:
            create_obstacle()
        if random.randint(1, 120) == 1:
            create_item()

def draw_ui():
    font = pygame.font.Font(None, 36)
    
    # スコア表示
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    
    # 時間表示
    minutes = game_time // 60
    seconds = game_time % 60
    time_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, BLACK)
    screen.blit(time_text, (10, 50))
    
    if game_over:
        game_over_text = font.render("GAME OVER - Press SPACE to restart", True, RED)
        text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(game_over_text, text_rect)

async def main():
    global plane_x, game_over
    
    reset_game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_over:
                    reset_game()
        
        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and plane_x > 20:
                plane_x -= 8
            if keys[pygame.K_RIGHT] and plane_x < WIDTH - 20:
                plane_x += 8
        
        update_game()
        check_collisions()
        
        # 描画
        draw_background()
        draw_obstacles()
        draw_items()
        draw_plane()
        draw_ui()
        
        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
