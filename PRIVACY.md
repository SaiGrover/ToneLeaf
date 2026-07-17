# Toneleaf privacy boundary

Toneleaf has two explicit privacy modes. Device-local mode analyzes text in a
Python process bound to `127.0.0.1`. The production container serves the web UI
and API from one operator-controlled origin. Both modes have no application
database, disable request access logs, and set `Cache-Control: no-store`.

## Data lifecycle

1. The browser sends entered text to the configured Toneleaf API. This stays on
   the device in local mode and travels over HTTPS to the operator's service in
   hosted mode.
2. Python holds it in process memory while calculating the result.
3. The API returns scores and cues and does not persist the request.
4. Recent history remains only in page-session memory and disappears on reload.

No analytics, account, remote model API, or application database is used.

## Hosted-mode boundary

Hosted deployment changes the boundary: text leaves the user's device, is
decrypted by the operator's HTTPS endpoint, and exists transiently in FastAPI
process memory. Toneleaf does not persist it or forward it to a model provider.
The hosting platform may still observe network metadata and infrastructure logs;
operators must configure HTTPS, access controls, retention, and regional hosting
appropriately. Device-local mode is recommended for highly sensitive text.

## Optional deep-learning model

Set `TONELEAF_MODEL_PATH` to an existing local Hugging Face sentiment model
directory and install `requirements-ml.txt`. Loading uses `local_files_only=True`.
Toneleaf never downloads a model at analysis time and never sends user text to a
model host. Without that configuration, the Python lexicon engine is used.

## Voice warning

Browser speech recognition may use a browser or operating-system speech service.
For sensitive content, type or paste a locally produced transcript instead. The
Toneleaf Python API itself does not receive audio.

## Threat-model boundary

Device-local processing prevents Toneleaf from sending text to an application
server. Neither mode can protect text from malware, browser extensions, screen
capture, a compromised operating system, or another person with access to the
same browser profile. Hosted mode additionally trusts the operator and hosting
platform. Distress results are language-screening signals, not diagnoses.
