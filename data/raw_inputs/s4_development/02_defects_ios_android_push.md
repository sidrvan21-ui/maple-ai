# Defect log — push (open)

QA: Priya-friend “Lina” + Nikhil. 2026-06-20+

| ID | Sev | Client | Notes |
|---|---|---|---|
| P-11 | S1 | iOS | First push after magic link sometimes lands without sound if user never opened Settings. Looks like we “didn’t notify.” |
| P-14 | S1 | Android 14 | OEM battery killers (Xiaomi etc.) — our demographic has fewer of these than a global app but students in Mount Pleasant will have them. |
| P-17 | S2 | iOS | Quiet hours used device TZ not building TZ. Fine until someone travels. |
| P-19 | S2 | both | Duplicate tap from Antoine-style fat button = two instants. No idempotency key. |
| P-22 | S3 | Android | Digest notification looks like a second instant. Mina wants a different template. |
| P-23 | S2 | iOS | Preview of unit number in notification **shade** even if we linted the body — composer title field unbound. Helen-level incident if we ship. |

P-23 is why we do not go to Cooper-wide without a checklist.
