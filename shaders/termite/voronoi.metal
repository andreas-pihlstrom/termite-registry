// Voronoi — drifting cells, edges barely glowing.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/voronoi

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


    // Voronoi: drifting cells, edges barely glowing.
    float2 g = sq * 4.0 + float2(u.time * 0.015, 0.0);
    float2 cell = floor(g), f = fract(g);
    float f1 = 8.0, f2 = 8.0;
    for (int yy = -1; yy <= 1; yy++) {
        for (int xx = -1; xx <= 1; xx++) {
            float2 nb = float2(xx, yy);
            float2 pt = nb + 0.5
                      + 0.35 * float2(sin(u.time * 0.12 + termite_hash(cell + nb) * 6.28),
                                      cos(u.time * 0.10 + termite_hash(cell + nb + 3.3) * 6.28));
            float d = length(pt - f);
            if (d < f1) { f2 = f1; f1 = d; } else if (d < f2) { f2 = d; }
        }
    }
    fx = float3(0.06, 0.08, 0.10) * exp(-(f2 - f1) * 9.0)
       + float3(0.02, 0.03, 0.04) * (1.0 - f1);
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
