#version 330 core

layout (triangles) in;
layout (triangle_strip, max_vertices = 12) out;

in vec3 vNormal[];
out vec3 Normal;

uniform float u_time;
uniform float u_gravity;
uniform int u_intensity;
uniform vec3 u_explosion_origin;

uniform mat4 projection;
uniform mat4 view;

vec3 getNormal() {
    vec3 a = vec3(gl_in[0].gl_Position) - vec3(gl_in[1].gl_Position);
    vec3 b = vec3(gl_in[2].gl_Position) - vec3(gl_in[1].gl_Position);
    return normalize(cross(a, b));
}

vec3 explode(vec3 v, vec3 center) {
    float t = max(0.0, u_time);

    vec3 dir = normalize(center - u_explosion_origin);
    float speed = float(u_intensity);
    vec3 acc = vec3(0.0, u_gravity, 0.0);

    vec3 movedCenter = center + dir * speed * t - 0.5 * acc * t * t;

    vec3 offset = v - center;
    return movedCenter + offset;
}

void emitTriangle(vec3 pos1, vec3 pos2, vec3 pos3, vec3 normal1, vec3 normal2, vec3 normal3) {
    vec3 center = (pos1 + pos2 + pos3) / 3.0;

    gl_Position = projection * view * vec4(explode(pos1, center), 1.0);
    Normal = normal1;
    EmitVertex();

    gl_Position = projection * view * vec4(explode(pos2, center), 1.0);
    Normal = normal2;
    EmitVertex();

    gl_Position = projection * view * vec4(explode(pos3, center), 1.0);
    Normal = normal3;
    EmitVertex();

    EndPrimitive();
}

void main() {
    vec3 n0 = normalize(vNormal[0]);
    vec3 n1 = normalize(vNormal[1]);
    vec3 n2 = normalize(vNormal[2]);

    vec3 v0 = gl_in[0].gl_Position.xyz;
    vec3 v1 = gl_in[1].gl_Position.xyz;
    vec3 v2 = gl_in[2].gl_Position.xyz;

    vec3 m01 = (v0 + v1) * 0.5;
    vec3 m12 = (v1 + v2) * 0.5;
    vec3 m20 = (v2 + v0) * 0.5;

    vec3 n01 = normalize(n0 + n1);
    vec3 n12 = normalize(n1 + n2);
    vec3 n20 = normalize(n2 + n0);

    emitTriangle(m01, m12, m20, n01, n12, n20);
    emitTriangle(v0, m01, m20, n0, n01, n20);
    emitTriangle(m01, v1, m12, n01, n1, n12);
    emitTriangle(m20, m12, v2, n20, n12, n2);
}