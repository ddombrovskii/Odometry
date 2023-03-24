#version 420
out vec4 outColor;

in float  v_GridXStep;
in float  v_GridYStep;
in float  v_LineSize;
in float  v_Fade;
in float  v_GridAlpha;
in float  v_FadeRadius;
in float4 v_YAxisColor;
in float4 v_XAxisColor;
in float4 v_LineColor;
in float  v_OrthoSize;
in float  v_ScreenAspect;

in vec2  v_scaling;
in vec2  v_texture;
in vec4  v_position;


void main()
{
	float fade_distance = length(v_texture.xy / v_scaling);
    
    float alpha = v_GridAlpha;

    float fade_bound = (v_FadeRadius) * 0.5 - v_Fade;

    if (fade_distance >= fade_bound)
    {   
        fade_distance -= fade_bound;
        alpha *=  (smoothstep(v_Fade, 0.0, fade_distance));
    }

    float lineSize = _LineSize;

    // if (unity_OrthoParams.w == 1.0)
    // {
    //     lineSize *= (unity_OrthoParams.y / v_OrthoSize);
    // }

    if (abs(v_texture.x) <= lineSize * 0.5)
    {
        return vec4(v_XAxisColor.x, v_XAxisColor.y, v_XAxisColor.z, alpha);
    }

    if (abs(v_texture.y) <= lineSize * 0.5)
    {
        return vec4(v_YAxisColor.x, v_YAxisColor.y, v_YAxisColor.z, alpha);
    }

    float dy = v_scaling.y / (v_GridYStep * 2);

    if (abs(round(v_texture.y / dy) * dy - v_texture.y) <= lineSize * 0.5)
    {
        return vec4(v_LineColor.x, v_LineColor.y, v_LineColor.z, alpha);
    }

    float dx = v_scaling.x / (v_GridXStep * 2);

    if (abs(round(v_texture.x / dx) * dx - v_texture.x) <= lineSize * 0.5)
    {
        return vec4(v_LineColor.x, v_LineColor.y, v_LineColor.z, alpha);
    }

    return vec4(0.0, 0.0, 0.0, 0.0);
}