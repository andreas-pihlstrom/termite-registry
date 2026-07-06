// Meadow — green ground glow + pollen adrift.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/meadow

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


    // Meadow: ground glow and pollen adrift.
    fx = float3(0.03, 0.09, 0.03) * smoothstep(0.55, 1.05, uv.y);
    float2 g = float2(uv.x * aspect + sin(u.time * 0.05) * 0.02, uv.y + u.time * 0.006) * 12.0;
    float2 cell = floor(g), f = fract(g);
    float h = termite_hash(cell + 40.0);
    if (h > 0.86) {
        float2 c = 0.3 + 0.4 * float2(termite_hash(cell + 3.0), termite_hash(cell + 9.0));
        c += float2(sin(u.time * 0.5 + h * 60.0), cos(u.time * 0.4 + h * 80.0)) * 0.08;
        fx += float3(0.15, 0.14, 0.07) * exp(-length(f - c) * 26.0);
    }
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
