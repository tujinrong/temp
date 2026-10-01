"""Synthetic OLE visibility regressions, no private workbook required."""
import tempfile, unittest, zipfile
from pathlib import Path
from src.ole_preview import discover_previews

M='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P='http://schemas.openxmlformats.org/package/2006/relationships'

class PreviewTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'x.xlsx'
    def tearDown(self):self.tmp.cleanup()
    def fixture(self,state='visible',style='',row='',vml=True,duplicate=False,external=False,ole=True):
        obj='<oleObject shapeId="42"><objectPr r:id="img"/></oleObject>' if ole else ''
        with zipfile.ZipFile(self.path,'w') as z:
            z.writestr('xl/workbook.xml',f'<workbook xmlns="{M}" xmlns:r="{R}"><sheets><sheet name="Flow" state="{state}" r:id="s"/></sheets></workbook>')
            z.writestr('xl/_rels/workbook.xml.rels',f'<Relationships xmlns="{P}"><Relationship Id="s" Target="worksheets/sheet1.xml"/></Relationships>')
            z.writestr('xl/worksheets/sheet1.xml',f'<worksheet xmlns="{M}" xmlns:r="{R}"><sheetData>{row}</sheetData><oleObjects>{obj}{obj if duplicate else ""}</oleObjects></worksheet>')
            z.writestr('xl/worksheets/_rels/sheet1.xml.rels',f'<Relationships xmlns="{P}"><Relationship Id="img" Target="../media/preview.emf" Type="{R}/image"'+(' TargetMode="External"' if external else '')+f'/><Relationship Id="vml" Target="../drawings/preview.vml" Type="{R}/vmlDrawing"/></Relationships>')
            shape=f'<v:shape id="_x0000_s42" style="{style}"><x:ClientData ObjectType="Pict"><x:Anchor>0,0,0,0,2,0,4,0</x:Anchor></x:ClientData></v:shape>' if vml else ''
            z.writestr('xl/drawings/preview.vml',f'<xml xmlns:v="urn:schemas-microsoft-com:vml" xmlns:x="urn:schemas-microsoft-com:office:excel">{shape}</xml>')
            z.writestr('xl/media/preview.emf',b'cached-preview')
    def test_visible(self):self.fixture();self.assertEqual(discover_previews(self.path)[0]['status'],'VISIBLE')
    def test_hidden_sheet(self):self.fixture(state='hidden');self.assertEqual(discover_previews(self.path),[])
    def test_very_hidden_sheet(self):self.fixture(state='veryHidden');self.assertEqual(discover_previews(self.path),[])
    def test_hidden_vml(self):self.fixture(style='visibility:hidden');self.assertEqual(discover_previews(self.path),[])
    def test_display_none(self):self.fixture(style='display:none');self.assertEqual(discover_previews(self.path),[])
    def test_partial_hidden_row(self):self.fixture(row='<row r="2" hidden="1"/>');self.assertEqual(discover_previews(self.path)[0]['status'],'REVIEW_REQUIRED')
    def test_zero_height_float(self):self.fixture(row='<row r="2" ht="0.0"/>');self.assertEqual(discover_previews(self.path)[0]['status'],'REVIEW_REQUIRED')
    def test_missing_vml(self):self.fixture(vml=False);self.assertEqual(discover_previews(self.path)[0]['status'],'REVIEW_REQUIRED')
    def test_duplicate(self):self.fixture(duplicate=True);self.assertEqual(len(discover_previews(self.path)),1)
    def test_external(self):self.fixture(external=True);self.assertEqual(discover_previews(self.path),[])
    def test_no_ole(self):self.fixture(ole=False);self.assertEqual(discover_previews(self.path),[])
if __name__=='__main__':unittest.main()
