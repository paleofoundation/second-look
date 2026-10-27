import importlib.util
import io
from pathlib import Path
import stat
import unittest
import warnings
import zipfile

spec=importlib.util.spec_from_file_location('tranche_inventory',Path(__file__).with_name('inventory.py'))
inventory=importlib.util.module_from_spec(spec);spec.loader.exec_module(inventory)


class ArchiveMetadataTests(unittest.TestCase):
    def make(self,entries):
        stream=io.BytesIO()
        with warnings.catch_warnings(), zipfile.ZipFile(stream,'w') as archive:
            warnings.simplefilter('ignore')
            for name,data in entries:archive.writestr(name,data)
        return stream.getvalue()

    def test_streamed_pdf_manifest_without_materializing(self):
        result=inventory.archive_inventory(self.make([('folder/supplement.pdf',b'%PDF-1.4 synthetic')]),lambda data:7)
        self.assertEqual(result[0]['pages'],7)
        self.assertFalse(result[0]['materialized'])
        self.assertFalse(result[0]['bodyTextExtracted'])

    def test_traversal_absolute_backslash_colon_and_controls_rejected(self):
        for name in ['../x.pdf','/x.pdf','a/../x.pdf','a\\x.pdf','C:x.pdf','a//x.pdf','a\nx.pdf']:
            with self.subTest(name=name),self.assertRaises(ValueError):
                inventory.archive_inventory(self.make([(name,b'%PDF-1.4')]),lambda data:1)

    def test_duplicate_case_collision_symlink_and_nonpdf_rejected(self):
        for entries in [[('a.pdf',b'%PDF-'),('a.pdf',b'%PDF-')],[('A.pdf',b'%PDF-'),('a.pdf',b'%PDF-')],[('a.pdf',b'<html>bad download')],[('nested.zip',b'PK')]]:
            with self.subTest(entries=entries),self.assertRaises(ValueError):inventory.archive_inventory(self.make(entries),lambda data:1)
        symlink=zipfile.ZipInfo('linked.pdf');symlink.external_attr=(stat.S_IFLNK|0o777)<<16
        with self.assertRaises(ValueError):inventory.archive_inventory(self.make([(symlink,b'outside.pdf')]),lambda data:1)

    def test_ratio_and_size_limits_fail_before_member_reading(self):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED) as archive:archive.writestr('huge.pdf',b'%PDF-'+b'x'*1000000)
        with self.assertRaisesRegex(ValueError,'ratio'):inventory.archive_inventory(stream.getvalue(),lambda data:1)
        old=inventory.MAX_MEMBER_BYTES
        try:
            inventory.MAX_MEMBER_BYTES=5
            with self.assertRaisesRegex(ValueError,'bytes'):inventory.archive_inventory(self.make([('a.pdf',b'%PDF-1.4')]),lambda data:1)
        finally:inventory.MAX_MEMBER_BYTES=old

    def test_html_inventory_uses_attributes_not_scientific_body(self):
        parser=inventory.Structure();parser.feed('<link rel="canonical" href="https://example.org/article/"><section id="s1">SECRET BODY</section><figure id="f1"><img src="f1.jpg"></figure><a href="s001.docx">SECRET CAPTION</a><a href="https://support.example.org/">Support</a>')
        result=parser.result()
        self.assertEqual(result['sectionIds'],['s1'])
        self.assertEqual(result['figureImageReferences'][0]['resolvedUrl'],'https://example.org/article/f1.jpg')
        self.assertEqual(len(result['documentLinkReferences']),1)
        self.assertNotIn('SECRET',str(result))


if __name__=='__main__':unittest.main()
