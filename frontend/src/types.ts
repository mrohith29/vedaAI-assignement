export type BoundingBox = { x: number; y: number; width: number; height: number };
export type Region = { page: number; bbox: BoundingBox };

export type Question = {
  id: string;
  number: string;
  text: string;
  max_score: number | null;
  status: "answered" | "unanswered";
  answer_text: string;
  confidence: number;
  regions: Region[];
  score: number | null;
  feedback: string;
};

export type DocumentInfo = {
  filename: string;
  page_count: number;
  page_urls: string[];
};

export type Assessment = {
  id: string;
  status: "queued" | "processing" | "completed" | "failed";
  progress: number;
  stage: string;
  error: string | null;
  question_paper: DocumentInfo;
  answer_sheet: DocumentInfo;
  questions: Question[];
  unmatched_answers: Array<{ label: string; answer_text: string; regions: Region[] }>;
  overall_feedback: string;
};

