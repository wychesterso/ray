import tkinter as tk
import random


class Enemy():
    """A red object falling from above that The Ray has to destroy."""
    def __init__(self, canvas: tk.Canvas, 
                 health: int, speed: int, spawn_x: int) -> None:
        """Creates an enemy.
        
        Parameters:
            canvas (tk.Canvas): The canvas that the enemy is in.
            health (int): The starting health of the enemy.
            speed (int): The speed at which the enemy falls.
            spawn_x (int): The x-coordinate where the enemy spawns.
        """
        self._canvas = canvas
        self._health = health
        self._speed = speed
        self._position = (spawn_x, 0)
        self._id = self._canvas.create_rectangle(spawn_x - 5, -5, 
                                                 spawn_x + 5, 5, fill="red")

    def is_alive(self) -> bool:
        """(bool): Returns true if enemy is alive."""
        return self._health > 0

    def get_id(self) -> int:
        """(int): Returns the id of the enemy object on the canvas."""
        return self._id

    def get_position(self) -> tuple[int, int]:
        """(tuple[int, int]: Returns the coordinate position of the enemy."""
        return self._position

    def damage(self, damage: int) -> None:
        """Damages the enemy.
        
        Parameters:
            damage (int): The amount of damage dealt.
        """
        self._health -= damage
        if self._health <= 0:
            self._canvas.delete(self._id)
    
    def move(self) -> None:
        """Moves the enemy downwards."""
        self._position = (self._position[0], self._position[1] + self._speed)
        self._canvas.move(self._id, 0, self._speed)


class InfoFrame(tk.Frame):
    """A frame for the information text at the bottom of the window."""
    def __init__(self, root: tk.Tk) -> None:
        """Creates an info frame.
        
        Parameters:
            root (tk.Tk): The root window.
        """
        super().__init__(root)

        self._level_label = tk.Label(self, text="", font=("Times", 15, "bold"))
        self._level_label.pack(side=tk.LEFT)

        self._lives_label = tk.Label(self, text="", font=("Times", 15, "bold"))
        self._lives_label.pack(side=tk.RIGHT)
    
    def update_level(self, level: int) -> None:
        """Updates the level label.
        
        Parameters:
            level (int): The current level.
        """
        self._level_label.config(text=f"LEVEL {level}")

    def update_lives(self, lives: int) -> None:
        """Updates the lives label.
        
        Parameters:
            lives (int): The current number of lives left.
        """
        self._lives_label.config(text=f"LIVES: {lives}")


class TheRay():
    """The Ray of Death."""
    _size = 500
    _origin = (_size // 2, _size)
    _shadow_origin = (_size // 2 + 2, _size + 2)
    
    def __init__(self, root: tk.Tk) -> None:
        """Creates The Ray.
        
        Parameters:
            root (tk.Tk): The root window.
        """
        self._root = root
        root.minsize(self._size, self._size)
        root.maxsize(self._size, self._size)

        self._id = None
        self._shadow_id = None

        self._canvas = tk.Canvas(root, bg="black", bd=2, relief=tk.SUNKEN)
        self._canvas.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self._info = InfoFrame(root)
        self._info.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self._game = False
        self._scheduled_movement = None
        self._scheduled_spawn = None
        self._enemies = []
        self._enemy_count = 0

        self._canvas.bind('<B1-Motion>', self.evt_click_motion)
        self._canvas.bind('<ButtonRelease-1>', self.evt_release)

        self.start_click()
    
    def start_click(self) -> None:
        """Initializes the title screen."""
        self._canvas.delete(tk.ALL)

        self._canvas.create_text(252, 252, text="THE RAY", fill="white", 
                                 font=("STHupo", 50, "bold"))
        self._canvas.create_text(250, 250, text="THE RAY", fill="red", 
                                 font=("STHupo", 50, "bold"))
        self._canvas.create_text(250, 300, text="Click to start", fill="white", 
                                 font=("Times", 15, "bold"))
        self._canvas.bind('<Button-1>', self.restart)

    def evt_click_motion(self, event) -> None:
        """Handles click and drag events."""
        self._x = event.x
        self._y = event.y

        self._canvas.delete(self._id)
        self._canvas.delete(self._shadow_id)

        line_points = list(self.bresenham_line(self._origin[0], self._origin[1],
                                               self._x, self._y))
        self.attack(line_points)
        # bug - only deals damage when The Ray moves

        self._shadow_id = self._canvas.create_line(self._shadow_origin, 
                                                   (self._x + 2, self._y + 2), 
                                                   width=3, fill="#ff8282")
        self._id = self._canvas.create_line(self._origin, 
                                            (self._x, self._y), 
                                            width=3, fill="red")

    def evt_release(self, event=None) -> None:
        """Handles release events."""
        self._canvas.delete(self._id)
        self._canvas.delete(self._shadow_id)

    def bresenham_line(self, x0: int, y0: int, x1: int, y1: int):
        """Generate integer coordinates on the line from (x0, y0) to (x1, y1)
        using Bresenham's algorithm.
        
        Parameters:
            x0 (int): Initial x-coordinate.
            y0 (int): Initial y-coordinate.
            x1 (int): Final x-coordinate.
            y1 (int): Final y-coordinate.

        Returns:
            An iterator that yields tuples of integers.
        """
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            yield (x0, y0)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def schedule_enemy_spawn(self) -> None:
        """Spawns enemies automatically, and ends the level when all enemies
        are dead."""
        if self._game:
            if self._level == 1:
                enemy_speed = 1
                spawn_delay = 1000
            elif self._level in [2, 3]:
                enemy_speed = 2
                spawn_delay = 800
            elif self._level in [4, 5]:
                enemy_speed = 3
                spawn_delay = 800
            else:
                enemy_speed = self._level // 2 + 1
                spawn_delay = 700

            if self._enemy_count < 10:
                spawn_x = random.randint(10, 490)
                new_enemy = Enemy(self._canvas, health=1, speed=enemy_speed, 
                                spawn_x=spawn_x)
                self._enemies.append(new_enemy)
                self._enemy_count += 1
                self._scheduled_spawn = self._root.after(spawn_delay, 
                                                        self.schedule_enemy_spawn)
            elif self._enemy_count >= 10:
                self._enemies = [enemy for enemy in self._enemies 
                                if enemy.is_alive()]
                if not self._lives <= 0:
                    if not self._enemies:
                        self.advance_level()
                    else:
                        # if any enemies are alive, recursion after 2000
                        self._scheduled_spawn = self._root.after(2000, self.schedule_enemy_spawn)

    def advance_level(self) -> None:
        """Handles transition into next level."""
        self._level += 1
        self._info.update_level(self._level)
        level_text = self._canvas.create_text(250, 250, 
                                              text=f"LEVEL {self._level}", 
                                              fill="red", 
                                              font=("STHupo", 35, "bold"))
        self._root.after(1500, lambda: self._canvas.delete(level_text))
        self._enemy_count = 0
        self.schedule_enemy_spawn()

    def schedule_enemy_movement(self) -> None:
        """Makes all enemies move automatically."""
        for enemy in self._enemies:
            enemy.move()
            if enemy.is_alive() and enemy.get_position()[1] >= 500:
                self._enemies.remove(enemy)
                self._lives -= 1
                self._info.update_lives(self._lives)
                if self._lives <= 0:
                    self._lives = 0
                    self.game_over()
                    return

        self._scheduled_movement = self._root.after(10, self.schedule_enemy_movement)

    def attack(self, target_positions: list[tuple[int, int]]) -> None:
        """Attacks all enemies on the given positions.
        
        Parameters:
            target_positions (list[tuple[int, int]]): A list of coordinates
                to attack.
        """
        enemy_dict = {}
        for enemy in self._enemies:
            enemy_dict[enemy.get_position()] = enemy
        
        for x, y in target_positions:
            # check the target position and some adjacent positions
            for x_add in range(-2, 3):
                for y_add in range(-2, 3):
                    attack_pos = (x + x_add, y + y_add)
                    if attack_pos in enemy_dict:
                        enemy_dict[attack_pos].damage(1)

    def game_over(self) -> None:
        """Handles game over."""
        self._game = False
        for enemy in self._enemies:
            self._canvas.delete(enemy.get_id())
        self._enemies.clear()

        self._lose_text_1 = self._canvas.create_text(252, 252, text="YOU LOSE", 
                                                     fill="white", 
                                                     font=("STHupo", 35, "bold"))
        self._lose_text_2 = self._canvas.create_text(250, 250, text="YOU LOSE", 
                                                     fill="red", 
                                                     font=("STHupo", 35, "bold"))
        
        self._root.after(3000, self.restart_click)

    def restart_click(self) -> None:
        """Initializes the restart screen."""
        self._canvas.delete(tk.ALL)

        self._canvas.create_text(252, 252, text="THE RAY", fill="white", 
                                 font=("STHupo", 50, "bold"))
        self._canvas.create_text(250, 250, text="THE RAY", fill="red", 
                                 font=("STHupo", 50, "bold"))
        self._canvas.create_text(250, 300, text="Click to restart", 
                                 fill="white", font=("Times", 15, "bold"))
        
        self._canvas.bind('<Button-1>', self.restart)

    def restart(self, event=None) -> None:
        """Handles game start."""
        self._canvas.unbind('<Button-1>')
        self._canvas.delete(tk.ALL)

        if self._scheduled_movement:
            self._root.after_cancel(self._scheduled_movement)
        if self._scheduled_spawn:
            self._root.after_cancel(self._scheduled_spawn)

        self._game = True
        self._lives = 5
        self._level = 0
        self._enemy_count = 0
        self._enemies.clear()

        self._info.update_lives(self._lives)
        self.advance_level()
        self.schedule_enemy_movement()


if __name__ == '__main__':
    root = tk.Tk()
    root.title("The Ray")
    app = TheRay(root)
    root.mainloop()