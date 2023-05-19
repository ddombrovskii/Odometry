#version 440
// out vec4 outColor;
layout(location = 0) out vec4 outColor;

layout(binding = 0) uniform sampler2D diffTex;
layout(binding = 1) uniform sampler2D specTex;
layout(binding = 2) uniform sampler2D normTex;

///////////////////////////////
//// VERTEX PROPERTIES OUT ////
///////////////////////////////
in VS_VERTEX_OUT
{
  vec2  uv;
  vec3  normal;
  vec3  position;
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



///////////////////////////////
/// MATERIAL PROPERTIES OUT ///
///////////////////////////////
in VS_MATERIAL_OUT
{
    vec3  diffuse_color;
    vec3  specular_color;
    float illum;
    float dissolve;
    float ni;
    float ns;
} vs_mat_in;


float illuminationBlinnPhong(vec3 lightPosition, float shininess)
{
    vec3 lightDir   = normalize(lightPosition      - vs_vert_in.position);
    vec3 viewDir    = normalize(vs_cam_in.position - vs_vert_in.position);
    vec3 halfwayDir = normalize(lightDir + viewDir);
    return pow(max(-dot(vs_vert_in.normal, halfwayDir), 0.0), shininess);
}

void main()
{
   float spec   = illuminationBlinnPhong(vec3(10, 10, 10), 6.75) +
                  max(dot(vs_vert_in.normal, vec3(-0.333, -0.333, -0.333)), 0.1);
   outColor = vec4(vs_mat_in.diffuse_color.xyz * spec ,  1.0) * texture(diffTex, vs_vert_in.uv);
}