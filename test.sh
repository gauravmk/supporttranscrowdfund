#!/bin/bash

flask run &
(sleep 10; exit 0) &

wait -n 
