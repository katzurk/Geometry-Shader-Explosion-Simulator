import os
from OpenGL.GL import *  # type: ignore
from OpenGL.GL import shaders

SHADER_DIR = os.path.join(os.path.dirname(__file__), "shaders")

def load_shader(filename: str) -> str:
    path = os.path.join(SHADER_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def create_shader_program() -> shaders.ShaderProgram:
    vertex_shader = shaders.compileShader(load_shader("explosion.vert"), GL_VERTEX_SHADER)
    geometry_shader = shaders.compileShader(load_shader("explosion.geom"), GL_GEOMETRY_SHADER)
    fragment_shader = shaders.compileShader(load_shader("explosion.frag"), GL_FRAGMENT_SHADER)
    shader_program = shaders.compileProgram(vertex_shader, geometry_shader, fragment_shader)
    return shader_program
