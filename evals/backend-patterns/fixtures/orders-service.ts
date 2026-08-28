type Order = { id: string; customerId: string; items?: Item[] };
type Item = { id: string; orderId: string };

export async function listOrders(customerId: string): Promise<Order[]> {
  const orders = await db.orders.findMany({ where: { customerId } });
  for (const order of orders) {
    order.items = await db.items.findMany({ where: { orderId: order.id } });
  }
  return orders;
}
