# PDF and DOCX Document Uploads Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Support PDF and DOCX document uploads in the guided wizard, parsing their text context using the backend FastAPI server to aid in deep research.

**Architecture:**
1. **FastAPI Upload Parser (`api.py`)**:
   - Expose `POST /api/context/upload` taking `UploadFile = File(...)`.
   - If the file is a PDF, use `pypdf.PdfReader` to extract text.
   - If the file is a DOCX, use `docx.Document` to extract text.
   - If plain text (txt, md, json), decode directly as text.
   - Return `{ "text": extracted_text }`.
2. **Frontend integration (`frontend/src/lib/api.ts` & `frontend/src/app/research/page.tsx`)**:
   - Expose `uploadDocument` in the api client.
   - If a binary file (PDF, DOCX) is uploaded in Step 4, show a loading spinner, call the backend parser, and populate the context text area.

**Tech Stack:** FastAPI, python-multipart, pypdf, python-docx, Next.js, React.

---

## Proposed Changes & Tasks

### Task 1: Implement Backend Context Upload Endpoint

**Files:**
- Modify: `api.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Update requirements.txt to include python-multipart**
  FastAPI requires `python-multipart` to parse form-data uploads.
  Add `python-multipart` to `requirements.txt`.
  Run: `pip install python-multipart`
  Expected: Package installs successfully.

- [ ] **Step 2: Add /api/context/upload in api.py**
  Add the endpoint to parse PDF, DOCX, and text files. Include `pypdf` and `docx` imports.
  
  ```python
  # Segment of api.py
  from fastapi import UploadFile, File
  import io
  import pypdf
  import docx

  @app.post("/api/context/upload")
  async def api_upload_context(file: UploadFile = File(...)):
      filename = file.filename or ""
      content = await file.read()
      text = ""
      
      try:
          if filename.endswith(".pdf"):
              reader = pypdf.PdfReader(io.BytesIO(content))
              pages_text = []
              for page in reader.pages:
                  t = page.extract_text()
                  if t:
                      pages_text.append(t)
              text = "\n".join(pages_text)
          elif filename.endswith(".docx"):
              doc = docx.Document(io.BytesIO(content))
              text = "\n".join([p.text for p in doc.paragraphs])
          else:
              # Fallback to plain text decoding
              text = content.decode("utf-8", errors="ignore")
              
          return {"text": text, "status": "success"}
      except Exception as e:
          raise HTTPException(status_code=400, detail=f"Failed to parse document: {str(e)}")
  ```

- [ ] **Step 3: Commit backend changes**
  ```bash
  git add api.py requirements.txt
  git commit -m "feat: add FastAPI endpoint to parse uploaded PDF and DOCX files"
  ```

---

### Task 2: Connect Frontend API and Add Upload Loader

**Files:**
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/app/research/page.tsx`

- [ ] **Step 1: Add uploadDocument wrapper in frontend/src/lib/api.ts**
  Create a fetch wrapper that formats the file into `FormData` and calls `/api/context/upload`.
  
  ```typescript
  // Segment of frontend/src/lib/api.ts
  export async function uploadDocument(file: File): Promise<{ text: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/context/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to upload and parse document');
    return res.json();
  }
  ```

- [ ] **Step 2: Update frontend/src/app/research/page.tsx to parse PDF/DOCX**
  Import `uploadDocument` in `page.tsx`. Add a `parsingDocument` loading state.
  Modify `handleFileUpload` to check the file extension:
  - If `.txt`, `.md`, `.json`, `.csv`: Parse client-side via `FileReader`.
  - If `.pdf`, `.docx`: Set `parsingDocument = true`, call `uploadDocument` backend endpoint, then set `contextText` to the response text.
  Display a nice loading spinner and message when `parsingDocument` is true.

  ```tsx
  // Segment of frontend/src/app/research/page.tsx
  // handleFileUpload update:
  const [parsingDocument, setParsingDocument] = useState(false);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setUploadedFileName(file.name);
    const filename = file.name.toLowerCase();
    
    if (filename.endsWith('.pdf') || filename.endsWith('.docx')) {
      setParsingDocument(true);
      try {
        const res = await uploadDocument(file);
        setContextText(res.text);
      } catch (err) {
        alert('Failed to parse document. Ensure the backend API server is running.');
        setUploadedFileName('');
      } finally {
        setParsingDocument(false);
      }
    } else {
      // client-side reader for txt, md, json, csv
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target?.result as string;
        setContextText(text);
      };
      reader.readAsText(file);
    }
  };
  ```

- [ ] **Step 3: Commit frontend changes**
  ```bash
  git add frontend/src/lib/api.ts frontend/src/app/research/page.tsx
  git commit -m "feat: integrate PDF and DOCX upload parsing in research wizard step"
  ```

---

## Verification Plan

### Automated Verification
- Verify Next.js compiles:
  `cd frontend; npm run build`
- Verify backend python tests continue to pass:
  `pytest`

### Manual Verification
1. Boot backend: `uvicorn api:app --reload --port 8000`
2. Boot frontend: `cd frontend; npm run dev`
3. Load `http://localhost:3000/research`
4. Advance to Step 4. Select a sample PDF or DOCX file.
5. Verify the loading spinner ("Extracting text context...") is displayed.
6. Verify the file's text contents are successfully populated into the textarea context box.
