import type { Assessment } from "./types";

export const demoAssessment: Assessment = {
  id: "demo",
  status: "completed",
  progress: 100,
  stage: "Review ready",
  error: null,
  question_paper: { filename: "physics-question-paper.pdf", page_count: 1, page_urls: ["/demo-question.svg"] },
  answer_sheet: { filename: "riya-answer-sheet.pdf", page_count: 2, page_urls: ["/demo-answer-1.svg", "/demo-answer-2.svg"] },
  questions: [
    {
      id: "1 (a)", number: "1 (a)", max_score: 2, score: 2, status: "answered", confidence: 0.98,
      text: "State Newton's first law of motion.",
      answer_text: "An object remains at rest or in uniform motion unless acted upon by an external force.",
      feedback: "Correct and clearly stated.",
      regions: [{ page: 1, bbox: { x: 0.095, y: 0.12, width: 0.82, height: 0.16 } }],
    },
    {
      id: "1 (b)", number: "1 (b)", max_score: 3, score: 2, status: "answered", confidence: 0.94,
      text: "A 5 kg body accelerates at 2 m/s². Calculate the force acting on it.",
      answer_text: "Using F = ma, F = 5 × 2 = 10 N.",
      feedback: "Correct method and final unit.",
      regions: [{ page: 1, bbox: { x: 0.09, y: 0.36, width: 0.82, height: 0.2 } }],
    },
    {
      id: "2", number: "2", max_score: 5, score: 4, status: "answered", confidence: 0.9,
      text: "Explain conservation of momentum with a suitable example.",
      answer_text: "Total momentum before and after a collision remains equal when no external force acts. Example and working continue on page 2.",
      feedback: "Good explanation; state that the system must be isolated.",
      regions: [
        { page: 1, bbox: { x: 0.09, y: 0.67, width: 0.82, height: 0.23 } },
        { page: 2, bbox: { x: 0.09, y: 0.11, width: 0.82, height: 0.3 } },
      ],
    },
    {
      id: "3", number: "3", max_score: 4, score: null, status: "unanswered", confidence: 0,
      text: "Draw and label the velocity-time graph for uniform acceleration.",
      answer_text: "", feedback: "No answer was identified.", regions: [],
    },
  ],
  unmatched_answers: [{
    label: "Unlabelled working", answer_text: "v = u + at", regions: [{ page: 2, bbox: { x: 0.1, y: 0.63, width: 0.8, height: 0.12 } }]
  }],
  overall_feedback: "Strong grasp of mechanics. Review the conditions required for conservation laws and complete all diagram questions.",
};

