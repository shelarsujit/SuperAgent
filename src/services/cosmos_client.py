from __future__ import annotations

from datetime import datetime
from typing import Any
import uuid

try:
    from azure.cosmos import CosmosClient, PartitionKey
except Exception:  # pragma: no cover - cosmos optional
    CosmosClient = None
    PartitionKey = None


class CosmosConversationLogger:
    """Store conversation messages in Azure Cosmos DB."""

    def __init__(self, connection_str: str, database: str, container: str) -> None:
        if CosmosClient is None:
            raise ImportError("azure-cosmos is required for CosmosConversationLogger")
        self.client = CosmosClient.from_connection_string(connection_str)
        self.database = self.client.create_database_if_not_exists(database)
        self.container = self.database.create_container_if_not_exists(
            id=container,
            partition_key=PartitionKey(path="/conversation_id"),
        )

    def log_message(self, conversation_id: str, role: str, content: Any) -> None:
        item = {
            "id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.container.upsert_item(item)
