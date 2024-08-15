from datetime import datetime, timedelta
import pygame
from seven_seg_pg import Seven_seg
from lcd_font_pg import LCD_font
from lcd_font_mc import LCD_font as LCD_font_mc
from mcje.minecraft import Minecraft
import param_MCJE as param

mc = Minecraft.create(port=param.PORT_MC)
mc.postToChat('経過時間の表示を開始します...')
mc.setBlock(5, 70, 5, param.GOLD_BLOCK)

DARK_GRAY = (40, 40, 40)
GRAY = (80, 80, 80)
RED = (255, 0, 0)
WHITE = (250, 250, 250)

pygame.init()

clock = pygame.time.Clock()
screen = pygame.display.set_mode([480, 320])
pygame.display.set_caption("経過時間表示")
screen.fill(DARK_GRAY)

# 7セグメントとLCDディスプレイを初期化
display5 = Seven_seg(screen)
display5.init_col(BLOCK_SIZE=9, BLOCK_INTV=9, COLOR_ON=(120, 200, 250), COLOR_OFF=GRAY)
display5.init_row(X_ORG=8, Y_ORG=8, COL_INTV=6)

display6 = LCD_font(screen)
display6.init_col(BLOCK_SIZE=4, BLOCK_INTV=6, COLOR_ON=WHITE, COLOR_OFF=GRAY)
display6.init_row(X_ORG=10, Y_ORG=21, COL_INTV=6)

display7 = LCD_font(screen)
display7.init_col(BLOCK_SIZE=6, BLOCK_INTV=8, COLOR_ON=RED, COLOR_OFF=GRAY)
display7.init_row(X_ORG=6, Y_ORG=24, COL_INTV=6)

display8 = LCD_font_mc(mc)
display8.init_col(COLOR_ON=param.IRON_BLOCK, COLOR_OFF=param.AIR)
display8.init_row(X_ORG=-26, Y_ORG=param.Y_SEA + 64, Z_ORG=5, COL_INTV=6)

display9 = LCD_font_mc(mc)
display9.init_col(COLOR_ON=param.SEA_LANTERN_BLOCK, COLOR_OFF=param.AIR)
display9.init_row(X_ORG=-20, Y_ORG=param.Y_SEA + 55, Z_ORG=5, COL_INTV=6)

start_time = datetime.now()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if not running:
        break

    elapsed_time = datetime.now() - start_time
    elapsed_seconds = int(elapsed_time.total_seconds())

    hours = elapsed_seconds // 3600
    minutes = (elapsed_seconds % 3600) // 60
    seconds = elapsed_seconds % 60

    time_display = hours * 10000 + minutes * 100 + seconds
    display5.disp_num2(zfil=True, rjust=6, num=time_display, base=10)

    display6.update_col(col=0, code=hours // 10)
    display6.update_col(col=1, code=hours % 10)
    display6.update_col(col=2, code=10)  # コロンのセパレータ
    display6.update_col(col=3, code=minutes // 10)
    display6.update_col(col=4, code=minutes % 10)
    display6.update_col(col=5, code=10)  # コロンのセパレータ
    display6.update_col(col=6, code=seconds // 10)
    display6.update_col(col=7, code=seconds % 10)

    display7.update_col(col=0, code=hours // 10)
    display7.update_col(col=1, code=hours % 10)
    display7.update_col(col=2, code=10)
    display7.update_col(col=3, code=minutes // 10)
    display7.update_col(col=4, code=minutes % 10)
    display7.update_col(col=5, code=10)
    display7.update_col(col=6, code=seconds // 10)
    display7.update_col(col=7, code=seconds % 10)

    pygame.display.flip()

    display8.update_col(col=0, code=hours // 10)
    display8.update_col(col=1, code=hours % 10)
    display8.update_col(col=2, code=10)
    display8.update_col(col=3, code=minutes // 10)
    display8.update_col(col=4, code=minutes % 10)
    display8.update_col(col=5, code=10)
    display8.update_col(col=6, code=seconds // 10)
    display8.update_col(col=7, code=seconds % 10)

    display9.update_col(col=0, code=hours // 10)
    display9.update_col(col=1, code=hours % 10)
    display9.update_col(col=2, code=10)
    display9.update_col(col=3, code=minutes // 10)
    display9.update_col(col=4, code=minutes % 10)
    display9.update_col(col=5, code=10)
    display9.update_col(col=6, code=seconds // 10)
    display9.update_col(col=7, code=seconds % 10)

    clock.tick(1)  # 毎秒更新

pygame.quit()

