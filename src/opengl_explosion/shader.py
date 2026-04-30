from OpenGL.GL import *  # type: ignore
from OpenGL.GL import shaders

VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;

out vec3 Normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    // Passing normal to fragment shader (assuming uniform scaling)
    Normal = mat3(transpose(inverse(model))) * aNormal;
}
"""

FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;

in vec3 Normal;

void main()
{
    // Remap normal from [-1, 1] to [0, 1] for a colorful simplistic look
    vec3 color = normalize(Normal) * 0.5 + 0.5;
    FragColor = vec4(color, 1.0);
}
"""


def create_shader_program() -> shaders.ShaderProgram:
    vertex_shader = shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER)
    fragment_shader = shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
    shader_program = shaders.compileProgram(vertex_shader, fragment_shader)
    return shader_program
