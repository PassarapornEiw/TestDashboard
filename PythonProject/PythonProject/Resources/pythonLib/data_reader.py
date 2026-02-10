import sys
from pathlib import Path
from typing import Dict, Any, Iterable, Optional
import re

# Ensure this directory is on path so base_library can be imported when loaded by path
_lib_dir = Path(__file__).resolve().parent
if str(_lib_dir) not in sys.path:
    sys.path.insert(0, str(_lib_dir))
from base_library import BaseLibrary
try:
    from xReader import excel  # type: ignore[import-untyped]
except ImportError:
    excel = None
try:
    from robot.api.decorators import keyword
except ImportError:
    def keyword(func):
        return func
from robot.libraries.BuiltIn import BuiltIn


class DataReader(BaseLibrary):
    """
    Robot Framework library สำหรับโหลดค่า config จาก *BaseLibrary* แล้วตั้งตัวแปรให้ใช้งานสะดวก

    แหล่งที่มาของคอนฟิก:
        - ใช้ BaseLibrary.load_settings(settings_path="Environment/DRDB_Config.yaml")
          (มี cache ให้อยู่แล้ว)

    Keywords หลัก:
        - Load All Sections From Settings         -> โหลดทุก section (หรือเฉพาะที่ระบุ)
        - Load Section From Settings               -> โหลดเฉพาะ section
        - Build Section Paths From Settings       -> สร้าง *_PATH ให้แต่ละคีย์ของ section
        - Get From Settings                       -> ดึงค่าด้วย dot path (เช่น Input_Test_Data.GDR_InputFileName)
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0'

    # ---------- internal helpers (ปรับเป็น instance methods เพื่อให้ Robot สแกนเจอได้ง่าย) ----------
    
    def _sanitize_key(self, text: str) -> str:
        """
        ทำให้ชื่อคีย์ปลอดภัยสำหรับชื่อตัวแปร Robot:
          - upper case
          - แทน non-alnum ด้วย '_'
          - ตัด '_' ต้น/ท้าย
          - ถ้าขึ้นต้นด้วยตัวเลข เติม '_' นำหน้า
        """
        up = str(text).upper()
        cleaned = re.sub(r"[^A-Z0-9]+", "_", up).strip("_")
        if re.match(r"^[0-9]", cleaned or ""):
            cleaned = "_" + cleaned
        return cleaned

    def _var_prefix(self, section_name: str, prefix: Optional[str]) -> str:
        return (prefix or self._sanitize_key(section_name))

    def _set_robot_var(self, name: str, value: Any, scope: str = "suite"):
        bi = BuiltIn()
        if scope.lower() == "global":
            bi.set_global_variable(f"${{{name}}}", value)
        else:
            bi.set_suite_variable(f"${{{name}}}", value)

    def _ensure_mapping_section(self, settings: Dict[str, Any], section: str) -> Dict[str, Any]:
        data = settings.get(section)
        if not isinstance(data, dict):
            raise KeyError(f"Section '{section}' not found or not a mapping in settings.")
        return data

    def _set_section_variables(
        self,
        section_name: str,
        section_dict: Dict[str, Any],
        prefix: Optional[str],
        scope: str = "suite",
    ):
        """ตั้งตัวแปรให้ Robot ทั้ง dict และ each key"""
        var_prefix = self._var_prefix(section_name, prefix)
        # dict ทั้งก้อน
        self._set_robot_var(var_prefix, section_dict, scope)
        # รายคีย์
        for k, v in section_dict.items():
            var_name = f"{var_prefix}_{self._sanitize_key(k)}"
            self._set_robot_var(var_name, v, scope)

    # ---------- public keywords ----------

    @keyword
    def load_section_from_settings(
        self,
        section: str = "Input_Test_Data",
        prefix: Optional[str] = None,
        scope: str = "suite",
        settings_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        โหลดเฉพาะ section จากไฟล์คอนฟิกของ BaseLibrary แล้วตั้งตัวแปร
        """
        settings = self.load_settings(settings_path) if settings_path else self.load_settings()
        section_dict = self._ensure_mapping_section(settings, section)
        self._set_section_variables(section, section_dict, prefix, scope)
        return section_dict

    @keyword
    def load_all_sections_from_settings(
        self,
        only_sections: Optional[Iterable[str]] = None,
        scope: str = "suite",
        settings_path: Optional[str] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        โหลดทุก top-level section (ที่เป็น dict) จากคอนฟิก แล้วตั้งตัวแปรให้หมด
        """
        settings = self.load_settings(settings_path) if settings_path else self.load_settings()
        loaded: Dict[str, Dict[str, Any]] = {}

        for sec, val in settings.items():
            if only_sections and sec not in only_sections:
                continue
            if isinstance(val, dict):
                self._set_section_variables(sec, val, None, scope)
                loaded[sec] = val

        if not loaded:
            raise ValueError("No dictionary-like sections found to load from settings.")
        return loaded

    @keyword
    def build_section_paths_from_settings(
        self,
        section: str = "Input_Test_Data",
        base_dir: str = ".",
        prefix: Optional[str] = None,
        suffix: str = "_PATH",
        scope: str = "suite",
        ensure_exists: bool = False,
        settings_path: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        สร้างตัวแปร PATH ให้คีย์ทุกตัวใน section โดยเอา base_dir มาต่อหน้า value
        """
        settings = self.load_settings(settings_path) if settings_path else self.load_settings()
        sec_dict = self._ensure_mapping_section(settings, section)

        var_prefix = self._var_prefix(section, prefix)
        base = self.resolve_path(base_dir)  # ใช้ของ BaseLibrary ให้ชี้จาก project root

        paths: Dict[str, str] = {}
        for k, v in sec_dict.items():
            if v is None:
                continue
            p = (base / str(v)).resolve()
            var_name = f"{var_prefix}_{self._sanitize_key(k)}{suffix}"
            self._set_robot_var(var_name, str(p), scope)
            paths[k] = str(p)
            if ensure_exists and not p.exists():
                raise FileNotFoundError(f"File not found for key '{k}': {p}")
        return paths

    @keyword
    def get_from_settings(
        self,
        dotted_path: str = "Input_Test_Data.GDR_InputFileName",
        default: Any = None,
        settings_path: Optional[str] = None,
    ) -> Any:
        """
        ดึงค่าแบบ dot path จากคอนฟิกของ BaseLibrary
        """
        # ใช้ get_setting ของ BaseLibrary
        parts = [p for p in dotted_path.split(".") if p]
        
        if settings_path:
            self.load_settings(settings_path)
            
        return self.get_setting(*parts, default=default)