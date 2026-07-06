// Petals — pink petals drifting down-wind with a sway.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/petals

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


    // Petals: pink flecks drifting down-wind with a sway.
    float2 g = float2(uv.x * aspect - u.time * 0.008, uv.y - u.time * 0.020) * 9.0;
    float2 cell = floor(g), f = fract(g);
    float h = termite_hash(cell);
    if (h > 0.78) {
        float2 c = float2(termite_hash(cell + 2.2), termite_hash(cell + 6.4)) * 0.5 + 0.25;
        c += float2(sin(u.time * 0.6 + h * 50.0), cos(u.time * 0.45 + h * 30.0)) * 0.06;
        float2 d = (f - c) * float2(1.0, 1.6);
        fx += float3(0.20, 0.09, 0.11) * exp(-dot(d, d) * 60.0);
    }
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
