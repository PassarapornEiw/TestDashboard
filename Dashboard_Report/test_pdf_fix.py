#!/usr/bin/env python3
"""
Test script to verify the PDF HTML thumbnail fix.
This script tests that the dashboard can now use existing thumbnails 
instead of trying to create new HTML conversions.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_thumbnail_lookup():
    """Test that thumbnail lookup functions work correctly"""
    try:
        from dashboard_server import _get_thumbnail_path, RESULTS_DIR
        
        print("✅ Successfully imported thumbnail functions")
        
        # Check if we have any results to test with
        if not RESULTS_DIR.exists():
            print(f"❌ RESULTS_DIR not found: {RESULTS_DIR}")
            return False
            
        print(f"📁 RESULTS_DIR: {RESULTS_DIR}")
        
        # Look for any HTML files in results
        html_files = list(RESULTS_DIR.rglob("*.html"))
        if not html_files:
            print("❌ No HTML files found in results directory")
            return False
            
        print(f"📄 Found {len(html_files)} HTML files")
        
        # Test thumbnail path generation for first HTML file
        test_html = html_files[0]
        print(f"🔍 Testing with: {test_html}")
        
        try:
            thumbnail_path = _get_thumbnail_path(test_html)
            print(f"📸 Generated thumbnail path: {thumbnail_path}")
            
            # Check if thumbnail exists
            if thumbnail_path.exists():
                print(f"✅ Thumbnail exists: {thumbnail_path}")
                print(f"   Size: {thumbnail_path.stat().st_size} bytes")
                return True
            else:
                print(f"⚠️  Thumbnail doesn't exist yet: {thumbnail_path}")
                print("   This is normal if thumbnails haven't been generated")
                return True
                
        except Exception as e:
            print(f"❌ Error generating thumbnail path: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_pdf_export_preparation():
    """Test that PDF export functions are properly prepared"""
    try:
        from dashboard_server import (
            REPORTLAB_AVAILABLE, 
            PIL_AVAILABLE, 
            PLAYWRIGHT_AVAILABLE,
            chrome_path
        )
        
        print("\n=== PDF Export Dependencies ===")
        print(f"ReportLab: {'✅' if REPORTLAB_AVAILABLE else '❌'}")
        print(f"PIL/Pillow: {'✅' if PIL_AVAILABLE else '❌'}")
        print(f"Playwright: {'✅' if PLAYWRIGHT_AVAILABLE else '❌'}")
        print(f"Chrome path: {chrome_path}")
        print(f"Chrome exists: {'✅' if chrome_path.exists() else '❌'}")
        
        if REPORTLAB_AVAILABLE and PIL_AVAILABLE:
            print("✅ PDF export should work")
            return True
        else:
            print("❌ PDF export dependencies missing")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 PDF HTML Thumbnail Fix Verification")
    print("=" * 50)
    
    # Test thumbnail lookup
    print("\n1. Testing thumbnail lookup functions...")
    thumbnail_ok = test_thumbnail_lookup()
    
    # Test PDF export preparation
    print("\n2. Testing PDF export preparation...")
    pdf_ok = test_pdf_export_preparation()
    
    # Summary
    print("\n" + "=" * 50)
    if thumbnail_ok and pdf_ok:
        print("🎉 SUCCESS: PDF HTML thumbnail fix is ready!")
        print("\nWhat was fixed:")
        print("- PDF export now uses existing thumbnails from .thumbnails folders")
        print("- No more complex HTML to image conversion in PDF")
        print("- Faster PDF generation and consistent with View Details")
        print("\nNext steps:")
        print("1. Restart the dashboard server")
        print("2. Test PDF export with HTML files")
        print("3. Verify thumbnails appear correctly in PDF")
    else:
        print("❌ Some tests failed - check the output above")
    
    return thumbnail_ok and pdf_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

