# Capability memo — digest engine (what we can actually build)

Author: Dev (Nikhil)  
Date: 2026-04-20  
Audience: strategy, not a PRD

## What “daily / weekly / monthly” means in code

Not three newsletters someone writes.

- **Instant:** event object (type, severity, window, building_id, channels)  
- **Daily:** 07:30 America/Vancouver cron that compiles unresolved + today’s windows. Helen will not type this.  
- **Weekly:** Sunday 18:00 compile of next 7 days + unresolved  
- **Monthly:** first Monday — finance **attachments optional**. If treasurer does not upload, the month still ships with ops-only. Do not block the product on a fax.

## Defaults (fight in scoping)

Nikhil’s vote: renters daily ON, owners daily OFF, weekly ON for all, monthly ON for owners/council. Requires a role. Derek wants magic link first — role might be wrong on day 1. **Conflict.**

## Timezone

America/Vancouver including PDT. If we ship UTC we will ship a bug (see later defect notes if they exist yet).

## What we will not build in v1 (Nikhil)

- WeChat official account  
- SMS except emergency override (cost + PIPA + Helen’s harassment fear)  
- Package scan  
- Amenity calendar  

If strategy sells those, find another tech lead.
