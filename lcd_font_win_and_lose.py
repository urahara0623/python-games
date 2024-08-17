import pygame
from pygame.locals import Rect

# 各文字の5x7ドットマトリクスを定義
LCD_Y = (1, 0, 0, 0, 1,
         0, 1, 0, 1, 0,
         0, 0, 1, 0, 0,
         0, 0, 1, 0, 0,
         0, 0, 1, 0, 0,
         0, 0, 1, 0, 0,
         0, 1, 1, 1, 0)

LCD_O = (0, 1, 1, 1, 0,
         1, 0, 0, 0, 1,
         1, 0, 0, 0, 1,
         1, 0, 0, 0, 1,
         1, 0, 0, 0, 1,
         1, 0, 0, 0, 1,
         0, 1, 1, 1, 0)

LCD_U = (1, 0, 0, 0, 1,
         1, 0, 0, 0, 1,
         1, 0, 0, 0, 1,
         1, 0, 0, 0, 1,
         1, 0, 0, 0, 1,
         1, 0, 0, 0, 1,
         0, 1, 1, 1, 0)

LCD_W = (1, 0, 0, 0, 1,
         1, 0, 0, 0, 1,
         1, 0, 1, 0, 1,
         1, 0, 1, 0, 1,
         1, 0, 1, 0, 1,
         1, 0, 1, 0, 1,
         0, 1, 0, 1, 0)

LCD_I = (0, 1, 1, 1, 0,
         0, 0, 1, 0, 0,
         0, 0, 1, 0, 0,
         0, 0, 1, 0, 0,
         0, 0, 1, 0, 0,
         0, 0, 1, 0, 0,
         0, 1, 1, 1, 0)

LCD_N = (1, 0, 0, 0, 1,
         1, 1, 0, 0, 1,
         1, 0, 1, 0, 1,
         1, 0, 0, 1, 1,
         1, 0, 0, 0, 1,
         1, 0, 0, 0, 1,
         1, 0, 0, 0, 1)

LCD_L = (1, 0, 0, 0, 0,
         1, 0, 0, 0, 0,
         1, 0, 0, 0, 0,
         1, 0, 0, 0, 0,
         1, 0, 0, 0, 0,
         1, 0, 0, 0, 0,
         1, 1, 1, 1, 1)

LCD_S = (0, 1, 1, 1, 0,
         1, 0, 0, 0, 0,
         0, 1, 1, 1, 0,
         0, 0, 0, 0, 1,
         0, 0, 0, 0, 1,
         1, 0, 0, 0, 1,
         0, 1, 1, 1, 0)

LCD_EXCLAMATION = (0, 1, 0, 1, 0,
                   0, 1, 0, 1, 0,
                   0, 1, 0, 1, 0,
                   0, 1, 0, 1, 0,
                   0, 1, 0, 1, 0,
                   0, 0, 0, 0, 0,
                   0, 1, 0, 1, 0)

# 数字と記号のLCD表示を含むリストを拡張
LCD_font_styles = {
    'Y': LCD_Y, 'O': LCD_O, 'U': LCD_U,
    'W': LCD_W, 'I': LCD_I, 'N': LCD_N,
    'L': LCD_L, 'S': LCD_S, '!': LCD_EXCLAMATION
}

DARK_GRAY = (40, 40, 40)
GRAY = (80, 80, 80)
WHITE = (250, 250, 250)


class LCD_font():
    def __init__(self, screen):
        self.screen = screen

    def init_col(self, BLOCK_SIZE=4, BLOCK_INTV=4, COLOR_ON=WHITE, COLOR_OFF=GRAY):
        self.BLOCK_SIZE = BLOCK_SIZE
        self.BLOCK_INTV = BLOCK_INTV
        self.COLOR_ON = COLOR_ON
        self.COLOR_OFF = COLOR_OFF

    def init_row(self, X_ORG=2, Y_ORG=8, COL_INTV=6):
        self.X_ORG = X_ORG * self.BLOCK_INTV
        self.Y_ORG = Y_ORG * self.BLOCK_INTV
        self.COL_INTV = COL_INTV * self.BLOCK_INTV

    def update_col(self, col=0, char='Y'):
        block_size = self.BLOCK_SIZE
        i = 0
        for y in range(7):
            for x in range(5):
                if LCD_font_styles[char][i] == 1:
                    color = self.COLOR_ON
                else:
                    color = self.COLOR_OFF
                x0 = self.X_ORG + self.COL_INTV * col
                y0 = self.Y_ORG
                org1 = (x0 + x * self.BLOCK_INTV, y0 + y * self.BLOCK_INTV)
                pygame.draw.rect(self.screen, color, Rect(org1[0], org1[1], block_size, block_size))
                i += 1


def display_message(screen, message):
    lcd = LCD_font(screen)
    lcd.init_col()
    lcd.init_row()
    for i, char in enumerate(message):
        lcd.update_col(col=i, char=char)


pygame.init()
screen = pygame.display.set_mode((320, 200))
pygame.display.set_caption('LCD Font Display')

# "You win!" と "You lose!" を表示
screen.fill(DARK_GRAY)
display_message(screen, "YOU WIN!")
pygame.display.update()
pygame.time.wait(2000)

screen.fill(DARK_GRAY)
display_message(screen, "YOU LOSE!")
pygame.display.update()
pygame.time.wait(2000)

pygame.quit()
