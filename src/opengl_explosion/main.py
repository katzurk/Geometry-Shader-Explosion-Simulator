import glfw
from OpenGL.GL import *  # type: ignore
import glm
import sys
from typing import Any
import numpy as np

from opengl_explosion.camera import Camera, Direction
from opengl_explosion.loader import Model
from opengl_explosion.shader import ShaderProgram

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720


class ViewerApp:
    def __init__(self, model_path: str) -> None:
        self.model_path = model_path
        self.camera = Camera((0.0, 0.0, 5.0))
        self.last_x = WINDOW_WIDTH / 2.0
        self.last_y = WINDOW_HEIGHT / 2.0
        self.first_mouse = True
        self.delta_time = 0.0
        self.last_frame = 0.0
        self.elapsed_time = 0.0
        self.cycle_delay = 3.0

        self.gravity = 25.0
        self.intensity = 20
        self.explosion_origin = (0.0, -0.2, 0.0)
        self.explosion_dir = (10.0, 2.0, 0.0)
        self.noise_strength = 0.4
        self.radial_ratio = 0.0

        self.offsets = self.generate_offsets(grid_size=10, spacing=4.0)

    def generate_offsets(self, grid_size: int, spacing: float) -> np.ndarray:
        offsets = []
        offset_start = (grid_size - 1) * spacing / 2.0
        for x in range(grid_size):
            for z in range(grid_size):
                pos_x = x * spacing - offset_start
                pos_z = z * spacing - offset_start
                offsets.append([pos_x, 0.0, pos_z])
        return np.array(offsets, dtype=np.float32)

    def mouse_callback(self, window: Any, xpos: float, ypos: float) -> None:
        if self.first_mouse:
            self.last_x = xpos
            self.last_y = ypos
            self.first_mouse = False

        xoffset = xpos - self.last_x
        yoffset = self.last_y - ypos  # y-coordinates go from bottom to top
        self.last_x = xpos
        self.last_y = ypos

        self.camera.process_mouse_movement(xoffset, yoffset)

    def process_input(self, window: Any) -> None:
        is_pressed = lambda key: glfw.get_key(window, key) == glfw.PRESS

        if is_pressed(glfw.KEY_ESCAPE):
            glfw.set_window_should_close(window, True)

        if is_pressed(glfw.KEY_W) or is_pressed(glfw.KEY_UP):
            self.camera.process_keyboard(Direction.FORWARD, self.delta_time)
        if is_pressed(glfw.KEY_S) or is_pressed(glfw.KEY_DOWN):
            self.camera.process_keyboard(Direction.BACKWARD, self.delta_time)
        if is_pressed(glfw.KEY_A) or is_pressed(glfw.KEY_LEFT):
            self.camera.process_keyboard(Direction.LEFT, self.delta_time)
        if is_pressed(glfw.KEY_D) or is_pressed(glfw.KEY_RIGHT):
            self.camera.process_keyboard(Direction.RIGHT, self.delta_time)
        if is_pressed(glfw.KEY_Q) or is_pressed(glfw.KEY_LEFT_CONTROL):
            self.camera.process_keyboard(Direction.DOWN, self.delta_time)
        if is_pressed(glfw.KEY_E) or is_pressed(glfw.KEY_LEFT_SHIFT):
            self.camera.process_keyboard(Direction.UP, self.delta_time)

    def run(self) -> None:
        if not glfw.init():
            print("Failed to initialize GLFW")
            return

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        window = glfw.create_window(
            WINDOW_WIDTH, WINDOW_HEIGHT, "OpenGL Explosion", None, None
        )
        if not window:
            print("Failed to create GLFW window")
            glfw.terminate()
            return

        glfw.make_context_current(window)
        glfw.set_cursor_pos_callback(window, self.mouse_callback)
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

        glEnable(GL_DEPTH_TEST)

        shader_program = ShaderProgram.from_files(
            "explosion.vert",
            "explosion.geom",
            "explosion.frag",
        )
        model = Model(self.model_path, self.offsets)

        shader_program.use()
        shader_program.set_gravity(self.gravity)
        shader_program.set_intensity(self.intensity)
        shader_program.set_explosion_origin(self.explosion_origin)
        shader_program.set_explosion_dir(self.explosion_dir)
        shader_program.set_noise_strength(self.noise_strength)
        shader_program.set_radial_ratio(self.radial_ratio)

        while not glfw.window_should_close(window):
            current_frame = glfw.get_time()
            self.delta_time = current_frame - self.last_frame
            self.last_frame = current_frame
            self.elapsed_time += self.delta_time

            self.process_input(window)

            glClearColor(0.1, 0.1, 0.1, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore

            projection = glm.perspective(
                glm.radians(45.0), WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 1000.0
            )
            view = self.camera.get_view_matrix()

            model_matrix = glm.mat4(1.0)

            shader_program.set_projection(projection)
            shader_program.set_view(view)
            shader_program.set_model(model_matrix)

            cycle_time = self.elapsed_time % 6.0
            time_with_delay = max(0.0, cycle_time - self.cycle_delay)
            shader_program.set_time(time_with_delay)
            shader_program.set_radial_ratio(self.radial_ratio)

            model.draw()

            glfw.swap_buffers(window)
            glfw.poll_events()

        glfw.terminate()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m opengl_explosion.main <path_to_model>")
        return

    model_path = sys.argv[1]
    app = ViewerApp(model_path)
    app.run()


if __name__ == "__main__":
    main()
