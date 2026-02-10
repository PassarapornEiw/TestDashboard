"""
Base Library for Robot Framework
Contains shared functionality for configuration and settings management
"""
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

class BaseLibrary:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0'
    
    # ใช้ Class Variables เก็บ Cache เพื่อให้ทุก Instance ใช้ร่วมกันได้
    _settings_cache: Optional[Dict[str, Any]] = None
    _project_root: Optional[Path] = None

    def get_project_root(self) -> Path:
        """Get project root directory (Instance Method)"""
        if BaseLibrary._project_root is None:
            # ชี้ขึ้นไป 3 ระดับจาก Resources/pythonLib/base_library.py -> DRDB root
            BaseLibrary._project_root = Path(__file__).resolve().parent.parent.parent
        return BaseLibrary._project_root

    def load_settings(self, settings_path: str = "Environment/DRDB_Config.yaml") -> Dict[str, Any]:
        """Load settings from YAML file (cached)"""
        if BaseLibrary._settings_cache is not None:
            return BaseLibrary._settings_cache
        
        settings_file = self.resolve_path(settings_path)
        
        if not settings_file.exists():
            raise FileNotFoundError(f"Settings file not found: {settings_file}")
        
        with open(settings_file, 'r', encoding='utf-8') as f:
            BaseLibrary._settings_cache = yaml.safe_load(f)
        
        return BaseLibrary._settings_cache

    def get_setting(self, *keys: str, default: Any = None) -> Any:
        """Get nested setting value by keys"""
        value = self.load_settings()
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, default)
            else:
                return default
        return value

    def get_timeout(self) -> int:
        """Get timeout from settings"""
        return self.get_setting('LDP_environment', 'timeout', default=30)

    def get_implicit_wait(self) -> int:
        """Get implicit wait from settings"""
        return self.get_setting('LDP_environment', 'implicit_wait', default=10)

    def resolve_path(self, relative_path: str) -> Path:
        """Resolve relative path to absolute path from project root"""
        path = Path(relative_path)
        if path.is_absolute():
            return path
        return self.get_project_root() / relative_path

    def clear_cache(self) -> None:
        """Clear settings cache"""
        BaseLibrary._settings_cache = None