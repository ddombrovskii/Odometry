#version 440
layout(location = 0) out vec4 outColor;
///////////////////////////////
/// MATERIAL PROPERTIES OUT ///
///////////////////////////////
in VS_MATERIAL_OUT
{
	vec3  color;
	float alpha;
} vs_mat_in;


void main()
{
   outColor = vec4(vs_mat_in.color,  vs_mat_in.alpha);
}