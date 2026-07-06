// Ink — ink blots blooming and dissolving in water.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/ink

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


    // Ink: blots bloom and dissolve.
    for (int i = 0; i < 2; i++) {
        float fi = float(i);
        float period = 7.0 + fi * 3.0;
        float tick = floor(u.time / period + fi * 0.5);
        float ph = fract(u.time / period + fi * 0.5);
        float2 c = float2((termite_hash(float2(tick, fi + 1.0)) - 0.5) * aspect * 0.8,
                          (termite_hash(float2(tick, fi + 5.0)) - 0.5) * 0.8);
        float rad = sqrt(ph) * 0.5;
        float d = length(sq - c);
        float edge = exp(-abs(d - rad) * 26.0);
        float body = smoothstep(rad, rad * 0.2, d) * 0.5;
        fx += float3(0.10, 0.10, 0.12) * (edge * 0.8 + body * 0.4) * (1.0 - ph);
    }
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
