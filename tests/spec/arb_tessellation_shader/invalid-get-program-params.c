/*
 * Copyright © 2014 Intel Corporation
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice (including the next
 * paragraph) shall be included in all copies or substantial portions of the
 * Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */

/**
 * \file invalid-get-program-params.c
 *
 * From the ARB_tessellation_shader spec (Errors section):
 *
 *    "The error INVALID_OPERATION is generated by GetProgramiv if <pname>
 *    identifies a tessellation control or evaluation shader-specific property
 *    and <program> has not been linked successfully, or does not contain
 *    objects to form a shader whose type corresponds to <pname>."
 *
 * Test to get parameters from programs that lack the required shader type.
 */

#include "piglit-util-gl.h"

PIGLIT_GL_TEST_CONFIG_BEGIN

	config.supports_gl_compat_version = 32;
	config.supports_gl_core_version = 32;

PIGLIT_GL_TEST_CONFIG_END


static const char *const tcs_source =
"#version 150\n"
"#extension GL_ARB_tessellation_shader: require\n"
"layout(vertices = 3) out;\n"
"void main() {\n"
"	gl_out[gl_InvocationID].gl_Position = vec4(0.0);\n"
"	gl_TessLevelOuter = float[4](1.0, 1.0, 1.0, 1.0);\n"
"	gl_TessLevelInner = float[2](1.0, 1.0);\n"
"}\n";

static const char *const tes_source =
"#version 150\n"
"#extension GL_ARB_tessellation_shader: require\n"
"layout(triangles) in;\n"
"void main() { gl_Position = vec4(0.0); }\n";


void
piglit_init(int argc, char **argv)
{
	bool pass = true;
	unsigned int tcs_prog, tes_prog;
	int i, v;
	static const GLenum tes_params[] = {
		GL_TESS_GEN_MODE,
		GL_TESS_GEN_SPACING,
		GL_TESS_GEN_VERTEX_ORDER,
		GL_TESS_GEN_POINT_MODE,
	};

	piglit_require_extension("GL_ARB_tessellation_shader");

	tcs_prog = glCreateShaderProgramv(GL_TESS_CONTROL_SHADER, 1,
					  (const GLchar *const*)&tcs_source);
	piglit_link_check_status(tcs_prog);

	tes_prog = glCreateShaderProgramv(GL_TESS_EVALUATION_SHADER, 1,
					  (const GLchar *const*)&tes_source);
	piglit_link_check_status(tes_prog);

	for (i = 0; i < ARRAY_SIZE(tes_params); ++i ) {
		pass = piglit_check_gl_error(GL_NO_ERROR) && pass;
		glGetProgramiv(tcs_prog, tes_params[i], &v);
		pass = piglit_check_gl_error(GL_INVALID_OPERATION) && pass;
	}

	pass = piglit_check_gl_error(GL_NO_ERROR) && pass;
	glGetProgramiv(tes_prog, GL_TESS_CONTROL_OUTPUT_VERTICES, &v);
	pass = piglit_check_gl_error(GL_INVALID_OPERATION) && pass;

	glDeleteProgram(tcs_prog);
	glDeleteProgram(tes_prog);

	pass = piglit_check_gl_error(GL_NO_ERROR) && pass;

	piglit_report_result(pass ? PIGLIT_PASS : PIGLIT_FAIL);
}


enum piglit_result
piglit_display(void)
{
	return PIGLIT_PASS;
}

