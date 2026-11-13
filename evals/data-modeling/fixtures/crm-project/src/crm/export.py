from .models import Client


def export_clients(clients: list[Client]) -> list[dict[str, object]]:
    return [client.model_dump(mode="json") for client in clients]
