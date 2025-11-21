Shader "Sanctuary/BioluminescentJellyfish"
{
    Properties
    {
        _MainTex ("Albedo (RGB)", 2D) = "white" {}
        _BumpMap ("Normal Map", 2D) = "bump" {}

        _Color ("Base Color", Color) = (0.1, 0.3, 0.5, 0.8)
        _Transparency ("Transparency", Range(0, 1)) = 0.7

        _EmissionColor ("Emission Color", Color) = (0, 1, 1, 1)
        _GlowIntensity ("Glow Intensity", Range(0, 5)) = 1.0
        _GlowPulseSpeed ("Pulse Speed", Range(0, 5)) = 1.0
        _GlowPulseAmplitude ("Pulse Amplitude", Range(0, 1)) = 0.3

        _FresnelPower ("Fresnel Power", Range(0, 10)) = 3.0
        _FresnelIntensity ("Fresnel Intensity", Range(0, 5)) = 1.5

        _RimColor ("Rim Color", Color) = (0, 0.8, 1, 1)
        _RimPower ("Rim Power", Range(0, 10)) = 4.0

        _WaveSpeed ("Wave Speed", Range(0, 5)) = 1.0
        _WaveAmplitude ("Wave Amplitude", Range(0, 0.5)) = 0.1
        _WaveFrequency ("Wave Frequency", Range(0, 20)) = 5.0
    }

    SubShader
    {
        Tags {
            "Queue"="Transparent"
            "RenderType"="Transparent"
            "IgnoreProjector"="True"
        }
        LOD 300

        CGPROGRAM
        #pragma surface surf Standard alpha:fade vertex:vert
        #pragma target 3.0

        sampler2D _MainTex;
        sampler2D _BumpMap;

        fixed4 _Color;
        half _Transparency;

        fixed4 _EmissionColor;
        half _GlowIntensity;
        half _GlowPulseSpeed;
        half _GlowPulseAmplitude;

        half _FresnelPower;
        half _FresnelIntensity;

        fixed4 _RimColor;
        half _RimPower;

        half _WaveSpeed;
        half _WaveAmplitude;
        half _WaveFrequency;

        struct Input
        {
            float2 uv_MainTex;
            float2 uv_BumpMap;
            float3 viewDir;
            float3 worldPos;
            float3 worldNormal;
            INTERNAL_DATA
        };

        void vert (inout appdata_full v)
        {
            // Animated wave deformation
            float wave = sin(_Time.y * _WaveSpeed + v.vertex.y * _WaveFrequency) * _WaveAmplitude;
            v.vertex.xyz += v.normal * wave;
        }

        void surf (Input IN, inout SurfaceOutputStandard o)
        {
            // Base color and transparency
            fixed4 c = tex2D(_MainTex, IN.uv_MainTex) * _Color;
            o.Albedo = c.rgb;
            o.Alpha = c.a * _Transparency;

            // Normal mapping
            o.Normal = UnpackNormal(tex2D(_BumpMap, IN.uv_BumpMap));

            // Fresnel effect (edge glow)
            half fresnel = 1.0 - saturate(dot(normalize(IN.viewDir), o.Normal));
            fresnel = pow(fresnel, _FresnelPower) * _FresnelIntensity;

            // Rim lighting
            half rim = 1.0 - saturate(dot(normalize(IN.viewDir), WorldNormalVector(IN, o.Normal)));
            rim = pow(rim, _RimPower);

            // Pulsing glow (heartbeat effect)
            half pulse = sin(_Time.y * _GlowPulseSpeed) * _GlowPulseAmplitude + 1.0;

            // Vertical gradient glow (brighter at top)
            half verticalGradient = saturate(IN.worldPos.y * 0.5 + 0.5);

            // Combine emission effects
            fixed3 emission = _EmissionColor.rgb * _GlowIntensity * pulse;
            emission += fresnel * _EmissionColor.rgb * _FresnelIntensity;
            emission += rim * _RimColor.rgb;
            emission *= verticalGradient;

            o.Emission = emission;

            // Slight metallic/smoothness for wet look
            o.Metallic = 0.2;
            o.Smoothness = 0.8;
        }
        ENDCG
    }

    FallBack "Standard"
}
