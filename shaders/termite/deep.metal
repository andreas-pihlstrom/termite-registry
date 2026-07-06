// Deep — abyssal gradient; a faint sonar ring every nine seconds.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/deep

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


    // Deep: abyssal gradient, a sonar ring every nine seconds.
    fx = float3(0.0, 0.02, 0.06) * (1.0 - uv.y);
    float tick = floor(u.time / 9.0);
    float ph = fract(u.time / 9.0);
    float2 src = float2((termite_hash(float2(tick, 4.0)) - 0.5) * aspect * 0.7,
                        (termite_hash(float2(tick, 8.0)) - 0.5) * 0.7);
    float ring = exp(-abs(length(sq - src) - ph * 0.9) * 26.0) * exp(-ph * 3.0);
    fx += float3(0.04, 0.10, 0.12) * ring;
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
