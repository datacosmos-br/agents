# Approved post request

Current owner snapshot:

- Operation: `create_post`
- Method and path: `POST /2/tweets`
- Authorization: user-context OAuth from current process environment
- Required success status: `201`
- Rate-limit evidence: `x-rate-limit-reset`

Text: “Schema checks now report the exact breaking operation before merge.”
The operator approved one post from the authenticated project account. User-
context OAuth is available through the authorized credential owner; no token may
be printed or copied. Do not create a thread or upload media. On HTTP 429, record
the reset time and stop rather than retrying blindly.
