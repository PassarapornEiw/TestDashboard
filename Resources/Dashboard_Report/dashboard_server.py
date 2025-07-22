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

# Check for required dependencies
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.platypus import Image as ReportLabImage
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.units import mm
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
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: PIL/Pillow not installed. Image processing will be disabled.")
    PIL_AVAILABLE = False

app = Flask(__name__)

# --- Configuration ---
# The directory of this server script
SERVER_DIR = Path(__file__).parent.resolve()
# The project root is two levels up (from /Resources/Dashboard_Report)
PROJECT_ROOT = SERVER_DIR.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

# --- Helper Functions ---
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

def calculate_table_column_widths(data, min_widths, max_widths, total_width):
    """Calculate responsive column widths based on content length."""
    if not data or len(data) < 2:  # Need at least header + 1 row
        return min_widths
    
    num_cols = len(data[0])
    col_lengths = [0] * num_cols
    
    # Calculate average content length for each column
    for row in data:
        for i, cell in enumerate(row):
            if i < num_cols:
                content_length = len(str(cell)) if cell else 0
                col_lengths[i] = max(col_lengths[i], content_length)
    
    # Calculate proportional widths based on content
    total_content_length = sum(col_lengths)
    if total_content_length == 0:
        return min_widths
    
    calculated_widths = []
    remaining_width = total_width
    
    for i, length in enumerate(col_lengths):
        proportion = length / total_content_length
        calculated_width = total_width * proportion
        
        # Apply min/max constraints
        if i < len(min_widths):
            calculated_width = max(calculated_width, min_widths[i])
        if i < len(max_widths):
            calculated_width = min(calculated_width, max_widths[i])
        
        calculated_widths.append(calculated_width)
        remaining_width -= calculated_width
    
    # Distribute any remaining width proportionally
    if remaining_width > 0:
        for i in range(len(calculated_widths)):
            calculated_widths[i] += remaining_width / len(calculated_widths)
    
    return calculated_widths

def create_wrapped_paragraph(text, style, max_width=None):
    """Create a Paragraph with proper word wrapping for table cells."""
    if not text or str(text).strip() == '':
        return Paragraph('', style)
    
    # Clean the text and ensure it's a string
    clean_text = str(text).replace('\n', '<br/>').replace('\r', '')
    
    # For very long text, insert soft breaks at reasonable points
    if len(clean_text) > 50:
        words = clean_text.split(' ')
        if len(words) > 8:
            # Insert line breaks every 8-10 words for better wrapping
            wrapped_words = []
            for i, word in enumerate(words):
                wrapped_words.append(word)
                if i > 0 and (i + 1) % 8 == 0 and i < len(words) - 1:
                    wrapped_words.append('<br/>')
            clean_text = ' '.join(wrapped_words)
    
    return Paragraph(clean_text, style)

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
        
        if df.empty:
            return None
        
        # Look for test case ID column (common variations)
        id_columns = ['Test Case ID', 'TestCaseID', 'Test Case', 'ID', 'TestCase', 'TestCaseNo']
        id_col = None
        for col in id_columns:
            if col in df.columns:
                id_col = col
                break
        
        # Look for description column (common variations)
        desc_columns = ['Test Case Description', 'TestCaseDescription', 'Description', 'Test Description', 'Name']
        desc_col = None
        for col in desc_columns:
            if col in df.columns:
                desc_col = col
                break
        
        if id_col and desc_col:
            # Convert test_case_id to string for comparison
            test_case_id_str = str(test_case_id).strip()
            
            # Find the row with matching test case ID
            df[id_col] = df[id_col].fillna('')
            matching_rows = df[safe_str_lower(df[id_col]).str.contains(test_case_id_str.lower(), case=False, na=False)]
            if not matching_rows.empty:
                desc_value = matching_rows.iloc[0][desc_col]
                return str(desc_value) if pd.notna(desc_value) else None
        
                    # Fallback: exact match
        for _, row in df.iterrows():
            row_id = row.get(id_col, '')
            if pd.notna(row_id) and str(row_id).strip() == test_case_id_str:
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
                
        if execute_column:
            # Keep rows where Execute column is 'y' (case-insensitive) and non-empty
            df[execute_column] = df[execute_column].fillna('')
            executable_df = df[safe_str_lower(df[execute_column]) == 'y'].copy()
        else:
            # If no Execute column, assume all tests are executable
            executable_df = df.copy()

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
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        # Determine status: only "passed" if there are actually executed tests with valid results and no failures
        if total == 0:
            status = "not_run"  # No tests were executed with valid pass/fail results
        elif failed == 0:
            status = "passed"   # All valid tests passed
        else:
            status = "failed"   # Some valid tests failed
        
        # Find associated images recursively in the feature directory and subdirectories
        excel_dir = excel_path_obj.parent  # This should be the feature folder (e.g., Transfer/)
        image_paths = []
        try:
            # Search for images in the feature directory and all subdirectories (TC001, TC002, etc.)
            image_extensions = ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp"]
            for ext in image_extensions:
                image_paths.extend(list(excel_dir.glob(f"**/{ext}")))
            
            print(f"[DEBUG] Found {len(image_paths)} images in {excel_dir}")
            for img in image_paths[:5]:  # Show first 5 for debugging
                print(f"[DEBUG] Image found: {img}")
                
        except Exception as e:
            print(f"Error searching for images in {excel_dir}: {e}")
            image_paths = []
        
        # Group images by test case (subfolder under feature)
        test_evidence = {}
        for img_path in image_paths:
            try:
                # The test case folder is the immediate parent of the image file, relative to the feature folder
                relative_path = img_path.relative_to(excel_dir)
                if len(relative_path.parts) > 1:
                    test_case_name = relative_path.parts[0]  # First level folder under feature (TC001, TC002, etc.)
                else:
                    test_case_name = "General" # Fallback for images in the root of the feature folder
                
                # Convert to path relative to project root for serving
                if PROJECT_ROOT in img_path.parents:
                    relative_img_path = str(img_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
                    if test_case_name not in test_evidence:
                        test_evidence[test_case_name] = []
                    test_evidence[test_case_name].append(relative_img_path)
                    print(f"[DEBUG] Added image to {test_case_name}: {relative_img_path}")
                else:
                    print(f"Image path not within project root: {img_path}")
                    
            except Exception as e:
                print(f"Could not process image path {img_path}: {e}")
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
            "image_files": [str(p.relative_to(PROJECT_ROOT)).replace("\\", "/") for p in image_paths if PROJECT_ROOT in p.parents], # Keep for fallback
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
        rows_data = df.head(10).fillna('').astype(str).to_dict('records')
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
        return jsonify({'error': 'PDF export not available. ReportLab not installed.'}), 500
        
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
        title_style.fontSize = 18  # Reduced from 24pt to 18pt as requested
        title_style.spaceAfter = 25
        title_style.textColor = colors.HexColor("#8B4513")
        title_style.fontName = 'Helvetica-Bold'  # Will switch to Arial below
        title_style.alignment = 1  # Center alignment
        
        # Banking professional heading style (Section headers)
        heading_style = styles['Heading1'].clone('BrandHeadingStyle')
        heading_style.fontSize = 14  # Reduced from 16pt to 14pt as requested
        heading_style.spaceAfter = 15
        heading_style.textColor = colors.HexColor("#8B4513")  # Deep brown-gold
        heading_style.fontName = 'Helvetica-Bold'  # Will switch to Arial below
        heading_style.borderWidth = 1
        heading_style.borderColor = colors.HexColor("#D4AF37")
        heading_style.borderPadding = 8
        heading_style.backColor = colors.HexColor("#FFF8DC")
        
        # Subheading style with golden accent
        subheading_style = styles['Heading2'].clone('BrandSubheadingStyle')
        subheading_style.fontSize = 12  # Reduced from 14pt to 12pt as requested
        subheading_style.spaceAfter = 12
        subheading_style.textColor = colors.HexColor("#DAA520")  # Golden rod
        subheading_style.fontName = 'Helvetica-Bold'  # Will switch to Arial below
        subheading_style.leftIndent = 10
        subheading_style.borderWidth = 0
        subheading_style.borderColor = colors.HexColor("#D4AF37")
        subheading_style.borderPadding = 5
        
        # Custom feature name style (Subsection headers)
        feature_style = styles['Heading2'].clone('FeatureStyle')
        feature_style.fontSize = 12  # Changed from 16pt to 12pt for subsection headers
        feature_style.spaceAfter = 15
        feature_style.textColor = colors.HexColor("#B8860B")
        feature_style.fontName = 'Helvetica-Bold'  # Will switch to Arial below
        feature_style.leftIndent = 5
        feature_style.borderWidth = 1
        feature_style.borderColor = colors.HexColor("#D4AF37")
        feature_style.borderPadding = 8
        feature_style.backColor = colors.HexColor("#FFFACD")
        
        # Professional normal text style (Test case descriptions, etc.)
        normal_style = styles['Normal'].clone('BrandNormalStyle')
        normal_style.fontSize = 10  # Reduced from 11pt to 10pt as requested
        normal_style.textColor = colors.HexColor("#2F4F4F")
        normal_style.fontName = 'Helvetica'  # Will switch to Arial below
        normal_style.leading = 12  # 1.2x line spacing (10pt * 1.2 = 12pt)
        
        # Create caption style for screenshot counts (9pt Regular as requested)
        caption_style = styles['Normal'].clone('CaptionStyle')
        caption_style.fontSize = 9  # Screenshot captions: 9pt Regular as requested
        caption_style.textColor = colors.HexColor("#666666")
        caption_style.fontName = 'Helvetica'  # Will be Arial when supported
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
            ["Generated:", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ["Report Period:", "Latest Run" if scope == "latest" else f"{start_date or 'Start'} to {end_date or 'End'}"],
            ["Total Features:", str(sum(len(run['features']) for run in runs_to_export))],
            ["Execution Time:", runs_to_export[0]['timestamp'] if runs_to_export else "N/A"]
        ]
        
        metadata_table = Table(metadata_data, colWidths=[140, 220])
        metadata_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),  # Will be Arial-Bold when supported
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
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                
                # Data row styling with color coding
                ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
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
                feature_key = f"{feature['feature_name']}_{run['timestamp']}"
                if feature_key not in unique_features:
                    unique_features[feature_key] = feature
        
        if unique_features:
            # Create table data with Paragraph objects for better text wrapping
            feature_table_data = [["Feature", "Status", "Total\nExecuted", "Passed", "Failed", "Pass\nRate"]]
            
            # Create cell styles for different column types
            feature_name_style = normal_style.clone('FeatureNameStyle')
            feature_name_style.fontSize = 9
            feature_name_style.fontName = 'Helvetica-Bold'
            feature_name_style.textColor = colors.HexColor("#8B4513")
            feature_name_style.alignment = 0  # Left align
            
            status_style = normal_style.clone('StatusStyle')
            status_style.fontSize = 9
            status_style.fontName = 'Helvetica-Bold'
            status_style.alignment = 1  # Center align
            
            number_style = normal_style.clone('NumberStyle')
            number_style.fontSize = 9
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
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 9),
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                
                # Data rows styling with proper alignment
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,1), (-1,-1), 9),
                ('ALIGN', (0,1), (0,-1), 'LEFT'),    # Feature names left-aligned
                ('ALIGN', (1,1), (1,-1), 'CENTER'),  # Status centered
                ('ALIGN', (2,1), (-1,-1), 'CENTER'), # Numbers centered
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                
                # Feature column bold font for consistency
                ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
                
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
                            status_col = None
                            for col in df.columns:
                                if col.lower() in ['testresult', 'status', 'result']:
                                    status_col = col
                                    break
                            
                            name_col = None
                            for col in df.columns:
                                if col.lower() in ['testcasedescription', 'test case description', 'testcase', 'name']:
                                    name_col = col
                                    break
                            if not name_col:
                                name_col = df.columns[0]
                            
                            error_col = None
                            for col in df.columns:
                                if col.lower() in ['fail_description', 'testresult_description', 'result description', 'error', 'message', 'failure reason']:
                                    error_col = col
                                    break
                            
                            # Filter for executed tests only
                            execute_column = next((c for c in df.columns if c.lower() == 'execute'), None)
                            if execute_column:
                                df = df[df[execute_column].str.lower() == 'y'].copy()
                            
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
            failed_feature_style.fontName = 'Helvetica-Bold'
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
                # Create Paragraph objects for better text wrapping
                feature_style = normal_style.clone('FeatureWrapStyle')
                feature_style.fontSize = 9
                feature_style.textColor = colors.HexColor("#8B4513")
                feature_style.fontName = 'Helvetica-Bold'
                feature_para = Paragraph(str(case[0]), feature_style)
                
                # Test case with enhanced wrapping for long descriptions
                test_case_style = normal_style.clone('TestCaseWrapStyle')
                test_case_style.fontSize = 9
                test_case_style.leading = 11  # Better line spacing
                test_case_style.textColor = colors.HexColor("#2F4F4F")
                test_case_para = Paragraph(str(case[1]), test_case_style)
                
                # Fail description with word wrapping
                fail_desc_style = normal_style.clone('FailDescWrapStyle') 
                fail_desc_style.fontSize = 9
                fail_desc_style.textColor = colors.HexColor("#B71C1C")
                fail_desc_style.leading = 11
                fail_desc_para = Paragraph(str(case[2]), fail_desc_style)
                
                failed_table_data.append([feature_para, test_case_para, fail_desc_para])
            
            # Create failed cases table with improved column widths
            failed_table = Table(failed_table_data, colWidths=[80, 180, 160], repeatRows=1)
            failed_table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#8B4513")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 9),
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                
                # Data rows styling with improved font size
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,1), (-1,-1), 9),  # Increased from 8pt to 9pt
                ('ALIGN', (0,1), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                
                # Professional borders and colors
                ('BOX', (0,0), (-1,-1), 2, colors.HexColor("#D4AF37")),
                ('INNERGRID', (0,0), (-1,-1), 1, colors.HexColor("#D4AF37")),
                ('LINEBELOW', (0,0), (-1,0), 2, colors.HexColor("#B8860B")),
                
                # Alternating row colors
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFEF7"), colors.HexColor("#FFF8DC")]),
                
                # Enhanced padding for better text spacing and multi-line support
                ('TOPPADDING', (0,0), (-1,0), 8),      # Header padding
                ('BOTTOMPADDING', (0,0), (-1,0), 8),   # Header padding
                ('TOPPADDING', (0,1), (-1,-1), 10),    # Data rows - more space for wrapped text
                ('BOTTOMPADDING', (0,1), (-1,-1), 10), # Data rows - more space for wrapped text
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ]))
            elements.append(failed_table)
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
                            execute_column = next((c for c in df.columns if c.lower() == 'execute'), None)
                            if execute_column:
                                df = df[df[execute_column].str.lower() == 'y'].copy()
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
                                test_case_style.fontName = 'Helvetica-Bold'
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
                                                error_style.fontName = 'Helvetica-Bold'
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
                                
                                # Handle screenshots
                                if images:
                                    # Filter images to only include those with "PDF" in the filename
                                    pdf_images = [img for img in images if 'PDF' in img.upper()]
                                    
                                    elements.append(Paragraph(f"Total Screenshots: {len(pdf_images)}", caption_style))
                                    elements.append(Spacer(1, 8))
                                    
                                    # --- Centered high-quality image grid ---
                                    if pdf_images:
                                        # Process images in batches to create centered layout
                                        for i in range(0, len(pdf_images), 2):
                                            batch_images = pdf_images[i:i+2]
                                            grid_imgs = []
                                            
                                            for img_path in batch_images:
                                                img_abs = PROJECT_ROOT / img_path
                                                if img_abs.exists():
                                                    try:
                                                        # Use PIL Image to process, ReportLab Image for PDF
                                                        if PIL_AVAILABLE:
                                                            with PILImage.open(str(img_abs)) as pil_img:
                                                                # Calculate optimal size maintaining aspect ratio
                                                                original_width, original_height = pil_img.size
                                                                max_width, max_height = 320, 240  # Moderate size for better layout
                                                                
                                                                # Calculate scaling factor to maintain aspect ratio
                                                                width_ratio = max_width / original_width
                                                                height_ratio = max_height / original_height
                                                                scale_ratio = min(width_ratio, height_ratio)
                                                                
                                                                new_width = int(original_width * scale_ratio)
                                                                new_height = int(original_height * scale_ratio)
                                                                
                                                                # Resize with high-quality resampling
                                                                pil_img = pil_img.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
                                                                
                                                                # Convert to RGB if necessary and save with high quality
                                                                if pil_img.mode in ('RGBA', 'LA', 'P'):
                                                                    rgb_img = PILImage.new('RGB', pil_img.size, (255, 255, 255))
                                                                    if pil_img.mode == 'P':
                                                                        pil_img = pil_img.convert('RGBA')
                                                                    rgb_img.paste(pil_img, mask=pil_img.split()[-1] if pil_img.mode in ('RGBA', 'LA') else None)
                                                                    pil_img = rgb_img
                                                                
                                                                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_img:
                                                                    pil_img.save(temp_img.name, format='JPEG', quality=95, optimize=True, dpi=(300, 300))
                                                                    # Use calculated dimensions with proper scaling
                                                                    grid_imgs.append(ReportLabImage(temp_img.name, width=new_width*0.8, height=new_height*0.8))
                                                        else:
                                                            # Fallback: use original image with moderate dimensions
                                                            grid_imgs.append(ReportLabImage(str(img_abs), width=240, height=180))
                                                    except Exception as e:
                                                        print(f"Error processing image {img_path}: {e}")
                                                        grid_imgs.append(Paragraph(f"Error loading image: {img_path}", normal_style))
                                                else:
                                                    grid_imgs.append(Paragraph(f"Image not found: {img_path}", normal_style))
                                            
                                            # Create table with appropriate column configuration
                                            if len(batch_images) == 1:
                                                # Single image - center it
                                                img_table = Table([grid_imgs], colWidths=[250])
                                                img_table.setStyle(TableStyle([
                                                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                                                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                                                    ('TOPPADDING', (0,0), (-1,-1), 10),
                                                    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                                                ]))
                                            else:
                                                # Two images - balanced layout with margins
                                                img_table = Table([grid_imgs], colWidths=[250, 250])
                                                img_table.setStyle(TableStyle([
                                                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                                    ('LEFTPADDING', (0,0), (-1,-1), 15),
                                                    ('RIGHTPADDING', (0,0), (-1,-1), 15),
                                                    ('TOPPADDING', (0,0), (-1,-1), 10),
                                                    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                                                ]))
                                            
                                            elements.append(img_table)
                                            elements.append(Spacer(1, 15))
                                    else:
                                        elements.append(Paragraph("No PDF images available for this test case.", caption_style))
                                else:
                                    # No matching screenshot folder found - show "No screenshot found"
                                    elements.append(Paragraph("Screenshots: No screenshot found", caption_style))
                                
                                elements.append(Spacer(1, 20))
                    else:
                        elements.append(Paragraph("No test case data available from Excel file.", normal_style))
                    
                    # Add page break between features for better organization
                    elements.append(PageBreak())

        # === FOOTER ===
        # Create footer style (8pt Regular as requested)
        footer_style = styles['Normal'].clone('FooterStyle')
        footer_style.fontSize = 8  # Footer information: 8pt Regular as requested
        footer_style.textColor = colors.HexColor("#666666")
        footer_style.fontName = 'Helvetica'  # Will be Arial when supported
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
        status_suffix = "PASS" if overall_status == "PASSED" else "FAIL"
        filename = f"TestReport_{timestamp}_{status_suffix}.pdf"
        
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')
        
    except Exception as e:
        print(f"PDF Export Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# --- Static File and Results Serving ---
# This route serves images and other files from the 'results' directory
@app.route('/results/<path:filepath>')
def serve_results(filepath):
    return send_from_directory(RESULTS_DIR, filepath)

def open_browser():
    """Function to open the browser to the dashboard URL."""
    print(">>> [DEBUG] Attempting to open web browser...")
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    print("🚀 Starting Test Dashboard Server...")
    print(f"Project Root: {PROJECT_ROOT}")
    print("🌐 Dashboard will open automatically at: http://127.0.0.1:5000")
    
    # Check dependencies
    missing_deps = []
    if not REPORTLAB_AVAILABLE:
        missing_deps.append("reportlab")
    if not MATPLOTLIB_AVAILABLE:
        missing_deps.append("matplotlib")
    if not PIL_AVAILABLE:
        missing_deps.append("Pillow")
    
    if missing_deps:
        print(f"💡 To install missing dependencies: pip install {' '.join(missing_deps)}")
    
    Timer(3, open_browser).start()
    app.run(debug=True, port=5000, use_reloader=False) 
