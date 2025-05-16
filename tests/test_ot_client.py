import pytest

import services.notion_ot_pb2 as pb2  # type: ignore
import services.notion_ot_pb2_grpc as grpc_stubs  # type: ignore
from services.ot_client import OTClient


@pytest.fixture(autouse=True)
def fake_stub(monkeypatch):
    class FakeStub:
        def __init__(self, channel):
            self.last_req = None

        def PushOps(self, req):
            # echo back version+1 and a dummy patch
            return pb2.OpsResponse(version=req.base_version + 1, patch=[b"p1", b"p2"])

        def Subscribe(self, req):
            # emit two patches
            yield pb2.OpsResponse(version=1, patch=[b"a"])
            yield pb2.OpsResponse(version=2, patch=[b"b", b"c"])

    # swap in our fake
    monkeypatch.setattr(grpc_stubs, "NotionOTStub", lambda channel: FakeStub(channel))
    yield


def test_push_ops_roundtrip():
    client = OTClient("dummy:1234")
    version, patch = client.push_ops("blk", "cl", base_version=0, ops=[b"x"])
    assert version == 1
    assert patch == [b"p1", b"p2"]


def test_subscribe_stream():
    client = OTClient("dummy:1234")
    items = list(client.subscribe("blk"))
    assert items == [(1, [b"a"]), (2, [b"b", b"c"])]
