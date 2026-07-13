# Manual Test Cases

## TC-1: Crop Recommendation
- **Module:** Crop Recommendation
- **Input:** N=40, P=80, K=20, pH=5.0
- **Expected Result:** Recommendation generated successfully.
- **Actual Result:** Recommendation generated successfully with fertilizer plan.
- **Status:** ✅ Pass

---

## TC-2: Input Validation
- **Module:** Input Validation
- **Input:** N=-10
- **Expected Result:** Nitrogen validation error displayed.
- **Actual Result:** Correct validation error displayed.
- **Status:** ✅ Pass

---

## TC-3: Input Validation
- **Module:** Input Validation
- **Input:** P=-15
- **Expected Result:** Phosphorus validation error displayed.
- **Actual Result:** Correct validation error displayed.
- **Status:** ✅ Pass

---

## TC-4: Input Validation
- **Module:** Input Validation
- **Input:** pH=16
- **Expected Result:** pH validation error displayed.
- **Actual Result:** Correct validation error displayed.
- **Status:** ✅ Pass

---

## TC-5: Input Validation
- **Module:** Input Validation
- **Input:** N=500
- **Expected Result:** High nitrogen warning displayed.
- **Actual Result:** Warning displayed successfully.
- **Status:** ✅ Pass

---

## TC-6: Dosage Calculator
- **Module:** Dosage Calculator
- **Input:** Farm Size = 2 acres
- **Expected Result:** Dosage calculated correctly.
- **Actual Result:** Total fertilizer requirement displayed correctly.
- **Status:** ✅ Pass