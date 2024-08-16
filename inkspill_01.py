# Ink Spill (a Flood It clone)
# http://inventwithpython.com/pygame
# By Al Sweigart al@inventwithpython.com
# Released under a "Simplified BSD" license

import random
import sys
import webbrowser
import copy
import pygame
# from pygame.locals import *

from mcje.minecraft import Minecraft
import param_MCJE as param

sys.setrecursionlimit(1100)

mc = Minecraft.create(port=param.PORT_MC)
mc.postToChat('Ink Spill in the Minecraft')

MC_X0, MC_Y0, MC_Z0 = 0, 127, 20

block_colors = (param.RED_WOOL,
                param.LIME_WOOL,  # green
                param.BLUE_WOOL,
                param.YELLOW_WOOL,
                param.ORANGE_WOOL,
                param.MAGENTA_WOOL)  # purple

# There are different box sizes, number of boxes, and
# life depending on the "board size" setting selected.
SMALLBOXSIZE = 40  # size is in pixels
MEDIUMBOXSIZE = 20
LARGEBOXSIZE = 10

SMALLBOARDSIZE = 8  # size is in boxes
MEDIUMBOARDSIZE = 16
LARGEBOARDSIZE = 32

SMALLMAXLIFE = 8  # number of turns
MEDIUMMAXLIFE = 20
LARGEMAXLIFE = 40

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
boxSize = MEDIUMBOXSIZE
PALETTEGAPSIZE = 10
PALETTESIZE = 45
EASY = 0    # arbitrary but unique value
MEDIUM = 1  # arbitrary but unique value
HARD = 2    # arbitrary but unique value

# Minecraft
PALETTEGAPSIZE_MC = 2
PALETTESIZE_MC = 9

difficulty = MEDIUM  # game starts in "medium" mode
maxLife = MEDIUMMAXLIFE
boardWidth = MEDIUMBOARDSIZE
boardHeight = MEDIUMBOARDSIZE

#            R    G    B
WHITE    = (255, 255, 255)
DARKGRAY = ( 70,  70,  70)
BLACK    = (  0,   0,   0)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)

# The first color in each scheme is the background color, the next six are the palette colors.
COLORSCHEMES = (((150, 200, 255), RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE),
                ((0, 155, 104),  (97, 215, 164),  (228, 0, 69),  (0, 125, 50),   (204, 246, 0),   (148, 0, 45),    (241, 109, 149)),
                ((195, 179, 0),  (255, 239, 115), (255, 226, 0), (147, 3, 167),  (24, 38, 176),   (166, 147, 0),   (197, 97, 211)),
                ((85, 0, 0),     (155, 39, 102),  (0, 201, 13),  (255, 118, 0),  (206, 0, 113),   (0, 130, 9),     (255, 180, 115)),
                ((191, 159, 64), (183, 182, 208), (4, 31, 183),  (167, 184, 45), (122, 128, 212), (37, 204, 7),    (88, 155, 213)),
                ((200, 33, 205), (116, 252, 185), (68, 56, 56),  (52, 238, 83),  (23, 149, 195),  (222, 157, 227), (212, 86, 185)))
for i in range(len(COLORSCHEMES)):
    assert len(COLORSCHEMES[i]) == 7, 'Color scheme %s does not have exactly 7 colors.' % (i)
bgColor = COLORSCHEMES[0][0]
paletteColors = COLORSCHEMES[0][1:]


def main():
    global FPSCLOCK, DISPLAYSURF, LOGOIMAGE, SPOTIMAGE, SETTINGSIMAGE, SETTINGSBUTTONIMAGE, RESETBUTTONIMAGE

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    # Load images
    LOGOIMAGE = pygame.image.load('inkspilllogo.png')
    SPOTIMAGE = pygame.image.load('inkspillspot.png')
    SETTINGSIMAGE = pygame.image.load('inkspillsettings.png')
    SETTINGSBUTTONIMAGE = pygame.image.load('inkspillsettingsbutton.png')
    RESETBUTTONIMAGE = pygame.image.load('inkspillresetbutton.png')

    pygame.display.set_caption('Ink Spill')
    mousex = 0
    mousey = 0
    mainBoard = generateRandomBoard(boardWidth, boardHeight, difficulty)
    life = maxLife
    lastPaletteClicked = None

    clear_board_mc()  # clear the board on Minecraft
    drawBoard_mc(mainBoard)
    clearLifeMeter_mc()
    drawLifeMeter_mc(life)
    drawAchievement(0)
    drawPalettes_mc()
    selected = 0
    draw_cursor_mc(selected)

    while True:  # main game loop
        paletteClicked = None
        resetGame = False

        # Draw the screen.
        DISPLAYSURF.fill(bgColor)
        drawLogoAndButtons()
        drawBoard(mainBoard)
        drawLifeMeter(life)
        drawPalettes()

        checkForQuit()
        for event in pygame.event.get():  # event handling loop
            if event.type == pygame.MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if pygame.Rect(WINDOWWIDTH - SETTINGSBUTTONIMAGE.get_width(),
                               WINDOWHEIGHT - SETTINGSBUTTONIMAGE.get_height(),
                               SETTINGSBUTTONIMAGE.get_width(),
                               SETTINGSBUTTONIMAGE.get_height()).collidepoint(mousex, mousey):
                    resetGame = showSettingsScreen()  # clicked on Settings button
                elif pygame.Rect(WINDOWWIDTH - RESETBUTTONIMAGE.get_width(),
                                 WINDOWHEIGHT - SETTINGSBUTTONIMAGE.get_height() - RESETBUTTONIMAGE.get_height(),
                                 RESETBUTTONIMAGE.get_width(),
                                 RESETBUTTONIMAGE.get_height()).collidepoint(mousex, mousey):
                    resetGame = True  # clicked on Reset button
                else:
                    # check if a palette button was clicked
                    paletteClicked = getColorOfPaletteAt(mousex, mousey)
            elif event.type == pygame.KEYDOWN:
                # support up to 9 palette keys
                try:
                    key = int(event.unicode)
                except:
                    key = None

                if key is not None and key > 0 and key <= len(paletteColors):
                    paletteClicked = key - 1

                if event.key == pygame.K_UP:
                    draw_cursor_mc(selected, clear=True)
                    selected = (selected - 1) % len(paletteColors)
                    draw_cursor_mc(selected)
                if event.key == pygame.K_DOWN:
                    draw_cursor_mc(selected, clear=True)
                    selected = (selected + 1) % len(paletteColors)
                    draw_cursor_mc(selected)
                if event.key == pygame.K_RETURN:
                    paletteClicked = selected

        if paletteClicked is not None and paletteClicked != lastPaletteClicked:
            # a palette button was clicked that is different from the
            # last palette button clicked (this check prevents the player
            # from accidentally clicking the same palette twice)
            lastPaletteClicked = paletteClicked
            achieve = floodAnimation(mainBoard, paletteClicked)
            life -= 1
            drawLifeMeter_mc(life)

            resetGame = False
            if hasWon(mainBoard):
                msg = 'You win!'
                mc.postToChat(msg)
                print(msg)
                for i in range(4):  # flash border 4 times
                    flashBorderAnimation(WHITE, mainBoard)
                resetGame = True
                pygame.time.wait(2000)  # pause so the player can bask in victory
            elif life == 0:
                # life is zero, so player has lost
                msg = 'You lose at ' + str(int(achieve + 0.5)) + '%'
                mc.postToChat(msg)
                print(msg)
                drawLifeMeter(0)
                drawLifeMeter_mc(0)
                pygame.display.update()
                pygame.time.wait(400)
                for i in range(4):
                    flashBorderAnimation(BLACK, mainBoard)
                resetGame = True
                pygame.time.wait(2000)  # pause so the player can suffer in their defeat

        if resetGame:
            # start a new game
            mainBoard = generateRandomBoard(boardWidth, boardHeight, difficulty)
            drawBoard_mc(mainBoard)
            drawAchievement(0)
            clearLifeMeter_mc()
            life = maxLife
            drawLifeMeter_mc(life)
            lastPaletteClicked = None
            drawPalettes_mc()
            draw_cursor_mc(selected, clear=True)
            selected = 0
            draw_cursor_mc(selected)
            # clear_board_mc()  # clear the board on Minecraft

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def checkForQuit():
    # Terminates the program if there are any QUIT or escape key events.
    for event in pygame.event.get(pygame.QUIT):  # get all the QUIT events
        pygame.quit() # terminate if any QUIT events are present
        sys.exit()
    for event in pygame.event.get(pygame.KEYUP):  # get all the KEYUP events
        if event.key == pygame.K_ESCAPE:
            pygame.quit()  # terminate if the KEYUP event was for the Esc key
            sys.exit()
        pygame.event.post(event)  # put the other KEYUP event objects back


def hasWon(board):
    # if the entire board is the same color, player has won
    for x in range(boardWidth):
        for y in range(boardHeight):
            if board[x][y] != board[0][0]:
                return False  # found a different color, player has not won
    return True


def showSettingsScreen():
    global difficulty, boxSize, boardWidth, boardHeight, maxLife, paletteColors, bgColor

    # The pixel coordinates in this function were obtained by loading
    # the inkspillsettings.png image into a graphics editor and reading
    # the pixel coordinates from there. Handy trick.

    origDifficulty = difficulty
    origBoxSize = boxSize
    screenNeedsRedraw = True

    while True:
        if screenNeedsRedraw:
            DISPLAYSURF.fill(bgColor)
            DISPLAYSURF.blit(SETTINGSIMAGE, (0, 0))

            # place the ink spot marker next to the selected difficulty
            if difficulty == EASY:
                DISPLAYSURF.blit(SPOTIMAGE, (30, 4))
            if difficulty == MEDIUM:
                DISPLAYSURF.blit(SPOTIMAGE, (8, 41))
            if difficulty == HARD:
                DISPLAYSURF.blit(SPOTIMAGE, (30, 76))

            # place the ink spot marker next to the selected size
            if boxSize == SMALLBOXSIZE:
                DISPLAYSURF.blit(SPOTIMAGE, (22, 150))
            if boxSize == MEDIUMBOXSIZE:
                DISPLAYSURF.blit(SPOTIMAGE, (11, 185))
            if boxSize == LARGEBOXSIZE:
                DISPLAYSURF.blit(SPOTIMAGE, (24, 220))

            for i in range(len(COLORSCHEMES)):
                drawColorSchemeBoxes(500, i * 60 + 30, i)

            pygame.display.update()

        screenNeedsRedraw = False  # by default, don't redraw the screen
        for event in pygame.event.get():  # event handling loop
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    # Esc key on settings screen goes back to game
                    return not (origDifficulty == difficulty and origBoxSize == boxSize)
            elif event.type == pygame.MOUSEBUTTONUP:
                screenNeedsRedraw = True  # screen should be redrawn
                mousex, mousey = event.pos  # syntactic sugar

                # check for clicks on the difficulty buttons
                if pygame.Rect(74, 16, 111, 30).collidepoint(mousex, mousey):
                    difficulty = EASY
                elif pygame.Rect(53, 50, 104, 29).collidepoint(mousex, mousey):
                    difficulty = MEDIUM
                elif pygame.Rect(72, 85, 65, 31).collidepoint(mousex, mousey):
                    difficulty = HARD

                # check for clicks on the size buttons
                elif pygame.Rect(63, 156, 84, 31).collidepoint(mousex, mousey):
                    # small board size setting:
                    boxSize = SMALLBOXSIZE
                    boardWidth = SMALLBOARDSIZE
                    boardHeight = SMALLBOARDSIZE
                    maxLife = SMALLMAXLIFE
                elif pygame.Rect(52, 192, 106, 32).collidepoint(mousex, mousey):
                    # medium board size setting:
                    boxSize = MEDIUMBOXSIZE
                    boardWidth = MEDIUMBOARDSIZE
                    boardHeight = MEDIUMBOARDSIZE
                    maxLife = MEDIUMMAXLIFE
                elif pygame.Rect(67, 228, 58, 37).collidepoint(mousex, mousey):
                    # large board size setting:
                    boxSize = LARGEBOXSIZE
                    boardWidth = LARGEBOARDSIZE
                    boardHeight = LARGEBOARDSIZE
                    maxLife = LARGEMAXLIFE
                elif pygame.Rect(14, 299, 371, 97).collidepoint(mousex, mousey):
                    # clicked on the "learn programming" ad
                    webbrowser.open('http://inventwithpython.com')  # opens a web browser
                elif pygame.Rect(178, 418, 215, 34).collidepoint(mousex, mousey):
                    # clicked on the "back to game" button
                    return not (origDifficulty == difficulty and origBoxSize == boxSize)

                for i in range(len(COLORSCHEMES)):
                    # clicked on a color scheme button
                    if pygame.Rect(500, 30 + i * 60, MEDIUMBOXSIZE * 3, MEDIUMBOXSIZE * 2).collidepoint(mousex, mousey):
                        bgColor = COLORSCHEMES[i][0]
                        paletteColors  = COLORSCHEMES[i][1:]


def drawColorSchemeBoxes(x, y, schemeNum):
    # Draws the color scheme boxes that appear on the "Settings" screen.
    for boxy in range(2):
        for boxx in range(3):
            pygame.draw.rect(DISPLAYSURF, COLORSCHEMES[schemeNum][3 * boxy + boxx + 1],
                             (x + MEDIUMBOXSIZE * boxx, y + MEDIUMBOXSIZE * boxy, MEDIUMBOXSIZE, MEDIUMBOXSIZE))
            if paletteColors == COLORSCHEMES[schemeNum][1:]:
                # put the ink spot next to the selected color scheme
                DISPLAYSURF.blit(SPOTIMAGE, (x - 50, y))


def flashBorderAnimation(color, board, animationSpeed=60):  # 30
    origSurf = DISPLAYSURF.copy()
    flashSurf = pygame.Surface(DISPLAYSURF.get_size())
    flashSurf = flashSurf.convert_alpha()
    for start, end, step in ((0, 256, 1), (255, 0, -1)):
        # the first iteration on the outer loop will set the inner loop
        # to have transparency go from 0 to 255, the second iteration will
        # have it go from 255 to 0. This is the "flash".
        for transparency in range(start, end, animationSpeed * step):
            DISPLAYSURF.blit(origSurf, (0, 0))
            r, g, b = color
            flashSurf.fill((r, g, b, transparency))
            DISPLAYSURF.blit(flashSurf, (0, 0))
            drawBoard(board)  # draw board ON TOP OF the transparency layer
            pygame.display.update()
            FPSCLOCK.tick(FPS)
    DISPLAYSURF.blit(origSurf, (0, 0))  # redraw the original surface


def floodAnimation(board, paletteClicked, animationSpeed=50):  # 25
    origBoard = copy.deepcopy(board)
    floodFill(board, board[0][0], paletteClicked, 0, 0)

    board_for_count = copy.deepcopy(board)
    achievement = floodFill(board_for_count, paletteClicked, -1, 0, 0)
    achieve = achievement / (boardWidth * boardHeight) * 100
    print(achievement, achieve, int(achieve + 0.5),  '%')
    drawAchievement(achieve)

    for transparency in range(0, 255, animationSpeed):
        # The "new" board slowly become opaque over the original board.
        drawBoard(origBoard)
        drawBoard(board, transparency)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

    return achieve


def generateRandomBoard(width, height, difficulty=MEDIUM):
    # Creates a board data structure with random colors for each box.
    board = []
    for x in range(width):
        column = []
        for y in range(height):
            column.append(random.randint(0, len(paletteColors) - 1))
        board.append(column)

    # Make board easier by setting some boxes to same color as a neighbor.

    # Determine how many boxes to change.
    if difficulty == EASY:
        if boxSize == SMALLBOXSIZE:
            boxesToChange = 100
        else:
            boxesToChange = 1500
    elif difficulty == MEDIUM:
        if boxSize == SMALLBOXSIZE:
            boxesToChange = 5
        else:
            boxesToChange = 200
    else:
        boxesToChange = 0

    # Change neighbor's colors:
    for i in range(boxesToChange):
        # Randomly choose a box whose color to copy
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)

        # Randomly choose neighbors to change.
        direction = random.randint(0, 3)
        if direction == 0:  # change left and up neighbor
            board[x - 1][y] = board[x][y]
            board[x][y - 1] = board[x][y]
        elif direction == 1:  # change right and down neighbor
            board[x + 1][y] = board[x][y]
            board[x][y + 1] = board[x][y]
        elif direction == 2:  # change right and up neighbor
            board[x][y - 1] = board[x][y]
            board[x + 1][y] = board[x][y]
        else: # change left and down neighbor
            board[x][y + 1] = board[x][y]
            board[x - 1][y] = board[x][y]
    return board


def drawLogoAndButtons():
    # draw the Ink Spill logo and Settings and Reset buttons.
    DISPLAYSURF.blit(LOGOIMAGE, (WINDOWWIDTH - LOGOIMAGE.get_width(), 0))
    DISPLAYSURF.blit(SETTINGSBUTTONIMAGE,
                     (WINDOWWIDTH - SETTINGSBUTTONIMAGE.get_width(),
                      WINDOWHEIGHT - SETTINGSBUTTONIMAGE.get_height()))
    DISPLAYSURF.blit(RESETBUTTONIMAGE,
                     (WINDOWWIDTH - RESETBUTTONIMAGE.get_width(),
                      WINDOWHEIGHT - SETTINGSBUTTONIMAGE.get_height() - RESETBUTTONIMAGE.get_height()))


def drawBoard(board, transparency=255):
    # The colored squares are drawn to a temporary surface which is then
    # drawn to the DISPLAYSURF surface. This is done so we can draw the
    # squares with transparency on top of DISPLAYSURF as it currently is.
    tempSurf = pygame.Surface(DISPLAYSURF.get_size())
    tempSurf = tempSurf.convert_alpha()
    tempSurf.fill((0, 0, 0, 0))

    for x in range(boardWidth):
        for y in range(boardHeight):
            left, top = leftTopPixelCoordOfBox(x, y)
            r, g, b = paletteColors[board[x][y]]
            pygame.draw.rect(tempSurf, (r, g, b, transparency), (left, top, boxSize, boxSize))
    left, top = leftTopPixelCoordOfBox(0, 0)
    pygame.draw.rect(tempSurf, BLACK, (left - 1, top - 1, boxSize * boardWidth + 1, boxSize * boardHeight + 1), 1)
    DISPLAYSURF.blit(tempSurf, (0, 0))


def drawBoard_mc(board):
    for x in range(boardWidth):
        for y in range(boardHeight):
            draw_block_mc(x, y, board)  # draw the block on Minecraft


def clear_board_mc():
    boardSize = LARGEBOARDSIZE - 1
    mc.setBlocks(MC_X0 - 20, MC_Y0, MC_Z0, MC_X0 + boardSize + 20, MC_Y0 - boardSize, MC_Z0, param.AIR)


def draw_block_mc(x, y, board):
    # pass
    global boxSize
    boxS = int(boxSize / 5)
    for i in range(boxS):
        for j in range(boxS):
            mc.setBlock(MC_X0 + x * boxS + i, MC_Y0 - y * boxS - j, MC_Z0, block_colors[board[x][y]])


def drawPalettes():
    # Draws the six color palettes at the bottom of the screen.
    numColors = len(paletteColors)
    xmargin = int((WINDOWWIDTH - ((PALETTESIZE * numColors) + (PALETTEGAPSIZE * (numColors - 1)))) / 2)
    for i in range(numColors):
        left = xmargin + (i * PALETTESIZE) + (i * PALETTEGAPSIZE)
        top = WINDOWHEIGHT - PALETTESIZE - 10
        pygame.draw.rect(DISPLAYSURF, paletteColors[i], (left, top, PALETTESIZE, PALETTESIZE))
        pygame.draw.rect(DISPLAYSURF, bgColor,   (left + 2, top + 2, PALETTESIZE - 4, PALETTESIZE - 4), 2)


def drawPalettes_mc():
    # Draws the six color palettes at the right of the Minecraft game board.
    numColors = len(paletteColors)
    for i in range(numColors):
        x1 = MC_X0 + 64 + 4
        x2 = x1 + PALETTESIZE_MC - 1
        y1 = MC_Y0 - i * (PALETTESIZE_MC + PALETTEGAPSIZE_MC)
        y2 = y1 - PALETTESIZE_MC + 1
        mc.setBlocks(x1, y1, MC_Z0,
                     x2, y2, MC_Z0, block_colors[i])
        draw_cursor_mc(i, clear=True)


def draw_cursor_mc(selected, clear=False):
        i = selected
        x1 = MC_X0 + 64 + 4 - 2
        x2 = x1 + PALETTESIZE_MC + 2
        y1 = MC_Y0 - i * (PALETTESIZE_MC + PALETTEGAPSIZE_MC) + 1
        y2 = y1 - PALETTESIZE_MC - 1
        if clear:
            color = param.GLASS
        else:
            color = param.SEA_LANTERN_BLOCK
        mc.setBlocks(x1, y1, MC_Z0, x1 + 1, y2, MC_Z0, color)
        mc.setBlocks(x1, y1, MC_Z0, x2, y1, MC_Z0, color)
        mc.setBlocks(x2, y1, MC_Z0, x2 + 1, y2, MC_Z0, color)
        mc.setBlocks(x1, y2, MC_Z0, x2, y2, MC_Z0, color)




def drawLifeMeter(currentLife):
    lifeBoxSize = int((WINDOWHEIGHT - 40) / maxLife)

    # Draw background color of life meter.
    pygame.draw.rect(DISPLAYSURF, bgColor, (20, 20, 20, 20 + (maxLife * lifeBoxSize)))

    for i in range(maxLife):
        if currentLife >= (maxLife - i): # draw a solid red box
            pygame.draw.rect(DISPLAYSURF, RED, (20, 20 + (i * lifeBoxSize), 20, lifeBoxSize))
        pygame.draw.rect(DISPLAYSURF, WHITE, (20, 20 + (i * lifeBoxSize), 20, lifeBoxSize), 1)  # draw white outline


def drawLifeMeter_mc(currentLife):
    lifeBoxSize_mc = 64 / maxLife

    for i in range(maxLife):
        x1 = MC_X0 - 5
        x2 = x1 + 2
        y1 = int(MC_Y0 - i * lifeBoxSize_mc)
        y2 = int(y1 - lifeBoxSize_mc + 1)
        z1 = MC_Z0
        if currentLife >= (maxLife - i):  # draw a solid red box
            mc.setBlocks(x1, y1, z1, x2, y2, z1, param.RED_WOOL)
        else: # draw an outlined white box
            mc.setBlocks(x1, y1, z1, x2, y2, z1, param.GLASS)

def clearLifeMeter_mc():
        x1 = MC_X0 - 5
        x2 = x1 + 2
        y1 = MC_Y0
        y2 = y1 - 128 + 1
        z1 = MC_Z0
        mc.setBlocks(x1, y1, z1, x2, y2, z1, param.AIR)

def drawAchievement(achievement):
    max = 64
    achieve = int(max * achievement / 100)

    for i in range(max):
        x1 = MC_X0 - 10
        x2 = x1 + 2
        y1 = MC_Y0 - i
        z1 = MC_Z0
        if achieve > i:
            mc.setBlocks(x1, y1, z1, x2, y1, z1, param.SEA_LANTERN_BLOCK)
        else:
            mc.setBlocks(x1, y1, z1, x2, y1, z1, param.GLASS)



def getColorOfPaletteAt(x, y):
    # Returns the index of the color in paletteColors that the x and y parameters
    # are over. Returns None if x and y are not over any palette.
    numColors = len(paletteColors)
    xmargin = int((WINDOWWIDTH - ((PALETTESIZE * numColors) + (PALETTEGAPSIZE * (numColors - 1)))) / 2)
    top = WINDOWHEIGHT - PALETTESIZE - 10
    for i in range(numColors):
        # Find out if the mouse click is inside any of the palettes.
        left = xmargin + (i * PALETTESIZE) + (i * PALETTEGAPSIZE)
        r = pygame.Rect(left, top, PALETTESIZE, PALETTESIZE)
        if r.collidepoint(x, y):
            return i
    return None  # no palette exists at these x, y coordinates


def floodFill(board, oldColor, newColor, x, y):
    if x < 0 or x >= boardWidth or y < 0 or y >= boardHeight:
        return 0

    if oldColor == newColor or board[x][y] != oldColor:
        return 0

    board[x][y] = newColor  # change the color of the current box
    count = 1
    if newColor != -1:
        draw_block_mc(x, y, board)

    # Make the recursive call for any neighboring boxes:
    count += floodFill(board, oldColor, newColor, x - 1, y)  # on box to the left
    count += floodFill(board, oldColor, newColor, x + 1, y)  # on box to the right
    count += floodFill(board, oldColor, newColor, x, y - 1)  # on box to up
    count += floodFill(board, oldColor, newColor, x, y + 1)  # on box to down

    return count

def leftTopPixelCoordOfBox(boxx, boxy):
    # Returns the x and y of the left-topmost pixel of the xth & yth box.
    xmargin = int((WINDOWWIDTH - (boardWidth * boxSize)) / 2)
    ymargin = int((WINDOWHEIGHT - (boardHeight * boxSize)) / 2)
    return (boxx * boxSize + xmargin, boxy * boxSize + ymargin)


if __name__ == '__main__':
    main()
