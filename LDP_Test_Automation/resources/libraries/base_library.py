"""
Base Library for Robot Framework
Contains shared functionality for configuration and settings management
"""
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class BaseLibrary:
    """Base class with shared settings functionality"""
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0'
    
    _settings_cache: Optional[Dict[str, Any]] = None
    _project_root: Optional[Path] = None
    
    @classmethod
    def get_project_root(cls) -> Path:
        """Get project root directory"""
        if cls._project_root is None:
            cls._project_root = Path(__file__).parent.parent.parent
        return cls._project_root
    
    @classmethod
    def load_settings(cls, settings_path: str = "config/LDP_UI.yaml") -> Dict[str, Any]:
        """Load settings from YAML file (cached)"""
        if cls._settings_cache is not None:
            return cls._settings_cache
        
        settings_file = Path(settings_path)
        if not settings_file.is_absolute():
            settings_file = cls.get_project_root() / settings_path
        
        if not settings_file.exists():
            raise FileNotFoundError(f"Settings file not found: {settings_file}")
        
        with open(settings_file, 'r', encoding='utf-8') as f:
            cls._settings_cache = yaml.safe_load(f)
        
        return cls._settings_cache
    
    @classmethod
    def get_setting(cls, *keys: str, default: Any = None) -> Any:
        """Get nested setting value by keys"""
        settings = cls.load_settings()
        value = settings
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, default)
            else:
                return default
        return value
    
    @classmethod
    def get_base_url(cls) -> str:
        """Get base URL from settings"""
        return cls.get_setting('environment', 'base_url', default='')
    
    @classmethod
    def get_timeout(cls) -> int:
        """Get timeout from settings"""
        return cls.get_setting('environment', 'timeout', default=30)
    
    @classmethod
    def get_implicit_wait(cls) -> int:
        """Get implicit wait from settings"""
        return cls.get_setting('environment', 'implicit_wait', default=10)
    
    @classmethod
    def resolve_path(cls, relative_path: str) -> Path:
        """Resolve relative path to absolute path from project root"""
        path = Path(relative_path)
        if path.is_absolute():
            return path
        return cls.get_project_root() / relative_path
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear settings cache (useful for testing)"""
        cls._settings_cache = None
