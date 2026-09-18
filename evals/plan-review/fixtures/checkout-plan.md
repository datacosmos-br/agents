# Guest checkout implementation plan

Goal: let an unauthenticated shopper submit one order and receive its public receipt.
Approved non-goal: account creation and saved payment methods.

1. Add a guest route.
2. Make payment robust and scalable.
3. Save the order and publish an event.
4. Deploy safely.
5. Add tests.
