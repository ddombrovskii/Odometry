// Upgrade NOTE: replaced 'mul(UNITY_MATRIX_MVP,*)' with 'UnityObjectToClipPos(*)'

Shader "Universal Render Pipeline/GridShader"
{
    Properties
    {
        _LineColor("Line Color", Color) = (0.5,0.5,0.5,1)
        _XAxisColor("X Color", Color) = (1,0,0,1)
        _YAxisColor("Y Color", Color) = (0,1,0,1)
        [FloatRange]_Fade("Fade", Range(0,1)) = 0
        [FloatRange]_FadeRadius("FadeRadius", Range(0,1)) = 1.0
        [IntRange]  _GridXStep("Grid X Size", Range(1,100)) = 1
        [IntRange]  _GridYStep("Grid Y Size", Range(1,100)) = 1
        [PerRendererData] _MainTex("Albedo (RGB)", 2D) = "white" {}
        _LineSize("Line Size", Range(0,1)) = 0.15
        _OrthoSize("OrthoSize", Float) = 22
        _ScreenAspect("ScreenAspect", Float) = 2
        _GridAlpha("GridAlpha", Float) = 0.7

    }
    SubShader
    {
        Tags {"Queue" = "Transparent" "RenderType" = "Transparent" }
        LOD 100

        ZWrite Off
        Blend SrcAlpha OneMinusSrcAlpha
       
        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_fog

            #include "UnityCG.cginc"

            struct VertexInData
            {
                float4 vertex : POSITION;
            };

            struct VertexOutData
            {
                float2 uv : TEXCOORD0;
                float2 scaling : TEXCOORD1;
                float4 vertex : SV_POSITION;
            };

            sampler2D _MainTex;

            float _GridXStep;
            float _GridYStep;
            float _LineSize;
            float _Fade;
            float _GridAlpha;
            float _FadeRadius;
            float4 _YAxisColor;
            float4 _XAxisColor;
            float4 _LineColor;
            float _OrthoSize;
            float _ScreenAspect;


            VertexOutData vert (VertexInData v)
            {
                VertexOutData o;
                
                o.vertex = UnityObjectToClipPos(v.vertex);
                
                float x_scale = sqrt(UNITY_MATRIX_M[0][0] * UNITY_MATRIX_M[0][0] + 
                                     UNITY_MATRIX_M[1][0] * UNITY_MATRIX_M[1][0] +
                                     UNITY_MATRIX_M[2][0] * UNITY_MATRIX_M[2][0]);
                
                float y_scale = sqrt(UNITY_MATRIX_M[0][2] * UNITY_MATRIX_M[0][2] +
                                     UNITY_MATRIX_M[1][2] * UNITY_MATRIX_M[1][2] +
                                     UNITY_MATRIX_M[2][2] * UNITY_MATRIX_M[2][2]);
                
                o.scaling = float2(x_scale, y_scale);

                o.uv = float2(v.vertex.x * x_scale, v.vertex.z * y_scale);
                
                return o;
            }

            fixed4 frag(VertexOutData i) : SV_Target
            {
                float fade_distance = length(i.uv.xy / i.scaling);
                
                float alpha = _GridAlpha;

                float fade_bound = (_FadeRadius) * 0.5 - _Fade;

                if (fade_distance >= fade_bound)
                {   
                    fade_distance -= fade_bound;
                    alpha *=  (smoothstep(_Fade, 0.0, fade_distance));
                }

                float lineSize = _LineSize;

                if (unity_OrthoParams.w == 1.0)
                {
                    lineSize *= (unity_OrthoParams.y / _OrthoSize);
                }

                if (abs(i.uv.x) <= lineSize * 0.5)
                {
                    return fixed4(_XAxisColor.x, _XAxisColor.y, _XAxisColor.z, alpha);
                }

                if (abs(i.uv.y) <= lineSize * 0.5)
                {
                    return fixed4(_YAxisColor.x, _YAxisColor.y, _YAxisColor.z, alpha);
                }

                float dy = i.scaling.y / (_GridYStep * 2);

                if (abs(round(i.uv.y / dy) * dy - i.uv.y) <= lineSize * 0.5)
                {
                    return fixed4(_LineColor.x, _LineColor.y, _LineColor.z, alpha);
                }

                float dx = i.scaling.x / (_GridXStep * 2);

                if (abs(round(i.uv.x / dx) * dx - i.uv.x) <= lineSize * 0.5)
                {
                    return fixed4(_LineColor.x, _LineColor.y, _LineColor.z, alpha);
                }

                return fixed4(0.0, 0.0, 0.0, 0.0);
            }
            ENDCG
        }
    }
}
