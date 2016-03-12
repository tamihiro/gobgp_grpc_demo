import gobgp_pb2
from grpc.beta import implementations
from cgopy import *
from ctypes import *
from struct import *
import sys
import re
import json
import traceback

_TIMEOUT_SECONDS = 10

def print_rib(dest):
  # prints out all about a single gobgp_pb2.Destination object
  print dest.prefix
  path = Path()
  for attr in [attr for attr in dir(dest.paths._values[0]) if re.match('^[a-z]', attr)]:
    if attr == "nlri":
      path.nlri = Buf()
      n_v = getattr(dest.paths._values[0], attr)
      n_v_buf = create_string_buffer(n_v)
      path.nlri.value = cast(n_v_buf, POINTER(c_char))
      path.nlri.len = c_int(len(n_v))
    elif attr == "pattrs":
      pattrs = []
      for pattr in getattr(dest.paths._values[0], attr):
        p_a = Buf()
        p_a_v = pattr
        p_a_v_buf = create_string_buffer(p_a_v)
        p_a.value = cast(p_a_v_buf, POINTER(c_char))
        p_a.len = c_int(len(p_a_v))
        pattrs.append(pointer(p_a))
      path.path_attributes = pointer((POINTER(Buf) * _PATTRS_CAP)(*pattrs))
    else:
      # print everything other than nlri and path_attributers
      print "  {}: {}".format(attr, getattr(dest.paths._values[0], attr))
  path.path_attributes_len = c_int(len(pattrs))
  path.path_attributes_cap = c_int(_PATTRS_CAP)
  decoded_path = libgobgp.decode_path(path)
  # format and print decoded_path
  for attr in [ attr.items() for attr in sorted(json.loads(decoded_path).get('attrs', []), key=lambda k: k['type']) ]:
    attr.sort(key=lambda k: str(k[0]) != 'type')
    if attr[1][0] == 'communities':
      attr[1][1][:] = map(lambda v: "{}:{}".format((int("0xffff0000",16)&v)>>16, int("0xffff",16)&v), attr[1][1])
    print "  attr " + ": ".join(map(lambda x: "{} {}".format(*x), attr))

def run(*prefixes):
  # either get all prefixes or search specific ones in global rib via grpc and print to stdout
  channel = implementations.insecure_channel("localhost", 50051)
  stub = gobgp_pb2.beta_create_GobgpApi_stub(channel)
  try:
    # grpc request
    response_table = stub.GetRib(
        gobgp_pb2.Table(
            type=gobgp_pb2.GLOBAL, 
            family=libgobgp.get_route_family("ipv4-unicast"), 
            destinations=[ gobgp_pb2.Destination(prefix=p) for p in prefixes ]
            ), 
        _TIMEOUT_SECONDS
        )
    if prefixes:
      for prefix in prefixes:
        try:
          i = map(lambda d: d.prefix, response_table.destinations).index(prefix)
          print_rib(response_table.destinations[i])
        except ValueError:    
          print prefix
          print "  not in table!"
    else:
      for pb2_dest in response_table.destinations:
        print_rib(pb2_dest)
  except:
    traceback.print_exc()    
    sys.exit(1)

def main():
  run(*sys.argv[1:])

if __name__ == '__main__':
  if len(sys.argv) == 2 and sys.argv[1] in ('-h', '--help', '?', ):
    print "usage:", sys.argv[0], "[prefix ... ]"
    sys.exit()
  main()
