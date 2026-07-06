// Lagoon — teal caustic light webs, pool-floor slow.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/lagoon

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


    // Lagoon: caustic light webs on a pool floor.
    float2 p = sq * 5.0;
    float t = u.time * 0.35;
    float ca = sin(p.x + sin(p.y + t)) * sin(p.y + sin(p.x - t * 0.8));
    float web = pow(clamp(1.0 - abs(ca), 0.0, 1.0), 6.0);
    fx = float3(0.05, 0.20, 0.22) * web * (0.6 + 0.4 * sin(t + p.x * 0.3));
    fx += float3(0.0, 0.03, 0.04) * (1.0 - uv.y) * 0.6;
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
