# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

#KRT 14/06/2012 modified Start Screen and Game Over screen to cope with mouse events
#KRT 14/06/2012 Added a non-busy wait to Game Over screen to reduce processor loading from near 100%
import random, pygame, sys
from pygame.locals import *

GAMEFPS = 10
OPENINGFPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
BLUE      = (  0,   0, 255)
LIGHTBLUE = (150, 150, 255)
DARKGREEN = (  0, 155,   0)
DARKBLUE  = (  0,   0, 150)
GRAY      = (100, 100, 100)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
OPPOSITE = {UP:DOWN, RIGHT:LEFT, LEFT:RIGHT, DOWN:UP}

HEAD = 0 # syntactic sugar: index of the worm's head

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption("Wormy's Revenge")

    showStartScreen()
    while True:
        winner, color = runGame()
        showGameOverScreen(winner, color)

class Worm:
    def __init__(self, startx, starty, direction):
        self.coords = [{'x': startx, 'y': starty}]
        self.direction = direction
        self.directionQueue = []
        self.controls = {}
        self.color = GREEN
        self.scoreLocation = ()
        self.length = 3
        self.score = 0
        self.lost = False
    
    def darken(self, c):
        return (int(c[0]/2), int(c[1]/2), int(c[2]/2))
    
    def draw(self):
        for coord in self.coords:
            x = coord['x'] * CELLSIZE
            y = coord['y'] * CELLSIZE
            wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
            pygame.draw.rect(DISPLAYSURF, self.darken(self.color), wormSegmentRect)
            wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
            pygame.draw.rect(DISPLAYSURF, self.color, wormInnerSegmentRect)
    
    def hasEatenApple(self, apple):
        return self.coords[HEAD]['x'] == apple['x'] and self.coords[HEAD]['y'] == apple['y']
    
    def processEvent(self, event):
        if self.controls.has_key(event.key):
            self.directionQueue.append(self.controls[event.key])
    
    def advanceDirection(self):
        if len(self.directionQueue):
            newDirection = self.directionQueue.pop(0)
            if OPPOSITE[newDirection] != self.direction:
                self.direction = newDirection
    
    def hasHitBounds(self):
        # check if the worm has hit itself or the edge
        head = self.coords[HEAD]
        if head['x'] < 0 or head['x'] >= CELLWIDTH or head['y'] < 0 or head['y'] == CELLHEIGHT:
            return True
        return False
    
    def hasEaten(self, opponent):
        head = self.coords[HEAD]
        start = 0
        if opponent == self:
            start = 1
        for wormBody in opponent.coords[start:]:
            if wormBody['x'] == head['x'] and wormBody['y'] == head['y']:
                return True
        return False
    
    def advanceHead(self):
        # move the worm by adding a segment in thedirection it is moving
        head = self.coords[HEAD]
        newHead = {}
        if self.direction == UP:
            newHead = {'x': head['x'], 'y': head['y'] - 1}
        elif self.direction == DOWN:
            newHead = {'x': head['x'], 'y': head['y'] + 1}
        elif self.direction == LEFT:
            newHead = {'x': head['x'] - 1, 'y': head['y']}
        elif self.direction == RIGHT:
            newHead = {'x': head['x'] + 1, 'y': head['y']}
        if len(self.coords) >= self.length:
            self.advanceTail()
        self.coords.insert(0, newHead)
    
    def advanceTail(self):
        del self.coords[-1]
    
    def drawScore(self):
        drawScore(self.score, self.scoreLocation, self.color)


def runGame():
    worm1 = Worm(4, int((CELLHEIGHT - 1) / 2), RIGHT)
    worm1.controls = {K_a:LEFT, K_w:UP, K_s:DOWN, K_d:RIGHT}
    worm1.color = LIGHTBLUE
    worm1.scoreLocation = (80, 10)
    
    worm2 = Worm(CELLWIDTH - 4, int((CELLHEIGHT - 1) / 2), LEFT)
    worm2.controls = {K_LEFT:LEFT, K_UP:UP, K_DOWN:DOWN, K_RIGHT:RIGHT}
    worm2.color = GREEN
    worm2.scoreLocation = (WINDOWWIDTH - 120, 10)
    
    allWorms = [worm1, worm2]
    
    # Start the apple in a random place.
    apples = [getRandomLocation(), getRandomLocation(), getRandomLocation()]
    
    while True: # main game loop
        allEvents = pygame.event.get()
        
        for event in allEvents:
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                terminate()
        
        eatenApples = []
        
        for worm in allWorms:
            for event in allEvents: # event handling loop
                if event.type == KEYDOWN:
                    worm.processEvent(event)
            
            worm.advanceDirection()
            
            if worm.hasHitBounds():
                worm.lost = True
            
            for opponent in allWorms:
                if worm.hasEaten(opponent):
                    worm.lost = True
            
            # check if worm has eaten an apple
            for apple in apples:
                if worm.hasEatenApple(apple):
                    worm.length += 3
                    worm.score += 1
                    eatenApples.append(apple)
        
        gameover = False
        for worm in allWorms:
            if worm.lost:
                gameover = True
        if gameover:
            break
        
        for worm in allWorms:
            if not worm.lost:
                worm.advanceHead()
        
        newApples = []
        for apple in apples:
            if apple in eatenApples:
                newApples.append(getRandomLocation())
            else:
                newApples.append(apple)
        apples = newApples
        
        drawGrid()
        
        for worm in allWorms:
            worm.draw()
        
        for apple in apples:
            drawApple(apple)
        
        for worm in allWorms:
            worm.drawScore()
        
        pygame.display.update()
        FPSCLOCK.tick(GAMEFPS)
    
    if worm1.lost and worm2.lost:
        return "Cat's game", WHITE
    
    if worm1.lost:
        return 'Worm 2 wins', worm2.color
    
    if worm2.lost:
        return 'Worm 1 wins', worm1.color

def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, GRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)



# KRT 14/06/2012 rewrite event detection to deal with mouse use
def checkForKeyPress():
    for event in pygame.event.get():
        if event.type == QUIT:      #event is quit 
            terminate()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:   #event is escape key
                terminate()
            else:
                return event.key   #key found return with it
    # no quit or key events in queue so return None    
    return None


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render("Revenge", True, BLACK, DARKBLUE)
    titleSurf2 = titleFont.render("Wormy's", True, BLUE)
    degrees1 = 0
    degrees2 = 0

#KRT 14/06/2012 rewrite event detection to deal with mouse use
    pygame.event.get()  #clear out event queue
    
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()
#KRT 14/06/2012 rewrite event detection to deal with mouse use
        if checkForKeyPress():
            return
        pygame.display.update()
        FPSCLOCK.tick(OPENINGFPS)
        degrees1 += 1.1
        degrees2 += 3.2


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def showGameOverScreen(winner, color):
    font = pygame.font.Font('freesansbold.ttf', 70)
    smallfont = pygame.font.Font('freesansbold.ttf', 30)
    surf = font.render('GAME OVER', True, WHITE)
    winnersurf = smallfont.render(winner, True, color)
    rect = surf.get_rect()
    winnerrect = winnersurf.get_rect()
    
    rect.midtop = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2 - rect.height / 2)
    winnerrect.midtop = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2 - rect.height / 2 + 100)

    DISPLAYSURF.blit(surf, rect)
    DISPLAYSURF.blit(winnersurf, winnerrect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
#KRT 14/06/2012 rewrite event detection to deal with mouse use
    pygame.event.get()  #clear out event queue 
    while True:
        if checkForKeyPress():
            return
#KRT 12/06/2012 reduce processor loading in gameover screen.
        pygame.time.wait(100)

def drawScore(score, location, color):
    scoreSurf = BASICFONT.render('Apples: %s' % (score), True, color)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = location
    DISPLAYSURF.blit(scoreSurf, scoreRect)

def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawGrid():
    DISPLAYSURF.fill(BGCOLOR)
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()
