---
finding: Naive string replacement breaks when query contains ? inside string literals, in comments, or uses ?? for JSON operators (PostgreSQL). Recommend removing positional params or documenting limitation.
id: RR-J8Z3
resolution: Removed positional parameter support entirely. API now only accepts dict params with :name syntax. This is cleaner, more readable, and avoids the fragile string replacement logic.
severity: significant
status: addressed
title: Positional parameter replacement is fragile
type: review-response
---
