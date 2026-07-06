// Breath — the background inhales on an 8s cycle; idling deepens it.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/breath

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


    // Breath: an 8-second inhale/exhale; idling deepens the breath,
    // typing steadies it back down.
    float calm = clamp(u.keypressAge / 10.0, 0.0, 1.0);
    float b = 0.5 + 0.5 * sin(u.time * 0.785);
    b = b * b * (3.0 - 2.0 * b);
    float vign = 1.0 - dot(sq, sq) * 0.9;
    fx = (u.background.rgb * 0.5 + float3(0.03, 0.04, 0.06))
       * b * (0.05 + 0.11 * calm) * vign;
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
