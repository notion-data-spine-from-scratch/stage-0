# save as check_health.py
import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc

ch = grpc.insecure_channel("localhost:50051")
stub = health_pb2_grpc.HealthStub(ch)
resp = stub.Check(health_pb2.HealthCheckRequest(service=""), timeout=5)
print("Status:", resp.status)  # should be SERVING (1)
