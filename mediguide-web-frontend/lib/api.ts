export type Citation = {
  source: string;
  snippet: string;
};

export type ChatResponse = {
  user_query: string;
  structured_symptoms: string;
  is_informational: boolean;
  answer: string;
  citations: Citation[];
  faithful: "Yes" | "No" | "Partially" | string;
  unsupported_claims: string[];
  needs_review: boolean;
  response_time_seconds: number;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.status = status;
  }
}

export async function askMediGuide(message: string): Promise<ChatResponse> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
  } catch {
    throw new ApiError(
      "Couldn't reach the MediGuide LK server. Check that the backend is running and NEXT_PUBLIC_API_URL is set correctly."
    );
  }

  if (!res.ok) {
    let detail = `Request failed (${res.status}).`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // ignore - use default message
    }
    throw new ApiError(detail, res.status);
  }

  return res.json();
}
