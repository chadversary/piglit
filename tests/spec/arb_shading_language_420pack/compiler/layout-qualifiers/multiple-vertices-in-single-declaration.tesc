// [config]
// expect_result: pass
// glsl_version: 1.50
// require_extensions: GL_ARB_shading_language_420pack GL_ARB_tessellation_shader
// check_link: true
// [end config]
//
// From the ARB_shading_language_420pack spec:
//
//    "More than one layout qualifier may appear in a single declaration. If
//     the same layout-qualifier-name occurs in multiple layout qualifiers for
//     the same declaration, the last one overrides the former ones."
//
// From the ARB_tessellation_shader spec:
//
//    "All tessellation control shader layout declarations in a program must
//     specify the same output patch vertex count."

#version 150
#extension GL_ARB_shading_language_420pack: enable
#extension GL_ARB_tessellation_shader: require

layout(vertices = 4) layout(vertices = 3) out;
layout(vertices = 3) out;

void main() {
    gl_out[gl_InvocationID].gl_Position = vec4(0.0);
    gl_TessLevelOuter = float[4](1.0, 1.0, 1.0, 1.0);
    gl_TessLevelInner = float[2](1.0, 1.0);
}
