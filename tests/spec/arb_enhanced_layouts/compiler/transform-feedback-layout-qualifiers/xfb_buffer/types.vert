// [config]
// expect_result: pass
// glsl_version: 1.50
// require_extensions: GL_ARB_enhanced_layouts
// [end config]
//
// From the GL_ARB_enhanced_layouts spec:
//
//    "Variables and block members qualified with *xfb_offset* can be scalars,
//    vectors, matrices, structures, and (sized) arrays of these. The offset
//    must be a multiple of the size of the first component of the first
//    qualified variable or block member, or a compile-time error results.
//    Further, if applied to an aggregate containing a double, the offset must
//    also be a multiple of 8, and the space taken in the buffer will be a
//    multiple of 8."
//
// We take this to mean xfb_buffer can also qualify these types.

#version 150
#extension GL_ARB_enhanced_layouts: require

struct S {
  vec3 x;
};

layout(xfb_buffer = 1) out float var1;

layout(xfb_buffer = 0) out vec4 var2;

layout(xfb_buffer = 3) out mat4 var3;

layout(xfb_buffer = 2) out S s;

void main()
{
}
