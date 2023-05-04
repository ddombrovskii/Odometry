#version 420
out vec4 outColor;

///////////////////////////////
//// CAMERA PROPERTIES OUT ////
///////////////////////////////
in VS_CAMERA_OUT
{
    vec3  position;
    mat4  projection;
    mat4  view;
} vs_cam_in;

///////////////////////////////
/// MATERIAL PROPERTIES OUT ///
///////////////////////////////
in VS_MATERIAL_OUT
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
} vs_mat_in;

///////////////////////////////
//// VERTEX PROPERTIES OUT ////
///////////////////////////////
in VS_VERTEX_OUT
{
  vec2  scaling;
  vec2  texture;
  vec4  position;
} vs_vert_in;


void main()
{
	float fade_distance = length(vs_vert_in.texture.xy / vs_vert_in.scaling);
    
    float alpha = 1.0; //vs_mat_in.grid_alpha;

    float fade_bound = (vs_mat_in.fade_radius) * 0.5 - vs_mat_in.fade;

    if (fade_distance >= fade_bound)
    {   
        fade_distance -= fade_bound;
        alpha *=  (smoothstep(vs_mat_in.fade, 0.0, fade_distance));
    }

    float lineSize = vs_mat_in.line_size;

    // if (unity_OrthoParams.w == 1.0)
    // {
    //     lineSize *= (unity_OrthoParams.y / v_OrthoSize);
    // }

    if (abs(vs_vert_in.texture.x) <= lineSize * 0.5)
    {
        outColor = vec4(vs_mat_in.x_axis_color, alpha);
        return;
    }

    if (abs(vs_vert_in.texture.y) <= lineSize * 0.5)
    {
        outColor = vec4(vs_mat_in.y_axis_color, alpha);
        return;
    }

    float dy = vs_vert_in.scaling.y / (vs_mat_in.grid_y_step * 2);

    if (abs(round(vs_vert_in.texture.y / dy) * dy - vs_vert_in.texture.y) <= lineSize * 0.5)
    {
        outColor = vec4(vs_mat_in.line_color, alpha);
        return;
    }

    float dx = vs_vert_in.scaling.x / (vs_mat_in.grid_x_step * 2);

    if (abs(round(vs_vert_in.texture.x / dx) * dx - vs_vert_in.texture.x) <= lineSize * 0.5)
    {
        outColor = vec4(vs_mat_in.line_color, alpha);
        return;
   }

    outColor = vec4(0.0, 0.0, 0.0, 0.0);
}