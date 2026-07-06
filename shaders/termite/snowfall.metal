// Snowfall — three parallax layers of unhurried flakes.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/snowfall

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


    // Snowfall: three parallax layers of unhurried flakes.
    for (int layer = 0; layer < 3; layer++) {
        float fl = float(layer);
        float scale = 14.0 + fl * 10.0;
        float2 g = float2(uv.x * aspect + sin(uv.y * 2.0 + u.time * 0.2 + fl) * 0.01,
                          uv.y - u.time * (0.030 - fl * 0.008)) * scale;
        float2 cell = floor(g), f = fract(g);
        float h = termite_hash(cell + fl * 91.0);
        if (h > 0.80) {
            float2 c = float2(termite_hash(cell + 1.3), termite_hash(cell + 7.7)) * 0.5 + 0.25;
            c.x += sin(u.time * (0.4 + h) + h * 20.0) * 0.08;
            float d = length(f - c);
            fx += float3(0.15, 0.16, 0.18) * exp(-d * 20.0) * (1.0 - fl * 0.25);
        }
    }
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
