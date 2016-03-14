# gobgp_grpc_demo
Yet another gobgpd grpc client written in Python

## About
Demonstrates how gobgpd rib can be controlled via grpc from Python client. 

This example also takes advantage of gobgp's shared library which can be loaded by a grpc client for easy serialization of arguments and decoding of responses.

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
Originate 10.0.0.1/32 with nexthop 192.0.2.1 and community 65004:999,no-export:
```
$ python modpath.py 10.0.0.1/32 -n 192.0.2.1 -c 65004:999 -c no-export
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
  attr type 1: value 2
  attr type 3: nexthop 192.0.2.1
  attr type 8: communities ['65004:999', '65535:65281']
  ```
  
Withdraw originating route:
  ```
  $ python modpath.py -d 10.0.0.1/32 -n 192.0.2.1
  ```
