import grpc

# relative imports inside the services package
from .notion_ot_pb2 import OpsRequest, SubscribeRequest  # type: ignore[attr-defined]
from .notion_ot_pb2_grpc import NotionOTStub


class OTClient:
    """Thin wrapper around the generated gRPC stub for NotionOT."""

    def __init__(self, target: str):
        """
        Args:
            target: host:port of your CRDT gRPC server
        """
        channel = grpc.insecure_channel(target)
        # allow tests to monkey-patch NotionOTStub on import
        import services.notion_ot_pb2_grpc as grpc_stubs  # noqa: E402

        self._stub = grpc_stubs.NotionOTStub(channel)

    def push_ops(
        self,
        block_id: str,
        client_id: str,
        *,
        base_version: int,
        ops: list[bytes],
    ) -> tuple[int, list[bytes]]:
        """
        Push a batch of operations to the CRDT server.

        Returns:
            (new_version, merged_patch)
        """
        req = OpsRequest(
            block_id=block_id,
            client_id=client_id,
            base_version=base_version,
            ops=ops,
        )
        resp = self._stub.PushOps(req)
        return resp.version, list(resp.patch)

    def subscribe(self, block_id: str):
        """
        Subscribe to a live stream of patches for a block.

        Yields:
            (version, patch_bytes_list)
        """
        req = SubscribeRequest(block_id=block_id)  # type: ignore[attr-defined]
        for resp in self._stub.Subscribe(req):
            yield resp.version, list(resp.patch)
