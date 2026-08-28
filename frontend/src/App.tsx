import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowLeft, Check, ChevronDown, FileCheck2, FileText, LayoutDashboard,
  LoaderCircle, LogOut, Sparkles, Upload, UserRound, X, ZoomIn, ZoomOut,
} from "lucide-react";
import { demoAssessment } from "./demo";
import type { Assessment, Question } from "./types";

const API = import.meta.env.VITE_API_URL ?? "";

function App() {
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [questionFile, setQuestionFile] = useState<File | null>(null);
  const [answerFile, setAnswerFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!assessment || ["completed", "failed"].includes(assessment.status) || assessment.id === "demo") return;
    const timer = window.setInterval(async () => {
      try {
        const response = await fetch(`${API}/api/assessments/${assessment.id}`);
        if (!response.ok) throw new Error("The assessment could not be refreshed.");
        setAssessment(await response.json());
      } catch (exception) {
        setError(exception instanceof Error ? exception.message : "Something went wrong.");
      }
    }, 1200);
    return () => window.clearInterval(timer);
  }, [assessment?.id, assessment?.status]);

  async function submit() {
    if (!questionFile || !answerFile) return;
    setUploading(true);
    setError("");
    const form = new FormData();
    form.append("question_paper", questionFile);
    form.append("answer_sheet", answerFile);
    try {
      const response = await fetch(`${API}/api/assessments`, { method: "POST", body: form });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "The files could not be uploaded.");
      setAssessment(payload);
    } catch (exception) {
      setError(exception instanceof Error ? exception.message : "The upload failed.");
    } finally {
      setUploading(false);
    }
  }

  const reset = () => {
    setAssessment(null); setQuestionFile(null); setAnswerFile(null); setError("");
  };

  return (
    <div className="app-shell">
      <Sidebar onReset={reset} />
      <main className="main">
        <Topbar />
        {!assessment ? (
          <UploadScreen
            questionFile={questionFile} answerFile={answerFile} setQuestionFile={setQuestionFile}
            setAnswerFile={setAnswerFile} onSubmit={submit} uploading={uploading} error={error}
            onDemo={() => setAssessment(demoAssessment)}
          />
        ) : assessment.status !== "completed" ? (
          <Processing assessment={assessment} error={error} onReset={reset} />
        ) : <Results assessment={assessment} onReset={reset} />}
      </main>
    </div>
  );
}

function Sidebar({ onReset }: { onReset: () => void }) {
  return <aside className="sidebar">
    <button className="brand" onClick={onReset} aria-label="Start a new assessment">
      <span className="brand-mark"><Sparkles size={17} /></span><span>VedaAI</span>
    </button>
    <nav>
      <button className="nav-item active"><LayoutDashboard size={18} /> Assessment</button>
      <button className="nav-item" disabled><FileText size={18} /> History <span className="soon">Soon</span></button>
    </nav>
    <div className="sidebar-spacer" />
    <div className="mini-card">
      <div className="mini-icon"><Sparkles size={17} /></div>
      <strong>AI-powered review</strong>
      <p>Question extraction, answer mapping, and feedback in one flow.</p>
    </div>
    <button className="nav-item muted"><LogOut size={18} /> Exit workspace</button>
  </aside>;
}

function Topbar() {
  return <header className="topbar">
    <div className="mobile-brand"><Sparkles size={18}/> VedaAI</div>
    <div className="teacher"><div className="avatar"><UserRound size={17}/></div><span>Teacher workspace</span><ChevronDown size={15}/></div>
  </header>;
}

type UploadProps = {
  questionFile: File | null; answerFile: File | null;
  setQuestionFile: (file: File | null) => void; setAnswerFile: (file: File | null) => void;
  onSubmit: () => void; onDemo: () => void; uploading: boolean; error: string;
};

function UploadScreen(props: UploadProps) {
  return <section className="upload-page">
    <div className="eyebrow"><span /> New assessment</div>
    <h1>Upload <em>Question Paper &amp; Answer Sheet</em></h1>
    <p className="lede">Add both documents and let AI organize every response for a fast, focused review.</p>
    <div className="steps"><span className="current">1 <b>Upload</b></span><i /><span>2 <b>Extract</b></span><i /><span>3 <b>Review</b></span></div>
    <div className="upload-grid">
      <Dropzone label="Question paper" hint="Printed questions · PDF or image" file={props.questionFile} onFile={props.setQuestionFile} tone="coral" />
      <Dropzone label="Student answer sheet" hint="Handwritten answers · PDF or image" file={props.answerFile} onFile={props.setAnswerFile} tone="amber" />
    </div>
    {props.error && <div className="error-banner">{props.error}</div>}
    <button className="primary" disabled={!props.questionFile || !props.answerFile || props.uploading} onClick={props.onSubmit}>
      {props.uploading ? <LoaderCircle className="spin" size={18}/> : <Sparkles size={18}/>} Analyze assessment
    </button>
    <button className="demo-link" onClick={props.onDemo}>Or explore with a sample assessment</button>
    <p className="privacy"><Check size={14}/> Your documents are processed only for this review and are not persisted in a database.</p>
  </section>;
}

function Dropzone({ label, hint, file, onFile, tone }: { label: string; hint: string; file: File | null; onFile: (file: File | null) => void; tone: string }) {
  const input = useRef<HTMLInputElement>(null);
  const onDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    const next = event.dataTransfer.files[0];
    if (next) onFile(next);
  }, [onFile]);
  return <div className={`upload-card ${tone}`}>
    <div className="upload-card-head"><div className="file-icon"><FileText size={20}/></div><div><h2>{label}</h2><p>{hint}</p></div></div>
    <button className={`dropzone ${file ? "has-file" : ""}`} onClick={() => input.current?.click()} onDragOver={(event) => event.preventDefault()} onDrop={onDrop}>
      <input ref={input} type="file" accept="application/pdf,image/png,image/jpeg,image/webp" hidden onChange={(event) => onFile(event.target.files?.[0] ?? null)} />
      {file ? <><span className="file-ok"><FileCheck2 size={25}/></span><strong>{file.name}</strong><small>{formatBytes(file.size)} · Ready to upload</small><span className="replace">Choose another file</span></>
        : <><span className="upload-icon"><Upload size={25}/></span><strong>Drop your file here</strong><small>or click to browse · up to 20 MB</small></>}
    </button>
    {file && <button className="remove" aria-label={`Remove ${file.name}`} onClick={() => onFile(null)}><X size={16}/></button>}
  </div>;
}

function Processing({ assessment, error, onReset }: { assessment: Assessment; error: string; onReset: () => void }) {
  const failed = assessment.status === "failed";
  return <section className="processing">
    <div className={`processing-orbit ${failed ? "failed" : ""}`}>
      {failed ? <X size={34}/> : <Sparkles size={30}/>}<span /><span /><span />
    </div>
    <div className="eyebrow"><span /> {failed ? "Needs attention" : "AI analysis in progress"}</div>
    <h1>{failed ? "We couldn't finish this review" : assessment.stage}</h1>
    <p>{failed ? assessment.error : "We’re extracting every question, locating the student’s work, and checking the mapping."}</p>
    {!failed && <><div className="progress"><span style={{ width: `${assessment.progress}%` }}/></div><strong className="progress-label">{assessment.progress}%</strong></>}
    {(failed || error) && <button className="secondary" onClick={onReset}><ArrowLeft size={17}/> Back to upload</button>}
  </section>;
}

function Results({ assessment, onReset }: { assessment: Assessment; onReset: () => void }) {
  const [selectedId, setSelectedId] = useState(assessment.questions[0]?.id ?? "");
  const selected = assessment.questions.find((question) => question.id === selectedId) ?? assessment.questions[0];
  const answered = assessment.questions.filter((question) => question.status === "answered").length;
  const points = assessment.questions.reduce((sum, item) => sum + (item.score ?? 0), 0);
  const maxPoints = assessment.questions.reduce((sum, item) => sum + (item.max_score ?? 0), 0);
  return <section className="results-page">
    <div className="results-heading">
      <div><button className="back-link" onClick={onReset}><ArrowLeft size={16}/> New assessment</button><h1>Assessment <em>Review</em></h1><p>{assessment.answer_sheet.filename}</p></div>
      <div className="summary-pill"><b>{answered}/{assessment.questions.length}</b><span>answered</span>{maxPoints > 0 && <><i/><b>{points}/{maxPoints}</b><span>points</span></>}</div>
    </div>
    <div className="results-grid">
      <div className="question-panel">
        <div className="panel-title"><div><h2>Questions</h2><p>Select one to locate its answer</p></div><span>{assessment.questions.length}</span></div>
        <div className="question-list">
          {assessment.questions.map((question) => <QuestionCard key={question.id} question={question} selected={selected?.id === question.id} onClick={() => setSelectedId(question.id)} />)}
          {assessment.unmatched_answers.length > 0 && <div className="unmatched-note"><strong>{assessment.unmatched_answers.length} unmatched answer region{assessment.unmatched_answers.length === 1 ? "" : "s"}</strong><span>Kept separate so no work is incorrectly assigned.</span></div>}
        </div>
      </div>
      {selected && <AnswerViewer question={selected} document={assessment.answer_sheet} />}
    </div>
    {assessment.overall_feedback && <div className="overall"><Sparkles size={20}/><div><strong>AI review summary</strong><p>{assessment.overall_feedback}</p></div></div>}
  </section>;
}

function QuestionCard({ question, selected, onClick }: { question: Question; selected: boolean; onClick: () => void }) {
  return <button className={`question-card ${selected ? "selected" : ""}`} onClick={onClick}>
    <span className="q-number">{question.number}</span>
    <span className="q-copy"><strong>{question.text}</strong><small>{question.status === "answered" ? `${Math.round(question.confidence * 100)}% mapping confidence` : "No answer identified"}</small></span>
    <span className={`status-dot ${question.status}`}><Check size={13}/></span>
  </button>;
}

function AnswerViewer({ question, document }: { question: Question; document: Assessment["answer_sheet"] }) {
  const firstRegionPage = question.regions[0]?.page ?? 1;
  const [page, setPage] = useState(firstRegionPage);
  const [zoom, setZoom] = useState(1);
  const [imageLoaded, setImageLoaded] = useState(false);
  const viewportRef = useRef<HTMLDivElement>(null);
  useEffect(() => { setPage(question.regions[0]?.page ?? 1); setZoom(1); setImageLoaded(false); }, [question.id]);
  const regions = useMemo(() => question.regions.filter((region) => region.page === page), [question, page]);
  const mappedPages = useMemo(() => new Set(question.regions.map((region) => region.page)), [question.regions]);
  useEffect(() => {
    const viewport = viewportRef.current;
    const target = viewport?.querySelector<HTMLElement>(".highlight");
    if (!viewport || !target || !imageLoaded) return;
    viewport.scrollTo({
      top: Math.max(0, target.offsetTop - (viewport.clientHeight - target.offsetHeight) / 2),
      left: Math.max(0, target.offsetLeft - (viewport.clientWidth - target.offsetWidth) / 2),
      behavior: "smooth",
    });
  }, [question.id, page, zoom, imageLoaded]);
  return <div className="viewer-panel">
    <div className="viewer-toolbar">
      <div><h2>Answer sheet</h2><p>{document.filename}</p></div>
      <div className="viewer-actions">
        <span className={`region-indicator ${regions.length ? "mapped" : ""}`}>{regions.length ? `${regions.length} mapped region${regions.length === 1 ? "" : "s"}` : "No mapped region"}</span>
        <label>Page <select value={page} onChange={(event) => { setImageLoaded(false); setPage(Number(event.target.value)); }}>{document.page_urls.map((_, index) => <option key={index} value={index + 1}>{index + 1} of {document.page_count}{mappedPages.has(index + 1) ? " •" : ""}</option>)}</select></label>
        <button aria-label="Zoom out" onClick={() => setZoom((value) => Math.max(.7, value - .15))}><ZoomOut size={17}/></button>
        <button aria-label="Zoom in" onClick={() => setZoom((value) => Math.min(1.6, value + .15))}><ZoomIn size={17}/></button>
      </div>
    </div>
    <div className="document-viewport" ref={viewportRef}>
      <div className="paper" style={{ width: `${zoom * 100}%`, maxWidth: `${570 * zoom}px` }}>
        <img src={`${API}${document.page_urls[page - 1]}`} alt={`Answer sheet page ${page}`} onLoad={() => setImageLoaded(true)} />
        {regions.map((region, index) => <div className="highlight" aria-label={`Mapped answer region ${index + 1} for question ${question.number}`} key={index} style={{ left: `${region.bbox.x * 100}%`, top: `${region.bbox.y * 100}%`, width: `${region.bbox.width * 100}%`, height: `${region.bbox.height * 100}%` }}><span>Q{question.number}{regions.length > 1 ? ` · ${index + 1}` : ""}</span><i className="corner top-left"/><i className="corner top-right"/><i className="corner bottom-left"/><i className="corner bottom-right"/></div>)}
      </div>
      {question.status === "unanswered" && <div className="empty-overlay"><FileText size={28}/><strong>No matching answer found</strong><span>Review the sheet manually if needed.</span></div>}
    </div>
    <div className="answer-detail">
      <div className="answer-meta"><span className={`badge ${question.status}`}>{question.status}</span>{question.score !== null && <span className="score">{question.score}/{question.max_score ?? "—"} points</span>}{mappedPages.size > 1 && <span className="pages-badge">Spans {mappedPages.size} pages</span>}</div>
      {question.answer_text && <p className="transcript">“{question.answer_text}”</p>}
      <div className="feedback"><Sparkles size={16}/><span>{question.feedback || "No AI feedback available."}</span></div>
    </div>
  </div>;
}

function formatBytes(value: number) {
  if (value < 1024 * 1024) return `${Math.max(1, Math.round(value / 1024))} KB`;
  return `${(value / 1024 / 1024).toFixed(1)} MB`;
}

export default App;
