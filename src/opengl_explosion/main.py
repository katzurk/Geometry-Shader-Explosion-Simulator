import glfw
from OpenGL.GL import *  # type: ignore
import glm
import sys
from typing import Any

from opengl_explosion.camera import Camera, Direction
from opengl_explosion.loader import Model
from opengl_explosion.shader import create_shader_program

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

    def mouse_callback(self, xpos: float, ypos: float) -> None:
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

        shader_program = create_shader_program()
        model = Model(self.model_path)

        while not glfw.window_should_close(window):
            current_frame = glfw.get_time()
            self.delta_time = current_frame - self.last_frame
            self.last_frame = current_frame

            self.process_input(window)

            glClearColor(0.1, 0.1, 0.1, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore

            glUseProgram(shader_program)

            projection = glm.perspective(
                glm.radians(45.0), WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 1000.0
            )
            view = self.camera.get_view_matrix()

            model_matrix = glm.mat4(1.0)

            proj_loc = glGetUniformLocation(shader_program, "projection")
            view_loc = glGetUniformLocation(shader_program, "view")
            model_loc = glGetUniformLocation(shader_program, "model")

            glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glm.value_ptr(projection))
            glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model_matrix))

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
