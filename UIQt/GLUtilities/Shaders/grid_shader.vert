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
   vec2  scaling;
   vec2  texture;
   vec4  position;
} vs_mat_out;


void main()
{
	vs_mat_out.GridXStep    = grid_x_step;
	vs_mat_out.GridYStep    = grid_y_step;
	vs_mat_out.LineSize     = line_size;
	vs_mat_out.Fade         = fade;
	vs_mat_out.GridAlpha    = grid_alpha;
	vs_mat_out.FadeRadius   = fade_radius;
	vs_mat_out.YAxisColor   = y_axis_color;
	vs_mat_out.XAxisColor   = x_axis_color;
	vs_mat_out.LineColor    = line_color;

    float x_scale = sqrt(model[0][0] * model[0][0] + 
                         model[1][0] * model[1][0] +
                         model[2][0] * model[2][0]);
    
    float z_scale = sqrt(model[0][2] * model[0][2] +
                         model[1][2] * model[1][2] +
                         model[2][2] * model[2][2]);
    
    vs_mat_out.v_scaling = float2(x_scale, z_scale);

    vs_mat_out.v_texture = float2(a_position.x * x_scale, a_position.z * z_scale);
	
	vs_mat_out.v_position       = model * vec4(a_position, 1.0);
    
	gl_Position      = projection * view * vs_mat_out.v_position;
}