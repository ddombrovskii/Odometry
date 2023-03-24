#version 420
layout(location = 0)in vec3 a_position;
layout(location = 2)in vec2 a_texture;

uniform float  GridXStep;
uniform float  GridYStep;
uniform float  LineSize;
uniform float  Fade;
uniform float  GridAlpha;
uniform float  FadeRadius;
uniform float4 YAxisColor;
uniform float4 XAxisColor;
uniform float4 LineColor;
uniform float  OrthoSize;
uniform float  ScreenAspect;

uniform mat4  model;
uniform mat4  view;
uniform mat4  projection;

out float  v_GridXStep;
out float  v_GridYStep;
out float  v_LineSize;
out float  v_Fade;
out float  v_GridAlpha;
out float  v_FadeRadius;
out float4 v_YAxisColor;
out float4 v_XAxisColor;
out float4 v_LineColor;
out float  v_OrthoSize;
out float  v_ScreenAspect;

out vec2  v_scaling;
out vec2  v_texture;
out vec4  v_position;


void main()
{
	v_GridXStep    = GridXStep;
	v_GridYStep    = GridYStep;
	v_LineSize     = LineSize;
	v_Fade         = Fade;
	v_GridAlpha    = GridAlpha;
	v_FadeRadius   = FadeRadius;
	v_YAxisColor   = YAxisColor;
	v_XAxisColor   = XAxisColor;
	v_LineColor    = LineColor;
	v_OrthoSize    = OrthoSize;
	v_ScreenAspect = ScreenAspect;
	
    float x_scale = sqrt(model[0][0] * model[0][0] + 
                         model[1][0] * model[1][0] +
                         model[2][0] * model[2][0]);
    
    float z_scale = sqrt(model[0][2] * model[0][2] +
                         model[1][2] * model[1][2] +
                         model[2][2] * model[2][2]);
    
    v_scaling = float2(x_scale, z_scale);

    v_texture = float2(v.vertex.x * x_scale, v.vertex.z * z_scale);
	
	v_position       = model * vec4(a_position, 1.0);
    
	gl_Position      = projection * view * v_position;
}