import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc


def main() -> int:
    channel = grpc.insecure_channel("localhost:50051")
    stub = health_pb2_grpc.HealthStub(channel)
    try:
        resp = stub.Check(health_pb2.HealthCheckRequest(service=""), timeout=2)
    except Exception:
        return 1
    return 0 if resp.status == health_pb2.HealthCheckResponse.SERVING else 1


if __name__ == "__main__":
    raise SystemExit(main())
