export const BASE_URL = "http://127.0.0.1:8000";
const DEFAULT_REQUEST_TIMEOUT_MS = 30000;
const GENERATE_REQUEST_TIMEOUT_MS = 180000;

export interface GenerateRequestPayload {
  interests: string[];
  style: string;
  scenario: string;
  target_user: string;
  input_text?: string;
}

export interface GenerateResponse {
  id: number;
  profile_summary: string;
  title: string;
  content: string;
  tags: string[];
  image_url: string;
  created_at: string;
}

export interface HistoryListItem {
  id: number;
  title: string;
  profile_summary: string;
  image_url: string;
  created_at: string;
}

export interface HistoryDetail extends GenerateResponse {
  interests: string;
  style: string;
  scenario: string;
  target_user: string;
  input_text?: string | null;
}

export interface DeleteHistoryResponse {
  message: string;
}

async function requestJson<T>(
  path: string,
  init?: RequestInit,
  timeoutMs: number = DEFAULT_REQUEST_TIMEOUT_MS,
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  let response: Response;

  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...init,
      signal: controller.signal,
    });
  } catch (error) {
    window.clearTimeout(timeoutId);

    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error(`Request timeout after ${timeoutMs}ms`);
    }

    throw error;
  }

  window.clearTimeout(timeoutId);

  if (!response.ok) {
    let message = "请求失败，请稍后重试。";

    try {
      const errorData = (await response.json()) as { detail?: string };
      if (errorData.detail) {
        message = errorData.detail;
      }
    } catch {
      // Keep the default message if the error response is not JSON.
    }

    throw new Error(message);
  }

  return (await response.json()) as T;
}

export function buildImageUrl(imageUrl: string) {
  if (!imageUrl) {
    return "";
  }

  if (imageUrl.startsWith("http://") || imageUrl.startsWith("https://")) {
    return imageUrl;
  }

  return `${BASE_URL}${imageUrl}`;
}

export function generateContent(payload: GenerateRequestPayload) {
  return requestJson<GenerateResponse>(
    "/api/generate",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    },
    // Local text and image generation can take noticeably longer than normal CRUD requests.
    // Give the final local-only demo flow enough time to finish model inference.
    GENERATE_REQUEST_TIMEOUT_MS,
  );
}

export function getHistoryList() {
  return requestJson<HistoryListItem[]>("/api/history");
}

export function getHistoryDetail(recordId: number) {
  return requestJson<HistoryDetail>(`/api/history/${recordId}`);
}

export function deleteHistoryRecord(recordId: number) {
  return requestJson<DeleteHistoryResponse>(`/api/history/${recordId}`, {
    method: "DELETE",
  });
}
