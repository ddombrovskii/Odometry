#version 420
layout(location = 0)in vec3 a_position;
layout(location = 1)in vec3 a_normal;
layout(location = 2)in vec2 a_texture;

out vec2  v_texture;
out vec4  v_normal;
out vec4  v_position;
out vec3  v_diffuse_color;
out vec3  v_specular_color;
out mat4  v_projection;
out mat4  v_view;
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

uniform mat4  model;
uniform mat4  view;
uniform mat4  projection;

void main()
{
	v_diffuse_color  = diffuse_color ;
	v_specular_color = specular_color;
	v_illum   	     = illum   	     ;
	v_dissolve	     = dissolve	     ;
	v_ni	         = ni	         ;
	v_ns	         = ns	         ;
    v_texture        = a_texture ;
	v_projection     = projection;
	v_view           = view      ;
	v_normal		 = model * vec4(a_normal,   0.0);
	v_position       = model * vec4(a_position, 1.0);
    gl_Position      = projection * view * v_position;
}