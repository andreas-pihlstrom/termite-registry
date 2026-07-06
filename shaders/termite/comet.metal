// Comet — every ~17s one soft comet crosses the upper sky.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/comet

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


    // Comet: one soft visitor crosses the upper sky every ~17s.
    float ph = fract(u.time / 17.0);
    if (ph < 0.28) {
        float tick = floor(u.time / 17.0);
        float tp = ph / 0.28;
        float2 a = float2(-0.62 * aspect, -0.42 + termite_hash(float2(tick, 1.0)) * 0.5);
        float2 b = float2( 0.62 * aspect, -0.30 + termite_hash(float2(tick, 2.0)) * 0.4);
        float2 head = mix(a, b, tp);
        float2 dirv = (b - a) / max(length(b - a), 0.001);
        float2 rel = sq - head;
        float along = dot(rel, dirv);
        float side = dot(rel, float2(-dirv.y, dirv.x));
        float tail = exp(along * 7.0) * step(along, 0.0) * exp(-side * side * 400.0);
        float headGlow = exp(-dot(rel, rel) * 700.0);
        float fade = sin(tp * 3.14159);
        fx += (float3(0.32, 0.35, 0.42) * headGlow + float3(0.11, 0.13, 0.19) * tail) * fade;
    }
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
