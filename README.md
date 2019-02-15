# gobgp_grpc_demo
Yet another gobgpd grpc client written in Python

## Updates
The demo program here works with GoBGP up until 1.26, but not any more with recent versions. The GoBGP development team has decided to renew its API by leveraging protobuf structure, and it will hopefully fixed in 2.0. See discussion in [this issue](https://github.com/osrg/gobgp/issues/1763).

A working demo for the newer GoBGP 2.0 is [here](https://github.com/tamihiro/gobgp_grpc_demo).

## About
Demonstrates how gobgpd rib can be controlled via grpc from Python client. 

This example also shows how to load gobgp's shared library and directly make its function calls in order to simplify serialization of request arguments and decoding of responses.

## Requirements

Tested on ubuntu-14.04, with the following installed. 

* go1.6
* protobuf v3.0.0-beta-2
* gRPC-Python
* gobgp

## How to use

* Compile gobgp C-shared library.
```
cd $GOPATH/src/github.com/osrg/gobgp/gobgp/lib
go build --buildmode=c-shared -o libgobgp.so *go
```

* Create grpc stub.
```
cd $GOPATH/src/github.com/osrg/gobgp/tools/grpc/python
GOBGP_API=$GOPATH/src/github.com/osrg/gobgp/api
protoc  -I $GOBGP_API --python_out=. --grpc_out=. --plugin=protoc-gen-grpc=`which grpc_python_plugin` $GOBGP_API/gobgp.proto
```

* Copy all scripts in this repository under `$GOPATH/src/github.com/osrg/gobgp/tools/grpc/python`, and run gobgpd if you haven't already.

---
Originate 10.0.0.1/32 with the path-attribute origin igp (default), nexthop 192.0.2.1, and communities [65004:999, no-export]:
```
$ python modpath.py 10.0.0.1/32 -n 192.0.2.1 -c 65004:999 no-export
```

Search route in global RIB:
```
$ python getrib.py 10.0.0.1/32
10.0.0.1/32
  age: 1457879657
  best: True
  family: 65537
  filtered: False
  is_from_external: False
  is_withdraw: False
  neighbor_ip: <nil>
  no_implicit_withdraw: False
  source_asn: 65004
  source_id: <nil>
  stale: False
  validation: -1
  attr type 1: value 0
  attr type 3: nexthop 192.0.2.1
  attr type 8: communities ['65004:999', '65535:65281']
  ```
  
Withdraw an announced route:
  ```
  $ python modpath.py -d 10.0.0.1/32 -n 192.0.2.1
  ```

For more options:
  ```
  $ python modpath.py -h
  ```

Default address family is ipv4-unicast, and "-6" option is available for ipv6-unicast.
Feel free to modify the code if you want to play with other address families.
