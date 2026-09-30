"""Visible-only scope shared by readers and evaluators.

This module uses only the standard library. It inspects saved OOXML visibility;
it does not unhide, recalculate, or save the source workbook.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import posixpath
import re
from typing import Callable
from xml.etree import ElementTree as ET
from zipfile import ZipFile

M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"m": M}
MAX_PART = 25_000_000
EXCLUDED_NAMES = {"凡例", "変更履歴", "改訂履歴", "修正履歴",
                  "legend", "revision history", "change history", "changelog"}

def truth(value: str | None) -> bool:
    return str(value).lower() in {"1", "true"}

def is_zero(value: str | None) -> bool:
    if value is None:
        return False
    try:
        return float(value) == 0.0
    except ValueError:
        raise ValueError(f"Invalid dimension: {value!r}")

def coordinates(ref: str) -> tuple[int, int]:
    match = re.fullmatch(r"\$?([A-Za-z]+)\$?([1-9][0-9]*)", ref)
    if not match:
        raise ValueError(f"Invalid cell reference: {ref!r}")
    col = 0
    for ch in match[1].upper():
        col = col * 26 + ord(ch) - ord("A") + 1
    row = int(match[2])
    if row > 1048576 or col > 16384:
        raise ValueError("Cell reference outside Excel bounds.")
    return row, col

def safe_xml(data: bytes) -> ET.Element:
    if len(data) > MAX_PART:
        raise ValueError("OOXML part exceeds inspection limit.")
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError("DTD and entity declarations are not accepted.")
    return ET.fromstring(data)

@dataclass
class SheetScope:
    name: str
    state: str = "visible"
    reason: str | None = None
    default_rows_visible: bool = True
    default_columns_visible: bool = True
    rows: dict[int, bool] = field(default_factory=dict)
    columns: list[tuple[int, int, bool]] = field(default_factory=list)

    @property
    def included(self) -> bool:
        return self.state == "visible" and self.reason is None

    @classmethod
    def from_xml(cls, name: str, data: bytes | None,
                 state: str = "visible") -> "SheetScope":
        scope = cls(name=name, state=state)
        if state != "visible":
            scope.reason = "hidden-sheet"
            return scope
        if name.strip().casefold() in EXCLUDED_NAMES:
            scope.reason = "legend-or-history"
            return scope
        if data is None:
            raise ValueError(f"Missing visible worksheet XML: {name}")
        sheet = safe_xml(data)
        fmt = sheet.find("m:sheetFormatPr", NS)
        if fmt is not None:
            scope.default_rows_visible = not truth(fmt.get("zeroHeight"))
            scope.default_columns_visible = not is_zero(fmt.get("defaultColWidth"))
        for row in sheet.findall("m:sheetData/m:row", NS):
            r = int(row.get("r", "0"))
            if not 1 <= r <= 1048576:
                raise ValueError("Invalid row index.")
            visible = scope.default_rows_visible
            if row.get("hidden") is not None:
                visible = not truth(row.get("hidden"))
            if row.get("ht") is not None:
                visible = not is_zero(row.get("ht")) and not truth(row.get("hidden"))
            scope.rows[r] = visible
        for col in sheet.findall("m:cols/m:col", NS):
            lo, hi = int(col.get("min", "0")), int(col.get("max", "0"))
            if not 1 <= lo <= hi <= 16384:
                raise ValueError("Invalid column interval.")
            visible = scope.default_columns_visible
            if col.get("hidden") is not None:
                visible = not truth(col.get("hidden"))
            if col.get("width") is not None:
                visible = not is_zero(col.get("width")) and not truth(col.get("hidden"))
            scope.columns.append((lo, hi, visible))
        return scope

    def row_visible(self, row: int) -> bool:
        return self.included and self.rows.get(row, self.default_rows_visible)

    def column_visible(self, col: int) -> bool:
        if not self.included:
            return False
        result = self.default_columns_visible
        for lo, hi, visible in self.columns:
            if lo <= col <= hi:
                result = visible
        return result

    def cell_visible(self, ref: str) -> bool:
        row, col = coordinates(ref)
        return self.row_visible(row) and self.column_visible(col)

    def anchor_state(self, anchor: ET.Element) -> str:
        """Return visible, excluded, or review; never infer floating visibility."""
        d = "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"
        origin = anchor.find(f"{{{d}}}from")
        if origin is None:
            return "review"
        row = int(origin.findtext(f"{{{d}}}row", "0")) + 1
        col = int(origin.findtext(f"{{{d}}}col", "0")) + 1
        end = anchor.find(f"{{{d}}}to")
        if end is None or anchor.get("editAs", "twoCell") != "twoCell":
            return "visible" if self.row_visible(row) and self.column_visible(col) else "review"
        r2 = int(end.findtext(f"{{{d}}}row", "0")) + 1
        c2 = int(end.findtext(f"{{{d}}}col", "0")) + 1
        if int(end.findtext(f"{{{d}}}rowOff", "0")) == 0:
            r2 -= 1
        if int(end.findtext(f"{{{d}}}colOff", "0")) == 0:
            c2 -= 1
        if r2 < row or c2 < col:
            return "review"
        rv = [self.row_visible(r) for r in range(row, r2 + 1)]
        cv = [self.column_visible(c) for c in range(col, c2 + 1)]
        if not any(rv) or not any(cv):
            return "excluded"
        return "visible" if all(rv) and all(cv) else "review"

@dataclass
class WorkbookScope:
    sheets: dict[str, SheetScope]

    @classmethod
    def from_zip(cls, archive: ZipFile) -> "WorkbookScope":
        if len(archive.infolist()) > 10000 or sum(x.file_size for x in archive.infolist()) > 150_000_000:
            raise ValueError("Workbook exceeds inspection limit.")
        def read(name: str) -> bytes:
            if archive.getinfo(name).file_size > MAX_PART:
                raise ValueError(f"OOXML part too large: {name}")
            return archive.read(name)
        workbook = safe_xml(read("xl/workbook.xml"))
        rels = safe_xml(read("xl/_rels/workbook.xml.rels"))
        targets = {}
        for rel in rels:
            if rel.get("TargetMode") == "External":
                continue
            raw = rel.get("Target", "")
            path = raw.lstrip("/") if raw.startswith("/") else posixpath.normpath(posixpath.join("xl", raw))
            if path.startswith("../") or ":" in path:
                raise ValueError("Unsafe OOXML relationship.")
            targets[rel.get("Id")] = path
        sheets = {}
        for node in workbook.findall("m:sheets/m:sheet", NS):
            name = node.get("name", "")
            state = node.get("state", "visible")
            excluded = state != "visible" or name.strip().casefold() in EXCLUDED_NAMES
            data = None if excluded else read(targets[node.get("{" + R + "}id")])
            sheets[name] = SheetScope.from_xml(name, data, state)
        return cls(sheets)

    @classmethod
    def from_xlsx(cls, path: str | Path) -> "WorkbookScope":
        with ZipFile(path) as archive:
            return cls.from_zip(archive)

    def mask_loaded_workbook(self, workbook):
        """Clear hidden source content in a temporary in-memory reader only.

        Coordinates remain stable for existing renderers. Never save this reader
        back to the source file. The caller supplies its existing workbook loader.
        """
        for sheet in tuple(workbook.worksheets):
            scope = self.sheets[sheet.title]
            if not scope.included:
                workbook.remove(sheet)
                continue
            for row in sheet.iter_rows():
                for cell in row:
                    if scope.cell_visible(cell.coordinate):
                        continue
                    if cell.value is not None:
                        cell.value = None
                    if getattr(cell, "comment", None) is not None:
                        cell.comment = None
                    if getattr(cell, "hyperlink", None) is not None:
                        cell.hyperlink = None
        return workbook

def load_visible_workbook(path, *, loader: Callable, **kwargs):
    """Use a caller-provided loader; exclude hidden data before interpretation."""
    if kwargs.get("read_only"):
        raise ValueError("Visibility masking requires an in-memory reader.")
    scope = WorkbookScope.from_xlsx(path)
    workbook = loader(path, **kwargs)
    return scope.mask_loaded_workbook(workbook)
