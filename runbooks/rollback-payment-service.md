# Rolling Back the Payment Service

## When to roll back
Roll back if a fresh deploy of the payment service causes a spike in 5xx errors, failed
transactions, or a latency regression that breaches SLO, and a fix-forward is not ready
within the incident's error budget. Rolling back is usually faster and safer than debugging live.

## Rollback steps (Kubernetes)
1. Confirm the bad version: `kubectl rollout history deployment/payment-service`.
2. Roll back to the previous revision:
   `kubectl rollout undo deployment/payment-service`.
   To target a specific known-good revision: add `--to-revision=<n>`.
3. Watch the rollout complete: `kubectl rollout status deployment/payment-service`.
4. If the deploy also ran a database migration, do NOT assume rollback reverses it -
   check whether the schema change is backward compatible before rolling back code.

## Rollback steps (Helm)
`helm rollback payment-service <previous-revision>` then `helm status payment-service`.

## Verify
Error rate and transaction success return to baseline on the dashboard, `kubectl get pods`
shows the payment-service pods Running on the previous image tag, and a test payment succeeds.
Announce the rollback in the incident channel and note it in the postmortem.
