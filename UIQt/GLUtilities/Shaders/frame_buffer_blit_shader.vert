#version 420
layout(location = 0)in vec3 a_position;
layout(location = 2)in vec2 a_texture;
out vec2 v_texture;

void main()
{
    gl_Position = vec4(vec3(a_position.x, a_position.z, 0.0), 1.0f);
    v_texture   = a_texture;
}