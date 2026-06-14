# Document Upload & Bibliography Citations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow users to upload local text files/documents to aid in research, and format cited references as a formal open bibliography section at the bottom of the rendered report.

**Architecture:** 
1. **7-Step Wizard (`frontend/src/app/research/page.tsx`)**:
   - Insert Step 4: Document Upload & Context. Use HTML5 `FileReader` client-side to read `.txt`, `.md`, `.json`, and `.csv` files directly into the research `context_text` payload.
   - Display a checklist of selected sources on the final Review step (Step 7) to show citations before launching.
2. **References Section (`frontend/src/app/research/[task_id]/page.tsx`)**:
   - Format citation URLs as a formal, static **References & Bibliography** section at the bottom of the paper sheet container, utilizing numbering (`[1]`, `[2]`) and clean links.

**Tech Stack:** Next.js, React, HTML5 FileReader API, Lucide Icons.

---

## Proposed Changes & Tasks

### Task 1: Refactor Wizard Stepper & Add Document Upload Step

**Files:**
- Modify: `frontend/src/app/research/page.tsx`

- [ ] **Step 1: Increase wizard steps to 7 and implement FileReader**
  Update the wizard stepper layout to render 7 steps, shifting subsequent steps down.
  Add a drag-and-drop area or standard file input in the new Step 4 that parses selected text files (.txt, .md, .json) and appends their contents to the `contextText` state.
  Also, update the final Review step (Step 7) to list the titles and domains of all curated selected sources.

  ```tsx
  // Segment of frontend/src/app/research/page.tsx
  // Add file reading handler:
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      if (file.name.endsWith('.json')) {
        try {
          // Format JSON prettily
          const parsed = JSON.parse(text);
          setContextText(JSON.stringify(parsed, null, 2));
        } catch {
          setContextText(text);
        }
      } else {
        setContextText(text);
      }
    };
    reader.readAsText(file);
  };
  ```

- [ ] **Step 2: Commit Wizard updates**
  ```bash
  git add frontend/src/app/research/page.tsx
  git commit -m "feat: add dedicated document upload wizard step and source checklist review"
  ```

---

### Task 2: Redesign Citations as Formal References Section

**Files:**
- Modify: `frontend/src/app/research/[task_id]/page.tsx`

- [ ] **Step 1: Replace collapsible citations details with a static bibliography**
  Edit the completed task view so that citations are rendered at the bottom of the document sheet as an open list under a formal `References & Bibliography` header, using standard document typography and numbered links.

  ```tsx
  // Segment of frontend/src/app/research/[task_id]/page.tsx
  {art.citations && art.citations.length > 0 && (
    <div className="px-10 md:px-14 py-8 border-t border-slate-100 bg-slate-50/30">
      <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 font-sans select-none">
        References & Cited Bibliography
      </h3>
      <ol className="space-y-3 font-sans text-xs text-slate-600 list-decimal pl-5">
        {art.citations.map((cite, i) => (
          <li key={i} className="leading-relaxed">
            <a 
              href={cite} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="text-indigo-650 hover:underline break-all font-medium"
            >
              {cite}
            </a>
          </li>
        ))}
      </ol>
    </div>
  )}
  ```

- [ ] **Step 2: Commit Citation updates**
  ```bash
  git add frontend/src/app/research/[task_id]/page.tsx
  git commit -m "style: render citations as an open bibliography reference section at document bottom"
  ```

---

## Verification Plan

### Automated Verification
- Verify compilation passes:
  `cd frontend; npm run build`

### Manual Verification
1. Boot backend: `uvicorn api:app --reload --port 8000`
2. Boot frontend: `cd frontend; npm run dev`
3. Load `http://localhost:3000/research`
4. Advance to **Step 4: Context & Document Upload**.
5. Upload a local `.txt` or `.md` file, verify its text content extracts and populates the text area.
6. Progress to **Step 7: Review**. Verify the chosen curated sources list displays correctly.
7. Launch deep research and monitor progress.
8. Once complete, verify the references display as an open bibliography list at the bottom of the document container.
