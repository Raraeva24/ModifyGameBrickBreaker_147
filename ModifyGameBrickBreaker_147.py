import tkinter as tk
import random

class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)

class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 10
        item = canvas.create_oval(
            x - self.radius,
            y - self.radius,
            x + self.radius,
            y + self.radius,
            fill='white'
        )
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()

class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill='#ffd500'
        )
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)

class Brick(GameObject):
    COLORS = {1: '#C98DAC', 2: '#75425C', 3: '#4A2B46'}

    def __init__(self, canvas, x, y, hits, game):
        self.width = 75
        self.height = 20
        self.hits = hits
        self.game = game
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.drop_coin()
            self.create_sparks()
            self.delete()
        else:
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])

    def drop_coin(self):
        coords = self.get_position()
        x = (coords[0] + coords[2]) / 2
        y = coords[3]
        coin = Coin(self.canvas, x, y, self.game)
        self.game.items[coin.item] = coin

    def create_sparks(self):
        coords = self.get_position()
        x = (coords[0] + coords[2]) / 2
        y = (coords[1] + coords[3]) / 2
        for _ in range(10):
            spark_x = x + random.randint(-10, 10)
            spark_y = y + random.randint(-10, 10)
            spark = self.canvas.create_oval(
                spark_x - 2, spark_y - 2,
                spark_x + 2, spark_y + 2,
                fill='red', tags='spark'
            )
            self.canvas.after(200, lambda item=spark: self.canvas.delete(item))

class Coin(GameObject):
    def __init__(self, canvas, x, y, game):
        self.game = game
        self.width = 15
        self.height = 15
        item = canvas.create_oval(
            x - self.width / 2, y - self.height / 2,
            x + self.width / 2, y + self.height / 2,
            fill='gold', tags='coin'
        )
        super(Coin, self).__init__(canvas, item)
    def update(self):
        self.move(0, 5)
        if self.get_position()[3] > self.game.height:
            self.delete()

class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3  # Set initial life count here
        self.score = 0
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#D6D1F5',
                                width=self.width,
                                height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle

        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

        self.hud_lives = None
        self.hud_score = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))

    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        self.update_score_text()
        self.text = self.draw_text(300, 200, 'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits, self)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='50'):
        font = ('Small Fonts', size)
        return self.canvas.create_text(x, y, text=text, font=font)

    def update_lives_text(self):
        if self.hud_lives is None:
            self.hud_lives = self.draw_text(50, 20, f'Lives: {self.lives}', 15)
        else:
            self.canvas.itemconfig(self.hud_lives, text=f'Lives: {self.lives}')

    def update_score_text(self):
        if self.hud_score is None:
            self.hud_score = self.draw_text(200, 20, f'Score: {self.score}', 15)
        else:
            self.canvas.itemconfig(self.hud_score, text=f'Score: {self.score}')

    def update_score(self, points):
        self.score += points
        self.update_score_text()

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.ball.speed = None
            self.draw_text(300, 200, 'You win! You are the Breaker of Bricks.')
        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = None
            self.lives -= 1
            self.update_lives_text()
            if self.lives < 0:
                self.draw_text(300, 200, 'You Lose! Game Over!')
            else:
                                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            for item in self.canvas.find_withtag('coin'):
                self.items[item].update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)

        # Check for coin collisions
        paddle_coords = self.paddle.get_position()
        for item in self.canvas.find_withtag('coin'):
            coin = self.items.get(item)
            if coin:
                coin_coords = coin.get_position()
                if (
                    paddle_coords[0] < coin_coords[2]
                    and paddle_coords[2] > coin_coords[0]
                    and paddle_coords[1] < coin_coords[3]
                ):
                    self.update_score(1)
                    coin.delete()

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break those Bricks!')
    game = Game(root)
    game.mainloop()
