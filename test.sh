#!/bin/bash

flask shell &
(sleep 10; exit 0) &

wait -n 
