#version 420
out vec4 outColor;

layout(binding = 0)uniform sampler2D fb_texture;

in vec2 v_texture;

void main()
{
    outColor = texture(fb_texture, v_texture);
}