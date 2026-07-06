// Waterline — the scene reflects in water along the bottom edge.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/waterline

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


    // Waterline: the scene reflects in water along the bottom edge.
    float yl = 0.82;
    if (uv.y > yl) {
        float depth = (uv.y - yl) / (1.0 - yl);
        float wob = sin(pp.x * 0.05 + u.time * 1.1) * 0.004 * depth
                  + sin(pp.x * 0.013 - u.time * 0.7) * 0.006 * depth;
        float3 refl = scene.sample(smp, float2(uv.x + wob, 2.0 * yl - uv.y)).rgb;
        fx = (refl - u.background.rgb) * (1.0 - depth) * 0.35;
        fx += float3(0.01, 0.02, 0.03) * depth;
    }
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
