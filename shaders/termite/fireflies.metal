// Fireflies — wandering green-gold points, soft blinking.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/fireflies

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


    // Fireflies: wandering points that blink in soft green-gold.
    float2 g = float2(uv.x * aspect, uv.y) * 7.0;
    float2 cell = floor(g);
    float h = termite_hash(cell);
    if (h > 0.72) {
        float2 wander = float2(sin(u.time * (0.15 + h * 0.2) + h * 31.0),
                               cos(u.time * (0.11 + h * 0.25) + h * 17.0)) * 0.32 + 0.5;
        float d = length(fract(g) - wander);
        float blink = smoothstep(0.35, 1.0, sin(u.time * (0.5 + h) + h * 90.0) * 0.5 + 0.5);
        fx += float3(0.17, 0.23, 0.08) * exp(-d * 18.0) * blink;
    }
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
