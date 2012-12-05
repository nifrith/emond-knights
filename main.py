import pygame, os, sys, copy
from pygame.locals import *
from threading import Thread

# Constants
main_dir = os.path.split(os.path.abspath(__file__))[0]

# Asset loading functions..

# Helper functions
def fadeToHandler(screen, speed, destinationHander):
  if screen.get_alpha() > 0:
    screen.set_alpha(screen.get_alpha() - speed)
  else:
    Game.handler = destinationHander

class Handler:
  # Handlers are the wrappers for the more separated parts of the game,
  # like the title screen, the main game screen, the game over..
  def update(self):
    print("Default handler")
    return True

## Loading screen stuff
def dummyLoadingFunction():
  pass

class LoadingScreenHandler(Handler):
  def __init__(self, callback, nextHandler=None):
    # Make the background stuff here.
    background = pygame.Surface(Game.screen.get_size())
    background = background.convert()
    background.fill((50,50,50))
    background.set_alpha(255)
    font = pygame.font.Font(None, 36)
    text = font.render("Loading, please wait!", 1, (255,255,255))
    textpos = text.get_rect(centerx=background.get_width()/2, centery=background.get_height()/2)
    background.blit(text, textpos)
    self.background = background

    # Start the loading callback.
    self.thread = Thread(target=callback)
    self.thread.start()

    self.nextHandler = nextHandler

  def update(self):
    # Loading finished? Transition to next handler.
    if not self.thread.isAlive():
      fadeToHandler(self.background, 3, self.nextHandler)
    # Print a black screen that says 'Loading'!
    Game.screen.blit(self.background, (0,0))
    pygame.display.flip()
    return True

## Menu and Title Screen stuff

class Button:
  def __init__(self, text, function):
    self.text = text
    self.function = function

def quitButtonFunction():
  Game.run = False

def newButtonFunction():
  Game.handler = GameScreenHandler()

class TitleScreenHandler(Handler):
  def __init__(self, buttons):
    background = pygame.Surface(Game.screen.get_size())
    background = background.convert()
    background.fill((50,50,50))
    font = pygame.font.Font(None, 36)
    text = font.render("Emond Knights", 1, (255,255,255))
    textpos = text.get_rect(centerx=background.get_width()/2, centery=background.get_height()/4)
    background.blit(text, textpos)
    self.background = background
    self.buttons = buttons[:]
    self.buttonHighlighted = 0
    self.buttonOffset = background.get_height() / 2

  def _draw(self):
    # Draw the background..
    Game.screen.blit(self.background, (0,0))
    # Now draw the buttons
    for idx, button in enumerate(self.buttons):
      fontSize = 24
      if idx == self.buttonHighlighted:
        fontSize += 4
      font = pygame.font.Font(None, fontSize)
      text = font.render(button.text, 1, (255,255,255))
      textpos = text.get_rect(centerx=self.background.get_width()/2, centery=self.buttonOffset + idx * 60)
      Game.screen.blit(text, textpos)
    # Handle any button presses here: Navigating menu, quitting game, selecting things.
    pygame.display.flip()

  def _handleInput(self):
    for event in pygame.event.get():
        if event.type == QUIT or \
            (event.type == KEYDOWN and event.key == K_ESCAPE):
                Game.run = False
        elif event.type == KEYDOWN and event.key == K_DOWN:
          if self.buttonHighlighted + 1 < len(self.buttons):
            self.buttonHighlighted += 1
        elif event.type == KEYDOWN and event.key == K_UP:
          if self.buttonHighlighted - 1 >= 0:
            self.buttonHighlighted -= 1
        elif event.type == KEYDOWN and event.key == K_RETURN:
          self.buttons[self.buttonHighlighted].function()

  def update(self):
    self._draw()
    self._handleInput()
    return True

## Game stuff

class Player(pygame.sprite.Sprite):
  def __init__(self):
    super(Player, self).__init__()
    self.xvel = 0
    self.yvel = 0
    self.image = pygame.Surface((50,50))
    self.image.fill((0,200,0))
    self.rect = self.image.get_rect()

class Camera(pygame.rect.Rect):
  def __init__(self, position):
    super(Camera, self).__init__(position)
    self.xvel = 0
    self.yvel = 0

class GameScreenHandler(Handler):
  # The game proper, if you like. An instance of this is created for each level.
  # Contains instances for the platforms you can jump on, enemies, etc.
  # Pass in the level information and whatnot.

  # Constants. Sorry, CONSTANTS!
  TILE_WIDTH = 20

  def __init__(self):
    # Vital level statistics: Height and width in tiles, and in
    # pixels, for the benefit of the camera and.. everything else.
    self.xtiles = 50
    self.ytiles = 50
    self.xpixels = self.xtiles * self.TILE_WIDTH
    self.ypixels = self.ytiles * self.TILE_WIDTH

    # Background. Right now, doesn't move and is static.
    background = pygame.Surface(Game.screen.get_size())
    background = background.convert()
    background.fill((50,50,50))
    self.background = background

    # Camera stuff. In reality, camera will be centered on player, rather than 'moving'.
    # That is to say, no xvel or yvel.
    self.camera = Camera(Game.screen.get_rect())

    # Player stuff.
    self.player = Player()

    self.testSurface = pygame.Surface((100,100))
    self.testSurface = self.testSurface.convert()
    self.testSurface.fill((200,0,0))

  def _draw(self):
    # Draw the background! Let's say it never scrolls, for now.
    Game.screen.blit(self.background, (0,0))
    Game.screen.blit(self.testSurface, (400 - self.camera.x, 300 - self.camera.y))
    Game.screen.blit(self.player.image, (self.player.rect.x - self.camera.x, self.player.rect.y - self.camera.y))
    pygame.display.flip()

  def _handleKeyDown(self,event):
    if event.key == K_UP:
      self.player.yvel -= 5
    elif event.key == K_DOWN:
      self.player.yvel += 5
    elif event.key == K_LEFT:
      self.player.xvel -= 5
    elif event.key == K_RIGHT:
      self.player.xvel += 5

  def _handleKeyUp(self, event):
    if event.key == K_UP:
      self.player.yvel += 5
    elif event.key == K_DOWN:
      self.player.yvel -= 5
    elif event.key == K_LEFT:
      self.player.xvel += 5
    elif event.key == K_RIGHT:
      self.player.xvel -= 5

  def _handleInput(self):
    for event in pygame.event.get():
        if event.type == QUIT or \
            (event.type == KEYDOWN and event.key == K_ESCAPE):
                Game.run = False
        elif event.type == KEYDOWN:
          self._handleKeyDown(event)
        elif event.type == KEYUP:
          self._handleKeyUp(event)

  def _logic(self):
    # Handle damage and whatnot
    # Handle player movement
    self.player.rect.x += self.player.xvel
    self.player.rect.y += self.player.yvel
    self.player.rect.x = max(0, self.player.rect.x)
    self.player.rect.y = max(0, self.player.rect.y)
    self.player.rect.x = min(self.player.rect.x, self.xpixels - self.player.rect.width)
    self.player.rect.y = min(self.player.rect.y, self.ypixels - self.player.rect.height)
    # Handle enemy movement
    # Adjust camera position
    self.camera.x = self.player.rect.x + (self.player.rect.width / 2) - (Game.xres / 2)
    self.camera.y = self.player.rect.y + (self.player.rect.height / 2) - (Game.yres / 2)
    self.camera.x = max(0, self.camera.x)
    self.camera.y = max(0, self.camera.y)
    self.camera.x = min(self.camera.x, self.xpixels - self.camera.width)
    self.camera.y = min(self.camera.y, self.ypixels - self.camera.height)


  def update(self):
    self._draw()
    self._handleInput()
    self._logic()
    return True

class Game:
  # Resolution..
  xres = 800
  yres = 600

  # Contains variables that are consistant across all handlers,
  # and indeed the current handler.
  handler = Handler()
  
  # PyGame variables..
  screen = None
  run = True

  # Example variables..
  lives = 0
  score = 0
  currentLevelIndex = 0
  levelFlow = ["level01", "level02", "level03"]
  levelFileMap = {"level01": "data/level01.dat"} #etc

def main():
  # Initialise stuff: Pygame, the clock..
  pygame.init()
  clock = pygame.time.Clock()

  # Get the PyGame variables in to Game.
  Game.screen = pygame.display.set_mode((Game.xres,Game.yres))
  pygame.display.set_caption('Emond Knights')

  # Load the loading screen stuff, and set the handler.
  newGame = Button("New Game", newButtonFunction)
  exitGame = Button("Exit Game", quitButtonFunction)
  Game.handler = LoadingScreenHandler(dummyLoadingFunction, TitleScreenHandler([newGame, exitGame]))
  #Game.handler = GameScreenHandler()

  blackground = pygame.Surface(Game.screen.get_size())
  blackground = blackground.convert()
  blackground.fill((0,0,0))
  blackground.set_alpha(255)

  # Let's get in to that main loop!
  while Game.run:
    # Cap the frame rate.
    clock.tick(60)

    # For all the fading and whatnot!
    Game.screen.blit(blackground, (0,0))

    # Run the current handler, which will update the screen, etc..
    if (Game.handler == None) or not Game.handler.update():
      break

  pygame.quit()

if __name__ == "__main__":
  main()