// Lanterns — five paper lanterns climbing on staggered loops.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/lanterns

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


    // Lanterns: five paper lanterns climbing on staggered loops.
    for (int i = 0; i < 5; i++) {
        float fi = float(i);
        float seed = fi * 13.7;
        float y = fract(termite_hash(float2(fi, 5.0)) - u.time * (0.014 + termite_hash(float2(fi, 2.0)) * 0.012));
        float x = (termite_hash(float2(fi, 9.0)) - 0.5) * aspect * 0.9 + sin(u.time * 0.2 + seed) * 0.03;
        float2 d = sq - float2(x, y - 0.5);
        float glow = exp(-dot(d, d) * 90.0);
        float warm = 0.55 + 0.45 * sin(u.time * 0.8 + seed);
        fx += float3(0.28, 0.15, 0.05) * glow * (0.45 + 0.30 * warm);
    }
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
