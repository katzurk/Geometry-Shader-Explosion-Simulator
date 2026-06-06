import os
from typing import Any

from OpenGL.GL import *
from OpenGL.GL import shaders
import glm

SHADER_DIR = os.path.join(os.path.dirname(__file__), "shaders")

def load_shader_source(filename: str) -> str:
    path = os.path.join(SHADER_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

class ShaderProgram:
    U_TIME = "u_time"
    U_GRAVITY = "u_gravity"
    U_INTENSITY = "u_intensity"
    U_EXPLOSION_ORIGIN = "u_explosion_origin"
    U_EXPLOSION_DIR = "u_explosion_dir"
    U_NOISE_STRENGTH = "u_noise_strength"
    U_RADIAL_RATIO = "u_radial_ratio"
    U_PROJECTION = "projection"
    U_VIEW = "view"
    U_MODEL = "model"

    def __init__(self, vertex_source: str, geometry_source: str, fragment_source: str,) -> None:
        self.program = shaders.compileProgram(
            shaders.compileShader(vertex_source, GL_VERTEX_SHADER),
            shaders.compileShader(geometry_source, GL_GEOMETRY_SHADER),
            shaders.compileShader(fragment_source, GL_FRAGMENT_SHADER),
        )
        self._uniform_cache: dict[str, int] = {}

    @classmethod
    def from_files(cls, vertex_filename: str, geometry_filename: str, fragment_filename: str) -> "ShaderProgram":
        return cls(
            load_shader_source(vertex_filename),
            load_shader_source(geometry_filename),
            load_shader_source(fragment_filename),
        )

    def use(self) -> None:
        glUseProgram(self.program)

    def get_uniform_location(self, name: str) -> int:
        if name in self._uniform_cache:
            return self._uniform_cache[name]

        location = glGetUniformLocation(self.program, name)
        if location == -1:
            raise ValueError(f"Uniform '{name}' not found in shader program.")

        self._uniform_cache[name] = location
        return location

    def set_bool(self, name: str, value: bool) -> None:
        glUniform1i(self.get_uniform_location(name), int(value))

    def set_int(self, name: str, value: int) -> None:
        glUniform1i(self.get_uniform_location(name), value)

    def set_float(self, name: str, value: float) -> None:
        glUniform1f(self.get_uniform_location(name), value)

    def set_vec3(self, name: str, value: Any) -> None:
        if hasattr(value, "x") and hasattr(value, "y") and hasattr(value, "z"):
            x, y, z = value.x, value.y, value.z
        else:
            x, y, z = value
        glUniform3f(self.get_uniform_location(name), float(x), float(y), float(z))

    def set_mat4(self, name: str, matrix: Any, transpose: bool = False) -> None:
        glUniformMatrix4fv(
            self.get_uniform_location(name),
            1,
            GL_TRUE if transpose else GL_FALSE,
            glm.value_ptr(matrix),
        )

    def set_time(self, value: float) -> None:
        self.set_float(self.U_TIME, value)

    def set_gravity(self, value: float) -> None:
        self.set_float(self.U_GRAVITY, value)

    def set_intensity(self, value: int) -> None:
        self.set_int(self.U_INTENSITY, value)

    def set_explosion_origin(self, value: Any) -> None:
        self.set_vec3(self.U_EXPLOSION_ORIGIN, value)

    def set_explosion_dir(self, value: Any) -> None:
        self.set_vec3(self.U_EXPLOSION_DIR, value)

    def set_noise_strength(self, value: float) -> None:
        self.set_float(self.U_NOISE_STRENGTH, value)

    def set_radial_ratio(self, value: float) -> None:
        self.set_float(self.U_RADIAL_RATIO, value)

    def set_projection(self, matrix: Any) -> None:
        self.set_mat4(self.U_PROJECTION, matrix)

    def set_view(self, matrix: Any) -> None:
        self.set_mat4(self.U_VIEW, matrix)

    def set_model(self, matrix: Any) -> None:
        self.set_mat4(self.U_MODEL, matrix)

    def delete(self) -> None:
        glDeleteProgram(self.program)
