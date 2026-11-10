---
name: project-frost-dates-api
description: "Frost dates come from the open climate API, cached per postal code for 30 days"
metadata:
  type: reference
---

garden-planner reads average first and last frost dates from the open climate API at
/v2/frost?postal=, cached in Redis per postal code for 30 days because the API allows
100 requests a day.
