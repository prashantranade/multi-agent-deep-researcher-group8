# Design Spec: PDF Print Footer, Persona-Specific Suggestions, and Step Label Wraps

This specification details the changes needed to remove the `about:blank` footer from print-to-PDF reports, implement persona-specific suggested topics, and prevent step indicator text from wrapping.

## Proposed Changes

### 1. Print Layout CSS Update
* **File:** `frontend/src/app/research/[task_id]/page.tsx`
* **Change:** Add `@page { size: auto; margin: 0; }` to the print template stylesheet inside `handlePrint` to hide browser headers and footers. Add corresponding print media padding on the body element so content remains correctly spaced from page margins:
  ```css
  @page {
    size: auto;
    margin: 0;
  }
  @media print {
    body {
      padding: 20mm 15mm;
      max-width: none;
      margin: 0;
    }
  }
  ```

### 2. Suggested Topics per Persona
* **File:** `frontend/src/app/research/page.tsx`
* **Change:** Define a constant mapping `SUGGESTED_TOPICS` at the file scope and dynamically render these suggested topics in the Step 2 Topic selection card.
  * **Product Manager Suggestions:**
    * Comparison of LLM evaluation frameworks
    * B2B SaaS pricing model optimizations
  * **Content Creator Suggestions:**
    * SaaS content marketing trends for 2026
    * Reaching Gen Z through authentic brand storytelling
  * **Bharat Desha Suggestions:**
    * Jaipur cultural tourism itineraries
    * Ecotourism projects in Rajasthan

### 3. Step 4 Label Text Wrap Prevention
* **File:** `frontend/src/app/research/page.tsx`
* **Change:** Add the `whitespace-nowrap` CSS class to the step labels `span` element in the step indicator header (around line 196) to prevent multi-word step labels (like "Context Docs") from wrapping onto two lines.
  ```tsx
  <span className={`text-xs font-bold hidden md:inline whitespace-nowrap ...`}>
  ```
