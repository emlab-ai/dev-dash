# import pygame

# # pygame setup
# pygame.init()
# screen = pygame.display.set_mode((1280, 720))
# clock = pygame.time.Clock()
# running = True
# dt = 0


# def check_for_exit():
#     global running
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False


# class Dino:
#     position = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
#     velocity = 0

#     def draw(self):
#         # todo: render image
#         pygame.draw.circle(screen, "red", self.position, 40)
#         pygame.draw.circle(screen, "blue", self.position, 20)

#     def jump(self):
#         if self.velocity != 0:
#             return

#         self.velocity = -600  # initial jump velocity

#     def update(self, dt):
#         self.velocity += 981 * dt  # gravity
#         self.position.y += self.velocity * dt

#         # Check if dino has landed on the ground
#         if self.position.y >= screen.get_height() / 2:
#             self.position.y = screen.get_height() / 2
#             self.velocity = 0

#     def move_left(self, dt):
#         self.position.x -= 300 * dt

#     def move_right(self, dt):
#         self.position.x += 300 * dt


# max = Dino()

# while running:

#     check_for_exit()

#     # fill the screen with a color to wipe away anything from last frame
#     screen.fill("purple")

#     max.update(dt)
#     max.draw()

#     keys = pygame.key.get_pressed()
#     if keys[pygame.K_SPACE]:
#         max.jump()
#     if keys[pygame.K_a]:
#         max.move_left(dt)
#     if keys[pygame.K_d]:
#         max.move_right(dt)

#     # flip() the display to put your work on screen
#     pygame.display.flip()

#     # limits FPS to 60
#     # dt is delta time in seconds since last frame, used for framerate-
#     # independent physics.
#     dt = clock.tick(60) / 1000

# pygame.quit()


import asyncio
import json
from app_sql import setup_async_sql_engine, setup_sql_engine
from db.repository.asyncRepository import AsyncRepository
from db.model.metric import Metric
from db.repository.githubEventsRepository import GithubEventsRepository
from services.githubWebhookService import GithubWebhookService

setup_sql_engine()
Session = setup_async_sql_engine()


async def testrun():
    async with Session() as session:
        ws = GithubWebhookService(session, inprocess=True)
        er = GithubEventsRepository()
        event = er.get(1, "3cdb19c2-bee3-11ef-8be6-708ffbfa36b7")
        data = event['data']
        await ws.record_event_async("issue_comment", "3cdb19c2-bee3-11ef-8be6-708ffbfa36b7", data)
        print("done")


asyncio.run(testrun())
