# Incident — daily digest in the middle of the night

Date: 2026-06-18  
Owner: Nikhil  
Witness: Mina, demo to Jules

Cron was `0 14 * * *` UTC thinking that was 07:30 PDT. It is not in June (PDT is UTC-7 → 07:00 not 07:30, and we used 14:00 anyway which is 07:00 **PST math from a stackoverflow snippet**). Result: 00:30 America/Vancouver.

Priya-type users would have been correct to delete us.

## Fix

Store building IANA TZ. Vancouver buildings = `America/Vancouver`. Compute 07:30 local. Tests for a date in January and July.

## Product note

Capability memo already said this. Scoping already said this. We still shipped UTC. Put it in UAT as a **Must**.
