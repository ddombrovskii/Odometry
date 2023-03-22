#version 420
layout(location = 0)in vec3 a_position;
layout(location = 2)in vec2 a_normal;
layout(location = 2)in vec2 a_texture;

out vec2  v_texture;
out vec3  v_diffuse_color;
out vec3  v_specular_color;
out float v_illum;
out float v_dissolve;
out float v_ni;
out float v_ns;

uniform vec3  diffuse_color;
uniform vec3  specular_color;
uniform float illum;
uniform float dissolve;
uniform float ni;
uniform float ns;

uniform mat4  transform;
uniform mat4  projection;
uniform mat4  view;

void main()
{
	v_diffuse_color  = diffuse_color ;
	v_specular_color = specular_color;
	v_illum   	     = illum   	     ;
	v_dissolve	     = dissolve	     ;
	v_ni	         = ni	         ;
	v_ns	         = ns	         ;
    v_texture        = a_texture;
    gl_Position      = transform * vec4(vec3(a_position.x, a_position.z, 0.0), 1.0f);
}