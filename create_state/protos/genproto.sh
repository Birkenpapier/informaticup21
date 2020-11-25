#!/bin/sh
python -m grpc_tools.protoc -I./ --python_out=. --grpc_python_out=. ./ic20_module_createstate.proto
python -m grpc_tools.protoc -I./ --python_out=. --grpc_python_out=. ./check.proto