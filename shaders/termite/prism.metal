// Prism — one faint light shaft, spectrum-fringed, slowly swinging.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/prism

float4 termite_main(float2 uv, float4 sceneColor,
                    constant TermiteUniforms &u,
                    texture2d<float> scene, sampler smp) {
    float3 rgb = sceneColor.rgb;
    float aspect = u.resolution.x / u.resolution.y;
    float2 sq = (uv - 0.5) * float2(aspect, 1.0);
    float2 pp = uv * u.resolution;
    float mask = termite_textMask(rgb, u.background.rgb);
    float3 fx = float3(0.0);
    (void)pp;


    // Prism: one faint shaft, spectrum-fringed, slowly swinging.
    float ang = 0.7 + sin(u.time * 0.03) * 0.15;
    float2 dirv = float2(cos(ang), sin(ang));
    float side = dot(sq - float2(-0.5 * aspect, -0.5), float2(-dirv.y, dirv.x));
    float beam = exp(-side * side * 60.0);
    float3 spectrum = termite_palette(clamp(side * 2.0 + 0.5, 0.0, 1.0) * 0.8);
    fx = (float3(0.09, 0.09, 0.10) + spectrum * 0.09) * beam;
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
