#version 400 core

out vec4 FragColor;

in vec3 Normal;

uniform vec3 meshColor = vec3(0.2, 0.5, 0.8);
uniform vec3 lightDir = normalize(vec3(7.5, 4.0, 7.0));

void main() {
    vec3 N = normalize(Normal);
    float diff = max(dot(N, lightDir), 0.0);
    vec3 ambient = 0.2 * meshColor;
    vec3 diffuse = 0.8 * diff * meshColor;
    FragColor = vec4(ambient + diffuse, 1.0);
}