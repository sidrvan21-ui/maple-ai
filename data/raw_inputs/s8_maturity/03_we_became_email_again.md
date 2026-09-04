# Postmortem — “we became email again”

Author: Jules  
Date: 2027-07-02

Two buildings (not Cooper) started **attaching the same PDF to a monthly** and blasting Instant “see monthly.” Residents treated Porter as a noisier Gmail.

Root: we shipped monthly attach; we did not ship **discipline**. Severity rules don’t apply if Instant copy is “see PDF.”

Fix options: ban Instant+PDF, or force monthly-only for attachments. Fight not resolved. File this as tech+product debt.

Quote from a resident: “congrats you rebuilt email.”
