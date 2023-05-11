#version 420
out vec4 outColor;

layout(binding = 0)uniform sampler2D ui_texture;
layout(binding = 1)uniform sampler2D ui_texture_info;
layout(binding = 2)uniform sampler2D ui_transparent_texture;
layout(binding = 3)uniform sampler2D ui_transparent_texture_info;

in vec2 v_texture;

void main()
{
    float transparency = texture(ui_transparent_texture_info, v_texture).a;

    if (transparency == 0.0)
    {
        outColor = texture(ui_texture, v_texture);
        return;
    }
    float blur = 0.002;

    vec4 transparentColor = texture(ui_transparent_texture, v_texture);
    vec4 mainColor        = texture(ui_texture, v_texture);
    outColor              = mainColor * transparency + transparentColor * (1 - transparency);
}