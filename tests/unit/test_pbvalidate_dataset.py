
import unittest
import os.path as op
import os

import pbcore.data.datasets as data
import pbcore.io

from pbcoretools.pbvalidate.dataset import *

TESTDATA_DIR = op.join(op.dirname(op.dirname(__file__)), "data")
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class TestCase (unittest.TestCase):

    @unittest.skip("currently disabled")
    def test_missing_resource(self):
        xml_str = """\
<?xml version='1.0' encoding='UTF-8'?>
<DataSet xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" CreatedAt="2015-06-17T12:30:18" MetaType="PacBio.DataSet.DataSet" Name="" Tags="" UniqueId="167462a6-5a2a-bfd2-8218-36add6b1ed4f" Version="2.3.0" xmlns="http://pacificbiosciences.com/PacBioDataModel.xsd" xsi:schemaLocation="http://pacificbiosciences.com/PacBioDataModel.xsd"><ExternalResources><ExternalResource ResourceId="file:///foo/bar/sorted.bam"><FileIndices><FileIndex ResourceId="file:///foo/bar/sorted.bam.bai" /></FileIndices></ExternalResource></ExternalResources></DataSet>"""
        xml_tmp = "tst_pbvalidate_1.xml"
        with open(xml_tmp, "w") as f:
            f.write(xml_str)
        try:
            v = ValidateResources()
            ds = pbcore.io.DataSet(xml_tmp)
            self.assertFalse(v.validate(ds))
            self.assertEqual([type(e).__name__ for e in v.to_errors(ds)],
                             ["MissingResourceError"])
            e, c = validate_dataset(xml_tmp)
        finally:
            os.remove(xml_tmp)

    def test_reader(self):
        n_aln = 0
        ds_file = os.path.join(TESTDATA_DIR, "tst_2_subreads.xml")
        with DatasetReader(pbcore.io.AlignmentSet, ds_file) as f:
            for aln in f:
                n_aln += 1
        self.assertEqual(n_aln, 4)

    def test_api(self):
        ds_file = os.path.join(TESTDATA_DIR, "tst_1.alignmentset.xml")
        ds = pbcore.io.openDataSet(ds_file)
        self.assertTrue(ValidateNamespace().validate(ds))
        ds2 = DatasetReader(pbcore.io.AlignmentSet, ds_file)
        self.assertTrue(ValidateNamespace().validate(ds2))
        self.assertTrue(ValidateFileName(ds_file).validate(ds2))

    def test_bad_subreadset(self):
        # bad file
        ds_file = os.path.join(TESTDATA_DIR, "tst_2_subreads.xml")
        ds = pbcore.io.openDataSet(ds_file)
        v = ValidateContents(aligned=None, content_type=None)
        self.assertTrue(v.validate(ds))
        v = ValidateContents(aligned=False, content_type="CCS")
        self.assertFalse(v.validate(ds))
        self.assertEqual([type(e).__name__ for e in v.to_errors(ds)],
                         ["FileAlignedError", "FileContentMismatchError"])
        v = ValidateResources()
        self.assertTrue(v.validate(ds))
        v = ValidateDatasetType("ReferenceSet")
        self.assertFalse(v.validate(ds))
        self.assertEqual([type(e).__name__ for e in v.to_errors(ds)],
                         ['DatasetTypeError'])
        self.assertFalse(ValidateNamespace().validate(ds))
        self.assertFalse(ValidateFileName(ds_file).validate(ds))

    def test_file_name_and_contents_consistency(self):
        # file name/content type mismatch
        ds_file = os.path.join(TESTDATA_DIR, "tst_1.ccs.xml")
        ds = pbcore.io.DataSet(ds_file)
        v = ValidateFileName("tst_1.ccs.xml")
        self.assertFalse(v.validate(ds))
        self.assertEqual([type(e).__name__ for e in v.to_errors(ds)],
                         ["FileNameError"])

    def test_root_tag_type(self):
        # MetaType wrong
        file_name = os.path.join(TESTDATA_DIR, "tst_1b_subreads.xml")
        self.assertFalse(ValidateRootTag().validate(file_name))

    def test_validate_encoding(self):
        # good file
        file_name = os.path.join(TESTDATA_DIR, "tst_1.subreadset.xml")
        self.assertTrue(ValidateEncoding().validate(file_name))
        # no header
        file_name = os.path.join(TESTDATA_DIR, "tst_1b.subreadset.xml")
        self.assertFalse(ValidateEncoding().validate(file_name))
        file_name = os.path.join(TESTDATA_DIR, "tst_1c.subreadset.xml")
        self.assertFalse(ValidateEncoding().validate(file_name))

    def test_validate_xml_pyxb(self):
        file_name = os.path.join(TESTDATA_DIR, "tst_1d.subreadset.xml")
        ds = pbcore.io.SubreadSet(file_name)
        v = ValidateXML()
        self.assertFalse(v.validate(file_name))
        e = v.to_errors(file_name)
        self.assertTrue(str(e[0]).startswith("XML schema error:"))


if __name__ == "__main__":
    unittest.main()
