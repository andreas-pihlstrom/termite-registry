// Dunes — layered dune silhouettes, crest light, sand haze.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/dunes

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


    // Dunes: layered silhouettes with crest light.
    for (int i = 0; i < 3; i++) {
        float fi = float(i);
        float depth = 1.0 - fi * 0.28;
        float ridge = 0.55 + fi * 0.13
                    + sin(sq.x * (1.2 + fi * 0.8) + fi * 7.0 + u.time * (0.02 + fi * 0.01)) * 0.06
                    + sin(sq.x * (2.7 + fi) + fi * 3.0) * 0.025;
        float under = smoothstep(ridge, ridge + 0.01, uv.y);
        fx = mix(fx, float3(0.15, 0.10, 0.05) * (0.4 + 0.6 * depth), under * 0.85);
        fx += float3(0.05, 0.03, 0.01) * exp(-abs(uv.y - ridge) * 90.0) * depth;
    }
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
