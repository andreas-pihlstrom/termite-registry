// Ember — sparse warm motes rising and winking out.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/ember

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


    // Ember: sparse warm motes rising, winking.
    for (int layer = 0; layer < 2; layer++) {
        float fl = float(layer);
        float scale = 26.0 - fl * 9.0;
        float2 g = float2(uv.x * aspect, uv.y + u.time * (0.020 + fl * 0.012)) * scale;
        float2 cell = floor(g), f = fract(g);
        float h = termite_hash(cell + fl * 51.0);
        if (h > 0.93) {
            float2 c = float2(termite_hash(cell + 1.7), termite_hash(cell + 3.1)) * 0.6 + 0.2;
            float d = length(f - c);
            float tw = 0.6 + 0.4 * sin(u.time * (1.0 + h * 3.0) + h * 40.0);
            fx += float3(0.30, 0.12, 0.03) * exp(-d * 14.0) * tw * (0.5 + fl * 0.5);
        }
    }
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
