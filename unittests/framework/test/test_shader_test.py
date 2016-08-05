# Copyright (c) 2014, 2016 Intel Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

""" Provides tests for the shader_test module """

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)
import os
import textwrap
try:
    import mock
except ImportError:
    from unittest import mock

import pytest
import six

from framework import exceptions
from framework.test import shader_test

# pylint: disable=invalid-name,no-self-use


class _Setup(object):
    def __init__(self):
        self.__patchers = []
        self.__patchers.append(mock.patch.dict(
            'framework.test.base.options.OPTIONS.env',
            {'PIGLIT_PLATFORM': 'foo'}))

    def setup(self, _):
        for patcher in self.__patchers:
            patcher.start()

    def teardown(self, _):
        for patcher in self.__patchers:
            patcher.stop()


_setup = _Setup()
setup_module = _setup.setup
teardown_module = _setup.teardown


class TestConfigParsing(object):
    """Tests for ShaderRunner config parsing."""

    @pytest.mark.parametrize('gles,operator,expected', [
        # pylint: disable=bad-whitespace
        ('2.0', '>=', 'shader_runner_gles2'),
        ('2.0', '<=', 'shader_runner_gles2'),
        ('2.0', '=',  'shader_runner_gles2'),
        ('2.0', '>',  'shader_runner_gles3'),
        ('3.0', '>=', 'shader_runner_gles3'),
        ('3.0', '<=', 'shader_runner_gles2'),
        ('3.0', '=',  'shader_runner_gles3'),
        ('3.0', '>',  'shader_runner_gles3'),
        ('3.0', '<',  'shader_runner_gles2'),
        ('3.1', '>=', 'shader_runner_gles3'),
        ('3.1', '<=', 'shader_runner_gles2'),
        ('3.1', '=',  'shader_runner_gles3'),
        ('3.1', '>',  'shader_runner_gles3'),
        ('3.1', '<',  'shader_runner_gles2'),
        ('3.2', '>=', 'shader_runner_gles3'),
        ('3.2', '<=', 'shader_runner_gles2'),
        ('3.2', '=',  'shader_runner_gles3'),
        ('3.2', '<',  'shader_runner_gles2'),
    ])
    def test_bin(self, gles, operator, expected, tmpdir):
        """Test that the shader_runner parse picks the correct binary."""
        p = tmpdir.join('test.shader_test')
        p.write(textwrap.dedent("""\
            [require]
            GL ES {} {}
            GLSL ES >= 1.00

            [next section]
            """.format(operator, gles)))
        test = shader_test.ShaderTest(six.text_type(p))

        assert os.path.basename(test.command[0]) == expected

    def test_gles3_bin(self, tmpdir):
        """test.shader_test.ShaderTest: Identifies GLES3 tests successfully."""
        p = tmpdir.join('test.shader_test')
        p.write(textwrap.dedent("""\
            [require]
            GL ES >= 3.0
            GLSL ES >= 3.00 es
            """))
        test = shader_test.ShaderTest(six.text_type(p))

        assert os.path.basename(test.command[0]) == "shader_runner_gles3"

    def test_skip_gl_required(self, tmpdir):
        """test.shader_test.ShaderTest: populates gl_requirements properly"""
        p = tmpdir.join('test.shader_test')
        p.write(textwrap.dedent("""\
            [require]
            GL >= 3.0
            GL_ARB_ham_sandwhich
            """))
        test = shader_test.ShaderTest(six.text_type(p))

        assert test.gl_required == {'GL_ARB_ham_sandwhich'}

    def test_skip_gl_version(self, tmpdir):
        """test.shader_test.ShaderTest: finds gl_version."""
        p = tmpdir.join('test.shader_test')
        p.write(textwrap.dedent("""\
            [require]
            GL >= 2.0
            GL_ARB_ham_sandwhich
            """))
        test = shader_test.ShaderTest(six.text_type(p))

        assert test.gl_version == 2.0

    def test_skip_gles_version(self, tmpdir):
        """test.shader_test.ShaderTest: finds gles_version."""
        p = tmpdir.join('test.shader_test')
        p.write(textwrap.dedent("""\
            [require]
            GL ES >= 2.0
            GL_ARB_ham_sandwhich
            """))
        test = shader_test.ShaderTest(six.text_type(p))

        assert test.gles_version == 2.0

    def test_skip_glsl_version(self, tmpdir):
        """test.shader_test.ShaderTest: finds glsl_version."""
        p = tmpdir.join('test.shader_test')
        p.write(textwrap.dedent("""\
            [require]
            GL >= 2.1
            GLSL >= 1.20
            """))
        test = shader_test.ShaderTest(six.text_type(p))

        assert test.glsl_version == 1.2

    def test_skip_glsl_es_version(self, tmpdir):
        """test.shader_test.ShaderTest: finds glsl_es_version."""
        p = tmpdir.join('test.shader_test')
        p.write(textwrap.dedent("""\
            [require]
            GL ES >= 2.0
            GLSL ES >= 1.00
            """))
        test = shader_test.ShaderTest(six.text_type(p))

        assert test.glsl_es_version == 1.0

    def test_ignore_directives(self, tmpdir):
        """There are some directives for shader_runner that are not interpreted
        by the python layer, they are only for the C layer. These should be
        ignored by the python layer.
        """
        p = tmpdir.join('test.shader_test')
        p.write(textwrap.dedent("""\
            [require]
            GL >= 3.3
            GLSL >= 1.50
            GL_MAX_VERTEX_OUTPUT_COMPONENTS
            GL_MAX_FRAGMENT_UNIFORM_COMPONENTS
            GL_MAX_VERTEX_UNIFORM_COMPONENTS
            GL_MAX_VARYING_COMPONENTS
            GL_ARB_foobar
            """))
        test = shader_test.ShaderTest(six.text_type(p))

        assert test.gl_version == 3.3
        assert test.glsl_version == 1.50
        assert test.gl_required == {'GL_ARB_foobar'}


def test_command_add_auto(tmpdir):
    """test.shader_test.ShaderTest: -auto is added to the command."""
    p = tmpdir.join('test.shader_test')
    p.write(textwrap.dedent("""\
        [require]
        GL ES >= 3.0
        GLSL ES >= 3.00 es
        """))
    test = shader_test.ShaderTest(six.text_type(p))

    assert '-auto' in test.command