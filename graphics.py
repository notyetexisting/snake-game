import turtle as t

class Graphics:
    def __init__(self):
        self.screen = t.Screen()
        self.screen.title("SNAKE GAME")
        self.screen.bgcolor("green")
        self.screen.setup(width=600, height=600)
        self.screen.tracer(0)

        self.snake_head = self.load_image("assets/images/snake_head.gif")
        self.snake_body = self.load_image("assets/images/snake_body.gif")
        self.food_image = self.load_image("assets/images/food.gif")

        self.screen.addshape(self.snake_head)
        self.screen.addshape(self.snake_body)
        self.screen.addshape(self.food_image)

    def load_image(self, path):
        return path

    def draw_snake(self, segments):
        for segment in segments:
            segment.shape(self.snake_body)

    def draw_food(self, food):
        food.shape(self.food_image)

    def update_screen(self):
        self.screen.update()