# Manual Test Cases

## TC-1: Crop Recommendation
- Module: Crop Recommendation
- Input:
  - N=40
  - P=80
  - K=20
  - Temperature=25°C
  - Humidity=65%
  - pH=5.0
  - Rainfall=120 mm
- Expected Result:
  Crop recommendation is generated successfully.
- Actual Result:
  Crop recommendation generated successfully along with AI explanation.
- Status: ✅ Pass

---

## TC-2: Fertilizer Recommendation
- Module: Fertilizer Recommendation
- Input:
  - Crop = Rice
  - N=40
  - P=80
  - K=20
  - Soil Type = Loamy
  - Farm Size = 2 acres
- Expected Result:
  Fertilizer recommendation and dosage are generated.
- Actual Result:
  Fertilizer recommendation and dosage displayed correctly.
- Status: ✅ Pass

---

## TC-3: Invalid Nitrogen Input
- Module: Input Validation
- Input:
  N = -10
- Expected Result:
  Validation error displayed.
- Actual Result:
  Correct validation message displayed.
- Status: ✅ Pass

---

## TC-4: Invalid pH Input
- Module: Input Validation
- Input:
  pH = 16
- Expected Result:
  Validation error displayed.
- Actual Result:
  Correct validation message displayed.
- Status: ✅ Pass

---

## TC-5: Unrealistic Soil Reading
- Module: Input Validation
- Input:
  N = 500
- Expected Result:
  Warning that the reading is outside realistic agricultural ranges.
- Actual Result:
  Appropriate warning displayed.
- Status: ✅ Pass

---

## TC-6: Dosage Calculator
- Module: Dosage Calculator
- Input:
  Farm Size = 2 acres
- Expected Result:
  Fertilizer dosage calculated correctly.
- Actual Result:
  Dosage displayed correctly.
- Status: ✅ Pass

---

## TC-7: AI Explanation
- Module: Gemini AI Explanation
- Input:
  Generate explanation in Hindi.
- Expected Result:
  AI explanation generated in Hindi.
- Actual Result:
  Explanation generated successfully.
- Status: ✅ Pass

---

## TC-8: Language Selection
- Module: Multi-language Support
- Input:
  Select different supported languages.
- Expected Result:
  Explanation generated in the selected language.
- Actual Result:
  Language selection works correctly.
- Status: ✅ Pass