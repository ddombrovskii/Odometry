#version 440
out vec4 outColor;
layout(binding = 0)uniform sampler2D diffuse;
layout(binding = 1)uniform sampler2D specular;
layout(binding = 2)uniform sampler2D normals;

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
    vec3  v_diffuse_color;
    vec3  v_specular_color;
    float v_illum;
    float v_dissolve;
    float v_ni;
    float v_ns;
} vs_mat_in;


layout(binding = 0) uniform sampler2D diffTex;
layout(binding = 1) uniform sampler2D specTex;
layout(binding = 2) uniform sampler2D normTex;


float illuminationBlinnPhong(vec3 lightPosition, float shininess)
{
    vec3 lightDir   = normalize(lightPosition      - vs_vert_in.position);
    vec3 viewDir    = normalize(vs_cam_in.position - vs_vert_in.position);
    vec3 halfwayDir = normalize(lightDir + viewDir);
    return pow(max(-dot(vs_vert_in.normal, halfwayDir), 0.0), shininess);
}

void main()
{
   float spec   = illuminationBlinnPhong(vec3(10, 10, 10), 6.75);
   // outColor = vec4(spec, spec, spec,  1.0);
   // float spec = min(max(0.125, dot(-vec3( 0.33333, 0.33333,  0.33333), vs_vert_in.normal)), 1.0);
   // float v  = v_illum   *
   //            v_dissolve*
   //            v_ni      *
   //            v_ns      ;
   //
   outColor = vec4(spec, spec, spec,  1.0) * texture(diffTex, vs_vert_in.uv);
}