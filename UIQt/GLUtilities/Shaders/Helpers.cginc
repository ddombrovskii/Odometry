// Upgrade NOTE: replaced 'mul(UNITY_MATRIX_MVP,*)' with 'UnityObjectToClipPos(*)'


uniform  float4x4 local_transform;

struct vertexIN
{
    float4 vertex : POSITION;
    float4 color : COLOR;
#if defined(UNITY_PROCEDURAL_INSTANCING_ENABLED)
    UNITY_VERTEX_INPUT_INSTANCE_ID
#endif
};

struct fragmentIN
{
    float4 vertex : SV_POSITION;
    float4 vertexWS : NORMAL;
    float2 uv: TEXCOORD0;
    float4 color : COLOR;
};

struct PointProperties
{
    float3 Origin;
    float3 Color;
    float2 SizeXZ;
};

struct SectionProperties
{
    float3 P1;
    float3 P2;
    float3 Color;
    float2 SizeXZ;
};

struct ColorWidthProperties
{
    float3 Color;
    float  Width;
};

float Signum(float v)
{
    if (v < 0)
    {
        return -1.0f;
    }
    return 1.0f;
}

float3 PerpVector(float dx, float dz)
{
    if (dx == 0)
    {
        return float3(Signum(dz), 0, 0);
    }

    if (dz == 0)
    {
        return float3(0, 0, -Signum(dx));
    }

    float3 perp = Signum(dx / dz) * float3(1.0f / dx, 0, -1.0f / dz);

    perp = normalize(perp);

    return perp;
}

void ConfigurePointProcedural(PointProperties pointProp)
{
    unity_ObjectToWorld = float4x4(pointProp.SizeXZ.x, 0, 0,                  pointProp.Origin.x,
                                        0,             1, 0,                  pointProp.Origin.y,
                                        0,             0, pointProp.SizeXZ.y, pointProp.Origin.z,
                                        0,             0, 0, 1);

}
void ConfigureSectionProcedural(SectionProperties sectProp)
{
    float3 ez = (sectProp.P2 - sectProp.P1);

    float3 orig = (sectProp.P2 + sectProp.P1) / 2;

    float3 ex = PerpVector(ez.x, ez.z);

    unity_ObjectToWorld = float4x4(
        ex.x * sectProp.SizeXZ.x, 0, ez.x, orig.x,
        ex.y * sectProp.SizeXZ.x, 1, ez.y, orig.y - 0.01f,
        ex.z * sectProp.SizeXZ.x, 0, ez.z, orig.z,
        0, 0, 0, 1);
}

///id Unity instance id
///origin_ circle center origin
/// a0 - arc start angle
/// da - arc angle step
/// r  - arc radius
/// tick - wich part of section will be drawn
/// line width - line width
void ConfigureCircArcProcedural(int id, float3 origin_, float a0, float da, float r, float ticks, float lineWidth)
{
    float angle = a0 + da * id;
    float sectionLength = ticks * 2 * r * sin(da / 2);
    float3 origin = float3(origin_.x + r * cos(angle), origin_.y, origin_.z + r * sin(angle));
    unity_ObjectToWorld = float4x4(
                                    cos(angle) * lineWidth, 0, -sin(angle) * sectionLength, origin.x,
                                    0,                      0, 0,                           origin.y,
                                    sin(angle) * lineWidth, 0, cos(angle) * sectionLength,  origin.z,
                                    0,                      0, 0,                           1);
}

fragmentIN VertexOrthXScaleShader(vertexIN v, float4 color, float OrthoSize)
{
    fragmentIN o;
  
    o.color = color;

    if (unity_OrthoParams.w == 1.0)
    {
        
        o.vertexWS = mul(UNITY_MATRIX_M, float4(unity_OrthoParams.y / OrthoSize, 1, 1, 1) * v.vertex);
        
        o.vertex = o.vertexWS;

        o.vertex = mul(UNITY_MATRIX_VP, o.vertex);
        
        return o;
    }

    o.vertexWS = mul(UNITY_MATRIX_M, v.vertex);

    o.vertex = o.vertexWS;

    o.vertex = mul(UNITY_MATRIX_VP, o.vertex);

    return o;
}

fragmentIN VertexOrthXZScaleShader(vertexIN v, float4 color, float OrthoSize)
{
    fragmentIN o;

    o.color = color;

    if (unity_OrthoParams.w == 1.0)
    {
        float orthoScale = unity_OrthoParams.y / OrthoSize;
        o.vertex = UnityObjectToClipPos(float4(orthoScale, 1, orthoScale, 1) * v.vertex);
        o.uv = (v.vertex.xz + float2(0.5, 0.5));
        return o;
    }
    o.vertex = UnityObjectToClipPos(v.vertex);
    o.uv = (v.vertex.xz + float2(0.5, 0.5)) ;
    return o;
}

fragmentIN VertexDefaultShader(vertexIN v) 
{
    fragmentIN o;
    o.vertex = UnityObjectToClipPos(v.vertex);
    o.color = v.color;
    return o;
}