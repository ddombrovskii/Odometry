#version 440
// out vec4 outColor;
layout(location = 0) out vec4 outColor;

///////////////////////////////
//// CAMERA PROPERTIES IN  ////
///////////////////////////////
in VS_CAMERA_OUT
{
    vec3  position;
    mat4  projection;
    mat4  view;
} vs_cam_in;

///////////////////////////////
/// MATERIAL PROPERTIES IN  ///
///////////////////////////////
in VS_MATERIAL_OUT
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
} vs_mat_in;

///////////////////////////////
//// VERTEX PROPERTIES IN  ////
///////////////////////////////
in VS_VERTEX_OUT
{
  vec2  texture;
  vec4  position;
} vs_vert_in;


void main()
{
	vec3 direction = normalize(vs_vert_in.position.xyz);
	float factor = smoothstep(-0.0125, 0.0125, direction.y);
	vec3 color = vs_mat_in.sky_color * (1 - factor) + vs_mat_in.ground_color * factor;
	factor = smoothstep(0.333, 0.9, -direction.y);
	color = vs_mat_in.deep_sky_color * factor  + color * (1 - factor);
	factor = dot(direction, -vs_mat_in.sun_position);
	factor = factor > 0 ? factor: 0.0;
	factor = pow(smoothstep(0.96, 1.0, factor), 8);
	color = color * (1 - factor) + factor * vs_mat_in.sun_color;
	
	outColor = vec4(color, 1);
	//vec3 viewDir = normalize(vs_vert_in.position);
	//float ground_factor = viewDir.y;
	
   // float spec   = illuminationBlinnPhong(vec3(10, 10, 10), 6.75) +
   //                max(dot(vs_vert_in.normal, vec3(-0.333, -0.333, -0.333)), 0.1);
   // outColor = vec4(vs_mat_in.diffuse_color.xyz * spec ,  1.0) * texture(diffTex, vs_vert_in.uv);
}