#version 440
// out vec4 outColor;
layout(location = 0) out vec4 outColor;

///////////////////////////////
//// VERTEX PROPERTIES OUT ////
///////////////////////////////
in  VS_VERTEX_OUT
{
  vec2  uv;
  vec3  position;
  vec3  max_bound;
  vec3  min_bound;
  // int   heat_or_height;
} vs_vert_in;

///////////////////////////////
//// CAMERA PROPERTIES OUT ////
///////////////////////////////
in VS_CAMERA_OUT
{
    vec3  position;
    mat4  projection;
    mat4  view;
} vs_cam_in;

float height_map(float v, float vmin, float vmax)
{
	return 1 - min(max(( 2 *  v - vmin)/(vmax - vmin), 0.0), 1.0);
}

vec3 heat_map(float v, float vmin, float vmax)
{
   vec3 c = vec3(1.0, 1.0, 1.0); // white
	
   v = height_map(v, vmin, vmax);

   if (v < 0.25)
	   {
      c.x = 0.0;
      c.y = 4.0 * v;
   }
   else if (v < 0.5)
   {
      c.x = 0.0;
      c.z = 1.0 + 4.0 * (0.25 - v);
   } 
   else if (v < 0.75)
   {
      c.x = 4.0 * (v - 0.5);
      c.z = 0.0;
   } 
   else
   {
      c.y = 1.0 + 4.0 * (0.75 - v);
      c.z = 0.0;
   }

   return c;
}/**/


void main()
{
	float spec = height_map(vs_vert_in.position.y, vs_vert_in.min_bound.y, vs_vert_in.max_bound.y);
	outColor = vec4(spec, spec, spec,  1.0);
}