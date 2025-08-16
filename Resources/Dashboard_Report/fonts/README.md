# Thai Fonts for PDF Generation

This directory contains Thai fonts needed for proper Thai text display in PDF reports.

## Required Fonts

### Option 1: THSarabunNew (Recommended)
- **THSarabunNew.ttf** - Regular weight
- **THSarabunNew Bold.ttf** - Bold weight

Download from: https://www.f0nt.com/release/th-sarabun-new/

### Option 2: Noto Sans Thai
- **NotoSansThai-Regular.ttf** - Regular weight  
- **NotoSansThai-Bold.ttf** - Bold weight

Download from: https://fonts.google.com/noto/specimen/Noto+Sans+Thai

## Installation Steps

1. Download the font files from the links above
2. Place both .ttf files in this `fonts` directory
3. Restart the dashboard server
4. Check console output for font loading confirmation

## File Structure
```
Resources/Dashboard_Report/fonts/
├── README.md
├── THSarabunNew.ttf          # Regular weight
├── THSarabunNew Bold.ttf     # Bold weight
└── (or Noto Sans Thai files)
```

## Verification

After placing the fonts, restart the server and look for this message in the console:
```
[INFO] ✅ Thai fonts loaded successfully: THSarabunNew
[INFO] Font files: THSarabunNew.ttf, THSarabunNew Bold.ttf
```

## Troubleshooting

If you see this warning:
```
[WARNING] ⚠️ No Thai fonts found!
```

1. Check that font files are in the correct directory
2. Verify file names match exactly (including spaces)
3. Ensure files are valid .ttf format
4. Restart the server after adding fonts

## Notes

- THSarabunNew is recommended for best Thai text rendering
- Font files must be in .ttf format
- Both regular and bold weights are required
- Server must be restarted after adding fonts
