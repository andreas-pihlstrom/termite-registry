// Halo — a breathing glow that follows the cursor.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/halo

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


    // Halo: a breathing glow that follows the cursor.
    float2 cq = (u.cursor / u.resolution - 0.5) * float2(aspect, 1.0);
    float d = length(sq - cq);
    float breathe = 0.85 + 0.15 * sin(u.time * 0.6);
    float typing = clamp(u.typingRate / 6.0, 0.0, 1.0);
    fx = float3(0.09, 0.10, 0.14) * exp(-d * (5.5 - typing * 1.5)) * breathe;
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
