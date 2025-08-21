import os
import glob
import pandas as pd
from flask import Flask, jsonify, render_template, abort, send_from_directory, request, send_file
from pathlib import Path
import webbrowser
from threading import Timer
import io
import tempfile
from datetime import datetime
import zipfile
import threading
import html
import re
import hashlib
import shutil

# Check for required dependencies

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.platypus import Image as ReportLabImage
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: ReportLab not installed. PDF export will be disabled.")
    REPORTLAB_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: Matplotlib not installed. Charts in PDF will be disabled.")
    MATPLOTLIB_AVAILABLE = False

try:
    from PIL import Image as PILImage, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: PIL/Pillow not installed. Image processing will be disabled.")
    PIL_AVAILABLE = False

# Optional: Playwright for HTML thumbnail rendering
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
    print("✅ Playwright available for HTML thumbnail generation")
except Exception as e:
    print("⚠️ Warning: Playwright not available. HTML thumbnail generation disabled.")
    print(f"   To enable: pip install playwright && playwright install chromium")
    PLAYWRIGHT_AVAILABLE = False

# Check if we have the minimum requirements for thumbnails
THUMBNAIL_CAPABLE = PIL_AVAILABLE or PLAYWRIGHT_AVAILABLE
if not THUMBNAIL_CAPABLE:
    print("❌ Warning: No thumbnail generation capability available!")
    print("   Install either PIL/Pillow or Playwright for thumbnail support")
else:
    print("✅ Thumbnail generation capability available")

app = Flask(__name__)

# --- Configuration ---
# The directory of this server script
SERVER_DIR = Path(__file__).parent.resolve()
# The project root is two levels up (from /Resources/Dashboard_Report)
PROJECT_ROOT = SERVER_DIR.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

# PDF font configuration (try Unicode CID fonts first, then fallback to local/system Thai TTFs)
PDF_FONT_NORMAL = 'Helvetica'
PDF_FONT_BOLD = 'Helvetica-Bold'

def setup_unicode_cid_fonts() -> bool:
    """Try to register Unicode CID fonts that support Thai without external TTF files."""
    global PDF_FONT_NORMAL, PDF_FONT_BOLD
    if not REPORTLAB_AVAILABLE:
        return False
    try:
        pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
        pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
        
        # IMPORTANT: Update global variables using globals() to ensure they persist
        globals()['PDF_FONT_NORMAL'] = 'HeiseiMin-W3'
        globals()['PDF_FONT_BOLD'] = 'HeiseiKakuGo-W5'
        
        print(f'[INFO] Using Unicode CID fonts: HeiseiMin-W3 / HeiseiKakuGo-W5')
        print(f'[DEBUG] Global vars updated: Normal={globals()["PDF_FONT_NORMAL"]}, Bold={globals()["PDF_FONT_BOLD"]}')
        
        return True
    except Exception as e:
        print(f'[WARN] Unicode CID fonts not available: {e}')
        return False

def _try_register_font(font_name: str, ttf_path: Path) -> bool:
    """Helper to register a font."""
    try:
        if ttf_path and ttf_path.exists():
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            pdfmetrics.registerFont(TTFont(font_name, str(ttf_path)))
            print(f"[REGISTERED] Font '{font_name}' from {ttf_path}")
            return True
    except Exception as e:
        print(f"[WARN] Could not register font {ttf_path}: {e}")
    return False

def verify_font_settings():
    """Verify current font settings."""
    print("\n" + "="*60)
    print("FONT VERIFICATION")
    print("="*60)
    print(f"PDF_FONT_NORMAL = {PDF_FONT_NORMAL}")
    print(f"PDF_FONT_BOLD = {PDF_FONT_BOLD}")
    
    if REPORTLAB_AVAILABLE:
        from reportlab.pdfbase import pdfmetrics
        
        # Check if fonts are registered
        try:
            # Try to get font info
            normal_font = pdfmetrics.getFont(PDF_FONT_NORMAL)
            bold_font = pdfmetrics.getFont(PDF_FONT_BOLD)
            print(f"✅ Normal font registered: {normal_font}")
            print(f"✅ Bold font registered: {bold_font}")
        except Exception as e:
            print(f"❌ Font not properly registered: {e}")
    
    # Check if Thai fonts
    is_thai = not (PDF_FONT_NORMAL == 'Helvetica' or PDF_FONT_BOLD == 'Helvetica-Bold')
    if is_thai:
        print("✅ Thai fonts are active")
    else:
        print("❌ Still using default Helvetica (no Thai support)")
    
    print("="*60 + "\n")
    return is_thai

def ensure_thai_fonts():
    """Ensure Thai fonts are available for PDF generation.

    This function now attempts to register built-in Unicode CID fonts (HeiseiMin/HeiseiKakuGo) before
    searching for external TTF files. If those CID fonts are available, the global font variables
    are updated and no further work is needed. Otherwise, it searches for common Thai fonts on the
    local filesystem and registers them. As a final fallback, it resets the fonts to Helvetica.
    """
    global PDF_FONT_NORMAL, PDF_FONT_BOLD

    # Bail out early if ReportLab isn't installed
    if not REPORTLAB_AVAILABLE:
        print("[ERROR] ReportLab not available!")
        return False

    # Keep the fonts if they've already been set to something other than the defaults
    if (PDF_FONT_NORMAL != 'Helvetica' and PDF_FONT_BOLD != 'Helvetica-Bold' and
        PDF_FONT_NORMAL != 'Helvetica-Bold' and PDF_FONT_BOLD != 'Helvetica'):
        print(f"✅ Thai fonts already loaded: {PDF_FONT_NORMAL}, {PDF_FONT_BOLD}")
        return True

    # Step 1: Look for Thai fonts first (local/system TTFs).
    candidates = [
        ("THSarabunNew", "THSarabunNew.ttf", "THSarabunNew-Bold", "THSarabunNew Bold.ttf"),
        ("THSarabunNew", "THSarabunNew.ttf", "THSarabunNew-Bold", "THSarabunNew-Bold.ttf"),
        ("Sarabun", "Sarabun-Regular.ttf", "Sarabun-Bold", "Sarabun-Bold.ttf"),
        ("NotoSansThai", "NotoSansThai-Regular.ttf", "NotoSansThai-Bold", "NotoSansThai-Bold.ttf"),
    ]
    
    search_dirs = [
        SERVER_DIR / 'fonts',
        PROJECT_ROOT / 'fonts',
        Path('C:/Windows/Fonts'),
        Path('/usr/share/fonts'),
        Path('/usr/local/share/fonts'),
        Path('/System/Library/Fonts'),
        Path.home() / '.fonts',
    ]
    
    print(f"[INFO] Searching for Thai fonts in: {[str(d) for d in search_dirs if d.exists()]}")
    
    for family_name, normal_file, bold_name, bold_file in candidates:
        normal_path = None
        bold_path = None
        
        for d in search_dirs:
            if not d.exists():
                continue
                
            if not normal_path:
                p = d / normal_file
                if p.exists():
                    normal_path = p
                    print(f"[FOUND] Normal font: {normal_path}")
            
            if not bold_path:
                p = d / bold_file
                if p.exists():
                    bold_path = p
                    print(f"[FOUND] Bold font: {bold_path}")
                # Try without space
                elif not bold_path:
                    alt_bold = d / bold_file.replace(" ", "")
                    if alt_bold.exists():
                        bold_path = alt_bold
                        print(f"[FOUND] Bold font (alt): {bold_path}")
        
        if normal_path and bold_path:
            norm_reg_name = f"{family_name}-Regular"
            bold_reg_name = f"{family_name}-Bold"
            
            if _try_register_font(norm_reg_name, normal_path) and \
               _try_register_font(bold_reg_name, bold_path):
                # IMPORTANT: Set the global variables using globals() to ensure they persist
                globals()['PDF_FONT_NORMAL'] = norm_reg_name
                globals()['PDF_FONT_BOLD'] = bold_reg_name
                
                print(f"[SUCCESS] ✅ Registered Thai fonts: {family_name}")
                print(f"  Normal: {globals()['PDF_FONT_NORMAL']} -> {normal_path}")
                print(f"  Bold: {globals()['PDF_FONT_BOLD']} -> {bold_path}")
                
                # Double check the values
                print(f"[VERIFY] Global vars: Normal={globals()['PDF_FONT_NORMAL']}, Bold={globals()['PDF_FONT_BOLD']}")
                
                return True
    
    # If still no Thai fonts found locally, try built-in CID fonts as a fallback.
    try:
        if setup_unicode_cid_fonts():
            return True
    except Exception as e:
        print(f"⚠️ Could not register CID fonts: {e}")

    # If nothing works, warn and keep Helvetica (no Thai support)
    print("[WARNING] ⚠️ No Thai fonts found! Using Helvetica (no Thai support)")
    return False

def escape_html_for_pdf(text):
    """
    Safely escape HTML/XML characters for use in ReportLab Paragraphs.
    Also handles very long text by adding soft breaks.
    Specially optimized for Thai text and very long content (10,000+ characters).
    """
    if not text or text in ['nan', 'none', '', 'None']:
        return ''
    
    # Convert to string and strip
    text = str(text).strip()
    
    # Log text statistics for debugging
    text_length = len(text)
    has_thai = any(ord(c) > 127 for c in text)
    print(f"[DEBUG] Processing text for PDF: length={text_length}, has_non_ascii={has_thai}")
    
    # For extremely long text (>10,000 chars), truncate with warning
    if text_length > 10000:
        print(f"[WARNING] Very long text detected ({text_length} chars), truncating to 10,000 characters")
        text = text[:10000] + "... [เนื้อหาถูกตัดทอนเนื่องจากมีความยาวมาก]"
    
    # Escape HTML/XML characters
    text = html.escape(text)
    
    # Handle very long lines by adding soft breaks
    # Use shorter line length for Thai text as it tends to be more dense
    max_line_length = 80 if has_thai else 100
    
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        if len(line) > max_line_length:
            # For Thai text, break more frequently as word boundaries are harder to detect
            if has_thai:
                # Break Thai text every 80 characters regardless of word boundaries
                for i in range(0, len(line), max_line_length):
                    chunk = line[i:i + max_line_length]
                    processed_lines.append(chunk)
            else:
                # For English text, try to preserve word boundaries
                words = line.split(' ')
                current_line = []
                current_length = 0
                
                for word in words:
                    if current_length + len(word) + 1 > max_line_length and current_line:
                        processed_lines.append(' '.join(current_line))
                        current_line = [word]
                        current_length = len(word)
                    else:
                        current_line.append(word)
                        current_length += len(word) + 1
                
                if current_line:
                    processed_lines.append(' '.join(current_line))
        else:
            processed_lines.append(line)
    
    result = '<br/>'.join(processed_lines)
    print(f"[DEBUG] Text processing completed: original_length={text_length}, processed_length={len(result)}, lines={len(processed_lines)}")
    return result

# --- Helper Functions ---
def sanitize_filename(name: str, replacement: str = "_") -> str:
    """Return a filesystem and header safe filename.
    Removes characters invalid on Windows or HTTP headers and collapses repeats.
    """
    if name is None:
        return "file"
    text = str(name)
    # Remove path separators and illegal characters: \\/:*?"<>| and control chars
    illegal_chars = "\\/:*?\"<>|\r\n\t"
    for ch in illegal_chars:
        text = text.replace(ch, replacement)
    # Also guard against commas and semicolons in headers
    for ch in [',', ';']:
        text = text.replace(ch, replacement)
    # Collapse repeats of replacement
    while replacement * 2 in text:
        text = text.replace(replacement * 2, replacement)
    text = text.strip().strip('.')
    return text or "file"
def is_valid_timestamp_folder(folder_name):
    """Check if folder name is a valid timestamp format (YYYYMMDD-HHMMSS or YYYYMMDD_HHMMSS)."""
    if len(folder_name) != 15:
        return False
    
    # Check for valid separators at position 8
    if folder_name[8] not in ['-', '_']:
        return False
    
    # Check if date and time parts are digits
    date_part = folder_name[:8]
    time_part = folder_name[9:]
    
    return date_part.isdigit() and time_part.isdigit()

def extract_timestamp_from_path(path_obj):
    """Extract timestamp from path, keeping original format."""
    try:
        # Try path parts first
        for part in path_obj.parts:
            if is_valid_timestamp_folder(part):
                return part  # Keep original format
        
        # Try filename parts if not found in path
        filename_parts = path_obj.stem.split('_')
        for part in filename_parts:
            if is_valid_timestamp_folder(part):
                return part  # Keep original format
                
        return "unknown"
    except Exception as e:
        print(f"Error extracting timestamp from {path_obj}: {e}")
        return "unknown"



def find_excel_files(base_dir):
    """Finds all relevant feature excel files in valid timestamp directories only."""
    try:
        if not base_dir.exists() or not base_dir.is_dir():
            print(f"Results directory not found: {base_dir}")
            return []
        
        valid_excel_paths = []
        
        # Iterate through direct subdirectories of results
        for item in base_dir.iterdir():
            if item.is_dir():
                # Only process directories with valid timestamp format
                if is_valid_timestamp_folder(item.name):
                    print(f"[DEBUG] Processing valid timestamp folder: {item.name}")
                    # Search for .xlsx files in this valid timestamp directory
                    excel_paths = glob.glob(str(item / "**" / "*.xlsx"), recursive=True)
                    valid_excel_paths.extend(excel_paths)
                else:
                    print(f"[DEBUG] Ignoring invalid timestamp folder: {item.name}")
        
        return sorted(valid_excel_paths, reverse=True)
    except Exception as e:
        print(f"Error finding Excel files: {e}")
        return []

def safe_str_lower(series):
    """Safely convert series to lowercase, handling NaN values."""
    try:
        if hasattr(series, 'fillna'):
            return series.fillna('').astype(str).str.lower()
        else:
            return pd.Series(series).fillna('').astype(str).str.lower()
    except Exception:
        return pd.Series(series).fillna('').astype(str).str.lower()

def find_first_column(headers, candidates):
    """Return the first column name found from candidates list (case-sensitive as Excel provides), or None."""
    for name in candidates:
        if name in headers:
            return name
    return None

def filter_executed_rows(df):
    """Return DataFrame filtered by Execute == 'Y' if column exists; otherwise original df."""
    try:
        execute_column = next((c for c in df.columns if c.lower() == 'execute'), None)
        if execute_column:
            temp = df.copy()
            temp[execute_column] = temp[execute_column].fillna('')
            return temp[temp[execute_column].astype(str).str.lower() == 'y'].copy()
        return df
    except Exception:
        return df

def get_row_by_id(df, id_candidates, target_id):
    """Return the row that matches target_id using the first available id column. Exact match only; None if not found."""
    id_col = find_first_column(df.columns, id_candidates)
    if not id_col:
        return None
    for _, row in df.iterrows():
        row_id = str(row.get(id_col, '')).strip()
        if row_id == str(target_id).strip():
            return row
    return None

def get_test_case_description(excel_path, test_case_id):
    """
    Extracts test case description from Excel file based on test case ID.
    Returns the description or None if not found.
    """
    try:
        if not Path(excel_path).exists():
            print(f"Excel file not found: {excel_path}")
            return None
            
        df = pd.read_excel(excel_path)
        try:
            print(f"[DEBUG][Excel Load] path={excel_path} rows={len(df)} cols={len(df.columns)} headers={list(df.columns)}")
        except Exception:
            pass
        
        if df.empty:
            return None
        
        # Look for test case ID column (common variations)
        id_columns = ['Test Case ID', 'TestCaseID', 'Test Case', 'ID', 'TestCase', 'TestCaseNo']
        id_col = None
        for col in id_columns:
            if col in df.columns:
                id_col = col
                break
        
        # Look for description column (common variations) - do NOT use 'Name' (often holds ID)
        desc_columns = ['Test Case Description', 'TestCaseDescription', 'Description', 'Test Description', 'Scenario', 'Title']
        desc_col = None
        for col in desc_columns:
            if col in df.columns:
                desc_col = col
                break
        
        if id_col and desc_col:
            # Normalize for matching
            test_case_id_str = str(test_case_id).strip()
            df[id_col] = df[id_col].fillna('').astype(str)
            norm_series = df[id_col].str.strip().str.casefold()
            target = test_case_id_str.casefold()

            # 1) Exact match first (case-insensitive)
            exact_mask = norm_series == target
            if exact_mask.any():
                row = df[exact_mask].iloc[0]
                desc_value = row.get(desc_col, '')
                return str(desc_value) if pd.notna(desc_value) and str(desc_value).strip() else None

            # 2) Fuzzy fallback: startswith id (e.g., TC001_1234)
            starts_mask = norm_series.str.startswith(target + '_') | norm_series.str.startswith(target + '-')
            if starts_mask.any():
                row = df[starts_mask].iloc[0]
                desc_value = row.get(desc_col, '')
                return str(desc_value) if pd.notna(desc_value) and str(desc_value).strip() else None
        
        return None
    except Exception as e:
        print(f"Error getting test case description for {test_case_id} from {excel_path}: {e}")
        return None

def parse_excel_data(excel_path):
    """
    Parses a single feature's Excel file to extract summary data.
    Returns a dictionary with summary, or None on error.
    """
    try:
        excel_path_obj = Path(excel_path)
        if not excel_path_obj.exists():
            print(f"Excel file not found: {excel_path}")
            return None
            
        df = pd.read_excel(excel_path)
        
        if df.empty:
            print(f"Empty Excel file: {excel_path}")
            return None
        
        # Check for different possible column names for test results
        status_column = None
        for col_name in ['TestResult', 'Status', 'Result']:
            if col_name in df.columns:
                status_column = col_name
                break
        
        if not status_column:
            print(f"No status column found in {excel_path}. Available columns: {df.columns.tolist()}")
            
            # Extract timestamp even for files without status column
            run_timestamp = extract_timestamp_from_path(excel_path_obj)
            
            # For files without status column, create a basic summary with 0 counts
            return {
                "feature_name": excel_path_obj.stem,
                "excel_path": str(excel_path_obj.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "total": 0,
                "passed": 0,
                "failed": 0,
                "pass_rate": 0,
                "status": "not_run",
                "run_timestamp": run_timestamp,
                "test_evidence": {},
                "image_files": []
            }

        # Filter for rows that should be executed
        execute_column = None
        for col in df.columns:
            if col.lower() == 'execute':
                execute_column = col
                break
                
        # Use common filter helper
        executable_df = filter_executed_rows(df)
        try:
            print(f"[DEBUG][Execute Filter] execute_col={execute_column} before={len(df)} after={len(executable_df)}")
        except Exception:
            pass

        if executable_df.empty:
            print(f"No executable tests found in {excel_path}")
            return None

        # Count passed and failed tests from the executable set (case insensitive)
        # Handle potential empty cells in status column gracefully
        executable_df = executable_df.copy()
        if status_column in executable_df.columns:
            executable_df[status_column] = executable_df[status_column].fillna('')
            status_lower = safe_str_lower(executable_df[status_column])
        else:
            status_lower = pd.Series(dtype=str)
        
        # Only count tests that have Execute = 'Y' AND TestResult is either 'pass' or 'fail'
        # Tests with empty/null/other status values should not be counted in total
        pass_mask = status_lower == 'pass'
        fail_mask = status_lower == 'fail'
        
        passed = int(pass_mask.sum())
        failed = int(fail_mask.sum())
        total = passed + failed
        try:
            print(f"[DEBUG][Status Count] status_col={status_column} total={total} passed={passed} failed={failed}")
        except Exception:
            pass
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        # Determine status: only "passed" if there are actually executed tests with valid results and no failures
        if total == 0:
            status = "not_run"  # No tests were executed with valid pass/fail results
        elif failed == 0:
            status = "passed"   # All valid tests passed
        else:
            status = "failed"   # Some valid tests failed
        
        # Find associated evidence files recursively in the feature directory and subdirectories
        excel_dir = excel_path_obj.parent  # This should be the feature folder (e.g., Transfer/)
        evidence_paths = []
        try:
            # Search for images, HTML, and Excel files in the feature directory and all subdirectories (TC001, TC002, etc.)
            evidence_patterns = ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.html", "*.htm", "*.xlsx", "*.xls"]
            for ext in evidence_patterns:
                evidence_paths.extend(list(excel_dir.glob(f"**/{ext}")))
            
            print(f"[DEBUG] Found {len(evidence_paths)} evidence files in {excel_dir}")
            for evidence in evidence_paths[:5]:  # Show first 5 for debugging
                print(f"[DEBUG] Evidence found: {evidence}")
                
        except Exception as e:
            print(f"Error searching for evidence files in {excel_dir}: {e}")
            evidence_paths = []
        
        # Group evidence files by test case (subfolder under feature)
        test_evidence = {}
        for evidence_path in evidence_paths:
            try:
                # The test case folder is the immediate parent of the evidence file, relative to the feature folder
                relative_path = evidence_path.relative_to(excel_dir)
                if len(relative_path.parts) > 1:
                    test_case_name = relative_path.parts[0]  # First level folder under feature (TC001, TC002, etc.)
                else:
                    test_case_name = "General" # Fallback for evidence files in the root of the feature folder
                
                # Convert to path relative to project root for serving
                if PROJECT_ROOT in evidence_path.parents:
                    relative_evidence_path = str(evidence_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
                    if test_case_name not in test_evidence:
                        test_evidence[test_case_name] = []
                    test_evidence[test_case_name].append(relative_evidence_path)
                    print(f"[DEBUG] Added evidence file to {test_case_name}: {relative_evidence_path}")
                else:
                    print(f"Evidence path not within project root: {evidence_path}")
                    
            except Exception as e:
                print(f"Could not process evidence path {evidence_path}: {e}")
                continue
                
        print(f"[DEBUG] Final test_evidence: {test_evidence}")
        
        # Extract run timestamp from directory path
        run_timestamp = extract_timestamp_from_path(excel_path_obj)
        print(f"[DEBUG] Extracted timestamp: {run_timestamp}")
        
        # Extract feature name from folder structure (e.g., results/20250620_111221/Transfer/...)
        feature_name = excel_path_obj.stem  # Default fallback
        try:
            path_parts = excel_path_obj.parts
            # Look for pattern: results/timestamp/feature_folder/...
            for i, part in enumerate(path_parts):
                # Use the same validation function for timestamp folders
                if is_valid_timestamp_folder(part):
                    # Found valid timestamp folder, next folder should be feature name
                    if i + 1 < len(path_parts):
                        feature_name = path_parts[i + 1]  # Use folder name as feature name
                        print(f"[DEBUG] Extracted feature name from folder: {feature_name} (from valid timestamp: {part})")
                        break
        except Exception as e:
            print(f"Error extracting feature name from path: {e}")
            
        return {
            "feature_name": feature_name,
            "excel_path": str(excel_path_obj.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(pass_rate, 2),
            "status": status,
            "run_timestamp": run_timestamp,
            "test_evidence": test_evidence,
            "evidence_files": [str(p.relative_to(PROJECT_ROOT)).replace("\\", "/") for p in evidence_paths if PROJECT_ROOT in p.parents], # Keep for fallback
        }
    except Exception as e:
        print(f"Error parsing Excel data from {excel_path}: {e}")
        return None

# --- Routes ---
@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/api/data")
def get_dashboard_data():
    try:
        all_excel_files = find_excel_files(RESULTS_DIR)
        
        # Group by run timestamp
        runs = {}
        for excel_file in all_excel_files:
            feature_data = parse_excel_data(excel_file)
            # Only include features that have been executed (total > 0)
            if feature_data and feature_data.get("total", 0) > 0:
                timestamp = feature_data["run_timestamp"]
                if timestamp not in runs:
                    runs[timestamp] = {
                        "timestamp": timestamp,
                        "features": []
                    }
                runs[timestamp]["features"].append(feature_data)
        
        # Sort runs by timestamp (most recent first)
        sorted_runs = sorted(runs.values(), key=lambda x: x["timestamp"], reverse=True)
        
        return jsonify({
            "runs": sorted_runs,
            "total_runs": len(sorted_runs)
        })
    except Exception as e:
        print(f"Error in get_dashboard_data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/excel_preview")
def excel_preview():
    """Preview Excel file content for debugging."""
    try:
        excel_path = request.args.get('path')
        if not excel_path:
            return jsonify({"error": "No path provided"}), 400
            
        full_path = PROJECT_ROOT / excel_path
        if not full_path.exists():
            return jsonify({"error": f"File not found: {excel_path}"}), 404
            
        df = pd.read_excel(full_path)
        
        # Convert to JSON-serializable format with correct field names
        rows_data = df.fillna('').astype(str).to_dict('records')
        preview_data = {
            "headers": df.columns.tolist(),  # JavaScript expects 'headers'
            "rows": rows_data,               # JavaScript expects 'rows'
            "total_rows": len(df)
        }
        
        return jsonify(preview_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export_pdf', methods=['POST'])
def export_pdf():
    """Export test results to PDF with enhanced formatting and optional screenshots."""
    if not REPORTLAB_AVAILABLE:
        return jsonify({'error': 'PDF download not available. ReportLab not installed.'}), 500
        
    try:
        options = request.get_json()
        if not options:
            return jsonify({'error': 'No options provided'}), 400
            
        scope = options.get('scope', 'latest')
        include_screenshots = options.get('include_screenshots', True)
        include_details = options.get('include_details', True)
        include_summary = options.get('include_summary', True)
        start_date = options.get('start_date')
        end_date = options.get('end_date')
        selected_features = options.get('features', [])

        # Gather all runs with unique feature identification
        all_excel_files = find_excel_files(RESULTS_DIR)
        runs = {}
        seen_features = set()  # Track unique features to prevent duplicates
        
        for excel_file in all_excel_files:
            feature_data = parse_excel_data(excel_file)
            if feature_data and feature_data["total"] > 0:  # Filter out NOT RUN features
                ts = feature_data["run_timestamp"]
                feature_key = f"{ts}_{feature_data['feature_name']}"
                
                # Skip if we've already seen this feature in this run
                if feature_key in seen_features:
                    continue
                    
                seen_features.add(feature_key)
                
                if ts not in runs:
                    runs[ts] = {"timestamp": ts, "features": []}
                runs[ts]["features"].append(feature_data)
                
        sorted_runs = sorted(runs.values(), key=lambda r: r["timestamp"], reverse=True)

        # Filter runs/features based on scope
        if scope == "latest":
            runs_to_export = [sorted_runs[0]] if sorted_runs else []
        elif scope == "features":
            runs_to_export = []
            for run in sorted_runs:
                filtered_features = [f for f in run["features"] if f["feature_name"] in selected_features]
                if filtered_features:
                    runs_to_export.append({"timestamp": run["timestamp"], "features": filtered_features})
        elif scope == "date_range":
            runs_to_export = [run for run in sorted_runs if (not start_date or run["timestamp"] >= start_date) and (not end_date or run["timestamp"] <= end_date)]
        else:
            runs_to_export = sorted_runs

        # Calculate overall metrics
        total_tests = sum(f['total'] for run in runs_to_export for f in run['features'])
        passed_tests = sum(f['passed'] for run in runs_to_export for f in run['features'])
        failed_tests = sum(f['failed'] for run in runs_to_export for f in run['features'])
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        overall_status = "PASSED" if failed_tests == 0 else "FAILED"

        # Prepare PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()
        elements = []

        # Custom styles with banking brand theme - Updated font sizes for better readability
        title_style = styles['Title'].clone('BrandTitleStyle')
        title_style.fontSize = 20  # Increased from 18pt to 20pt for better readability
        title_style.spaceAfter = 25
        title_style.textColor = colors.HexColor("#8B4513")
        title_style.fontName = PDF_FONT_BOLD
        title_style.alignment = 1  # Center alignment
        
        # Banking professional heading style (Section headers)
        heading_style = styles['Heading1'].clone('BrandHeadingStyle')
        heading_style.fontSize = 16  # Increased from 14pt to 16pt for better readability
        heading_style.spaceAfter = 15
        heading_style.textColor = colors.HexColor("#8B4513")  # Deep brown-gold
        heading_style.fontName = PDF_FONT_BOLD
        heading_style.borderWidth = 1
        heading_style.borderColor = colors.HexColor("#D4AF37")
        heading_style.borderPadding = 8
        heading_style.backColor = colors.HexColor("#FFF8DC")
        
        # Subheading style with golden accent
        subheading_style = styles['Heading2'].clone('BrandSubheadingStyle')
        subheading_style.fontSize = 14  # Increased from 12pt to 14pt for better readability
        subheading_style.spaceAfter = 12
        subheading_style.textColor = colors.HexColor("#DAA520")  # Golden rod
        subheading_style.fontName = PDF_FONT_BOLD
        subheading_style.alignment = 1  # Center alignment
        subheading_style.borderWidth = 0
        subheading_style.borderColor = colors.HexColor("#D4AF37")
        subheading_style.borderPadding = 5
        
        # Custom feature name style (Subsection headers)
        feature_style = styles['Heading2'].clone('FeatureStyle')
        feature_style.fontSize = 14  # Increased from 12pt to 14pt for better readability
        feature_style.spaceAfter = 15
        feature_style.textColor = colors.HexColor("#B8860B")
        feature_style.fontName = PDF_FONT_BOLD
        feature_style.leftIndent = 5
        feature_style.borderWidth = 1
        feature_style.borderColor = colors.HexColor("#D4AF37")
        feature_style.borderPadding = 8
        feature_style.backColor = colors.HexColor("#FFFACD")
        
        # Professional normal text style (Test case descriptions, etc.)
        normal_style = styles['Normal'].clone('BrandNormalStyle')
        normal_style.fontSize = 12  # Increased from 10pt to 12pt for better readability
        normal_style.textColor = colors.HexColor("#2F4F4F")
        normal_style.fontName = PDF_FONT_NORMAL
        normal_style.leading = 12  # 1.2x line spacing (10pt * 1.2 = 12pt)
        
        # Create caption style for screenshot counts (9pt Regular as requested)
        caption_style = styles['Normal'].clone('CaptionStyle')
        caption_style.fontSize = 11  # Increased from 9pt to 11pt for better readability
        caption_style.textColor = colors.HexColor("#666666")
        caption_style.fontName = PDF_FONT_NORMAL
        caption_style.leading = 11  # 1.2x line spacing (9pt * 1.2 = 11pt)

        # === HEADER SECTION WITH BANKING BRAND ===
        # Create gradient-style title section
        title_table = Table([
            [Paragraph("TEST AUTOMATION REPORT", title_style)],
            [Paragraph("Krungsri Automation Project", subheading_style)]
        ], colWidths=[500])
        title_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFF8DC")),
            ('LINEBELOW', (0,0), (-1,-1), 3, colors.HexColor("#D4AF37")),
            ('LINEABOVE', (0,0), (-1,-1), 3, colors.HexColor("#B8860B")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 20),
            ('BOTTOMPADDING', (0,0), (-1,-1), 20),
            ('LEFTPADDING', (0,0), (-1,-1), 40),
            ('RIGHTPADDING', (0,0), (-1,-1), 40),
        ]))
        elements.append(title_table)
        elements.append(Spacer(1, 25))
        
        # Professional report metadata with golden borders
        metadata_data = [
            ["Execution Time:", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ["Total Features:", str(sum(len(run['features']) for run in runs_to_export))],
        ]
        
        metadata_table = Table(metadata_data, colWidths=[140, 220])
        metadata_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), PDF_FONT_BOLD),
            ('FONTSIZE', (0,0), (-1,-1), 9),  # Reduced to 9pt for metadata
            ('ALIGN', (0,0), (0,-1), 'RIGHT'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor("#8B4513")),
            ('TEXTCOLOR', (1,0), (1,-1), colors.HexColor("#2F4F4F")),
            ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor("#D4AF37")),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFEF7")),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#D4AF37")),
            ('TOPPADDING', (0,0), (-1,-1), 6),  # Improved padding
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('LEADING', (0,0), (-1,-1), 11),  # 1.2x line spacing (9pt * 1.2 = 11pt)
        ]))
        elements.append(metadata_table)
        elements.append(Spacer(1, 25))

        # === EXECUTIVE SUMMARY ===
        if include_summary:
            elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
            elements.append(Spacer(1, 15))
            
            # Create horizontal summary table with proper borders and header separation
            summary_table_data = [
                # Header row
                ["Total Tests", "Passed", "Failed", "Pass Rate"],
                # Data row  
                [str(total_tests), str(passed_tests), str(failed_tests), f"{pass_rate:.2f}%"]
            ]
            
            # Create professional horizontal summary table with enhanced styling
            summary_table = Table(summary_table_data, colWidths=[105, 105, 105, 105])
            summary_table.setStyle(TableStyle([
                # Header styling - matches other tables
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#8B4513")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), PDF_FONT_BOLD),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                
                # Data row styling with color coding
                ('FONTNAME', (0,1), (-1,1), PDF_FONT_BOLD),
                ('FONTSIZE', (0,1), (-1,1), 14),
                ('ALIGN', (0,1), (-1,1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                
                # Color coding for data values
                ('TEXTCOLOR', (0,1), (0,1), colors.HexColor("#2F4F4F")),   # Total Tests (dark gray)
                ('TEXTCOLOR', (1,1), (1,1), colors.HexColor("#228B22")),   # Passed (green)
                ('TEXTCOLOR', (2,1), (2,1), colors.HexColor("#CD5C5C")),   # Failed (red)
                ('TEXTCOLOR', (3,1), (3,1), colors.HexColor("#DAA520")),   # Pass Rate (gold)
                
                # Enhanced borders with Krungsri golden theme
                ('BOX', (0,0), (-1,-1), 2, colors.HexColor("#D4AF37")),
                ('INNERGRID', (0,0), (-1,-1), 1, colors.HexColor("#D4AF37")),
                ('LINEBELOW', (0,0), (-1,0), 2, colors.HexColor("#B8860B")),  # Clear header separator
                
                # Background colors for data row
                ('BACKGROUND', (0,1), (0,1), colors.HexColor("#F5F5F5")),   # Total Tests bg
                ('BACKGROUND', (1,1), (1,1), colors.HexColor("#E8F5E8")),   # Passed bg
                ('BACKGROUND', (2,1), (2,1), colors.HexColor("#FFEBEE")),   # Failed bg
                ('BACKGROUND', (3,1), (3,1), colors.HexColor("#FFF3E0")),   # Pass Rate bg
                
                # Enhanced padding for better appearance
                ('TOPPADDING', (0,0), (-1,0), 8),      # Header padding
                ('BOTTOMPADDING', (0,0), (-1,0), 8),   # Header padding
                ('TOPPADDING', (0,1), (-1,1), 12),     # Data row padding (larger for emphasis)
                ('BOTTOMPADDING', (0,1), (-1,1), 12),  # Data row padding
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 25))

            # Charts (only if matplotlib is available)
            if MATPLOTLIB_AVAILABLE:
                # Professional pie chart with banking color scheme
                if passed_tests > 0 or failed_tests > 0:
                    # Only include labels and values that are greater than 0
                    pie_labels = []
                    pie_sizes = []
                    pie_colors = []
                    
                    if passed_tests > 0:
                        pie_labels.append('Passed')
                        pie_sizes.append(passed_tests)
                        pie_colors.append('#228B22')  # Forest green
                    
                    if failed_tests > 0:
                        pie_labels.append('Failed')
                        pie_sizes.append(failed_tests)
                        pie_colors.append('#CD5C5C')  # Indian red
                    
                    # Create perfectly circular pie chart
                    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect="equal"))
                    pie_result = ax.pie(pie_sizes, labels=pie_labels, colors=pie_colors, 
                                        autopct='%1.2f%%', startangle=90, 
                                        textprops={'color':'#2F4F4F', 'fontweight':'bold', 'fontsize':10})
                    
                    # Add golden border to pie chart
                    wedges = pie_result[0]
                    for wedge in wedges:
                        wedge.set_edgecolor('#D4AF37')
                        wedge.set_linewidth(2)
                    
                    # Set title with simpler text
                    ax.set_title('TEST RESULT', fontsize=14, fontweight='bold', color='#8B4513', pad=20)
                    
                    # Ensure perfect circle
                    ax.axis('equal')
                    
                    pie_buf = io.BytesIO()
                    plt.savefig(pie_buf, format='png', bbox_inches='tight', transparent=True, dpi=200, 
                               facecolor='#FFFEF7', pad_inches=0.1)
                    plt.close(fig)  # Properly close the figure
                    pie_buf.seek(0)
                    
                    elements.append(ReportLabImage(pie_buf, width=70*mm, height=70*mm))
                    elements.append(Spacer(1, 15))



        # === FEATURE RESULTS SUMMARY ===
        elements.append(PageBreak())  # Start Feature Results on a new page
        elements.append(Paragraph("FEATURE TEST RESULTS", heading_style))
        elements.append(Spacer(1, 15))
        
        # Collect unique features to prevent duplicates
        unique_features = {}
        for run in runs_to_export:
            for feature in run['features']:
                # Ensure test_evidence present for this feature by re-parsing if needed
                try:
                    if not feature.get('test_evidence'):
                        reparsed = parse_excel_data(PROJECT_ROOT / feature['excel_path'])
                        if reparsed and reparsed.get('test_evidence'):
                            feature['test_evidence'] = reparsed['test_evidence']
                except Exception:
                    pass
                feature_key = f"{feature['feature_name']}_{run['timestamp']}"
                if feature_key not in unique_features:
                    unique_features[feature_key] = feature
        
        if unique_features:
            # Create table data with Paragraph objects for better text wrapping
            feature_table_data = [["Feature", "Status", "Total\nExecuted", "Passed", "Failed", "Pass\nRate"]]
            
            # Create cell styles for different column types
            feature_name_style = normal_style.clone('FeatureNameStyle')
            feature_name_style.fontSize = 11
            feature_name_style.fontName = PDF_FONT_BOLD
            feature_name_style.textColor = colors.HexColor("#8B4513")
            feature_name_style.alignment = 0  # Left align
            
            status_style = normal_style.clone('StatusStyle')
            status_style.fontSize = 11
            status_style.fontName = PDF_FONT_BOLD
            status_style.alignment = 1  # Center align
            
            number_style = normal_style.clone('NumberStyle')
            number_style.fontSize = 11
            number_style.alignment = 1  # Center align
            
            # Add data rows with simple string formatting (avoids Paragraph type issues)
            for feature in unique_features.values():
                # Status without icons - clean text only
                if feature['status'] == 'passed':
                    status_display = 'PASSED'
                elif feature['status'] == 'failed':
                    status_display = 'FAILED'
                else:
                    status_display = 'NOT RUN'
                
                feature_table_data.append([
                    feature["feature_name"],
                    status_display,
                    str(feature["total"]),
                    str(feature["passed"]),
                    str(feature["failed"]),
                    f'{feature["pass_rate"]:.2f}%'
                ])
            
            # Create professional table with flexible column widths
            feature_results_table = Table(feature_table_data, 
                                        colWidths=[100, 70, 70, 50, 50, 60], 
                                        repeatRows=1)
            
            # Create enhanced table style with better text handling
            feature_table_style = [
                # Header styling with golden theme
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#8B4513")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                # ส่วนหัวของตารางควรใช้ฟอนต์ตัวหนาที่รองรับภาษาไทย
                ('FONTNAME', (0,0), (-1,0), PDF_FONT_BOLD),
                ('FONTSIZE', (0,0), (-1,0), 11),  # เพิ่มจาก 9 เป็น 11 เพื่อให้อ่านง่ายขึ้น
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                
                # Data rows styling with proper alignment
                ('FONTNAME', (0,1), (-1,-1), PDF_FONT_NORMAL),
                ('FONTSIZE', (0,1), (-1,-1), 11),  # เพิ่มจาก 9 เป็น 11 เพื่อให้อ่านง่ายขึ้น
                ('ALIGN', (0,1), (0,-1), 'LEFT'),    # Feature names left-aligned
                ('ALIGN', (1,1), (1,-1), 'CENTER'),  # Status centered
                ('ALIGN', (2,1), (-1,-1), 'CENTER'), # Numbers centered
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                
                # Feature column bold font for consistency
                ('FONTNAME', (0,1), (0,-1), PDF_FONT_BOLD),
                
                # Enhanced borders with Krungsri golden theme
                ('BOX', (0,0), (-1,-1), 2, colors.HexColor("#D4AF37")),
                ('INNERGRID', (0,0), (-1,-1), 1, colors.HexColor("#D4AF37")),
                ('LINEBELOW', (0,0), (-1,0), 2, colors.HexColor("#B8860B")),
                
                # Alternating row colors
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFEF7"), colors.HexColor("#FFF8DC")]),
                
                # Text colors for specific columns
                ('TEXTCOLOR', (0,1), (0,-1), colors.HexColor("#8B4513")),  # Feature names
                ('TEXTCOLOR', (2,1), (2,-1), colors.HexColor("#2F4F4F")),  # Total tests
                ('TEXTCOLOR', (3,1), (3,-1), colors.HexColor("#228B22")),  # Passed (green)
                ('TEXTCOLOR', (4,1), (4,-1), colors.HexColor("#CD5C5C")),  # Failed (red)
                ('TEXTCOLOR', (5,1), (5,-1), colors.HexColor("#DAA520")),  # Pass rate
                
                # Enhanced padding for better readability
                ('TOPPADDING', (0,0), (-1,0), 6),      # Header padding reduced
                ('BOTTOMPADDING', (0,0), (-1,0), 6),   # Header padding reduced
                ('TOPPADDING', (0,1), (-1,-1), 8),     # Data rows padding
                ('BOTTOMPADDING', (0,1), (-1,-1), 8),  # Data rows padding
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ]
            
            # Add status-specific colors for status column
            feature_list = list(unique_features.values())
            for row_idx, feature in enumerate(feature_list, start=1):
                if feature['status'] == 'passed':
                    status_color = colors.HexColor("#228B22")
                elif feature['status'] == 'failed':
                    status_color = colors.HexColor("#CD5C5C")
                else:
                    status_color = colors.HexColor("#666666")
                
                feature_table_style.append(('TEXTCOLOR', (1, row_idx), (1, row_idx), status_color))
            
            feature_results_table.setStyle(TableStyle(feature_table_style))
            elements.append(feature_results_table)
        else:
            elements.append(Paragraph("No feature test results available.", normal_style))
        
        elements.append(Spacer(1, 25))

        # === FAILED TEST CASES (Only if there are failures) ===
        failed_cases = []
        processed_features = set()  # Track processed features to prevent duplicates
        
        for run in runs_to_export:
            for feature in run['features']:
                feature_key = f"{feature['feature_name']}_{run['timestamp']}"
                if feature['failed'] > 0 and feature_key not in processed_features:
                    processed_features.add(feature_key)
                    excel_path = PROJECT_ROOT / feature['excel_path']
                    if excel_path.exists():
                        try:
                            df = pd.read_excel(excel_path)
                            
                            # Find relevant columns
                            status_col = next((c for c in df.columns if c.lower() in ['testresult', 'status', 'result']), None)
                            name_col = next((c for c in df.columns if c.lower() in ['testcasedescription', 'test case description', 'testcase', 'name']), None)
                            if not name_col:
                                name_col = df.columns[0]
                            
                            error_col = next((c for c in df.columns if c.lower() in ['fail_description', 'testresult_description', 'result description', 'error', 'message', 'failure reason']), None)
                            
                            # Filter for executed tests only
                            df = filter_executed_rows(df)

                            # (Removed: not needed in failed cases section)
                            
                            # Find failed test cases
                            if status_col:
                                failed_df = df[df[status_col].str.lower() == 'fail']
                                for _, row in failed_df.iterrows():
                                    # Get error message and add proper spacing
                                    error_msg = str(row.get(error_col, "No error message")) if error_col else "No error message"
                                    
                                    failed_cases.append([
                                        str(feature['feature_name']),
                                        str(row.get(name_col, "")),
                                        str(error_msg)
                                    ])
                        except Exception as e:
                            print(f"Error processing failed cases for {feature['feature_name']}: {e}")

        if failed_cases:
            elements.append(Paragraph("FAILED TEST CASES DETAILS", heading_style))
            elements.append(Spacer(1, 15))
            
            # Create cell styles for failed cases table
            failed_feature_style = normal_style.clone('FailedFeatureStyle')
            failed_feature_style.fontSize = 8
            failed_feature_style.fontName = PDF_FONT_BOLD
            failed_feature_style.textColor = colors.HexColor("#8B4513")
            failed_feature_style.alignment = 0  # Left align
            
            failed_testcase_style = normal_style.clone('FailedTestCaseStyle')
            failed_testcase_style.fontSize = 8
            failed_testcase_style.textColor = colors.HexColor("#2F4F4F")
            failed_testcase_style.alignment = 0  # Left align
            
            failed_error_style = normal_style.clone('FailedErrorStyle')
            failed_error_style.fontSize = 8
            failed_error_style.textColor = colors.HexColor("#B71C1C")
            failed_error_style.alignment = 0  # Left align
            
            # Create table data with Paragraph objects for better text wrapping
            failed_table_data = [["Feature", "Test Case", "Fail Description"]]
            
            for case in failed_cases:
                # Truncate long text to prevent table overflow
                feature_name = str(case[0])[:20] + "..." if len(str(case[0])) > 20 else str(case[0])
                test_case_name = str(case[1])[:30] + "..." if len(str(case[1])) > 30 else str(case[1])
                error_msg = str(case[2])[:50] + "..." if len(str(case[2])) > 50 else str(case[2])
                
                # Create Paragraph objects with smaller font sizes
                feature_style = normal_style.clone('FeatureWrapStyle')
                feature_style.fontSize = 8
                feature_style.textColor = colors.HexColor("#8B4513")
                feature_style.fontName = PDF_FONT_BOLD
                feature_para = Paragraph(feature_name, feature_style)
                
                # Test case with smaller font
                test_case_style = normal_style.clone('TestCaseWrapStyle')
                test_case_style.fontSize = 8
                test_case_style.leading = 10  # Reduced line spacing
                test_case_style.textColor = colors.HexColor("#2F4F4F")
                test_case_para = Paragraph(test_case_name, test_case_style)
                
                # Fail description with smaller font
                fail_desc_style = normal_style.clone('FailDescWrapStyle') 
                fail_desc_style.fontSize = 8
                fail_desc_style.textColor = colors.HexColor("#B71C1C")
                fail_desc_style.leading = 10
                fail_desc_para = Paragraph(error_msg, fail_desc_style)
                
                failed_table_data.append([feature_para, test_case_para, fail_desc_para])
            
            # Create failed cases table with improved column widths and better size management
            # Use smaller column widths to prevent overflow
            failed_table = Table(failed_table_data, colWidths=[70, 150, 140], repeatRows=1)
            failed_table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#8B4513")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                # ส่วนหัวของตารางควรใช้ฟอนต์ตัวหนาที่รองรับภาษาไทย
                ('FONTNAME', (0,0), (-1,0), PDF_FONT_BOLD),
                ('FONTSIZE', (0,0), (-1,0), 10),  # เพิ่มจาก 8 เป็น 10 เพื่อให้อ่านง่ายขึ้น
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                
                # Data rows styling with smaller font size
                ('FONTNAME', (0,1), (-1,-1), PDF_FONT_NORMAL),
                ('FONTSIZE', (0,1), (-1,-1), 10),  # เพิ่มจาก 8 เป็น 10 เพื่อให้อ่านง่ายขึ้น
                ('ALIGN', (0,1), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                
                # Professional borders and colors
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#D4AF37")),  # Reduced border width
                ('INNERGRID', (0,0), (-1,-1), 1, colors.HexColor("#D4AF37")),
                ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor("#B8860B")),  # Reduced border width
                
                # Alternating row colors
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFEF7"), colors.HexColor("#FFF8DC")]),
                
                # Reduced padding to save space
                ('TOPPADDING', (0,0), (-1,0), 6),      # Header padding
                ('BOTTOMPADDING', (0,0), (-1,0), 6),   # Header padding
                ('TOPPADDING', (0,1), (-1,-1), 6),     # Data rows - reduced padding
                ('BOTTOMPADDING', (0,1), (-1,-1), 6),  # Data rows - reduced padding
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ]))
            
            # Add table with page break handling
            try:
                elements.append(failed_table)
            except Exception as table_error:
                print(f"Table overflow error, trying to split: {table_error}")
                # If table is too large, try to split it into smaller chunks
                elements.append(Paragraph("FAILED TEST CASES (Table too large, showing summary only)", heading_style))
                for i, case in enumerate(failed_cases[:5]):  # Show only first 5 cases
                    elements.append(Paragraph(f"• {case[0]}: {case[1]}", normal_style))
                if len(failed_cases) > 5:
                    elements.append(Paragraph(f"... and {len(failed_cases) - 5} more failed cases", normal_style))
            elements.append(Spacer(1, 25))

        # === SCREENSHOTS SECTION (Optional) ===
        if include_screenshots:
            elements.append(PageBreak())  # Start screenshots on new page
            elements.append(Paragraph("TEST EVIDENCE SCREENSHOTS", heading_style))
            elements.append(Spacer(1, 15))
            
            for run in runs_to_export:
                for feature in run['features']:
                    elements.append(Paragraph(f"Feature: {feature['feature_name']}", feature_style))
                    elements.append(Spacer(1, 10))
                    
                    # Get Excel file path for this feature to extract test case descriptions and status
                    excel_path = PROJECT_ROOT / feature['excel_path']
                    df = None
                    if excel_path.exists():
                        try:
                            df = pd.read_excel(excel_path)
                            # Filter for executed tests only
                            df = filter_executed_rows(df)
                        except Exception as e:
                            df = None
                    
                    if df is not None and not df.empty:
                        # Get test case ID column
                        id_columns = ['Test Case ID', 'TestCaseID', 'Test Case', 'ID', 'TestCase', 'TestCaseNo', 'Name']
                        id_col = next((col for col in id_columns if col in df.columns), None)
                        status_columns = ['TestResult', 'Status', 'Result']
                        status_col = next((col for col in status_columns if col in df.columns), None)
                        
                        if id_col and status_col:
                            # Loop through Excel test cases instead of screenshot folders
                            for _, row in df.iterrows():
                                test_case = str(row[id_col]).strip()
                                test_case_status = str(row[status_col]).strip().upper()
                                
                                # Skip if test case is empty or status is not PASS/FAIL
                                if not test_case or test_case.lower() in ['nan', 'none', '']:
                                    continue
                                if test_case_status not in ['PASS', 'FAIL']:
                                    continue
                                
                                # Find matching screenshot folder for this Excel test case
                                images = []
                                actual_folder_name = test_case
                                
                                if feature.get('test_evidence'):
                                    # Try exact match first
                                    if test_case in feature['test_evidence']:
                                        images = feature['test_evidence'][test_case]
                                        actual_folder_name = test_case
                                    else:
                                        # Try fuzzy matching: find folders that start with test_case + "_"
                                        # e.g., "TC001" matches folder "TC001_52224444444"
                                        for folder_name, folder_images in feature['test_evidence'].items():
                                            if folder_name.startswith(test_case + '_') or folder_name == test_case:
                                                images = folder_images
                                                actual_folder_name = folder_name
                                                break
                                
                                # Create test case header with status
                                status_str = f" <font color='#28a745'>[PASS]</font>" if test_case_status == "PASS" else \
                                             f" <font color='#dc3545'>[FAIL]</font>" if test_case_status == "FAIL" else ""
                                
                                test_case_style = styles['Heading4'].clone('TestCaseStyle')
                                test_case_style.fontSize = 12
                                test_case_style.spaceAfter = 10
                                test_case_style.textColor = colors.HexColor("#B8860B")
                                test_case_style.fontName = PDF_FONT_BOLD
                                test_case_style.leftIndent = 5
                                test_case_style.borderWidth = 1
                                test_case_style.borderColor = colors.HexColor("#D4AF37")
                                test_case_style.borderPadding = 6
                                test_case_style.backColor = colors.HexColor("#FFFEF7")
                                
                                elements.append(Paragraph(f"Test Case: {actual_folder_name}{status_str}", test_case_style))
                                
                                # Get and display test case description from Excel file
                                test_case_description = get_test_case_description(excel_path, test_case)
                                if test_case_description:
                                    elements.append(Paragraph(f"<b>Description:</b> {test_case_description}", normal_style))
                                    elements.append(Spacer(1, 8))
                                else:
                                    elements.append(Paragraph("<b>Description:</b> No description available", normal_style))
                                    elements.append(Spacer(1, 8))
                                
                                # Add failure reason for failed test cases
                                if test_case_status == "FAIL":
                                    try:
                                        # Find error column
                                        error_col = None
                                        for col in df.columns:
                                            if col.lower() in ['fail_description', 'testresult_description', 'result description', 'error', 'message', 'failure reason']:
                                                error_col = col
                                                break
                                        
                                        if error_col:
                                            error_msg = str(row[error_col]).strip()
                                            if error_msg and error_msg.lower() not in ['nan', 'none', '']:
                                                # Create custom style for error message
                                                error_style = styles['Normal'].clone('ErrorStyle')
                                                error_style.fontSize = 10
                                                error_style.textColor = colors.HexColor("#dc3545")
                                                error_style.fontName = PDF_FONT_BOLD
                                                error_style.leftIndent = 12
                                                error_style.rightIndent = 12
                                                error_style.spaceBefore = 8
                                                error_style.spaceAfter = 8
                                                error_style.backColor = colors.HexColor("#FFEBEE")
                                                error_style.borderColor = colors.HexColor("#dc3545")
                                                error_style.borderWidth = 1
                                                error_style.borderPadding = 8
                                                error_style.borderRadius = 4
                                                
                                                elements.append(Paragraph(f"<b><font color='#B71C1C'>❌ Failure Reason:</font></b><br/><font color='#D32F2F'>{error_msg}</font>", error_style))
                                                elements.append(Spacer(1, 8))
                                    except Exception as e:
                                        print(f"Error getting failure reason for {actual_folder_name}: {e}")
                                
                                                                # Handle screenshots and HTML files
                                if images:
                                    # Show all screenshots, not just PDF ones
                                    all_images = images
                                    
                                    elements.append(Paragraph(f"Total Evidence Files: {len(all_images)}", caption_style))
                                    elements.append(Spacer(1, 8))
                                    
                                    # --- High-quality image grid with original resolution and captions ---
                                    if all_images:
                                        # Process images one by one to maintain original resolution
                                        for img_path in all_images:
                                            img_abs = PROJECT_ROOT / img_path
                                            if img_abs.exists():
                                                try:
                                                    # Get filename for caption
                                                    img_filename = img_path.split('/')[-1]
                                                    file_extension = img_path.lower().split('.')[-1] if '.' in img_path else ''
                                    
                                                    # Check if this is an HTML file
                                                    if file_extension in ['html', 'htm']:
                                                        # Convert HTML to image for PDF display with full page capture
                                                        print(f"[DEBUG] Converting HTML to image: {img_path}")
                                                        reportlab_img = create_html_preview_image(img_abs, max_width=500, max_height=400, full_page=True)
                                                        
                                                        if reportlab_img:
                                                            pdf_width = reportlab_img.imageWidth
                                                            pdf_height = reportlab_img.imageHeight
                                                            print(f"[DEBUG] HTML converted successfully. Dimensions: {pdf_width}x{pdf_height}")
                                                        else:
                                                            # Fallback: create placeholder for HTML
                                                            print(f"[DEBUG] HTML conversion failed, creating placeholder")
                                                            if PIL_AVAILABLE:
                                                                placeholder_img = PILImage.new("RGB", (500, 400), color=(245, 247, 250))
                                                                draw = ImageDraw.Draw(placeholder_img)
                                                                try:
                                                                    font = ImageFont.load_default()
                                                                except Exception:
                                                                    font = None
                                                                
                                                                # Draw placeholder text
                                                                draw.text((20, 200), "HTML Preview", fill=(64, 64, 64), font=font)
                                                                draw.text((20, 230), img_filename[:50], fill=(96, 96, 96), font=font)
                                                                
                                                                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_img:
                                                                    placeholder_img.save(temp_img.name, format='JPEG', quality=75)
                                                                    reportlab_img = ReportLabImage(temp_img.name, width=500, height=400)
                                                                    pdf_width, pdf_height = 500, 400
                                                                    
                                                                    # Clean up temp file
                                                                    try:
                                                                        os.unlink(temp_img.name)
                                                                    except:
                                                                        pass
                                                            else:
                                                                # If PIL not available, create text placeholder
                                                                elements.append(Paragraph(f"<b>HTML File:</b> {img_filename}", normal_style))
                                                                elements.append(Paragraph("(HTML preview not available - PIL/Pillow required)", caption_style))
                                                                elements.append(Spacer(1, 10))
                                                                continue
                                                    else:
                                                        # Regular image file processing
                                                        # Use PIL Image to process, ReportLab Image for PDF
                                                        if PIL_AVAILABLE:
                                                            with PILImage.open(str(img_abs)) as pil_img:
                                                                # Get original dimensions
                                                                original_width, original_height = pil_img.size
                                                                
                                                                # Calculate maximum dimensions for PDF (maintain aspect ratio)
                                                                max_width_pdf = 500  # Maximum width in points
                                                                max_height_pdf = 400  # Maximum height in points
                                                                
                                                                # Calculate scaling factor to maintain aspect ratio
                                                                width_ratio = max_width_pdf / original_width
                                                                height_ratio = max_height_pdf / original_height
                                                                scale_ratio = min(width_ratio, height_ratio)
                                                                
                                                                # Calculate final dimensions for PDF
                                                                pdf_width = original_width * scale_ratio
                                                                pdf_height = original_height * scale_ratio
                                                                
                                                                # Convert to RGB if necessary and save with high quality
                                                                if pil_img.mode in ('RGBA', 'LA', 'P'):
                                                                    rgb_img = PILImage.new('RGB', pil_img.size, (255, 255, 255))
                                                                    if pil_img.mode == 'P':
                                                                        pil_img = pil_img.convert('RGBA')
                                                                    rgb_img.paste(pil_img, mask=pil_img.split()[-1] if pil_img.mode in ('RGBA', 'LA') else None)
                                                                    pil_img = rgb_img
                                                                
                                                                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_img:
                                                                    pil_img.save(temp_img.name, format='JPEG', quality=75, optimize=True, dpi=(150, 150))
                                                                    # Use original resolution with calculated PDF dimensions
                                                                    reportlab_img = ReportLabImage(temp_img.name, width=pdf_width, height=pdf_height)
                                                                    
                                                                    # Clean up temp file
                                                                    try:
                                                                        os.unlink(temp_img.name)
                                                                    except:
                                                                        pass
                                                        else:
                                                            # Fallback: use original image with moderate dimensions
                                                            reportlab_img = ReportLabImage(str(img_abs), width=400, height=300)
                                                            pdf_width, pdf_height = 400, 300
                                                    
                                                    # Create image with caption
                                                    file_type_label = "HTML File" if file_extension in ['html', 'htm'] else "Screenshot"
                                                    img_with_caption = [
                                                        [reportlab_img],
                                                        [Paragraph(f"<b>{file_type_label}:</b> {img_filename}", caption_style)]
                                                    ]
                                                    
                                                    # Create table for image and caption
                                                    img_table = Table(img_with_caption, colWidths=[pdf_width])
                                                    img_table.setStyle(TableStyle([
                                                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                                        ('LEFTPADDING', (0,0), (-1,-1), 0),
                                                        ('RIGHTPADDING', (0,0), (-1,-1), 0),
                                                        ('TOPPADDING', (0,0), (-1,0), 10),  # Image padding
                                                        ('BOTTOMPADDING', (0,0), (-1,0), 5),  # Image padding
                                                        ('TOPPADDING', (0,1), (-1,1), 5),   # Caption padding
                                                        ('BOTTOMPADDING', (0,1), (-1,1), 15), # Caption padding
                                                    ]))
                                                    
                                                    elements.append(img_table)
                                                    elements.append(Spacer(1, 10))
                                                    
                                                except Exception as e:
                                                    print(f"Error processing file {img_path}: {e}")
                                                    elements.append(Paragraph(f"Error loading file: {img_path}", normal_style))
                                                    elements.append(Spacer(1, 10))
                                            else:
                                                elements.append(Paragraph(f"File not found: {img_path}", normal_style))
                                                elements.append(Spacer(1, 10))
                                    else:
                                        elements.append(Paragraph("No evidence files available for this test case.", caption_style))
                                else:
                                    # No matching evidence folder found - show "No evidence found"
                                    elements.append(Paragraph("Evidence Files: No evidence found", caption_style))
                                
                                elements.append(Spacer(1, 20))
                    else:
                        elements.append(Paragraph("No test case data available from Excel file.", normal_style))
                    
                    # Add page break between features for better organization
                    elements.append(PageBreak())

        # === FOOTER ===
        # Create footer style (8pt Regular as requested)
        footer_style = styles['Normal'].clone('FooterStyle')
        footer_style.fontSize = 10  # Increased from 8pt to 10pt for better readability
        footer_style.textColor = colors.HexColor("#666666")
        footer_style.fontName = PDF_FONT_NORMAL  # Use Thai font
        footer_style.leading = 10  # 1.25x line spacing (8pt * 1.25 = 10pt)
        footer_style.alignment = 1  # Center alignment
        
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("_______________________________________________", footer_style))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Generated by: Test Automation Dashboard v1.0", footer_style))
        elements.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
        elements.append(Paragraph("Confidential - For Internal Use Only", footer_style))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"DRDB_TestReport_{timestamp}.pdf"
        
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')
        
    except Exception as e:
        print(f"PDF Export Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def generate_test_case_pdf_core(test_case_id, feature_name, run_timestamp, feature_data, test_case_row):
    """Core PDF generation logic - reusable for both individual and ZIP downloads.
    Robust to both pandas.Series and dict rows.
    """
    try:
        # Normalize access helpers (support pandas Series or dict)
        try:
            available_fields = list(getattr(test_case_row, 'index', getattr(test_case_row, 'keys', lambda: [])()))
        except Exception:
            available_fields = []

        def row_get(key, default=None):
            try:
                if key is None:
                    return default
                # Use mapping-style get when available
                if hasattr(test_case_row, 'get'):
                    return test_case_row.get(key, default)
                # Fallback for Series without .get
                return test_case_row[key] if key in available_fields else default
            except Exception:
                return default

        def pick_col(candidates):
            for c in candidates:
                if c in available_fields:
                    return c
            return None

        # Get test case information
        desc_columns = ['Test Case Description', 'TestCaseDescription', 'Description', 'Test Description', 'Name']
        desc_col = pick_col(desc_columns)
        status_columns = ['TestResult', 'Status', 'Result']
        status_col = pick_col(status_columns)
        error_columns = ['Fail_Description', 'Fail Description', 'TestResult Description', 'Result Description', 'Error', 'Message', 'Failure Reason']
        error_col = pick_col(error_columns)
        expected_result_columns = ['ExpectedResult', 'Expected Result', 'Expected', 'Expected Outcome']
        expected_result_col = pick_col(expected_result_columns)

        try:
            print(f"[DEBUG][Row Mapping] test_case_id={test_case_id} available_fields={list(available_fields)}")
            print(f"[DEBUG][Row Mapping] chosen -> desc_col={desc_col}, status_col={status_col}, error_col={error_col}, expected_result_col={expected_result_col}")
        except Exception:
            pass
        
        # Get screenshots for this test case and find folder name
        screenshots = []
        folder_name_for_title = None
        
        if feature_data.get('test_evidence'):
            # First priority: Look for exact match
            if test_case_id in feature_data['test_evidence']:
                screenshots = feature_data['test_evidence'][test_case_id]
                folder_name_for_title = test_case_id
            else:
                # Second priority: Look for fuzzy match
                for folder_name, folder_images in feature_data['test_evidence'].items():
                    if folder_name.startswith(test_case_id + '_') or folder_name == test_case_id:
                        screenshots = folder_images
                        folder_name_for_title = folder_name
                        break
        
        # Extract test case information with correct separation
        # 1. Title: Use folder name from screenshot folder (as requested)
        # 2. Test Case Description: Use Excel data (separate field)
        
        # Get title from folder name (for header)
        if folder_name_for_title and folder_name_for_title != test_case_id:
            if folder_name_for_title.startswith(test_case_id + '_'):
                title_name = folder_name_for_title[len(test_case_id + '_'):]  # Use "225522422" for title
            else:
                title_name = folder_name_for_title
        else:
            title_name = test_case_id  # fallback to ID if no folder
        
        # Get Test Case Description from Excel (separate field)
        test_case_description = str(row_get(desc_col, test_case_id))
        if not test_case_description or test_case_description.lower() in ['nan', 'none', '']:
            test_case_description = test_case_id  # fallback to ID if no description
        
        # Use title_name for header, test_case_description for description field
        test_case_name = title_name  # This will be used for the title

        status_raw = row_get(status_col, 'UNKNOWN')
        test_case_status = str(status_raw).strip().upper() if status_raw is not None else 'UNKNOWN'
        error_val = row_get(error_col, '')
        error_message = str(error_val) if error_val is not None else ''
        expected_val = row_get(expected_result_col, '')
        expected_result = str(expected_val) if expected_val is not None else ''

        try:
            print(f"[DEBUG][Row Values] name='{test_case_name}' status='{test_case_status}' has_error={bool(error_message)} has_expected={bool(expected_result)}")
        except Exception:
            pass

        # Generate PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        elements = []

        # Custom styles
        title_style = styles['Title'].clone('TestCaseTitleStyle')
        title_style.fontSize = 18
        title_style.spaceAfter = 20
        title_style.textColor = colors.HexColor("#8B4513")
        title_style.fontName = PDF_FONT_BOLD
        title_style.alignment = 1
        
        header_style = styles['Heading1'].clone('TestCaseHeaderStyle')
        header_style.fontSize = 16
        header_style.spaceAfter = 15
        header_style.textColor = colors.HexColor("#8B4513")
        header_style.fontName = PDF_FONT_BOLD
        
        normal_style = styles['Normal'].clone('TestCaseNormalStyle')
        normal_style.fontSize = 12
        normal_style.textColor = colors.HexColor("#2F4F4F")
        normal_style.fontName = PDF_FONT_NORMAL
        normal_style.leading = 12

        caption_style = styles['Normal'].clone('TestCaseCaptionStyle')
        caption_style.fontSize = 11
        caption_style.textColor = colors.HexColor("#666666")
        caption_style.fontName = PDF_FONT_NORMAL
        caption_style.leading = 11
        caption_style.alignment = 1

        # Header - Use folder name as priority  
        safe_title = escape_html_for_pdf(f"{test_case_id}: {test_case_name}")
        elements.append(Paragraph(safe_title, title_style))
        
        # Status
        if test_case_status == "PASS":
            status_color = colors.HexColor("#28a745")
            status_bg_color = colors.HexColor("#d4edda")
        elif test_case_status == "FAIL":
            status_color = colors.HexColor("#dc3545")
            status_bg_color = colors.HexColor("#f8d7da")
        else:
            status_color = colors.HexColor("#6c757d")
            status_bg_color = colors.HexColor("#e2e3e5")
            
        status_style = styles['Normal'].clone('StatusStyle')
        status_style.fontSize = 14  # ลดขนาดลงเล็กน้อยเพื่อให้ข้อความพอดี
        status_style.fontName = PDF_FONT_BOLD
        status_style.textColor = status_color
        status_style.alignment = 1
        status_style.borderWidth = 2
        status_style.borderColor = status_color
        status_style.borderPadding = 12  # ลด padding ลงเล็กน้อย
        status_style.backColor = status_bg_color
        
        # Make status badge take the full content width so we can match the metadata table width
        content_width = A4[0] - doc.leftMargin - doc.rightMargin
        status_table = Table(
            [[Paragraph(f"Test Result: {test_case_status}", status_style)]],
            colWidths=[content_width]
        )
        status_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        elements.append(status_table)
        elements.append(Spacer(1, 20))
        
        # Metadata
        metadata_data = [
            ["Execution Date & Time:", format_timestamp_professional(run_timestamp)],
            ["Feature Category:", feature_name],
            ["Test Case ID:", test_case_id]
        ]
        
        if test_case_description and test_case_description != test_case_id:
            metadata_data.append(["Test Case Description:", test_case_description])
        
        if expected_result and expected_result.strip() and expected_result.lower() not in ['nan', 'none', '']:
            metadata_data.append(["Expected Result:", expected_result])

        # Move Fail_Description outside the table to prevent a single very-tall row
        fail_desc_text = None
        if error_message and error_message.strip() and error_message.lower() not in ['nan', 'none', '']:
            fail_desc_text = error_message
        
        # Build metadata rows with Paragraphs and CJK word wrapping to avoid overflow with long text
        label_style = styles['Normal'].clone('MetaLabelStyle')
        label_style.fontSize = 11  # เพิ่มจาก 9 เป็น 11 เพื่อให้อ่านง่ายขึ้น
        label_style.textColor = colors.HexColor("#8B4513")
        label_style.fontName = PDF_FONT_BOLD
        label_style.leading = 13  # เพิ่ม leading ให้เหมาะสมกับขนาดฟอนต์
        label_style.wordWrap = 'CJK'

        value_style = styles['Normal'].clone('MetaValueStyle')
        value_style.fontSize = 11  # เพิ่มจาก 9 เป็น 11 เพื่อให้อ่านง่ายขึ้น
        value_style.textColor = colors.HexColor("#2F4F4F")
        value_style.fontName = PDF_FONT_NORMAL
        value_style.leading = 13  # เพิ่ม leading ให้เหมาะสมกับขนาดฟอนต์
        value_style.wordWrap = 'CJK'

        metadata_rows = []
        for label, value in metadata_data:
            try:
                # Safely process both label and value text
                safe_label = escape_html_for_pdf(str(label))
                safe_value = escape_html_for_pdf(str(value))
                metadata_rows.append([
                    Paragraph(safe_label, label_style),
                    Paragraph(safe_value, value_style)
                ])
            except Exception as e:
                print(f"[ERROR] Failed to add metadata row '{label}': {e}")
                # Fallback to plain text
                metadata_rows.append([
                    Paragraph(str(label), label_style),
                    Paragraph(str(value).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;'), value_style)
                ])

        # Make table span the full content width (same as status badge)
        label_col_width = 160
        if content_width - label_col_width < 160:
            label_col_width = max(120, content_width * 0.33)
        value_col_width = content_width - label_col_width

        metadata_table = Table(metadata_rows, colWidths=[label_col_width, value_col_width])
        metadata_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (0,-1), PDF_FONT_BOLD),
            ('FONTNAME', (1,0), (1,-1), PDF_FONT_NORMAL),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (0,0), (0,-1), 'RIGHT'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor("#8B4513")),
            ('TEXTCOLOR', (1,0), (1,-1), colors.HexColor("#2F4F4F")),
            ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor("#D4AF37")),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFEF7")),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#D4AF37")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(metadata_table)
        elements.append(Spacer(1, 25))

        # Render long Fail_Description as a standalone paragraph block (can break across pages)
        if fail_desc_text is not None:
            try:
                error_style = styles['Normal'].clone('ErrorBlockStyle')
                error_style.fontSize = 11  # เพิ่มจาก 10 เป็น 11 เพื่อให้อ่านง่ายขึ้น
                error_style.textColor = colors.HexColor("#dc3545")
                # ใช้ฟอนต์ตัวหนาที่รองรับภาษาไทยแทนการฮาร์ดโค้ด Helvetica
                error_style.fontName = PDF_FONT_BOLD
                error_style.leftIndent = 6
                error_style.rightIndent = 6
                error_style.spaceBefore = 6
                error_style.spaceAfter = 12
                error_style.backColor = colors.HexColor("#FFEBEE")
                error_style.borderColor = colors.HexColor("#dc3545")
                error_style.borderWidth = 1
                error_style.borderPadding = 8
                error_style.borderRadius = 4
                error_style.leading = 14  # เพิ่ม leading จาก 12 เป็น 14 เพื่อเว้นบรรทัดเหมาะสม
                error_style.wordWrap = 'CJK'

                # Safely escape the text to prevent XML/HTML parsing errors
                print(f"[DEBUG] Processing Fail_Description for PDF (length: {len(fail_desc_text)} chars)")
                safe_fail_text = escape_html_for_pdf(fail_desc_text)
                print(f"[DEBUG] Escaped text length: {len(safe_fail_text)}")
                
                elements.append(Paragraph(f"<b>Fail_Description:</b><br/>{safe_fail_text}", error_style))
                elements.append(Spacer(1, 10))
                print(f"[DEBUG] Successfully added Fail_Description to PDF")
            except Exception as e:
                print(f"[ERROR] Failed to add Fail_Description to PDF: {e}")
                import traceback
                traceback.print_exc()
                
                # Fallback: Add as plain text without formatting
                try:
                    print(f"[DEBUG] Trying fallback method for Fail_Description")
                    fallback_style = styles['Normal'].clone('FallbackErrorStyle')
                    fallback_style.fontSize = 11  # เพิ่มจาก 9 เป็น 11 เพื่อให้อ่านง่ายขึ้น
                    fallback_style.textColor = colors.HexColor("#dc3545")
                    fallback_style.fontName = PDF_FONT_NORMAL
                    fallback_style.leading = 13  # เพิ่ม leading ให้เหมาะสมกับขนาดฟอนต์
                    fallback_style.wordWrap = 'CJK'
                    
                    # Remove any potentially problematic characters and truncate if extremely long
                    clean_text = re.sub(r'[<>&"\']', ' ', str(fail_desc_text))
                    if len(clean_text) > 5000:
                        clean_text = clean_text[:5000] + "... [ตัดทอนเนื่องจากข้อความยาวมาก]"
                    
                    elements.append(Paragraph(f"Fail_Description: {clean_text}", fallback_style))
                    elements.append(Spacer(1, 10))
                    print(f"[DEBUG] Fallback method succeeded")
                except Exception as e2:
                    print(f"[ERROR] Fallback Fail_Description also failed: {e2}")
                    import traceback
                    traceback.print_exc()
                    
                    # Last resort: Add a simple note
                    try:
                        simple_msg = f"Fail_Description: [ไม่สามารถแสดงข้อความได้เนื่องจากข้อความมีความยาว {len(str(fail_desc_text))} ตัวอักษร]"
                        elements.append(Paragraph(simple_msg, styles['Normal']))
                        elements.append(Spacer(1, 10))
                        print(f"[DEBUG] Added simplified error message")
                    except Exception as e3:
                        print(f"[ERROR] Even simple error message failed: {e3}")
                        # Skip this section entirely if all methods fail

        # Screenshots and HTML files (include all evidence, no limit)
        if screenshots:
            elements.append(PageBreak())  # Start evidence on new page
            elements.append(Paragraph("Test Evidence Files", header_style))
            elements.append(Spacer(1, 15))
            
            # Show all evidence files, not just screenshots, but limit to prevent huge files
            all_evidence = screenshots
            
            # Limit evidence files to prevent huge PDF files (max 20 files)
            if len(all_evidence) > 20:
                print(f"[WARNING] Too many evidence files ({len(all_evidence)}), limiting to 20")
                all_evidence = all_evidence[:20]
                
            if all_evidence:
                evidence_count_msg = f"Evidence Files: {len(all_evidence)}"
                if len(screenshots) > 20:
                    evidence_count_msg += f" (limited from {len(screenshots)} total)"
                elements.append(Paragraph(evidence_count_msg, caption_style))
                elements.append(Spacer(1, 15))
                
                # Sort evidence files by file modification time for execution sequence
                sorted_evidence = sorted(all_evidence, key=lambda file_path: (PROJECT_ROOT / file_path).stat().st_mtime if (PROJECT_ROOT / file_path).exists() else 0)
                
                for idx, file_path in enumerate(sorted_evidence, 1):
                    file_abs = PROJECT_ROOT / file_path
                    # Get filename (defined outside try block for error handling)
                    filename = file_path.split('/')[-1] if file_path else f"file_{idx}"
                    file_extension = file_path.lower().split('.')[-1] if '.' in file_path else ''
                    
                    if file_abs.exists():
                        try:
                            # Check if this is an HTML file
                            if file_extension in ['html', 'htm']:
                                # Convert HTML to image for PDF display with full page capture
                                print(f"[DEBUG] Converting HTML to image for PDF: {file_path}")
                                reportlab_img = create_html_preview_image(file_abs, max_width=400, max_height=300, full_page=True)
                                
                                if reportlab_img:
                                    pdf_width = reportlab_img.imageWidth
                                    pdf_height = reportlab_img.imageHeight
                                    print(f"[DEBUG] HTML converted successfully for PDF. Dimensions: {pdf_width}x{pdf_height}")
                                else:
                                    # Fallback: create placeholder for HTML
                                    print(f"[DEBUG] HTML conversion failed for PDF, creating placeholder")
                                    if PIL_AVAILABLE:
                                        placeholder_img = PILImage.new("RGB", (400, 300), color=(245, 247, 250))
                                        draw = ImageDraw.Draw(placeholder_img)
                                        try:
                                            font = ImageFont.load_default()
                                        except Exception:
                                            font = None
                                        
                                        # Draw placeholder text
                                        draw.text((20, 150), "HTML Preview", fill=(64, 64, 64), font=font)
                                        draw.text((20, 180), filename[:40], fill=(96, 96, 96), font=font)
                                        
                                        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_img:
                                            placeholder_img.save(temp_img.name, format='JPEG', quality=75)
                                            reportlab_img = ReportLabImage(temp_img.name, width=400, height=300)
                                            pdf_width, pdf_height = 400, 300
                                            
                                            # Clean up temp file
                                            try:
                                                os.unlink(temp_img.name)
                                            except:
                                                pass
                                    else:
                                        # If PIL not available, create text placeholder
                                        elements.append(Paragraph(f"<b>HTML File:</b> {filename}", normal_style))
                                        elements.append(Paragraph("(HTML preview not available - PIL/Pillow required)", caption_style))
                                        elements.append(Spacer(1, 10))
                                        continue
                            else:
                                # Regular image file processing
                                # Process image with PIL for high quality
                                if PIL_AVAILABLE:
                                    with PILImage.open(str(file_abs)) as pil_img:
                                        # Get original dimensions
                                        original_width, original_height = pil_img.size
                                        
                                        # Calculate maximum dimensions for PDF (reduced for smaller file size)
                                        max_width, max_height = 400, 300
                                        
                                        # Calculate scaling factor to maintain aspect ratio
                                        width_ratio = max_width / original_width
                                        height_ratio = max_height / original_height
                                        scale_ratio = min(width_ratio, height_ratio)
                                        
                                        # Calculate final dimensions for PDF
                                        pdf_width = original_width * scale_ratio
                                        pdf_height = original_height * scale_ratio
                                        
                                        # Convert to RGB if necessary
                                        if pil_img.mode in ('RGBA', 'LA', 'P'):
                                            rgb_img = PILImage.new('RGB', pil_img.size, (255, 255, 255))
                                            if pil_img.mode == 'P':
                                                pil_img = pil_img.convert('RGBA')
                                            rgb_img.paste(pil_img, mask=pil_img.split()[-1] if pil_img.mode in ('RGBA', 'LA') else None)
                                            pil_img = rgb_img
                                        
                                        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_img:
                                            pil_img.save(temp_img.name, format='JPEG', quality=75, optimize=True, dpi=(150, 150))
                                            reportlab_img = ReportLabImage(temp_img.name, width=pdf_width, height=pdf_height)
                                            
                                            # Clean up temp file
                                            try:
                                                os.unlink(temp_img.name)
                                            except:
                                                pass
                                else:
                                    reportlab_img = ReportLabImage(str(file_abs), width=400, height=300)
                                    pdf_width, pdf_height = 400, 300
                            
                            # Create image with caption
                            file_type_label = "HTML File" if file_extension in ['html', 'htm'] else "Screenshot"
                            img_with_caption = [
                                [reportlab_img],
                                [Paragraph(f"<b>{file_type_label}:</b> {filename}", caption_style)]
                            ]
                            
                            img_table = Table(img_with_caption, colWidths=[pdf_width])
                            img_table.setStyle(TableStyle([
                                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                ('LEFTPADDING', (0,0), (-1,-1), 0),
                                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                                ('TOPPADDING', (0,0), (-1,0), 10),
                                ('BOTTOMPADDING', (0,0), (-1,0), 5),
                                ('TOPPADDING', (0,1), (-1,1), 5),
                                ('BOTTOMPADDING', (0,1), (-1,1), 15),
                            ]))
                            
                            elements.append(img_table)
                            elements.append(Spacer(1, 15))
                            
                        except Exception as e:
                            print(f"Error processing evidence file {file_path}: {e}")
                            # Create error info table
                            file_type = "HTML File" if file_extension in ['html', 'htm'] else "Screenshot"
                            error_info = [
                                [f"{file_type} #{idx}", f"Status: Error"],
                                [f"File: {filename}", f"Error: {str(e)[:50]}..."]
                            ]
                            
                            error_table = Table(error_info, colWidths=[200, 200])
                            error_table.setStyle(TableStyle([
                                ('FONTNAME', (0,0), (-1,-1), PDF_FONT_NORMAL),
                                ('FONTSIZE', (0,0), (-1,-1), 8),
                                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#B71C1C")),
                                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFEBEE")),
                                ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#B71C1C")),
                                ('TOPPADDING', (0,0), (-1,-1), 4),
                                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                                ('LEFTPADDING', (0,0), (-1,-1), 6),
                                ('RIGHTPADDING', (0,0), (-1,-1), 6),
                            ]))
                            
                            elements.append(error_table)
                            elements.append(Spacer(1, 10))
                    else:
                        # Create missing file info table
                        file_type = "HTML File" if file_extension in ['html', 'htm'] else "Screenshot"
                        missing_info = [
                            [f"{file_type} #{idx}", f"Status: Missing"],
                            [f"File: {filename}", f"Path: {file_path}"]
                        ]
                        
                        missing_table = Table(missing_info, colWidths=[200, 200])
                        missing_table.setStyle(TableStyle([
                            ('FONTNAME', (0,0), (-1,-1), PDF_FONT_NORMAL),
                            ('FONTSIZE', (0,0), (-1,-1), 8),
                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#FF9800")),
                            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFF3E0")),
                            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#FF9800")),
                            ('TOPPADDING', (0,0), (-1,-1), 4),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                            ('LEFTPADDING', (0,0), (-1,-1), 6),
                            ('RIGHTPADDING', (0,0), (-1,-1), 6),
                        ]))
                        
                        elements.append(missing_table)
                        elements.append(Spacer(1, 10))
            else:
                elements.append(Paragraph("No evidence files available for this test case.", normal_style))
        else:
            elements.append(PageBreak())
            elements.append(Paragraph("Test Evidence Files", header_style))
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("No evidence files available for this test case.", normal_style))

        # Footer
        footer_style = styles['Normal'].clone('FooterStyle')
        footer_style.fontSize = 8
        footer_style.textColor = colors.HexColor("#666666")
        footer_style.fontName = PDF_FONT_NORMAL
        footer_style.leading = 10
        footer_style.alignment = 1
        
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("_______________________________________________", footer_style))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Generated by: Test Automation Dashboard v1.0", footer_style))
        elements.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
        elements.append(Paragraph("Confidential - For Internal Use Only", footer_style))

        # Build PDF with enhanced error handling
        try:
            doc.build(elements)
            buffer.seek(0)
            return buffer
        except Exception as build_error:
            print(f"[ERROR] PDF build failed for {test_case_id}: {build_error}")
            # Create a simpler PDF with basic information if the full build fails
            try:
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)
                simple_elements = []
                
                # Simple title
                simple_elements.append(Paragraph(f"Test Case: {test_case_id}", styles['Title']))
                simple_elements.append(Spacer(1, 20))
                
                # Simple status
                simple_elements.append(Paragraph(f"Status: {test_case_status}", styles['Normal']))
                simple_elements.append(Spacer(1, 10))
                
                # Simple description (without special formatting)
                if test_case_name and test_case_name != test_case_id:
                    clean_name = re.sub(r'[<>&"\']', '', str(test_case_name))
                    simple_elements.append(Paragraph(f"Description: {clean_name}", styles['Normal']))
                    simple_elements.append(Spacer(1, 10))
                
                # Simple error message (if any) - truncated and cleaned
                if fail_desc_text:
                    clean_error = re.sub(r'[<>&"\']', '', str(fail_desc_text)[:1000])  # Truncate to 1000 chars
                    simple_elements.append(Paragraph(f"Error Description: {clean_error}...", styles['Normal']))
                    simple_elements.append(Spacer(1, 10))
                
                simple_elements.append(Spacer(1, 20))
                simple_elements.append(Paragraph("Note: This is a simplified PDF due to formatting issues in the original content.", styles['Normal']))
                simple_elements.append(Paragraph(f"Original error: {str(build_error)[:200]}", styles['Normal']))
                
                doc.build(simple_elements)
                buffer.seek(0)
                return buffer
            except Exception as simple_error:
                print(f"[ERROR] Even simple PDF build failed for {test_case_id}: {simple_error}")
                raise build_error
        
    except Exception as e:
        print(f"Error generating test case PDF for {test_case_id}: {e}")
        return None

def generate_optimized_test_case_pdf(test_case_id, feature_name, run_timestamp, feature_data, test_case_row):
    """Generate an optimized PDF with reduced content for large files."""
    try:
        print(f"[DEBUG] Generating optimized PDF for {test_case_id}")
        
        # Use similar structure but with content limitations
        try:
            available_fields = list(getattr(test_case_row, 'index', getattr(test_case_row, 'keys', lambda: [])()))
        except Exception:
            available_fields = []

        def row_get(key, default=None):
            try:
                if key is None:
                    return default
                if hasattr(test_case_row, 'get'):
                    return test_case_row.get(key, default)
                return test_case_row[key] if key in available_fields else default
            except Exception:
                return default

        def pick_col(candidates):
            for c in candidates:
                if c in available_fields:
                    return c
            return None

        # Get basic info
        desc_columns = ['Test Case Description', 'TestCaseDescription', 'Description', 'Test Description', 'Name']
        desc_col = pick_col(desc_columns)
        status_columns = ['TestResult', 'Status', 'Result']
        status_col = pick_col(status_columns)
        error_columns = ['Fail_Description', 'Fail Description', 'TestResult Description', 'Result Description', 'Error', 'Message', 'Failure Reason']
        error_col = pick_col(error_columns)

        test_case_name = str(row_get(desc_col, test_case_id))
        status_raw = row_get(status_col, 'UNKNOWN')
        test_case_status = str(status_raw).strip().upper() if status_raw is not None else 'UNKNOWN'
        error_val = row_get(error_col, '')
        error_message = str(error_val) if error_val is not None else ''

        # Create simplified PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        elements = []

        # Simple title
        title_style = styles['Title'].clone('OptimizedTitleStyle')
        title_style.fontSize = 16
        title_style.spaceAfter = 20
        title_style.textColor = colors.HexColor("#8B4513")
        title_style.fontName = PDF_FONT_BOLD
        title_style.alignment = 1
        
        elements.append(Paragraph(f"Test Case: {escape_html_for_pdf(test_case_id)}", title_style))
        elements.append(Spacer(1, 20))

        # Status
        status_style = styles['Normal'].clone('OptimizedStatusStyle')
        status_style.fontSize = 14
        status_style.fontName = PDF_FONT_BOLD
        status_style.alignment = 1
        
        if test_case_status == "PASS":
            status_style.textColor = colors.HexColor("#28a745")
        elif test_case_status == "FAIL":
            status_style.textColor = colors.HexColor("#dc3545")
        else:
            status_style.textColor = colors.HexColor("#6c757d")
            
        elements.append(Paragraph(f"Status: {test_case_status}", status_style))
        elements.append(Spacer(1, 20))

        # Basic metadata
        normal_style = styles['Normal'].clone('OptimizedNormalStyle')
        normal_style.fontSize = 10
        normal_style.leading = 12
        
        elements.append(Paragraph(f"<b>Test Case ID:</b> {escape_html_for_pdf(test_case_id)}", normal_style))
        elements.append(Spacer(1, 10))
        
        if test_case_name and test_case_name != test_case_id:
            elements.append(Paragraph(f"<b>Description:</b> {escape_html_for_pdf(test_case_name[:500])}...", normal_style))
            elements.append(Spacer(1, 10))
        
        elements.append(Paragraph(f"<b>Feature:</b> {escape_html_for_pdf(feature_name)}", normal_style))
        elements.append(Spacer(1, 10))
        
        elements.append(Paragraph(f"<b>Execution Time:</b> {format_timestamp_professional(run_timestamp)}", normal_style))
        elements.append(Spacer(1, 20))

        # Truncated error message if any
        if error_message and error_message.strip():
            error_style = styles['Normal'].clone('OptimizedErrorStyle')
            error_style.fontSize = 10
            error_style.textColor = colors.HexColor("#dc3545")
            error_style.fontName = PDF_FONT_NORMAL
            error_style.leading = 12
            
            # Limit error message to 2000 characters
            truncated_error = error_message[:2000]
            if len(error_message) > 2000:
                truncated_error += "... [ข้อความถูกตัดทอนเนื่องจากความยาว]"
            
            safe_error = escape_html_for_pdf(truncated_error)
            elements.append(Paragraph(f"<b>Error Description:</b><br/>{safe_error}", error_style))
            elements.append(Spacer(1, 20))

        # Limited evidence files (max 5)
        evidence_files = []
        if feature_data.get('test_evidence'):
            if test_case_id in feature_data['test_evidence']:
                evidence_files = feature_data['test_evidence'][test_case_id][:5]  # Limit to 5 files

        if evidence_files:
            elements.append(Paragraph("<b>Evidence Files (Limited to 5):</b>", normal_style))
            elements.append(Spacer(1, 10))
            
            for idx, file_path in enumerate(evidence_files, 1):
                file_abs = PROJECT_ROOT / file_path
                if file_abs.exists():
                    try:
                        file_extension = file_path.lower().split('.')[-1] if '.' in file_path else ''
                        
                        # Check if this is an HTML file
                        if file_extension in ['html', 'htm']:
                            # Convert HTML to image for PDF display with full page capture
                            print(f"[DEBUG] Converting HTML to image for optimized PDF: {file_path}")
                            reportlab_img = create_html_preview_image(file_abs, max_width=300, max_height=200, full_page=True)
                            
                            if reportlab_img:
                                pdf_width = reportlab_img.imageWidth
                                pdf_height = reportlab_img.imageHeight
                            else:
                                # Fallback: create placeholder for HTML
                                if PIL_AVAILABLE:
                                    placeholder_img = PILImage.new("RGB", (300, 200), color=(245, 247, 250))
                                    draw = ImageDraw.Draw(placeholder_img)
                                    try:
                                        font = ImageFont.load_default()
                                    except Exception:
                                        font = None
                                    
                                    # Draw placeholder text
                                    draw.text((15, 100), "HTML Preview", fill=(64, 64, 64), font=font)
                                    draw.text((15, 120), file_path.split('/')[-1][:30], fill=(96, 96, 96), font=font)
                                    
                                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_img:
                                        placeholder_img.save(temp_img.name, format='JPEG', quality=70)
                                        reportlab_img = ReportLabImage(temp_img.name, width=300, height=200)
                                        pdf_width, pdf_height = 300, 200
                                        
                                        # Clean up temp file
                                        try:
                                            os.unlink(temp_img.name)
                                        except:
                                            pass
                                else:
                                    # If PIL not available, create text placeholder
                                    elements.append(Paragraph(f"<b>HTML File:</b> {file_path.split('/')[-1]}", normal_style))
                                    elements.append(Paragraph("(HTML preview not available)", caption_style))
                                    elements.append(Spacer(1, 10))
                                    continue
                        else:
                            # Regular image file processing
                            # Smaller images for optimization
                            if PIL_AVAILABLE:
                                with PILImage.open(str(file_abs)) as pil_img:
                                    # Smaller size for optimized PDF
                                    max_width, max_height = 300, 200
                                    original_width, original_height = pil_img.size
                                    
                                    width_ratio = max_width / original_width
                                    height_ratio = max_height / original_height
                                    scale_ratio = min(width_ratio, height_ratio)
                                    
                                    pdf_width = original_width * scale_ratio
                                    pdf_height = original_height * scale_ratio
                                    
                                    if pil_img.mode in ('RGBA', 'LA', 'P'):
                                        rgb_img = PILImage.new('RGB', pil_img.size, (255, 255, 255))
                                        if pil_img.mode == 'P':
                                            pil_img = pil_img.convert('RGBA')
                                        rgb_img.paste(pil_img, mask=pil_img.split()[-1] if pil_img.mode in ('RGBA', 'LA') else None)
                                        pil_img = rgb_img
                                    
                                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_img:
                                        pil_img.save(temp_img.name, 'JPEG', quality=70, optimize=True)  # Lower quality
                                        reportlab_img = ReportLabImage(temp_img.name, width=pdf_width, height=pdf_height)
                                        
                                        # Clean up temp file
                                        try:
                                            os.unlink(temp_img.name)
                                        except:
                                            pass
                            else:
                                reportlab_img = ReportLabImage(str(file_abs), width=300, height=200)
                                pdf_width, pdf_height = 300, 200
                        
                        filename = file_path.split('/')[-1]
                        file_type_label = "HTML File" if file_extension in ['html', 'htm'] else "Screenshot"
                        img_table = Table([[reportlab_img], [Paragraph(f"<b>{file_type_label}:</b> {filename}", normal_style)]], colWidths=[300])
                        img_table.setStyle(TableStyle([
                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ]))
                        
                        elements.append(img_table)
                        elements.append(Spacer(1, 15))
                                
                    except Exception as e:
                        print(f"[ERROR] Failed to add evidence file {file_path}: {e}")
                        continue
        else:
            elements.append(Paragraph("No evidence files available.", normal_style))

        # Footer
        elements.append(Spacer(1, 30))
        footer_style = styles['Normal'].clone('OptimizedFooterStyle')
        footer_style.fontSize = 8
        footer_style.textColor = colors.HexColor("#666666")
        footer_style.alignment = 1
        
        elements.append(Paragraph("Generated by: Test Automation Dashboard (Optimized Version)", footer_style))
        elements.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
        elements.append(Paragraph("Note: This is an optimized version with limited content due to size constraints.", footer_style))

        # Build optimized PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"[ERROR] Optimized PDF generation failed for {test_case_id}: {e}")
        return None

@app.route('/api/export_testcase_pdf', methods=['POST'])
def export_testcase_pdf():
    """Export individual test case to PDF with detailed screenshots and information."""
    if not REPORTLAB_AVAILABLE:
        print("[ERROR] ReportLab not available for PDF export")
        return jsonify({'error': 'PDF download not available. ReportLab not installed.'}), 500
        
    try:
        print("[DEBUG] Starting PDF export request...")
        data = request.get_json()
        if not data:
            print("[ERROR] No JSON data provided in request")
            return jsonify({'error': 'No data provided'}), 400
            
        test_case_id = data.get('test_case_id')
        feature_name = data.get('feature_name')
        run_timestamp = data.get('run_timestamp')
        
        print(f"[DEBUG] PDF export request params: test_case_id='{test_case_id}', feature_name='{feature_name}', run_timestamp='{run_timestamp}'")
        
        if not all([test_case_id, feature_name, run_timestamp]):
            print(f"[ERROR] Missing required parameters: test_case_id={test_case_id}, feature_name={feature_name}, run_timestamp={run_timestamp}")
            return jsonify({'error': 'Missing required parameters: test_case_id, feature_name, run_timestamp'}), 400

        # Find the specific test case data
        print(f"[DEBUG] Searching for test case data in {RESULTS_DIR}")
        all_excel_files = find_excel_files(RESULTS_DIR)
        print(f"[DEBUG] Found {len(all_excel_files)} Excel files to search")
        target_feature_data = None
        
        for excel_file in all_excel_files:
            print(f"[DEBUG] Parsing Excel file: {excel_file}")
            feature_data = parse_excel_data(excel_file)
            if feature_data:
                print(f"[DEBUG] Excel file data: feature_name='{feature_data.get('feature_name')}', run_timestamp='{feature_data.get('run_timestamp')}'")
                if (feature_data.get("feature_name") == feature_name and 
                    feature_data.get("run_timestamp") == run_timestamp):
                    target_feature_data = feature_data
                    print(f"[DEBUG] Found matching feature data in {excel_file}")
                    break
            else:
                print(f"[DEBUG] Failed to parse Excel file: {excel_file}")
        
        if not target_feature_data:
            print(f"[ERROR] Test case not found: {test_case_id} in {feature_name} for timestamp {run_timestamp}")
            return jsonify({'error': f'Test case not found: {test_case_id} in {feature_name}'}), 404

        # Get Excel file for test case details
        excel_path = PROJECT_ROOT / target_feature_data['excel_path']
        print(f"[DEBUG] Reading Excel file: {excel_path}")
        if not excel_path.exists():
            print(f"[ERROR] Excel file not found: {excel_path}")
            return jsonify({'error': f'Excel file not found: {excel_path}'}), 404
            
        df = pd.read_excel(excel_path)
        print(f"[DEBUG] Excel file loaded successfully. Shape: {df.shape}")
        print(f"[DEBUG] Available columns: {list(df.columns)}")
        
        # Find relevant columns
        id_columns = ['Test Case ID', 'TestCaseID', 'Test Case', 'ID', 'TestCase', 'TestCaseNo', 'Name']
        id_col = find_first_column(df.columns, id_columns)
        
        desc_columns = ['Test Case Description', 'TestCaseDescription', 'Description', 'Test Description', 'Name']
        desc_col = find_first_column(df.columns, desc_columns)
        
        status_columns = ['TestResult', 'Status', 'Result']
        status_col = find_first_column(df.columns, status_columns)
        
        error_columns = ['Fail_Description', 'Fail Description', 'TestResult Description', 'Result Description', 'Error', 'Message', 'Failure Reason']
        error_col = find_first_column(df.columns, error_columns)
        
        expected_result_columns = ['ExpectedResult', 'Expected Result', 'Expected', 'Expected Outcome']
        expected_result_col = find_first_column(df.columns, expected_result_columns)
        
        print(f"[DEBUG] Column mapping: id_col='{id_col}', desc_col='{desc_col}', status_col='{status_col}', error_col='{error_col}', expected_result_col='{expected_result_col}'")
        
        # Find the specific test case row
        test_case_row = None
        print(f"[DEBUG] Searching for test case ID: '{test_case_id}'")
        for _, row in df.iterrows():
            row_id = str(row.get(id_col, '')).strip()
            if row_id == test_case_id:
                test_case_row = row
                print(f"[DEBUG] Found test case row for ID: '{test_case_id}'")
                
                # Debug the content length
                if error_col and error_col in row:
                    error_content = str(row[error_col]) if pd.notna(row[error_col]) else ''
                    print(f"[DEBUG] Error content length: {len(error_content)} characters")
                    if len(error_content) > 1000:
                        print(f"[DEBUG] Long error content detected. First 200 chars: {error_content[:200]}...")
                        print(f"[DEBUG] Contains Thai characters: {any(ord(c) > 127 for c in error_content)}")
                break
        
        if test_case_row is None:
            # Try to find by partial match or use default values
            print(f"Test case {test_case_id} not found in Excel, using default values")
            test_case_row = {
                id_col: test_case_id,
                desc_col: test_case_id,
                status_col: 'UNKNOWN',
                error_col: '',
                expected_result_col: ''
            }

        # Use core PDF generation function
        print(f"[DEBUG] Calling PDF generation for test case: {test_case_id}")
        try:
            pdf_buffer = generate_test_case_pdf_core(test_case_id, feature_name, run_timestamp, target_feature_data, test_case_row)
            print(f"[DEBUG] PDF generation completed. Buffer exists: {pdf_buffer is not None}")
        except Exception as pdf_error:
            print(f"[ERROR] PDF generation failed with error: {pdf_error}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'PDF generation failed: {str(pdf_error)}'}), 500
        
        if not pdf_buffer:
            print(f"[ERROR] PDF generation returned None for test case: {test_case_id}")
            return jsonify({'error': 'Failed to generate PDF - buffer is None'}), 500
        
        # Generate filename (sanitize to avoid header/path issues)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_tc = sanitize_filename(test_case_id)
        safe_feature = sanitize_filename(feature_name)
        filename = f"TestCase_{safe_tc}_{safe_feature}_{timestamp}.pdf"
        print(f"[DEBUG] Generated filename: {filename}")
        
        try:
            pdf_size = len(pdf_buffer.getvalue())
            print(f"[DEBUG] Sending PDF file. Buffer size: {pdf_size} bytes ({pdf_size / (1024*1024):.2f} MB)")
            
            # Check if PDF is too large (> 100 MB)
            if pdf_size > 100 * 1024 * 1024:  # 100 MB limit
                print(f"[WARNING] PDF is too large ({pdf_size / (1024*1024):.2f} MB), creating optimized version")
                
                # Create a simpler PDF with reduced content
                try:
                    optimized_buffer = generate_optimized_test_case_pdf(test_case_id, feature_name, run_timestamp, target_feature_data, test_case_row)
                    if optimized_buffer:
                        opt_size = len(optimized_buffer.getvalue())
                        print(f"[DEBUG] Optimized PDF size: {opt_size} bytes ({opt_size / (1024*1024):.2f} MB)")
                        return send_file(optimized_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')
                except Exception as opt_error:
                    print(f"[ERROR] Failed to create optimized PDF: {opt_error}")
                
                # If optimization fails, return error
                return jsonify({'error': f'PDF is too large ({pdf_size / (1024*1024):.2f} MB). Please contact administrator.'}), 413
            
            return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')
        except Exception as send_error:
            print(f"[ERROR] Failed to send PDF file: {send_error}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Failed to send PDF: {str(send_error)}'}), 500
        
    except Exception as e:
        print(f"[ERROR] Test Case PDF Export Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@app.route('/api/export_feature_pdfs_zip', methods=['POST'])
def export_feature_pdfs_zip():
    """Export all test case PDFs for a specific feature as a ZIP file."""
    if not REPORTLAB_AVAILABLE:
        return jsonify({'error': 'PDF generation not available. ReportLab not installed.'}), 500
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        feature_name = data.get('feature_name')
        run_timestamp = data.get('run_timestamp')
        run_index = data.get('run_index')
        feature_index = data.get('feature_index')
        
        if not all([feature_name, run_timestamp]):
            return jsonify({'error': 'Missing required parameters'}), 400

        # Find the specific feature data
        all_excel_files = find_excel_files(RESULTS_DIR)
        target_feature_data = None
        
        for excel_file in all_excel_files:
            feature_data = parse_excel_data(excel_file)
            if (feature_data and 
                feature_data.get("feature_name") == feature_name and 
                feature_data.get("run_timestamp") == run_timestamp):
                target_feature_data = feature_data
                break
        
        if not target_feature_data:
            return jsonify({'error': f'Feature not found: {feature_name}'}), 404

        # Get Excel file for test case details
        excel_path = PROJECT_ROOT / target_feature_data['excel_path']
        if not excel_path.exists():
            return jsonify({'error': f'Excel file not found: {excel_path}'}), 404
            
        df = pd.read_excel(excel_path)
        
        # Find relevant columns
        id_columns = ['Test Case ID', 'TestCaseID', 'Test Case', 'ID', 'TestCase', 'TestCaseNo', 'Name']
        id_col = find_first_column(df.columns, id_columns)
        status_columns = ['TestResult', 'Status', 'Result']
        status_col = find_first_column(df.columns, status_columns)
        
        if not id_col or not status_col:
            return jsonify({'error': 'Required columns not found in Excel file'}), 400

        # Filter for executed tests only (Execute == 'Y')
        execute_column = next((c for c in df.columns if c.lower() == 'execute'), None)
        if execute_column:
            df = df[df[execute_column].str.lower() == 'y'].copy()

        # Create temporary ZIP file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                
                # Process each test case that has Execute = 'Y'
                for _, row in df.iterrows():
                    test_case_id = str(row.get(id_col, '')).strip()
                    test_case_status = str(row.get(status_col, '')).strip().upper()
                    
                    # Skip if test case is empty
                    if not test_case_id or test_case_id.lower() in ['nan', 'none', '']:
                        continue
                    
                    try:
                        # Generate PDF for this test case (include all, regardless of status)
                        pdf_buffer = generate_test_case_pdf_core(
                            test_case_id, feature_name, run_timestamp, target_feature_data, row
                        )
                        
                        if pdf_buffer:
                            # Add PDF to ZIP
                            filename = f"{sanitize_filename(test_case_id)}_{sanitize_filename(feature_name)}.pdf"
                            zipf.writestr(filename, pdf_buffer.getvalue())
                            print(f"Added PDF for test case: {test_case_id}")
                        else:
                            print(f"Failed to generate PDF for test case: {test_case_id}")
                            
                    except Exception as e:
                        print(f"Error generating PDF for test case {test_case_id}: {e}")
                        continue

        # Read the ZIP file and return it
        with open(temp_zip.name, 'rb') as zip_file:
            zip_data = zip_file.read()
        
        # Clean up temporary file
        os.unlink(temp_zip.name)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{sanitize_filename(feature_name)}_AllTestCases_{timestamp}.zip"
        
        return send_file(
            io.BytesIO(zip_data),
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        print(f"ZIP Export Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/export_latest_all_features_zip', methods=['POST'])
def export_latest_all_features_zip():
    """Export all test case PDFs for all features in the latest run as a ZIP file."""
    if not REPORTLAB_AVAILABLE:
        return jsonify({'error': 'PDF generation not available. ReportLab not installed.'}), 500
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        run_timestamp = data.get('run_timestamp')
        features = data.get('features', [])
        
        if not run_timestamp or not features:
            return jsonify({'error': 'Missing required parameters'}), 400

        try:
            # Create ZIP in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                
                    # Process each feature
                    for feature in features:
                        feature_name = feature.get('name')
                        excel_path = feature.get('excel_path')
                        
                        if not feature_name or not excel_path:
                            continue
                        
                        # Find the specific feature data
                        full_excel_path = PROJECT_ROOT / excel_path
                        if not full_excel_path.exists():
                            print(f"Excel file not found: {full_excel_path}")
                            continue
                            
                        try:
                            df = pd.read_excel(full_excel_path)
                            
                            # Find relevant columns
                            id_columns = ['Test Case ID', 'TestCaseID', 'Test Case', 'ID', 'TestCase', 'TestCaseNo', 'Name']
                            id_col = find_first_column(df.columns, id_columns)
                            status_columns = ['TestResult', 'Status', 'Result']
                            status_col = find_first_column(df.columns, status_columns)
                            
                            if not id_col or not status_col:
                                print(f"Required columns not found in Excel file: {excel_path}")
                                continue

                            # Filter for executed tests only (Execute == 'Y')
                            df = filter_executed_rows(df)

                            # Create feature folder in ZIP
                            feature_folder = f"{feature_name}/"
                            
                            # Process each test case that has Execute = 'Y'
                            for _, row in df.iterrows():
                                test_case_id = str(row.get(id_col, '')).strip()
                                test_case_status = str(row.get(status_col, '')).strip().upper()
                                
                                # Skip if test case is empty
                                if not test_case_id or test_case_id.lower() in ['nan', 'none', '']:
                                    continue
                                
                                try:
                                    # Generate PDF for this test case
                                    # Build parsed_feature per feature (once outside loop would be better, but safe here)
                                    try:
                                        parsed_feature = parse_excel_data(str(full_excel_path))
                                    except Exception:
                                        parsed_feature = {'feature_name': feature_name, 'excel_path': excel_path, 'test_evidence': {}}
                                    pdf_buffer = generate_test_case_pdf_core(
                                        test_case_id, feature_name, run_timestamp, parsed_feature, row
                                    )
                                    
                                    if pdf_buffer:
                                        # Add PDF to ZIP with feature folder structure
                                        filename = f"{feature_folder}{sanitize_filename(test_case_id)}.pdf"
                                        zipf.writestr(filename, pdf_buffer.getvalue())
                                        print(f"Added PDF for test case: {test_case_id} in feature: {feature_name}")
                                    else:
                                        print(f"Failed to generate PDF for test case: {test_case_id}")
                                        
                                except Exception as e:
                                    print(f"Error generating PDF for test case {test_case_id}: {e}")
                                    continue
                                    
                        except Exception as e:
                            print(f"Error processing feature {feature_name}: {e}")
                            continue

            # Get the ZIP data from memory buffer
            zip_buffer.seek(0)
            zip_data = zip_buffer.getvalue()
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"LatestRun_AllFeatures_{timestamp}.zip"
            
            return send_file(
                io.BytesIO(zip_data),
                as_attachment=True,
                download_name=filename,
                mimetype='application/zip'
            )
                
        except Exception as e:
            print(f"Error during PDF generation: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500
        
    except Exception as e:
        print(f"Latest All Features ZIP Export Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def format_timestamp_professional(timestamp_str):
    """Format timestamp professionally (helper function)."""
    try:
        if timestamp_str and len(timestamp_str) >= 15:
            if timestamp_str[8] in ['-', '_']:
                year = timestamp_str[:4]
                month = timestamp_str[4:6]
                day = timestamp_str[6:8]
                hour = timestamp_str[9:11]
                minute = timestamp_str[11:13]
                second = timestamp_str[13:15]
                
                dt = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
                return dt.strftime("%B %d, %Y at %I:%M %p")
            else:
                dt = datetime.fromisoformat(timestamp_str.replace('T', ' '))
                return dt.strftime("%B %d, %Y at %I:%M %p")
        else:
            return timestamp_str
    except:
        return timestamp_str

# --- Static File and Results Serving ---
# This route serves images and other files from the 'results' directory
@app.route('/results/<path:filepath>')
def serve_results(filepath):
    return send_from_directory(RESULTS_DIR, filepath)

# --- HTML Thumbnail Generation (cached) ---
def _ensure_thumbnail_dir(html_path: Path = None) -> Path:
    """Ensure thumbnail directory exists. If html_path is provided, create a subdirectory 
    based on the test case folder structure to prevent cross-contamination.
    
    NEW STRUCTURE: results/YYYYMMDD_HHMMSS/FeatureName/TestCaseID/.thumbnails/
    """
    if html_path:
        # Create thumbnail directory structure that mirrors the test case folder structure
        # Example: results/20241201_120000/Feature1/TC001/file.html -> results/20241201_120000/Feature1/TC001/.thumbnails/
        try:
            # Get the relative path from results directory
            rel_path = html_path.relative_to(RESULTS_DIR)
            # Create thumbnail subdirectory structure INSIDE the test case folder
            thumb_subdir = RESULTS_DIR / rel_path.parent / ".thumbnails"
            thumb_subdir.mkdir(parents=True, exist_ok=True)
            print(f"[INFO] Created thumbnail directory: {thumb_subdir}")
            return thumb_subdir
        except Exception as e:
            print(f"[WARN] Could not create structured thumbnail directory: {e}")
            # Fallback to root thumbnail directory
            pass
    
    # Fallback: create root thumbnail directory (for backward compatibility)
    thumb_dir = RESULTS_DIR / ".thumbnails"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    return thumb_dir

def _get_thumbnail_path(html_path: Path) -> Path:
    """Generate a thumbnail path that maintains the folder structure of the original file.
    This prevents cross-contamination between different test cases.
    
    NEW STRUCTURE: results/YYYYMMDD_HHMMSS/FeatureName/TestCaseID/.thumbnails/file_hash.png
    """
    try:
        # Get the relative path from results directory
        rel_path = html_path.relative_to(RESULTS_DIR)
        # Create thumbnail path that mirrors the original structure INSIDE test case folder
        thumb_dir = _ensure_thumbnail_dir(html_path)
        
        # Create a unique filename based on the full path
        # Use hash of the full path to ensure uniqueness
        import hashlib
        path_hash = hashlib.md5(str(html_path).encode()).hexdigest()[:8]
        filename = f"{html_path.stem}_{path_hash}.png"
        
        return thumb_dir / filename
    except Exception as e:
        print(f"[WARN] Could not create structured thumbnail path: {e}")
        # Fallback to root thumbnail directory with simple naming
        thumb_dir = _ensure_thumbnail_dir()
        thumb_name = html_path.relative_to(RESULTS_DIR).as_posix().replace('/', '_').replace('\\', '_') + '.png'
        return thumb_dir / thumb_name

def _html_to_thumbnail(html_abs_path: Path, thumb_abs_path: Path = None, width: int = 800, height: int = 450):
    """Generate a PNG thumbnail for an HTML file using Playwright if available.
    Falls back to a simple placeholder PNG if Playwright is unavailable or errors occur.
    
    Args:
        html_abs_path: Path to the HTML file
        thumb_abs_path: Path where to save the thumbnail (if None, will be auto-generated)
        width: Thumbnail width
        height: Thumbnail height
    """
    # Auto-generate thumbnail path if not provided
    if thumb_abs_path is None:
        thumb_abs_path = _get_thumbnail_path(html_abs_path)
    
    print(f"[INFO] Generating thumbnail for {html_abs_path}")
    print(f"[INFO] Thumbnail will be saved to: {thumb_abs_path}")
    print(f"[DEBUG] PLAYWRIGHT_AVAILABLE = {PLAYWRIGHT_AVAILABLE}")
    print(f"[DEBUG] PIL_AVAILABLE = {PIL_AVAILABLE}")
    
    # REMOVED REDUNDANT CODE: thumb_abs_path.parent.mkdir(parents=True, exist_ok=True)
    # This is already handled by _ensure_thumbnail_dir() in _get_thumbnail_path()
    
    # Try Playwright first (best quality)
    if PLAYWRIGHT_AVAILABLE:
        try:
            print(f"[INFO] Attempting Playwright HTML capture...")
            playwright = sync_playwright().start()
            try:
                browser = playwright.chromium.launch()
                page = browser.new_page(viewport={"width": width, "height": height})

                # Build file URI for local HTML
                file_uri = f"file:///{html_abs_path.as_posix().replace(chr(92), chr(47))}"
                print(f"[INFO] Using file URI: {file_uri}")

                page.goto(file_uri, wait_until="load")
                page.wait_for_timeout(1000)

                # Full page to ensure content captured
                page.screenshot(path=str(thumb_abs_path), full_page=True, type='png')
                browser.close()

                if thumb_abs_path.exists() and thumb_abs_path.stat().st_size > 1000:
                    print(f"[INFO] Successfully generated HTML thumbnail with Playwright: {thumb_abs_path}")
                    return True
                else:
                    print(f"[WARN] Screenshot created but seems empty or too small")
                    if thumb_abs_path.exists():
                        thumb_abs_path.unlink()
                    raise Exception("Screenshot file is empty or too small")
            finally:
                playwright.stop()
        except Exception as e:
            print(f"[WARN] Playwright thumbnail failed for {html_abs_path}: {e}")
            print(f"[WARN] Error type: {type(e).__name__}")
            print(f"[WARN] Error details: {str(e)}")
    
    # Fallback: generate a simple placeholder PNG via Pillow
    if PIL_AVAILABLE:
        try:
            print(f"[INFO] Using Pillow fallback for HTML thumbnail...")
            img = PILImage.new("RGB", (width, height), color=(245, 247, 250))
            draw = ImageDraw.Draw(img)
            
            # Create a more attractive placeholder
            # Background rectangle
            draw.rectangle([(20, 20), (width-20, height-20)], fill=(255, 255, 255), outline=(220, 220, 220), width=2)
            
            # HTML icon representation
            icon_color = (74, 144, 226)  # Blue color for HTML
            draw.rectangle([(width//2-40, height//2-60), (width//2+40, height//2-20)], fill=icon_color)
            draw.text((width//2, height//2-40), "HTML", fill=(255, 255, 255), anchor="mm")
            
            # Text
            try:
                font = ImageFont.load_default()
            except Exception:
                font = None
            
            # Main text
            draw.text((width//2, height//2+20), "HTML Preview", fill=(64, 64, 64), font=font, anchor="mm")
            
            # Filename (truncated if too long)
            filename = html_abs_path.name
            if len(filename) > 30:
                filename = filename[:27] + "..."
            draw.text((width//2, height//2+50), filename, fill=(96, 96, 96), font=font, anchor="mm")
            
            # Add warning text
            draw.text((width//2, height//2+80), "Playwright not available", fill=(255, 100, 100), font=font, anchor="mm")
            draw.text((width//2, height//2+100), "Install: pip install playwright", fill=(255, 100, 100), font=font, anchor="mm")
            
            img.save(str(thumb_abs_path), format="PNG", optimize=True)
            print(f"[INFO] Generated fallback HTML thumbnail with Pillow: {thumb_abs_path}")
            return True
        except Exception as e:
            print(f"[WARN] Pillow fallback thumbnail failed for {html_abs_path}: {e}")

    # Last resort: create a very basic placeholder
    if PIL_AVAILABLE:
        try:
            print(f"[INFO] Using last resort placeholder...")
            # Create a simple colored rectangle as placeholder
            img = PILImage.new("RGB", (width, height), color=(240, 240, 240))
            draw = ImageDraw.Draw(img)
            draw.rectangle([(0, 0), (width, height)], fill=(200, 200, 200), outline=(150, 150, 150), width=3)
            draw.text((width//2, height//2), "HTML", fill=(100, 100, 100), anchor="mm")
            img.save(str(thumb_abs_path), format="PNG")
            print(f"[INFO] Generated basic HTML placeholder: {thumb_abs_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to create any HTML thumbnail for {html_abs_path}: {e}")
    
    print(f"[ERROR] No thumbnail generation method available for {html_abs_path}")
    return False

def _html_preview_placeholder_svg(filename: str, width: int = 800, height: int = 450) -> bytes:
    """Return a lightweight SVG placeholder for HTML preview thumbnails.
    This does not require any external dependencies and guarantees a visual thumbnail.
    """
    safe_name = (filename or "HTML Preview").replace("<", "&lt;").replace(">", "&gt;")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f5f7fa"/>
      <stop offset="100%" stop-color="#e4e7eb"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#g)"/>
  <rect x="20" y="20" width="{width-40}" height="{height-40}" fill="#ffffff" stroke="#dfe3e8" stroke-width="2" rx="10"/>
  <g font-family="Arial, Helvetica, sans-serif" text-anchor="middle">
    <text x="50%" y="48%" fill="#6b7280" font-size="28">HTML Preview</text>
    <text x="50%" y="58%" fill="#9ca3af" font-size="16">{safe_name}</text>
  </g>
</svg>'''
    return svg.encode("utf-8")

def _excel_preview_placeholder_svg(filename: str, width: int = 800, height: int = 450) -> bytes:
    """Return a lightweight SVG placeholder for Excel file preview thumbnails.
    This creates an Excel icon with filename for visual representation.
    """
    safe_name = (filename or "Excel File").replace("<", "&lt;").replace(">", "&gt;")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <defs>
    <linearGradient id="excel_g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#217346"/>
      <stop offset="100%" stop-color="#1e6b3d"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#excel_g)"/>
  <rect x="20" y="20" width="{width-40}" height="{height-40}" fill="#ffffff" stroke="#217346" stroke-width="2" rx="10"/>
  
  <!-- Excel Icon -->
  <g transform="translate({width//2 - 40}, {height//2 - 60})">
    <!-- Excel Sheet -->
    <rect x="0" y="0" width="80" height="100" fill="#ffffff" stroke="#217346" stroke-width="2"/>
    <!-- Excel Grid Lines -->
    <line x1="0" y1="20" x2="80" y2="20" stroke="#217346" stroke-width="1"/>
    <line x1="0" y1="40" x2="80" y2="40" stroke="#217346" stroke-width="1"/>
    <line x1="0" y1="60" x2="80" y2="60" stroke="#217346" stroke-width="1"/>
    <line x1="0" y1="80" x2="80" y2="80" stroke="#217346" stroke-width="1"/>
    <line x1="20" y1="0" x2="20" y2="100" stroke="#217346" stroke-width="1"/>
    <line x1="40" y1="0" x2="40" y2="100" stroke="#217346" stroke-width="1"/>
    <line x1="60" y1="0" x2="60" y2="100" stroke="#217346" stroke-width="1"/>
    <!-- Excel Logo -->
    <rect x="25" y="25" width="30" height="15" fill="#217346"/>
    <text x="40" y="35" fill="#ffffff" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" font-weight="bold">X</text>
  </g>
  
  <!-- Filename -->
  <g font-family="Arial, Helvetica, sans-serif" text-anchor="middle">
    <text x="50%" y="85%" fill="#ffffff" font-size="16" font-weight="bold">Excel File</text>
    <text x="50%" y="95%" fill="#ffffff" font-size="12">{safe_name[:30]}</text>
  </g>
</svg>'''
    return svg.encode("utf-8")

@app.route('/api/evidence_thumbnail')
def api_evidence_thumbnail():
    """Return (and cache) a thumbnail for evidence files (HTML, Excel, Images).
    Query param 'path' must be a project-root-relative path like 'results/..../file.html'.
    """
    rel_path = request.args.get('path')
    if not rel_path:
        return abort(400, description="Missing 'path' query parameter")

    # Normalize and validate path
    try:
        # Strip leading slashes if provided
        rel_path_norm = rel_path.lstrip('/\\')
        abs_path = (PROJECT_ROOT / rel_path_norm).resolve()
        if RESULTS_DIR not in abs_path.parents and abs_path != RESULTS_DIR:
            return abort(400, description="Path must be under results directory")
        
        # Check file extension
        file_ext = abs_path.suffix.lower()
        if file_ext not in ['.html', '.htm', '.xlsx', '.xls', '.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            return abort(404, description="Unsupported file type")
            
        if not abs_path.exists():
            return abort(404)
    except Exception:
        return abort(400, description="Invalid path")

    # For Excel files, return SVG placeholder directly
    if file_ext in ['.xlsx', '.xls']:
        placeholder = _excel_preview_placeholder_svg(abs_path.name)
        return send_file(io.BytesIO(placeholder), mimetype='image/svg+xml')

    # For HTML files, generate thumbnail with better error handling
    if file_ext in ['.html', '.htm']:
        # Generate thumbnail path that maintains folder structure
        thumb_path = _get_thumbnail_path(abs_path)
        
        # Regenerate thumbnail if missing or outdated
        try:
            source_mtime = abs_path.stat().st_mtime
            need_build = True
            if thumb_path.exists():
                thumb_mtime = thumb_path.stat().st_mtime
                need_build = thumb_mtime < source_mtime
                
            if need_build:
                print(f"[INFO] Generating thumbnail for {abs_path}")
                print(f"[INFO] Using structured thumbnail path: {thumb_path}")
                # Generate synchronously to ensure we have something to serve
                thumbnail_success = _html_to_thumbnail(abs_path, thumb_path)
                
                # Verify thumbnail was created successfully
                if not thumbnail_success or not thumb_path.exists():
                    print(f"[WARN] Thumbnail generation failed for {abs_path}")
                    # Return SVG placeholder as fallback
                    placeholder = _html_preview_placeholder_svg(abs_path.name)
                    return send_file(io.BytesIO(placeholder), mimetype='image/svg+xml')
                    
        except Exception as e:
            print(f"[ERROR] Error preparing thumbnail for {abs_path}: {e}")
            # Return SVG placeholder as fallback
            placeholder = _html_preview_placeholder_svg(abs_path.name)
            return send_file(io.BytesIO(placeholder), mimetype='image/svg+xml')

        if thumb_path.exists():
            try:
                response = send_file(str(thumb_path), mimetype='image/png')
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache' 
                response.headers['Expires'] = '0'
                return response
            except Exception as e:
                print(f"[ERROR] Error serving thumbnail {thumb_path}: {e}")
                # Return SVG placeholder as fallback
                placeholder = _html_preview_placeholder_svg(abs_path.name)
                return send_file(io.BytesIO(placeholder), mimetype='image/svg+xml')
        else:
            # Last-resort: return an inline SVG placeholder so UI always shows something
            placeholder = _html_preview_placeholder_svg(abs_path.name)
            return send_file(io.BytesIO(placeholder), mimetype='image/svg+xml')

    # For image files, return the image directly (resized if needed)
    if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
        return send_file(str(abs_path), mimetype=f'image/{file_ext[1:]}')

    # Fallback
    return abort(404, description="Unsupported file type")

# Keep backward compatibility
@app.route('/api/html_thumbnail')
def api_html_thumbnail():
    """Legacy endpoint for HTML thumbnails - redirects to evidence_thumbnail."""
    return api_evidence_thumbnail()

def open_browser():
    """Function to open the browser to the dashboard URL."""
    print(">>> [DEBUG] Attempting to open web browser...")
    webbrowser.open_new("http://127.0.0.1:5000")

# --- HTML to Image Conversion for PDF ---
def html_to_image_for_pdf(html_abs_path: Path, width: int = 800, height: int = 600, full_page: bool = True):
    """Convert HTML file to image for PDF display using Playwright.
    Returns a PIL Image object that can be used in ReportLab PDF.
    
    Args:
        html_abs_path: Path to HTML file
        width: Viewport width
        height: Viewport height  
        full_page: Whether to capture full page (True) or just viewport (False)
    """
    try:
        if PLAYWRIGHT_AVAILABLE:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                
                # Use larger viewport for better content rendering
                viewport_width = max(width, 1200)  # Minimum 1200px width
                viewport_height = max(height, 800)  # Minimum 800px height
                
                page = browser.new_page(viewport={"width": viewport_width, "height": viewport_height})
                page.goto(html_abs_path.as_uri(), wait_until="load")
                
                # Wait for initial content to load
                page.wait_for_timeout(1000)
                
                # Wait for any charts or dynamic content to render
                try:
                    # Wait for common chart elements to be visible
                    page.wait_for_selector('canvas, svg, .chart, .pie-chart, .status-badge', timeout=5000)
                except:
                    # If no charts found, continue anyway
                    pass
                
                # Additional wait for any animations or dynamic content
                page.wait_for_timeout(2000)
                
                # Get actual page dimensions for full page capture
                if full_page:
                    # Get the actual content dimensions
                    page_width = page.evaluate("() => Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)")
                    page_height = page.evaluate("() => Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)")
                    
                    print(f"[DEBUG] Page dimensions: {page_width}x{page_height} pixels")
                    
                    # Ensure minimum dimensions
                    page_width = max(page_width, viewport_width)
                    page_height = max(page_height, viewport_height)
                    
                    # Update viewport to match content
                    page.set_viewport_size({"width": page_width, "height": page_height})
                    
                    # Wait a bit more for layout to settle
                    page.wait_for_timeout(1000)
                
                # Take screenshot with full page option
                screenshot_bytes = page.screenshot(full_page=full_page, type='png')
                browser.close()
                
                # Convert to PIL Image
                if PIL_AVAILABLE:
                    from io import BytesIO
                    img = PILImage.open(BytesIO(screenshot_bytes))
                    print(f"[DEBUG] Screenshot captured: {img.size[0]}x{img.size[1]} pixels")
                    return img
                else:
                    # If PIL not available, return None
                    return None
                    
    except Exception as e:
        print(f"[WARN] Playwright HTML to image conversion failed for {html_abs_path}: {e}")
        return None

def create_html_preview_image(html_abs_path: Path, max_width: int = 500, max_height: int = 400, full_page: bool = True):
    """Create a preview image from HTML file for PDF display.
    Returns a ReportLab Image object ready for PDF insertion.
    
    Args:
        html_abs_path: Path to HTML file
        max_width: Maximum width for PDF display
        max_height: Maximum height for PDF display
        full_page: Whether to capture full page (True) or just viewport (False)
    """
    try:
        # Convert HTML to PIL Image with full page capture
        pil_img = html_to_image_for_pdf(html_abs_path, max_width, max_height, full_page=full_page)
        
        if pil_img is None:
            # Fallback: create a placeholder image
            if PIL_AVAILABLE:
                pil_img = PILImage.new("RGB", (max_width, max_height), color=(245, 247, 250))
                draw = ImageDraw.Draw(pil_img)
                try:
                    font = ImageFont.load_default()
                except Exception:
                    font = None
                
                # Draw placeholder text
                text = "HTML Preview"
                filename = html_abs_path.name
                draw.text((20, max_height // 2 - 20), text, fill=(64, 64, 64), font=font)
                draw.text((20, max_height // 2 + 10), filename[:50], fill=(96, 96, 96), font=font)
            else:
                return None
        
        # Get original dimensions
        original_width, original_height = pil_img.size
        print(f"[DEBUG] HTML image captured: {original_width}x{original_height} pixels")
        
        # Calculate scaling to fit PDF dimensions while maintaining aspect ratio
        width_ratio = max_width / original_width
        height_ratio = max_height / original_height
        scale_ratio = min(width_ratio, height_ratio)
        
        # Ensure we don't scale up (only scale down if needed)
        if scale_ratio > 1:
            scale_ratio = 1
        
        new_width = int(original_width * scale_ratio)
        new_height = int(original_height * scale_ratio)
        
        print(f"[DEBUG] Scaled to PDF dimensions: {new_width}x{new_height} points")
        
        # Resize image if scaling is needed
        if scale_ratio != 1:
            pil_img = pil_img.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
        
        # Convert to RGB if necessary
        if pil_img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = PILImage.new('RGB', pil_img.size, (255, 255, 255))
            if pil_img.mode == 'P':
                pil_img = pil_img.convert('RGBA')
            rgb_img.paste(pil_img, mask=pil_img.split()[-1] if pil_img.mode in ('RGBA', 'LA') else None)
            pil_img = rgb_img
        
        # Save to temporary file and create ReportLab Image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_img:
            pil_img.save(temp_img.name, format='JPEG', quality=90, optimize=True, dpi=(150, 150))
            reportlab_img = ReportLabImage(temp_img.name, width=new_width, height=new_height)
            
            # Clean up temp file after ReportLab loads it
            try:
                os.unlink(temp_img.name)
            except:
                pass
                
            return reportlab_img
            
    except Exception as e:
        print(f"[ERROR] Failed to create HTML preview image for {html_abs_path}: {e}")
        return None

def clear_thumbnail_cache():
    """Clear all thumbnail cache to force regeneration.
    
    NEW STRUCTURE: results/YYYYMMDD_HHMMSS/FeatureName/TestCaseID/.thumbnails/file_hash.png
    """
    try:
        cleared_count = 0
        
        # Clear all .thumbnails folders in the new structure
        for thumb_folder in RESULTS_DIR.rglob(".thumbnails"):
            try:
                # Check if this is in the correct location
                # Should be: results/YYYYMMDD_HHMMSS/FeatureName/TestCaseID/.thumbnails/
                parent_path = thumb_folder.parent
                if parent_path.name == ".thumbnails":
                    # Skip old centralized structure
                    continue
                
                # Check if parent is a test case folder
                grandparent = parent_path.parent
                if grandparent and grandparent.parent:
                    # Should be: results/YYYYMMDD_HHMMSS/FeatureName/TestCaseID/.thumbnails/
                    # Check if grandparent.parent is timestamp folder
                    timestamp_folder = grandparent.parent
                    if timestamp_folder.name and any(char.isdigit() for char in timestamp_folder.name):
                        # This is correct structure, clear it
                        import shutil
                        shutil.rmtree(thumb_folder)
                        cleared_count += 1
                        print(f"[INFO] Cleared thumbnail folder: {thumb_folder}")
            except Exception as e:
                print(f"[WARN] Error clearing thumbnail folder {thumb_folder}: {e}")
        
        # Also clear old centralized structure if it exists
        old_thumb_root = RESULTS_DIR / ".thumbnails"
        if old_thumb_root.exists():
            try:
                import shutil
                shutil.rmtree(old_thumb_root)
                print(f"[INFO] Cleared old centralized thumbnail structure: {old_thumb_root}")
            except Exception as e:
                print(f"[WARN] Could not clear old centralized structure: {e}")
        
        if cleared_count > 0:
            print(f"[INFO] Cleared {cleared_count} thumbnail folders")
            print(f"[INFO] All thumbnails will be regenerated with new structure")
        else:
            print(f"[INFO] No thumbnail folders found to clear")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to clear thumbnail cache: {e}")
        return False

def force_cleanup_and_restart():
    """Force cleanup of all thumbnails and prepare for fresh start.
    
    NEW STRUCTURE: results/YYYYMMDD_HHMMSS/FeatureName/TestCaseID/.thumbnails/file_hash.png
    """
    try:
        print("[FORCE_CLEANUP] Starting forced cleanup of all thumbnails...")
        
        # First, try normal cleanup
        cleanup_success = cleanup_old_thumbnail_structure()
        migration_success = migrate_old_thumbnails()
        
        # Then, clear everything if needed
        clear_success = clear_thumbnail_cache()
        
        # REMOVED: No need to create fresh thumbnail directory
        # Thumbnails will be created on-demand in their respective test case folders
        
        print(f"[FORCE_CLEANUP] All thumbnails have been cleared")
        print(f"[FORCE_CLEANUP] New thumbnails will be created in TestCaseID/.thumbnails/ when needed")
        
        return {
            "cleanup_success": cleanup_success,
            "migration_success": migration_success,
            "clear_success": clear_success,
            "message": "All thumbnails cleared, will be regenerated in new structure"
        }
    except Exception as e:
        print(f"[ERROR] Force cleanup failed: {e}")
        return {"error": str(e)}

def get_thumbnail_info():
    """Get information about thumbnail cache usage.
    
    NEW STRUCTURE: results/YYYYMMDD_HHMMSS/FeatureName/TestCaseID/.thumbnails/file_hash.png
    """
    try:
        total_files = 0
        total_size = 0
        folders = []
        
        # Scan for .thumbnails folders in the new structure
        for thumb_folder in RESULTS_DIR.rglob(".thumbnails"):
            try:
                # Check if this is in the correct location
                # Should be: results/YYYYMMDD_HHMMSS/FeatureName/TestCaseID/.thumbnails/
                parent_path = thumb_folder.parent
                if parent_path.name == ".thumbnails":
                    # Skip old centralized structure
                    continue
                
                # Check if parent is a test case folder
                grandparent = parent_path.parent
                if grandparent and grandparent.parent:
                    # Should be: results/YYYYMMDD_HHMMSS/FeatureName/TestCaseID/.thumbnails/
                    # Check if grandparent.parent is timestamp folder
                    timestamp_folder = grandparent.parent
                    if timestamp_folder.name and any(char.isdigit() for char in timestamp_folder.name):
                        # This is correct structure, count files
                        folder_info = f"{timestamp_folder.name}/{grandparent.name}/{parent_path.name}"
                        folders.append(folder_info)
                        
                        # Count files in this .thumbnails folder
                        for file_item in thumb_folder.iterdir():
                            if file_item.is_file() and file_item.suffix == '.png':
                                total_files += 1
                                total_size += file_item.stat().st_size
            except Exception as e:
                print(f"[WARN] Error scanning thumbnail folder {thumb_folder}: {e}")
        
        cache_size_mb = total_size / (1024 * 1024)
        
        return {
            "total_thumbnails": total_files,
            "cache_size_mb": round(cache_size_mb, 2),
            "folders": sorted(folders),
            "structure": "NEW: TestCaseID/.thumbnails/ in each test case folder"
        }
    except Exception as e:
        print(f"[ERROR] Failed to get thumbnail info: {e}")
        return {"error": str(e)}

@app.route('/api/thumbnail_info')
def api_thumbnail_info():
    """API endpoint to get thumbnail cache information."""
    return jsonify(get_thumbnail_info())

@app.route('/api/clear_thumbnails', methods=['POST'])
def api_clear_thumbnails():
    """API endpoint to clear thumbnail cache."""
    success = clear_thumbnail_cache()
    return jsonify({"success": success, "message": "Thumbnail cache cleared" if success else "Failed to clear cache"})

def cleanup_old_thumbnail_structure():
    """Clean up old thumbnail structure that doesn't follow the new organized format.
    
    NEW STRUCTURE: results/YYYYMMDD_HHMMSS/FeatureName/TestCaseID/.thumbnails/file_hash.png
    OLD STRUCTURE: results/.thumbnails/YYYYMMDD_HHMMSS/FeatureName/file_hash.png
    """
    try:
        # Clean up old centralized .thumbnails folder structure
        old_thumb_root = RESULTS_DIR / ".thumbnails"
        if old_thumb_root.exists():
            try:
                import shutil
                shutil.rmtree(old_thumb_root)
                print(f"[CLEANUP] Removed old centralized thumbnail structure: {old_thumb_root}")
                print(f"[CLEANUP] New structure will be: TestCaseID/.thumbnails/ in each test case folder")
            except Exception as e:
                print(f"[WARN] Could not remove old thumbnail structure: {e}")
        
        # Clean up any orphaned .thumbnails folders in wrong locations
        cleaned_orphans = 0
        for item in RESULTS_DIR.rglob(".thumbnails"):
            try:
                # Check if this .thumbnails folder is in the correct location
                # Should be: results/YYYYMMDD_HHMMSS/FeatureName/TestCaseID/.thumbnails/
                parent_path = item.parent
                if parent_path.name == ".thumbnails":
                    # This is the old centralized structure, already cleaned above
                    continue
                
                # Check if parent is a test case folder (should have timestamp/feature structure)
                grandparent = parent_path.parent
                if grandparent and grandparent.parent:
                    # Should be: results/YYYYMMDD_HHMMSS/FeatureName/TestCaseID/.thumbnails/
                    # Check if grandparent.parent is timestamp folder
                    timestamp_folder = grandparent.parent
                    if timestamp_folder.name and any(char.isdigit() for char in timestamp_folder.name):
                        # This looks like correct structure, keep it
                        continue
                
                # This .thumbnails folder is in wrong location, remove it
                try:
                    shutil.rmtree(item)
                    cleaned_orphans += 1
                    print(f"[CLEANUP] Removed orphaned .thumbnails folder: {item}")
                except Exception as e:
                    print(f"[WARN] Could not remove orphaned .thumbnails folder {item}: {e}")
                    
            except Exception as e:
                print(f"[WARN] Error checking .thumbnails folder {item}: {e}")
        
        if cleaned_orphans > 0:
            print(f"[CLEANUP] Cleaned up {cleaned_orphans} orphaned .thumbnails folders")
        else:
            print(f"[CLEANUP] No orphaned .thumbnails folders found")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to cleanup old thumbnail structure: {e}")
        return False

def migrate_old_thumbnails():
    """Attempt to migrate old thumbnails to new structure if possible.
    
    NEW STRUCTURE: results/YYYYMMDD_HHMMSS/FeatureName/TestCaseID/.thumbnails/file_hash.png
    """
    try:
        # Since we're changing to a completely different structure,
        # we can't reliably migrate old thumbnails. Just clean them up.
        print(f"[MIGRATION] New structure requires complete regeneration of thumbnails")
        print(f"[MIGRATION] Old thumbnails cannot be migrated, they will be regenerated on-demand")
        
        # Clean up any remaining old structure
        old_thumb_root = RESULTS_DIR / ".thumbnails"
        if old_thumb_root.exists():
            try:
                import shutil
                shutil.rmtree(old_thumb_root)
                print(f"[MIGRATION] Removed remaining old thumbnail structure")
            except Exception as e:
                print(f"[WARN] Could not remove remaining old structure: {e}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to migrate old thumbnails: {e}")
        return False

@app.route('/api/cleanup_old_thumbnails', methods=['POST'])
def api_cleanup_old_thumbnails():
    """API endpoint to cleanup old thumbnail structure."""
    cleanup_success = cleanup_old_thumbnail_structure()
    migration_success = migrate_old_thumbnails()
    
    return jsonify({
        "success": cleanup_success and migration_success,
        "cleanup_success": cleanup_success,
        "migration_success": migration_success,
        "message": "Old thumbnail cleanup completed" if (cleanup_success and migration_success) else "Some cleanup operations failed"
    })

@app.route('/api/thumbnail_status')
def api_thumbnail_status():
    """API endpoint to get comprehensive thumbnail status including cleanup info."""
    cache_info = get_thumbnail_info()
    
    # Check for old structure
    thumb_root = RESULTS_DIR / ".thumbnails"
    old_files_count = 0
    old_dirs_count = 0
    
    if thumb_root.exists():
        for item in thumb_root.iterdir():
            if item.is_file() and item.suffix == '.png':
                if '_' in item.stem:
                    old_files_count += 1
            elif item.is_dir():
                dir_name = item.name
                if not (dir_name.replace('_', '').replace('-', '').isdigit() or 
                       any(char.isdigit() for char in dir_name)):
                    old_dirs_count += 1
    
    return jsonify({
        "cache_info": cache_info,
        "old_structure": {
            "old_files": old_files_count,
            "old_directories": old_dirs_count,
            "needs_cleanup": old_files_count > 0 or old_dirs_count > 0
        },
        "recommendations": {
            "cleanup_needed": old_files_count > 0 or old_dirs_count > 0,
            "message": f"Found {old_files_count} old files and {old_dirs_count} old directories that should be cleaned up" if (old_files_count > 0 or old_dirs_count > 0) else "No cleanup needed"
        }
    })

@app.route('/api/force_cleanup_thumbnails', methods=['POST'])
def api_force_cleanup_thumbnails():
    """API endpoint to force cleanup all thumbnails and restart fresh."""
    result = force_cleanup_and_restart()
    return jsonify(result)

if __name__ == "__main__":
    print("🚀 Starting Dashboard Report Server...")
    print(f"📁 Project Root: {PROJECT_ROOT}")
    print(f"📊 Results Directory: {RESULTS_DIR}")
    
    # Verify font settings
    verify_font_settings()
    
    # Ensure Thai fonts are registered for ReportLab
    print("\n" + "="*60)
    print("THAI FONT SETUP")
    print("="*60)
    success = ensure_thai_fonts()
    print(f"Thai font setup result: {success}")
    print("="*60)
    
    # Check thumbnail capabilities
    print("\n" + "="*60)
    print("THUMBNAIL CAPABILITIES")
    print("="*60)
    if PLAYWRIGHT_AVAILABLE:
        print("✅ Playwright: Available for high-quality HTML thumbnails")
    else:
        print("❌ Playwright: Not available")
        print("   Install with: pip install playwright && playwright install chromium")
    
    if PIL_AVAILABLE:
        print("✅ PIL/Pillow: Available for fallback thumbnails")
    else:
        print("❌ PIL/Pillow: Not available")
        print("   Install with: pip install Pillow")
    
    if THUMBNAIL_CAPABLE:
        print("✅ Overall: Thumbnail generation is available")
    else:
        print("❌ Overall: No thumbnail generation capability")
        print("   Install either Playwright or PIL/Pillow")
    
    print("="*60)
    
    # Ensure thumbnail directory exists
    if THUMBNAIL_CAPABLE:
        # REMOVED: No need to create root thumbnail directory
        # Thumbnails will be created on-demand in TestCaseID/.thumbnails/ folders
        print(f"📸 Thumbnail system ready")
        print(f"📁 Thumbnails will be organized by test case folder structure")
        print(f"   NEW STRUCTURE: results/YYYYMMDD_HHMMSS/FeatureName/TestCaseID/.thumbnails/file_hash.png")
        
        # Clean up old thumbnail structure
        print("\n🧹 Cleaning up old thumbnail structure...")
        cleanup_success = cleanup_old_thumbnail_structure()
        if cleanup_success:
            print("✅ Old thumbnail structure cleanup completed")
        else:
            print("⚠️ Old thumbnail structure cleanup had issues")
        
        # Attempt to migrate old thumbnails
        print("🔄 Attempting to migrate old thumbnails...")
        migration_success = migrate_old_thumbnails()
        if migration_success:
            print("✅ Old thumbnail migration completed")
        else:
            print("⚠️ Old thumbnail migration had issues")
        
        # Test structured thumbnail creation
        try:
            test_html_path = RESULTS_DIR / "test_example.html"
            test_thumb_path = _get_thumbnail_path(test_html_path)
            print(f"🔍 Test thumbnail path structure: {test_thumb_path}")
            print(f"   This shows how thumbnails will be organized")
        except Exception as e:
            print(f"⚠️ Could not demonstrate thumbnail structure: {e}")
        
        # Show existing thumbnail cache info
        cache_info = get_thumbnail_info()
        if cache_info.get("total_thumbnails", 0) > 0:
            print(f"📊 Existing thumbnail cache: {cache_info['total_thumbnails']} files, {cache_info['cache_size_mb']} MB")
            if cache_info.get("folders"):
                print(f"📂 Cache folders: {', '.join(cache_info['folders'][:5])}{'...' if len(cache_info['folders']) > 5 else ''}")
        else:
            print(f"📊 No existing thumbnail cache found")
    
    print("="*60)
    
    print("\n🌐 Starting web server...")
    print("📱 Dashboard will be available at: http://127.0.0.1:5000")
    
    # Open browser after a short delay
    Timer(1.5, open_browser).start()
    
    # Start the Flask app
    app.run(debug=False, host='127.0.0.1', port=5000)
