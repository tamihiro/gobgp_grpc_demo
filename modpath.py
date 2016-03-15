import gobgp_pb2
from grpc.beta import implementations
from cgopy import *
from ctypes import *
from struct import *
import os
import sys
from uuid import UUID
import traceback
import argparse

_TIMEOUT_SECONDS = 10

def run(prefix, withdraw=False, **kw):
  # originate or withdraw route via grpc
  channel = implementations.insecure_channel("localhost", 50051)
  stub = gobgp_pb2.beta_create_GobgpApi_stub(channel)
  try:
    joined_args = prefix + " " + " ".join(map(lambda x: "{} {}".format(*x), kw.items()))
    serialized_path = libgobgp.serialize_path(libgobgp.get_route_family("ipv4-unicast"), joined_args, ).contents
    # nlri
    nlri = unpack_buf(serialized_path.nlri)
    # pattrs
    pattrs = []
    for pattr_p in serialized_path.path_attributes.contents[:serialized_path.path_attributes_len]:
      pattrs.append(unpack_buf(pattr_p.contents))
    # path dict
    path = dict([("nlri", nlri), ("pattrs", pattrs), ])
    if withdraw:
      path["is_withdraw"] = True
    # grpc request
    res = stub.ModPath(gobgp_pb2.ModPathArguments(family=4, path=path), _TIMEOUT_SECONDS)
    print str(UUID(bytes=res.uuid))
  except:
    traceback.print_exc()    
    sys.exit(1)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('prefix', action='store')
  parser.add_argument('-d', action='store_true', default=False, dest="withdraw", help="Withdraw route")
  parser.add_argument('-o', action='store', dest="origin", default="igp", help="Origin")
  parser.add_argument('-n', action='store', dest="nexthop", help="Next-hop")
  parser.add_argument('-m', action='store', type=int, dest="med", help="MED")
  parser.add_argument('-p', action='store', type=int, dest="local-pref", help="Local-preference")
  parser.add_argument('-c', action='append', dest="comms", default=[], help="Community")
  argopts = parser.parse_args()

  pattrs = {k:v for k, v in argopts.__dict__.items() if k not in ("prefix", "withdraw", "comms", ) and v is not None}
  if argopts.comms:
    pattrs['community'] = ",".join(argopts.comms)
  run(argopts.prefix, withdraw=argopts.withdraw, **pattrs)

if __name__ == '__main__':
  main()
