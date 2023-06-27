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
// layout(std140) uniform MatInfo
// {
//   float _illum;
//   float _dissolve;
//   float _ni;
//   float _ns;
//   vec3  _diffuse_color;
//   vec3  _specular_color;
// };

uniform vec3  diffuse_color;
uniform vec3  specular_color;
uniform float illum;
uniform float dissolve;
uniform float ni;
uniform float ns;

//////////////////////////////
//// CAMERA PROPERTIES IN ////
//////////////////////////////
uniform mat4  view;
uniform mat4  projection;
uniform vec3  cam_position;
uniform mat4  model;

///////////////////////////////
//// VERTEX PROPERTIES OUT ////
///////////////////////////////
out VS_VERTEX_OUT
{
  vec2  uv;
  vec3  normal;
  vec3  position;
} vs_vert_out;

///////////////////////////////
//// CAMERA PROPERTIES OUT ////
///////////////////////////////
out VS_CAMERA_OUT
{
    vec3  position;
    mat4  projection;
    mat4  view;
} vs_cam_out;

///////////////////////////////
/// MATERIAL PROPERTIES OUT ///
///////////////////////////////
out VS_MATERIAL_OUT
{
    vec3  diffuse_color;
    vec3  specular_color;
    float illum;
    float dissolve;
    float ni;
    float ns;
} vs_mat_out;

void main()
{
	vs_mat_out.diffuse_color  = diffuse_color ;
	vs_mat_out.illum   	      = illum   	  ;
	vs_mat_out.dissolve	      = dissolve	  ;
	vs_mat_out.ni	          = ni	          ;
	vs_mat_out.ns	          = ns	          ;
	vs_mat_out.specular_color = specular_color;
	vs_cam_out.projection     = projection;
	vs_cam_out.position       = cam_position;
	vs_cam_out.view           = view;

    vs_vert_out.uv           = a_texture ;
	vs_vert_out.normal		 = normalize((model * vec4(a_normal, 0.0)).xyz);
	vs_vert_out.position     = (model * vec4(a_position, 1.0)).xyz;

    gl_Position      = projection * view * vec4(vs_vert_out.position, 1.0);
}