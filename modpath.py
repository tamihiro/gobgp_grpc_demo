import gobgp_pb2
import gobgp_pb2_grpc
import grpc
from grpc.framework.interfaces.face.face import ExpirationError
from cgopy import *
from ctypes import *
from struct import *
import os
import sys
from uuid import UUID
import traceback
import argparse
import socket

_TIMEOUT_SECONDS = 2

def run(prefix, af, gobgpd_addr, withdraw=False, **kw):
  route_family = libgobgp.get_route_family(_AF_NAME[af])
  joined_args = prefix + " " + " ".join(map(lambda x: "{} {}".format(*x), kw.items()))
  serialized_path = libgobgp.serialize_path(route_family, joined_args, ).contents
  # nlri
  nlri = unpack_buf(serialized_path.nlri)
  # pattrs
  pattrs = []
  for pattr_p in serialized_path.path_attributes.contents[:serialized_path.path_attributes_len]:
    pattrs.append(unpack_buf(pattr_p.contents))
  # path dict
  path = dict([("family", route_family), ("nlri", nlri), ("pattrs", pattrs), ])
  # grpc request
  channel = grpc.insecure_channel(gobgpd_addr + ':50051')
  try:
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)
    if not withdraw:
      res = stub.AddPath(gobgp_pb2.AddPathRequest(path=path), _TIMEOUT_SECONDS)
      # AddPathResponse uuid seems to have become empty since uuid became a member of Path structure.
      if res.uuid:
        print str(UUID(bytes=res.uuid))
    else:
      path["is_withdraw"] = True
      res = stub.DeletePath(gobgp_pb2.DeletePathRequest(path=path), _TIMEOUT_SECONDS)
  except ExpirationError:
    print >> sys.stderr, "grpc request timed out!"
  except:
    traceback.print_exc()

def main():
  parser = argparse.ArgumentParser()
  parser_afg = parser.add_mutually_exclusive_group()
  parser_afg.add_argument('-4', action='store_const', dest="af", const=4, help="Address-family ipv4-unicast (default)")
  parser_afg.add_argument('-6', action='store_const', dest="af", const=6, help="Address-family ipv6-unicast")
  parser.add_argument('prefix', action='store')
  parser.add_argument('-r', action='store', default="localhost", dest="gobgpd_addr", help="GoBGPd address (default: localhost)")
  parser.add_argument('-d', action='store_true', default=False, dest="withdraw", help="Withdraw route (default: false)")
  parser.add_argument('-o', action='store', dest="origin", default="igp", help="Origin (default: igp)")
  parser.add_argument('-n', action='store', dest="nexthop", help="Next-hop")
  parser.add_argument('-m', action='store', type=int, dest="med", help="MED")
  parser.add_argument('-p', action='store', type=int, dest="local-pref", help="Local-preference")
  parser.add_argument('-c', action='store', nargs='*', dest="comms", help="Community")
  argopts = parser.parse_args()

  try:
    socket.gethostbyname(argopts.gobgpd_addr)
  except socket.gaierror, e:
    print >> sys.stderr, "no such host:", argopts.gobgpd_addr
    sys.exit(-1)
  pattrs = {k:v for k, v in argopts.__dict__.items() if k not in ("prefix", "af", "gobgpd_addr", "withdraw", "comms", ) and v is not None}
  if argopts.comms:
    pattrs['community'] = ",".join(argopts.comms)

  run(argopts.prefix, argopts.af or 4, argopts.gobgpd_addr, withdraw=argopts.withdraw, **pattrs)

if __name__ == '__main__':
  main()
