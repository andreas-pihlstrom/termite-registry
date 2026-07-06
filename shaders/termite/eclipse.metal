// Eclipse — a dark disc with a breathing corona, upper right.
// From termite's calm set. Fork freely: edit, save, the terminal restyles live.
// author: termite · license: MIT · marketplace id: termite/eclipse

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


    // Eclipse: a dark disc, corona breathing, upper right.
    float2 c = float2(aspect * 0.30, -0.26);
    float d = length(sq - c);
    float rad = 0.16;
    float corona = exp(-max(d - rad, 0.0) * (9.0 - sin(u.time * 0.3) * 2.0));
    float disc = smoothstep(rad, rad - 0.01, d);
    fx = float3(0.26, 0.15, 0.07) * corona * (1.0 - disc) * 0.8
       - u.background.rgb * disc * 0.35;
    rgb = mix(u.background.rgb + fx, rgb, mask);
    return float4(rgb, sceneColor.a);
}
