// Validation preamble — mirrors the contract termite's runtime prepends to
// user shaders (TermiteUniforms + free helpers). CI compiles
// `preamble.metal + <shader>.metal` to prove every marketplace shader builds.
#include <metal_stdlib>
using namespace metal;

struct TermiteUniforms {
    float2 resolution;
    float time;
    float curvature;
    float4 background;
    float2 cursor;
    float keypressAge;
    float typingRate;
};

static float termite_hash(float2 p) {
    return fract(sin(dot(p, float2(12.9898, 78.233))) * 43758.5453);
}

static float3 termite_palette(float t) {
    return 0.5 + 0.5 * cos(6.28318 * (t + float3(0.0, 0.33, 0.67)));
}

static float termite_textMask(float3 rgb, float3 bg) {
    float3 rel = abs(rgb - bg);
    return clamp(max(rel.r, max(rel.g, rel.b)) * 5.0, 0.0, 1.0);
}
