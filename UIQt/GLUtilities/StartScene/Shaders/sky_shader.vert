#version 440
//////////////////////////////
//// VERTEX PROPERTIES IN ////
//////////////////////////////
layout(location = 0)in vec3 a_position;
layout(location = 2)in vec2 a_texture;

uniform vec3  sky_color;
uniform vec3  deep_sky_color;
uniform vec3  ground_color;
uniform vec3  sun_color;
uniform vec3  sun_position;
uniform float sun_size;
uniform float ground_threshold;
uniform float sun_threshold;
uniform float deep_sky_threshold;

//////////////////////////////
//// CAMERA PROPERTIES IN ////
//////////////////////////////
uniform mat4  view;
uniform mat4  projection;
uniform vec3  cam_position;
uniform mat4  model;

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
   vec3  sky_color;
   vec3  deep_sky_color;
   vec3  ground_color;
   vec3  sun_color;
   vec3  sun_position;
   float sun_size;
   float ground_threshold;
   float sun_threshold;
   float deep_sky_threshold;
} vs_mat_out;

///////////////////////////////
//// VERTEX PROPERTIES OUT ////
///////////////////////////////
out VS_VERTEX_OUT
{
  vec2  texture;
  vec4  position;
} vs_vert_out;

void main()
{
	vs_mat_out.sky_color          = sky_color;
	vs_mat_out.deep_sky_color     = deep_sky_color;
	vs_mat_out.ground_color       = ground_color;
	vs_mat_out.sun_color          = sun_color;
	vs_mat_out.sun_position       = normalize(sun_position);
	vs_mat_out.sun_size           = sun_size;
	vs_mat_out.ground_threshold   = ground_threshold;
	vs_mat_out.sun_threshold      = sun_threshold;
	vs_mat_out.deep_sky_threshold = deep_sky_threshold;

    vs_vert_out.texture   = a_texture ;
	vs_vert_out.position  = (model * vec4(a_position, 1.0));

    vs_cam_out.projection = projection;
	vs_cam_out.position   = cam_position;
	vs_cam_out.view       = view;

    gl_Position      = projection * view * vs_vert_out.position;
}