# Reflection

## What was the hardest part?

The hardest part was debugging why ServiceNow kept rejecting my write-back requests
with a 401 "User is not authenticated" error, even though my username and password
were correct. I worked through it step by step — ruling out a locked account, then
ruling out a wrong password by testing the credentials directly in the REST API
Explorer and in a standalone Python script — before discovering that new ServiceNow
developer instances (as of mid-2026) block plain Basic Auth on the API by default
unless the user is explicitly granted the `snc_basic_auth_api_access` role. It wasn't
obvious from the error message itself, so it took real trial and error, isolating one
variable at a time (URL, username, password, account lock status), to track down.

A close second was realizing my Gemini prompt wasn't actually using the five
knowledge-base articles at all. The AI was making reasonable-sounding decisions, but
with no real grounding — so it wasn't reliable against the official test tickets
until I explicitly built the KB articles into the prompt and told the model exactly
how to distinguish "respond" (specific detail confirms an article applies) from "ask"
(the topic matches, but the ticket is too vague to confirm it).

## What would you improve with more time?

I'd replace the current text-based JSON parsing — asking Gemini to output JSON as
plain text, then manually stripping markdown fences and parsing it — with the SDK's
structured output mode, so the model is constrained to return valid JSON directly
instead of relying on prompt instructions and cleanup code. I'd also move the
in-memory `processed_tickets` set to a small persistent store (like SQLite) so
duplicate-processing protection survives a server restart, and add proper automated
tests for the decision logic, covering the three official test tickets plus a few
edge cases of my own.
