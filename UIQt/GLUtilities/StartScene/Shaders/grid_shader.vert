#version 420
layout(location = 0)in vec3 a_position;
layout(location = 2)in vec2 a_texture;

//////////////////////////////
/// MATERIAL PROPERTIES IN ///
//////////////////////////////
uniform float grid_x_step;
uniform float grid_y_step;
uniform float line_size;
uniform float fade;
uniform float grid_alpha;
uniform float fade_radius;
uniform vec3  y_axis_color;
uniform vec3  x_axis_color;
uniform vec3  line_color;

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
   float grid_x_step;
   float grid_y_step;
   float line_size;
   float fade;
   float grid_alpha;
   float fade_radius;
   vec3  y_axis_color;
   vec3  x_axis_color;
   vec3  line_color;
} vs_mat_out;

///////////////////////////////
//// VERTEX PROPERTIES OUT ////
///////////////////////////////
out VS_VERTEX_OUT
{
  vec2  scaling;
  vec2  texture;
  vec4  position;
} vs_vert_out;

void main()
{
	vs_mat_out.grid_x_step  = grid_x_step;
	vs_mat_out.grid_y_step  = grid_y_step;
	vs_mat_out.line_size    = line_size;
	vs_mat_out.fade         = fade;
	vs_mat_out.grid_alpha   = grid_alpha;
	vs_mat_out.fade_radius  = fade_radius;
	vs_mat_out.y_axis_color = y_axis_color;
	vs_mat_out.x_axis_color = x_axis_color;
	vs_mat_out.line_color   = line_color;
    float x_scale = sqrt(model[0][0] * model[0][0] +
                         model[1][0] * model[1][0] +
                         model[2][0] * model[2][0]);
    
    float z_scale = sqrt(model[0][2] * model[0][2] +
                         model[1][2] * model[1][2] +
                         model[2][2] * model[2][2]);
    
    vs_vert_out.scaling  = vec2(x_scale, z_scale);
    vs_vert_out.texture  = vec2(a_position.x * x_scale, a_position.z * z_scale);
	vs_vert_out.position = (model * vec4(a_position, 1.0));
    vs_cam_out.projection = projection;
	vs_cam_out.position   = cam_position;
	vs_cam_out.view       = view;
	gl_Position           = projection * view * vs_vert_out.position;
}