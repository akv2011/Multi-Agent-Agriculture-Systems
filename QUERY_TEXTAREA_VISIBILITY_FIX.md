# Query Textarea Visibility Fix

## Problem
The query textarea had dark/invisible text on dark background, making it impossible to read what users were typing.

## Root Cause
The global CSS in `index.css` sets the default text color to white:
```css
:root {
  color: rgba(255, 255, 255, 0.87);
}
```

This was being inherited by the textarea, causing white text on white background.

## Solution Applied

### 1. Enhanced CSS Styles
Updated `frontend/src/components/SimpleDemoInterface.css`:
- Added explicit `color: #2c3e50 !important` (dark blue-gray)
- Added explicit `background-color: #ffffff !important` (white)
- Added `!important` flags to override global styles
- Added multiple selector specificity levels
- Enhanced placeholder color visibility

### 2. Inline Style Backup
Added inline styles to the textarea in `SimpleDemoInterface.tsx`:
- Inline styles have highest specificity
- Guarantees text visibility regardless of CSS cascade issues
- Dark text (#2c3e50) on white background (#ffffff)

### 3. Enhanced Visual Design
- Improved font weight (500) for better readability
- Better border styling and focus states
- Enhanced placeholder text contrast

## Result
- **Before**: White text on white background (invisible)
- **After**: Dark blue-gray text on white background (highly visible)
- **Fallback**: Inline styles ensure it always works

## Testing
1. Navigate to the query tab
2. Click in the textarea
3. Type text - should now be clearly visible
4. Text should be dark blue-gray color on white background

The fix uses both CSS classes and inline styles to ensure maximum compatibility and visibility across different browsers and themes.
