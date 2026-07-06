// Rainfall — rain trails sliding down window glass.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/rainfall

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


    // Rainfall: trails sliding down window glass.
    float2 g = float2(uv.x * aspect * 22.0, uv.y);
    float colId = floor(g.x);
    float h = termite_hash(float2(colId, 5.0));
    if (h > 0.45) {
        float phase = fract(u.time * (0.035 + h * 0.05) + h * 9.0 - uv.y * (0.8 + h * 0.4));
        float streak = exp(-phase * 9.0);
        float lat = exp(-abs(fract(g.x) - 0.5) * 7.0);
        fx += float3(0.09, 0.11, 0.14) * streak * lat * 0.8;
    }
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
