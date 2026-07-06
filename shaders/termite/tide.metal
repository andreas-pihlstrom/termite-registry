// Tide — a waterline breathing at two-thirds height, foam whisper.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/tide

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


    // Tide: a waterline breathing at two-thirds height.
    float line = 0.68 + sin(u.time * 0.18) * 0.05 + sin(sq.x * 2.4 + u.time * 0.5) * 0.012;
    float below = smoothstep(line, line + 0.02, uv.y);
    fx = float3(0.03, 0.08, 0.11) * below * (1.0 - (uv.y - line) * 0.8);
    float foam = exp(-abs(uv.y - line) * 120.0) * (0.5 + 0.5 * sin(sq.x * 40.0 + u.time * 1.2));
    fx += float3(0.09, 0.11, 0.12) * foam * 0.6;
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
