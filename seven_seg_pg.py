# 7-seg display simulator for pygame
# 各セグメントをブロック２個で構成。
# 4x7ドットマトリクスになっている。

from math import log
import pygame
from pygame.locals import Rect


# 7セグのスタイル設定

# 7セグの配置  pygameの場合、y軸反転が必要
# 各ブロック、左下原点*(0,0)からのオフセット(x,y)
# y:
# 6     A A       A0(1,6)  A1(2,6)
# 5   F     B     F1(0,5)  B1(3,5)
# 4   F     B     F0(0,4)  B0(3,4)
# 3     G G       G0(1,3)  G1(2,3)
# 2   E     C     E1(0,2)  C1(3,2)
# 1   E     C     E0(0,1)  C0(3,1)
# 0   * D D       D0(1,0)  D1(2,0)
# x:  0 1 2 3

offset_A = ((1, 6), (2, 6))
offset_B = ((3, 4), (3, 5))
offset_C = ((3, 1), (3, 2))
offset_D = ((1, 0), (2, 0))
offset_E = ((0, 1), (0, 2))
offset_F = ((0, 4), (0, 5))
offset_G = ((1, 3), (2, 3))

# 表示する数字／記号のon/off情報
# セグメントAからGについて7種類、「タプル」で用意する。
# 加えて、各セグメントのオフセット情報を16番目の要素、セグメント名を17番目の要素として持つ。
# セグメント名は本来の動作には不要。
seg_A = (1, 0, 1, 1,   0, 1, 1, 1,   1, 1, 1, 0,   1, 0, 1, 1,  offset_A, "A")
seg_B = (1, 1, 1, 1,   1, 0, 0, 1,   1, 1, 1, 0,   0, 1, 0, 0,  offset_B, "B")
seg_C = (1, 1, 0, 1,   1, 1, 1, 1,   1, 1, 1, 1,   0, 1, 0, 0,  offset_C, "C")
seg_D = (1, 0, 1, 1,   0, 1, 1, 0,   1, 1, 0, 1,   1, 1, 1, 0,  offset_D, "D")
seg_E = (1, 0, 1, 0,   0, 0, 1, 0,   1, 0, 1, 1,   1, 1, 1, 1,  offset_E, "E")
seg_F = (1, 0, 0, 0,   1, 1, 1, 0,   1, 1, 1, 1,   1, 0, 1, 1,  offset_F, "F")
seg_G = (0, 0, 1, 1,   1, 1, 1, 0,   1, 1, 1, 1,   0, 1, 1, 1,  offset_G, "G")

# タプルの読み出し方法。インデックスとして3を指定。0番目、1番目、2番目、3番目。
# print(seg_A[3])

# さらに、タプルのタプルを作る。
segments = (seg_A, seg_B, seg_C, seg_D, seg_E, seg_F, seg_G)

# 色の準備。R, G, Bを0から255で指定。
DARK_GRAY = (40, 40, 40)
GRAY = (80, 80, 80)
RED = (255, 0, 0)
GREEN = (10, 250, 10)
YELLOW = (250, 250, 20)
WHITE = (250, 250, 250)


class Seven_seg():
    def __init__(self, screen):
        self.screen = screen

    def init_col(self, BLOCK_SIZE=3, BLOCK_INTV=4, COLOR_ON=WHITE, COLOR_OFF=GRAY):
        # ひと桁、コラムの設定
        # 7セグをセグメントあたり2個のブロックで構成
        # ブロックのサイズと配置間隔をピクセル指定（インターバル）
        self.BLOCK_SIZE = BLOCK_SIZE
        self.BLOCK_INTV = BLOCK_INTV
        # on/offのカラー
        self.COLOR_ON = COLOR_ON
        self.COLOR_OFF = COLOR_OFF

    def init_row(self, X_ORG=2, Y_ORG=8, COL_INTV=6):  # 表示行の設定
        # xy空間での7セグ表示、最上位桁の左下座標をブロック数で指定
        self.X_ORG = X_ORG * self.BLOCK_INTV
        self.Y_ORG = Y_ORG * self.BLOCK_INTV
        # 各桁のブロック間隔をブロック数で指定（インターバル）
        self.COL_INTV = COL_INTV * self.BLOCK_INTV

    def update_col(self, col=0, num=3, base=16, blank=False):  # ある桁にある数字を表示する関数
        # numをcol桁目に表示、桁は最上位桁の左から右へ進む。
        block_size = self.BLOCK_SIZE
        num = num % base  # デフォルトは16進数表示
        for segment in segments:  # 7つのセグメントのうちの、あるセグメントについて、
            if segment[num] == 1:
                color = self.COLOR_ON
            else:
                color = self.COLOR_OFF
            if blank is True:    # ブランク表示の場合は、すべてOFFで上書き
                color = self.COLOR_OFF
            # 桁の原点
            x0 = self.X_ORG + self.COL_INTV * col
            y0 = self.Y_ORG
            # ブロック1、ブロック2の座標オフセット
            x1, y1 = segment[16][0]
            x2, y2 = segment[16][1]
            # ブロック1、ブロック2の原点座標
            org1 = (x0 + x1 * self.BLOCK_INTV, y0 - y1 * self.BLOCK_INTV)
            org2 = (x0 + x2 * self.BLOCK_INTV, y0 - y2 * self.BLOCK_INTV)
            # ブロック１，２を描く
            pygame.draw.rect(self.screen, color, Rect(org1[0], org1[1], block_size, block_size))
            pygame.draw.rect(self.screen, color, Rect(org2[0], org2[1], block_size, block_size))

    def disp_num(self, num=1234, base=16):
        # numを複数桁で表示する。左詰め。
        if num <= 0:
            num = 1
        num_cols = int(log(num, base)) + 1
        for col in range(num_cols):
            self.update_col(col=col, num=num // (base ** (num_cols - col - 1)), base=base)

    def disp_num2(self, rjust=4, zfil=False, num=1234, base=16):
        # numをrjust桁で右詰め表示する。桁あふれが起きると、右にずれていく。
        # zfil==Trueの時、上位桁をゼロで埋める。Falseの場合は、ブランク表示。
        if num <= 0:
            num = 1
        num_cols = int(log(num, base)) + 1
        if num_cols > rjust:
            rjust = num_cols
        for disp_col in range(rjust):
            col = disp_col + num_cols - rjust
            if col >= 0:
                self.update_col(col=disp_col, num=num // (base ** (num_cols - col - 1)), base=base)
            else:
                if zfil is True:
                    self.update_col(col=disp_col, num=0)
                else:
                    self.update_col(col=disp_col, blank=True)
