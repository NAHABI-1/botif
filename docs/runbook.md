# Runbook

## Start-of-Day Checklist
1. Confirm MT5 terminal is logged in and connected.
2. Verify worker service is running on the MT5 host.
3. Check API health endpoint.
4. Verify dashboard access and operator roles.
5. Review risk events from the last 24 hours.
6. Confirm trading mode (paper/demo/live).

## Incident Handling
1. Pause trading immediately if risk is unclear.
2. Capture logs and screenshots.
3. Notify on-call and stakeholders.
4. Initiate reconciliation with broker state.
5. Document timeline for postmortem.

## How to Pause Trading
- Use operator control endpoint or dashboard.
- Confirm halt state is `HALTED`.

## How to Trigger Panic Stop
- Use operator control endpoint or dashboard.
- Confirm halt state is `PANIC_STOP`.

## What to Inspect After Broker Errors
- MT5 terminal journal and expert logs.
- Worker logs for retcodes and broker comments.
- Reconciliation results and risk event history.

## Rollback Process
1. Disable trading (halt or panic stop).
2. Roll back to the previous release version.
3. Re-run reconciliation and validate system health.

## Postmortem Template
- Summary
- Timeline
- Root Cause
- Customer Impact
- Corrective Actions
- Prevention Measures
