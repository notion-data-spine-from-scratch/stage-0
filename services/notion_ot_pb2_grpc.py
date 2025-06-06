# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import warnings

import grpc

from . import notion_ot_pb2 as notion__ot__pb2

GRPC_GENERATED_VERSION = "1.71.0"
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower

    _version_not_supported = first_version_is_lower(
        GRPC_VERSION, GRPC_GENERATED_VERSION
    )
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f"The grpc package installed is at version {GRPC_VERSION},"
        + f" but the generated code in notion_ot_pb2_grpc.py depends on"
        + f" grpcio>={GRPC_GENERATED_VERSION}."
        + f" Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}"
        + f" or downgrade your generated code using grpcio-tools<={GRPC_VERSION}."
    )


class NotionOTStub(object):
    """The OT service for pushing ops and subscribing to patches."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.PushOps = channel.unary_unary(
            "/notion_ot.NotionOT/PushOps",
            request_serializer=notion__ot__pb2.OpsRequest.SerializeToString,
            response_deserializer=notion__ot__pb2.OpsResponse.FromString,
            _registered_method=True,
        )
        self.Subscribe = channel.unary_stream(
            "/notion_ot.NotionOT/Subscribe",
            request_serializer=notion__ot__pb2.SubscribeRequest.SerializeToString,
            response_deserializer=notion__ot__pb2.OpsResponse.FromString,
            _registered_method=True,
        )


class NotionOTServicer(object):
    """The OT service for pushing ops and subscribing to patches."""

    def PushOps(self, request, context):
        """Apply a batch of operations and return a patch + new version."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Subscribe(self, request, context):
        """Subscribe to a stream of patches for a given block."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_NotionOTServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "PushOps": grpc.unary_unary_rpc_method_handler(
            servicer.PushOps,
            request_deserializer=notion__ot__pb2.OpsRequest.FromString,
            response_serializer=notion__ot__pb2.OpsResponse.SerializeToString,
        ),
        "Subscribe": grpc.unary_stream_rpc_method_handler(
            servicer.Subscribe,
            request_deserializer=notion__ot__pb2.SubscribeRequest.FromString,
            response_serializer=notion__ot__pb2.OpsResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "notion_ot.NotionOT", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers("notion_ot.NotionOT", rpc_method_handlers)


# This class is part of an EXPERIMENTAL API.
class NotionOT(object):
    """The OT service for pushing ops and subscribing to patches."""

    @staticmethod
    def PushOps(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/notion_ot.NotionOT/PushOps",
            notion__ot__pb2.OpsRequest.SerializeToString,
            notion__ot__pb2.OpsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )

    @staticmethod
    def Subscribe(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_stream(
            request,
            target,
            "/notion_ot.NotionOT/Subscribe",
            notion__ot__pb2.SubscribeRequest.SerializeToString,
            notion__ot__pb2.OpsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )
