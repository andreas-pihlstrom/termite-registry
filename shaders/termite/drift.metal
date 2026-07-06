// Drift — a dual-tone color field slowly folding over itself.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/drift

// Value noise + 3-octave fbm (the built-in helpers cover hash/palette/mask;
// organic fields bring their own noise).
static float termite_vnoise(float2 p) {
    float2 i = floor(p), f = fract(p);
    float2 s = f * f * (3.0 - 2.0 * f);
    float a = termite_hash(i);
    float b = termite_hash(i + float2(1.0, 0.0));
    float c = termite_hash(i + float2(0.0, 1.0));
    float d = termite_hash(i + float2(1.0, 1.0));
    return mix(mix(a, b, s.x), mix(c, d, s.x), s.y);
}
static float termite_fbm(float2 p) {
    float v = 0.0, amp = 0.5;
    for (int i = 0; i < 3; i++) {
        v += termite_vnoise(p) * amp;
        p = p * 2.03 + 17.31;
        amp *= 0.5;
    }
    return v;
}

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


    // Drift: two color fields folding over each other, barely moving.
    float n = termite_fbm(sq * 1.3 + float2(u.time * 0.020, -u.time * 0.012));
    float m = termite_fbm(sq * 1.3 - float2(u.time * 0.016, u.time * 0.010) + 5.2);
    fx = float3(0.05, 0.07, 0.14) * n + float3(0.10, 0.05, 0.12) * m;
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
