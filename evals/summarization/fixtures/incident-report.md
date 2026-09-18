# Checkout incident

On 2026-08-21 from 14:02 to 14:19 UTC, checkout errors rose from 0.4% to 18.7%. The
deployment at 13:58 changed the payment timeout from 4 seconds to 1 second. Rollback at
14:16 restored errors below 0.5% by 14:19. The team decided to add a timeout contract
test owned by Payments and require a 10-minute canary. Logs show correlation with the
timeout change, but the report does not prove every failure had the same cause. Owner:
Ana. Due date: 2026-08-28.
