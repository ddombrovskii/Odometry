#version 440
//////////////////////////////
//// VERTEX PROPERTIES IN ////
//////////////////////////////
layout(location = 0)in vec3 a_position;
layout(location = 2)in vec2 a_texture;

//////////////////////////////
/// OBJECT SIZE PROPERTIES ///
//////////////////////////////
uniform vec3  max_bound;
uniform vec3  min_bound;
// uniform int   heat_or_height;

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
  vec3  position;
  vec3  max_bound;
  vec3  min_bound;
  // int   heat_or_height;
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
void main()
{
	vs_cam_out.projection = projection;
	vs_cam_out.position   = cam_position;
	vs_cam_out.view       = view;
	// vs_vert_out.heat_or_height = heat_or_height;
    vs_vert_out.max_bound      = max_bound;
	vs_vert_out.min_bound      = min_bound;
	vs_vert_out.uv             = a_texture ;
	vs_vert_out.position       = (model * vec4(a_position, 1.0)).xyz;

    gl_Position      = projection * view * vec4(vs_vert_out.position, 1.0);
}