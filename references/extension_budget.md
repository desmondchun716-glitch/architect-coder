# Extension Budget

Protect known or high-probability change points, not imaginary futures.

| Task size | Default explicit seams |
|---|---:|
| Small | 0-1 |
| Medium | 1-3 |
| Large | each seam needs roadmap, risk, or NFR evidence |

Good seams include:

- an adapter around an external provider
- configuration for a real threshold, path, or feature toggle
- a strategy boundary for known ranking or fallback variants
- a small module with stable inputs and outputs
- a migration-friendly serialized structure

Reject:

- plugin systems for one implementation
- interfaces around every function
- vague TODOs presented as extensibility
- extra layers with no ownership or test boundary
- readability loss for hypothetical flexibility

Every explicit seam needs a test, example, or short extension note.
