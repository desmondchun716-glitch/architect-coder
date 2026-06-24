export type Result = { id: string; score: number };

export function rankResults(results: Result[]): Result[] {
  return [...results].sort((a, b) => b.score - a.score);
}
