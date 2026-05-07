# Extractor Manual Test Results

**Test Date**: 2026-05-07  
**Tester**: Cloud Server AI  
**Status**: Ready for Manual Testing

---

## Test Plan

### Objective
Validate that the Extractor Skill can produce valid Style JSON from diverse image styles.

### Test Images (Recommended)

1. **Watercolor Landscape**
   - Style: Soft, painterly, natural colors
   - Expected: `material.type = "watercolor"`, moderate saturation

2. **Flat Vector Illustration**
   - Style: Clean lines, solid colors, minimal depth
   - Expected: `material.type = "flat"`, `line.type = "clean"`, low depth

3. **Ink Drawing**
   - Style: Bold lines, high contrast, minimal color
   - Expected: `line.type = "ink"`, high contrast, low saturation

4. **Oil Painting Portrait**
   - Style: Thick texture, rich colors, directional lighting
   - Expected: `material.type = "oil"`, high texture_strength

5. **Digital Concept Art**
   - Style: Clean digital rendering, detailed, studio lighting
   - Expected: `material.type = "digital_paint"`, `lighting.type = "studio"`

---

## Test Procedure

### For Each Image:

1. **Extract Style**
   - Open ChatGPT
   - Paste system prompt from `SKILL.md`
   - Upload image
   - Request extraction

2. **Save Output**
   - Save JSON to `test_results/test_N_extracted.json`
   - Save original image to `test_results/test_N_original.png`

3. **Validate Schema**
   ```bash
   python -c "
   from src.core.schema import validate_style_json
   import json
   
   with open('test_results/test_N_extracted.json') as f:
       style = json.load(f)
   
   result = validate_style_json(style)
   print('Valid:', result['valid'])
   if not result['valid']:
       print('Errors:', result['errors'])
   "
   ```

4. **Test Normalization**
   ```bash
   python -c "
   from src.core.engine import StyleEngine
   import json
   
   with open('test_results/test_N_extracted.json') as f:
       style = json.load(f)
   
   engine = StyleEngine()
   normalized = engine.normalize(style)
   
   print('Normalization successful')
   print('Already normalized:', engine.is_normalized(style))
   
   with open('test_results/test_N_normalized.json', 'w') as f:
       json.dump(normalized, f, indent=2)
   "
   ```

5. **Record Results**
   - Document any validation errors
   - Document any normalization issues
   - Note if extracted values seem reasonable

---

## Test Results

### Test 1: [Image Type]
**Status**: ⚪ Not Started

**Extracted Style**: N/A

**Schema Validation**: N/A

**Normalization**: N/A

**Notes**: N/A

---

### Test 2: [Image Type]
**Status**: ⚪ Not Started

**Extracted Style**: N/A

**Schema Validation**: N/A

**Normalization**: N/A

**Notes**: N/A

---

### Test 3: [Image Type]
**Status**: ⚪ Not Started

**Extracted Style**: N/A

**Schema Validation**: N/A

**Normalization**: N/A

**Notes**: N/A

---

### Test 4: [Image Type]
**Status**: ⚪ Not Started

**Extracted Style**: N/A

**Schema Validation**: N/A

**Normalization**: N/A

**Notes**: N/A

---

### Test 5: [Image Type]
**Status**: ⚪ Not Started

**Extracted Style**: N/A

**Schema Validation**: N/A

**Normalization**: N/A

**Notes**: N/A

---

## Summary

**Total Tests**: 5  
**Passed**: 0  
**Failed**: 0  
**Not Started**: 5

### Issues Found
(To be filled during testing)

### Recommendations
(To be filled after testing)

---

## Next Steps

After manual testing is complete:
1. Review all test results
2. Identify common extraction errors
3. Update system prompt if needed
4. Document best practices
5. Proceed to Phase 3 (Image Generator)

---

**Note**: This document will be updated by the user during manual testing.
