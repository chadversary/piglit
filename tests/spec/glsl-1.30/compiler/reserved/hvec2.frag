// [config]
// expect_result: fail
// glsl_version: 1.30
// [end config]
//
// Check that 'hvec2' is a reserved keyword.

#version 130

int f()
{
	int hvec2;
	return 0;
}
