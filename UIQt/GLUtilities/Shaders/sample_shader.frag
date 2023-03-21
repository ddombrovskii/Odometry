#version 420
out vec4 outColor;

layout(binding = 0)uniform sampler2D diffuse;
layout(binding = 1)uniform sampler2D specular;
layout(binding = 2)uniform sampler2D normals;

in vec2  v_texture;
in vec3  v_diffuse_color;
in vec3  v_specular_color;
in float v_illum;
in float v_dissolve;
in float v_ni;
in float v_ns;

void main()
{
    outColor = vec4(1, 0, 0, 0);
}