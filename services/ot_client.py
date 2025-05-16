import grpc

from services.notion_ot_pb2 import (  # type: ignore[attr-defined]
    OpsRequest,
    SubscribeRequest,
)
from services.notion_ot_pb2_grpc import NotionOTStub


class OTClient:
    def __init__(self, target: str):
        """Construct a client connected to `target`."""
        channel = grpc.insecure_channel(target)
        # import stub here so tests can monkey-patch it
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
        """Push operations to the server, get back new version & patch."""
        req = OpsRequest(
            block_id=block_id,
            client_id=client_id,
            base_version=base_version,
            ops=ops,
        )
        resp = self._stub.PushOps(req)
        return resp.version, list(resp.patch)

    def subscribe(self, block_id: str):
        """Subscribe to a stream of patches for a given block."""
        req = SubscribeRequest(block_id=block_id)  # type: ignore[attr-defined]
        for resp in self._stub.Subscribe(req):
            yield resp.version, list(resp.patch)
