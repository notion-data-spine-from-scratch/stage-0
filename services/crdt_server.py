#!/usr/bin/env python3
from concurrent import futures

import grpc

# These two live alongside this file in the Docker build context
import notion_ot_pb2 as pb2
import notion_ot_pb2_grpc as pb2_grpc

# gRPC health-check plumbing
from grpc_health.v1 import health, health_pb2, health_pb2_grpc


class DummyServicer(pb2_grpc.NotionOTServicer):
    """A no-op CRDT service that just echoes back your requests."""

    def PushOps(self, request: pb2.OpsRequest, context) -> pb2.OpsResponse:
        # Echo back the version they sent and the ops they sent.
        return pb2.OpsResponse(version=request.base_version, patch=request.ops)

    def Subscribe(self, request: pb2.SubscribeRequest, context):
        # Stub: no actual streaming yet
        if False:
            yield pb2.OpsResponse()


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))

    # Register health service
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set("", health_pb2.HealthCheckResponse.ServingStatus.SERVING)

    # Register our dummy OT service
    pb2_grpc.add_NotionOTServicer_to_server(DummyServicer(), server)

    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
