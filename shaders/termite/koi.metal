// Koi — three blurred koi gliding under frosted ice.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/koi

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


    // Koi: three blurred bodies gliding under frosted ice.
    for (int i = 0; i < 3; i++) {
        float fi = float(i);
        float2 path = float2(sin(u.time * 0.09 + fi * 2.4) * 0.32 * aspect,
                             sin(u.time * 0.13 + fi * 4.1 + 1.2) * 0.30);
        float2 vel = float2(cos(u.time * 0.09 + fi * 2.4) * 0.09,
                            cos(u.time * 0.13 + fi * 4.1 + 1.2) * 0.13);
        float2 dirv = vel / max(length(vel), 0.001);
        float2 rel = sq - path;
        float2 lo = float2(dot(rel, dirv), dot(rel, float2(-dirv.y, dirv.x))) * float2(3.2, 9.0);
        float body = exp(-dot(lo, lo) * 4.0);
        fx += mix(float3(0.28, 0.14, 0.05), float3(0.22, 0.20, 0.18), fract(fi * 0.618)) * body * 0.8;
    }
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
