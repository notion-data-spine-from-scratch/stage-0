from concurrent import futures

import grpc

# gRPC‑generated code
import notion_ot_pb2 as pb2
import notion_ot_pb2_grpc as pb2_grpc

# Health‑check imports
from grpc_health.v1 import health, health_pb2, health_pb2_grpc


class DummyServicer(pb2_grpc.NotionOTServicer):
    def PushOps(self, request, context):
        # Echo back the base_version and ops as a patch
        return pb2.OpsResponse(
            version=request.base_version,
            patch=request.ops,
        )

    def Subscribe(self, request, context):
        # No patches to stream for now
        if False:
            yield None


def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))

    # Register the health service
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set(
        "",
        health_pb2.HealthCheckResponse.ServingStatus.SERVING,
    )

    # Register our dummy NotionOT service
    pb2_grpc.add_NotionOTServicer_to_server(DummyServicer(), server)

    # Listen on port 50051
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
