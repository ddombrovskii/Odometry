#version 440
//////////////////////////////
//// VERTEX PROPERTIES IN ////
//////////////////////////////
layout(location = 0)in vec3 a_position;
layout(location = 1)in vec3 a_normal;
layout(location = 2)in vec2 a_texture;

//////////////////////////////
/// MATERIAL PROPERTIES IN ///
//////////////////////////////
uniform vec3  color;
uniform float alpha;

//////////////////////////////
//// CAMERA PROPERTIES IN ////
//////////////////////////////
uniform mat4  view;
uniform mat4  projection;
uniform mat4  model;

///////////////////////////////
/// MATERIAL PROPERTIES OUT ///
///////////////////////////////
out VS_MATERIAL_OUT
{
	vec3  color;
	float alpha;
} vs_mat_out;

void main()
{
	vs_mat_out.color = color ;
	vs_mat_out.alpha = alpha;
    gl_Position      = projection * view * model * vec4(a_position, 1.0);
}