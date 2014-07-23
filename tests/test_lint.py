# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
import unittest
import mock
import simplejson
import StringIO

from checker.tests import downstream
from checker.tests.downstream.test_check_subsets_exists import File
from cli.ttfont import Font as OriginFont


def _get_tests(TestCase):
    return unittest.defaultTestLoader.loadTestsFromTestCase(TestCase)


def _run_font_test(TestCase):
    runner = unittest.TextTestRunner(stream=StringIO.StringIO())
    tests = _get_tests(TestCase)
    return runner.run(tests)


class Test_CheckCanonicalFilenamesTestCase(unittest.TestCase):

    @mock.patch.object(downstream.CheckCanonicalFilenames, 'read_metadata_contents')
    def test_one(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'name': 'FamilyName',
                'filename': 'FamilyName-Regular.ttf'
            }]
        })
        result = _run_font_test(downstream.CheckCanonicalFilenames)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))

        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'name': 'Family',
                'filename': 'Family-Bold.ttf'
            }]
        })
        result = _run_font_test(downstream.CheckCanonicalFilenames)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))


class Test_CheckCanonicalStyles(unittest.TestCase):

    @mock.patch.object(downstream.CheckCanonicalStyles, 'read_metadata_contents')
    def test_two(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'name': 'Family',
                'filename': 'Family-Regular.ttf'
            }]
        })

        class Font(object):
            macStyle = 0
            italicAngle = 0
            names = []

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.macStyle = downstream.CheckCanonicalStyles.ITALIC_MASK
            result = _run_font_test(downstream.CheckCanonicalStyles)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.macStyle = 0
            result = _run_font_test(downstream.CheckCanonicalStyles)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.italicAngle = 10
            result = _run_font_test(downstream.CheckCanonicalStyles)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))

        class name:
            string = ''

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            n = name()
            n.string = 'italic'
            mocked_get_ttfont.return_value.names.append(n)
            result = _run_font_test(downstream.CheckCanonicalStyles)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))


class Test_CheckCanonicalWeights(unittest.TestCase):

    @mock.patch.object(downstream.CheckCanonicalWeights, 'read_metadata_contents')
    def test_three(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'weight': 50
            }]
        })

        class Font(object):
            OS2_usWeightClass = 400

        # test if font weight less than 100 is invalid value
        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(downstream.CheckCanonicalWeights)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))

        # test if font weight larger than 900 is invalid value
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'weight': 901
            }]
        })

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(downstream.CheckCanonicalWeights)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))

        # test if range 100..900 is valid values and checked for fonts
        for n in range(1, 10):
            with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
                mocked_get_ttfont.return_value = Font()
                metadata_contents.return_value = simplejson.dumps({
                    'fonts': [{
                        'weight': n * 100
                    }]
                })
                mocked_get_ttfont.return_value.OS2_usWeightClass = n * 100
                result = _run_font_test(downstream.CheckCanonicalWeights)

            if result.errors:
                self.fail(result.errors[0][1])
            self.assertFalse(bool(result.failures))


class Test_CheckFamilyNameMatchesFontName(unittest.TestCase):

    @mock.patch.object(downstream.CheckFamilyNameMatchesFontNames, 'read_metadata_contents')
    def test_four(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'name': 'Family',
            'fonts': [{
                'name': 'Family'
            }]
        })
        result = _run_font_test(downstream.CheckFamilyNameMatchesFontNames)
        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))

        metadata_contents.return_value = simplejson.dumps({
            'name': 'Family',
            'fonts': [{
                'name': 'FontName'
            }]
        })
        result = _run_font_test(downstream.CheckFamilyNameMatchesFontNames)
        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))


class Test_CheckMenuSubsetContainsProperGlyphs(unittest.TestCase):

    @mock.patch.object(downstream.CheckMenuSubsetContainsProperGlyphs, 'read_metadata_contents')
    def test_five(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'name': 'Font Family',
            'fonts': [{
                'name': 'FontName',
                'filename': 'FontName-Regular.ttf'
            }]
        })

        class FontS:

            def retrieve_glyphs_from_cmap_format_4(self):
                return dict(map(lambda x: (ord(x), x), 'Font Name'))

        class FontF:

            def retrieve_glyphs_from_cmap_format_4(self):
                return dict(map(lambda x: (ord(x), x), 'FontName'))

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = FontS()
            result = _run_font_test(downstream.CheckMenuSubsetContainsProperGlyphs)
        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = FontF()
            result = _run_font_test(downstream.CheckMenuSubsetContainsProperGlyphs)
        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))


class Test_CheckMetadataMatchesNameTable(unittest.TestCase):

    @mock.patch.object(downstream.CheckMetadataMatchesNameTable, 'read_metadata_contents')
    def test_six(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'name': 'Font Family',
            'fonts': [{
                'name': 'Font Family',
                'filename': 'FontFamily-Regular.ttf'
            }]
        })

        class Font:
            familyname = 'Font Family'

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(downstream.CheckMetadataMatchesNameTable)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.familyname = 'Arial Font Family'
            result = _run_font_test(downstream.CheckMetadataMatchesNameTable)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))


class Test_CheckNbspWidthMatchesSpWidth(unittest.TestCase):

    @mock.patch.object(downstream.CheckNbspWidthMatchesSpWidth, 'read_metadata_contents')
    def test_seven(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'name': 'Font Name'
            }]
        })

        class Font:

            def advanceWidth(self, glyphId):
                return 1680

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(downstream.CheckNbspWidthMatchesSpWidth)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))


class Test_CheckSubsetsExist(unittest.TestCase):

    @mock.patch.object(downstream.CheckSubsetsExist, 'read_metadata_contents')
    def test_eight(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'filename': 'FontName-Regular.ttf'
            }],
            'subsets': ['cyrillic']
        })

        with mock.patch.object(File, 'exists') as exists, mock.patch.object(File, 'size') as size:
            size.return_value = 11
            result = _run_font_test(downstream.CheckSubsetsExist)
            if result.errors:
                self.fail(result.errors[0][1])
            self.assertFalse(bool(result.failures))
            exists.assert_called_with('FontName-Regular.cyrillic')
            self.assertEqual(size.call_args_list,
                             [mock.call('FontName-Regular.cyrillic'),
                              mock.call('FontName-Regular.ttf')])


class Test_CheckUnusedGlyphData(unittest.TestCase):

    def test_nine(self):

        class Font:

            def get_glyf_length(self):
                return 1234

            def get_loca_glyph_offset(self, num):
                return 1200

            def get_loca_glyph_length(self, num):
                return 34

            def get_loca_num_glyphs(self):
                return 123

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(downstream.CheckUnusedGlyphData)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))


class Test_CheckOS2WidthClass(unittest.TestCase):

    def test_ten(self):

        class Font:
            OS2_usWidthClass = 4

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(downstream.CheckOS2WidthClass)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            for i in [0, 10]:
                mocked_get_ttfont.return_value.OS2_usWidthClass = i
                result = _run_font_test(downstream.CheckOS2WidthClass)

                if result.errors:
                    self.fail(result.errors[0][1])
                self.assertTrue(bool(result.failures))


class Test_CheckNoProblematicFormats(unittest.TestCase):

    def test_eleven(self):

        class FontTool:

            @staticmethod
            def get_tables():
                return ['glyf', 'post', 'GPOS']

        import cli.ttfont
        with mock.patch.object(cli.ttfont.FontTool, 'get_tables') as get_tables:
            get_tables.return_value = FontTool.get_tables()
            result = _run_font_test(downstream.CheckNoProblematicFormats)

        if result.errors:
            self.fail(result.errors[0][1])

        self.assertTrue(bool(result.failures))


class Test_CheckHmtxHheaMaxAdvanceWidthAgreement(unittest.TestCase):

    def test_twelve(self):

        class Font:

            def get_hmtx_max_advanced_width(self):
                return 250

            @property
            def advance_width_max(self):
                return 250

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(downstream.CheckHmtxHheaMaxAdvanceWidthAgreement)

            if result.errors:
                self.fail(result.errors[0][1])

            self.assertFalse(bool(result.failures))

            mocked_get_ttfont.return_value.advance_width_max = 240

            result = _run_font_test(downstream.CheckHmtxHheaMaxAdvanceWidthAgreement)

            if result.errors:
                self.fail(result.errors[0][1])

            self.assertTrue(bool(result.failures))


class Test_CheckGlyfTableLength(unittest.TestCase):

    def test_thirteen(self):

        class Font:

            def get_loca_length(self):
                return 5541  # considering padding in 3 bytes

            def get_glyf_length(self):
                return 5544

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()

            result = _run_font_test(downstream.CheckGlyfTableLength)

            if result.errors:
                self.fail(result.errors[0][1])

            self.assertFalse(bool(result.failures))

    def test_fourteen(self):
        class Font:

            def get_loca_length(self):
                return 5550  # considering "loca" length greater than "glyf"

            def get_glyf_length(self):
                return 5544

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()

            result = _run_font_test(downstream.CheckGlyfTableLength)

            if result.errors:
                self.fail(result.errors[0][1])

            self.assertTrue(bool(result.failures))

    def test_fifteen(self):
        class Font:

            def get_loca_length(self):
                # considering "loca" less than glyf on more
                # than 3 bytes (allowed padding)
                return 5540

            def get_glyf_length(self):
                return 5544

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()

            result = _run_font_test(downstream.CheckGlyfTableLength)

            if result.errors:
                self.fail(result.errors[0][1])

            self.assertTrue(bool(result.failures))


class Test_CheckFullFontNameBeginsWithFamilyName(unittest.TestCase):

    def test_sixteen(self):
        class Font:
            bin2unistring = OriginFont.bin2unistring

            @property
            def names(self):
                return [
                    type('name', (object,),
                         {'nameID': 1, 'string': 'FamilyName', 'platEncID': 1,
                          'langID': 1, 'platformID': 1}),
                    type('name', (object,),
                         {'nameID': 4, 'string': 'FamilyNameRegular', 'platEncID': 1,
                          'langID': 1, 'platformID': 1})
                ]

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(downstream.CheckFullFontNameBeginsWithFamilyName)

        if result.errors:
            self.fail(result.errors[0][1])

        self.assertFalse(bool(result.failures))

    def test_seventeen(self):
        class Font:
            bin2unistring = OriginFont.bin2unistring

            @property
            def names(self):
                return [
                    type('name', (object,),
                         {'nameID': 1, 'string': 'FamilyName', 'platEncID': 1,
                          'langID': 1, 'platformID': 1}),
                    type('name', (object,),
                         {'nameID': 4, 'string': 'FamilyRegular', 'platEncID': 1,
                          'langID': 1, 'platformID': 1})
                ]

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(downstream.CheckFullFontNameBeginsWithFamilyName)

        if result.errors:
            self.fail(result.errors[0][1])

        self.assertTrue(bool(result.failures))


class Test_CheckUPMHeightsLess120(unittest.TestCase):

    def test_eighteen(self):

        class FakeAscents:

            maxv = 910

            def get_max(self):
                return self.maxv

        class FakeDescents:

            minv = -210

            def get_min(self):
                return self.minv

        class Font:

            @property
            def upm_heights(self):
                return 1024

            ascents = FakeAscents()
            descents = FakeDescents()

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(downstream.TestCheckUPMHeightsLess120)

            if result.errors:
                self.fail(result.errors[0][1])

            self.assertFalse(bool(result.failures))

            mocked_get_ttfont.return_value.ascents.maxv = 1400
            result = _run_font_test(downstream.TestCheckUPMHeightsLess120)

            if result.errors:
                self.fail(result.errors[0][1])

            self.assertTrue(bool(result.failures))


class Test_CheckFontNameInCamelCase(unittest.TestCase):

    @mock.patch.object(downstream.CheckFontNameNotInCamelCase, 'read_metadata_contents')
    def test_nineteen(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'name': 'Font Family',
            'fonts': [{
                'name': 'Font Family',
                'filename': 'FontFamily-Regular.ttf'
            }]
        })
        result = _run_font_test(downstream.CheckFontNameNotInCamelCase)

        if result.errors:
            self.fail(result.errors[0][1])

        self.assertFalse(bool(result.failures))

        metadata_contents.return_value = simplejson.dumps({
            'name': 'Font Family',
            'fonts': [{
                'name': 'FontFamily',
                'filename': 'FontFamily-Regular.ttf'
            }]
        })

        result = _run_font_test(downstream.CheckFontNameNotInCamelCase)

        if result.errors:
            self.fail(result.errors[0][1])

        self.assertTrue(bool(result.failures))


class Test_CheckMagicPREPByteCode(unittest.TestCase):

    def test_twenty(self):

        class Font:
            bytecode = '\xb8\x01\xff\x85\xb0\x04\x8d'

            def get_program_bytecode(self):
                return self.bytecode

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(downstream.CheckMagicPREPByteCode)

            if result.errors:
                self.fail(result.errors[0][1])

            self.assertFalse(bool(result.failures))

            mocked_get_ttfont.return_value.bytecode = '\x00'
            result = _run_font_test(downstream.CheckMagicPREPByteCode)

            if result.errors:
                self.fail(result.errors[0][1])

            self.assertTrue(bool(result.failures))


class Test_CheckFontNamesSameAcrossPlatforms(unittest.TestCase):

    def test_twenty_one(self):

        class Font:
            bin2unistring = OriginFont.bin2unistring

            @property
            def names(self):
                return [
                    type('name', (object,),
                         {'nameID': 1, 'string': 'FamilyName',
                          'langID': 0x409, 'platformID': 3}),
                    type('name', (object,),
                         {'nameID': 1, 'string': 'FamilyNameRegular',
                          'langID': 0, 'platformID': 1})
                ]

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(downstream.CheckNamesSameAcrossPlatforms)

            if result.errors:
                self.fail(result.errors[0][1])

            self.assertTrue(bool(result.failures))

            mocked_get_ttfont.return_value.names = [
                type('name', (object,),
                     {'nameID': 1, 'string': 'FamilyNameRegular',
                      'langID': 0x409, 'platformID': 3}),
                type('name', (object,),
                     {'nameID': 1, 'string': 'FamilyNameRegular',
                      'langID': 0, 'platformID': 1})
            ]

            result = _run_font_test(downstream.CheckNamesSameAcrossPlatforms)

            if result.errors:
                self.fail(result.errors[0][1])

            if result.failures:
                self.fail(result.failures[0][1])

            self.assertFalse(bool(result.failures))


class Test_CheckPostScriptNameMatchesWeight(unittest.TestCase):

    @mock.patch.object(downstream.CheckPostScriptNameMatchesWeight, 'read_metadata_contents')
    def test_three(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{'weight': 400, 'postScriptName': 'Family-Regular'},
                      {'weight': 400, 'postScriptName': 'Family-Italic'},
                      {'weight': 100, 'postScriptName': 'Family-Thin'},
                      {'weight': 100, 'postScriptName': 'Family-ThinItalic'},
                      {'weight': 200, 'postScriptName': 'Family-ExtraLight'},
                      {'weight': 200, 'postScriptName': 'Family-ExtraLightItalic'},
                      {'weight': 300, 'postScriptName': 'Family-Light'},
                      {'weight': 300, 'postScriptName': 'Family-LightItalic'},
                      {'weight': 500, 'postScriptName': 'Family-Medium'},
                      {'weight': 500, 'postScriptName': 'Family-MediumItalic'},
                      {'weight': 600, 'postScriptName': 'Family-SemiBold'},
                      {'weight': 600, 'postScriptName': 'Family-SemiBoldItalic'},
                      {'weight': 700, 'postScriptName': 'Family-Bold'},
                      {'weight': 700, 'postScriptName': 'Family-BoldItalic'},
                      {'weight': 800, 'postScriptName': 'Family-ExtraBold'},
                      {'weight': 800, 'postScriptName': 'Family-ExtraBoldItalic'},
                      {'weight': 900, 'postScriptName': 'Family-Black'},
                      {'weight': 900, 'postScriptName': 'Family-BlackItalic'}]
        })
        result = _run_font_test(downstream.CheckPostScriptNameMatchesWeight)

        if result.errors:
            self.fail(result.errors[0][1])

        if result.failures:
            self.fail(result.failures[0][1])

        self.assertFalse(bool(result.failures))

        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{'weight': 500, 'postScriptName': 'Family-Regular'}]
        })

        result = _run_font_test(downstream.CheckPostScriptNameMatchesWeight)

        if result.errors:
            self.fail(result.errors[0][1])

        self.assertTrue(bool(result.failures))


class Test_CheckMetadataContainsReservedFontName(unittest.TestCase):

    @mock.patch.object(downstream.CheckMetadataContainsReservedFontName, 'read_metadata_contents')
    def test_three(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{'copyright': 'Copyright (c) 2014 (mail@example.com) with Reserved Font Name'}]
        })
        result = _run_font_test(downstream.CheckMetadataContainsReservedFontName)

        if result.errors:
            self.fail(result.errors[0][1])

        if result.failures:
            self.fail(result.failures[0][1])

        self.assertFalse(bool(result.failures))

        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{'copyright': 'Copyright (c) 2014 (mail@example.com)'}]
        })

        result = _run_font_test(downstream.CheckMetadataContainsReservedFontName)

        if result.errors:
            self.fail(result.errors[0][1])

        self.assertTrue(bool(result.failures))

        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{'copyright': 'Copyright (c) 2014 with Reserved Font Name'}]
        })

        result = _run_font_test(downstream.CheckMetadataContainsReservedFontName)

        if result.errors:
            self.fail(result.errors[0][1])

        self.assertTrue(bool(result.failures))
