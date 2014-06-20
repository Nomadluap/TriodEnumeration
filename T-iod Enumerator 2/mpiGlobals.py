#!/usr/bin/env python
#This file stores global definitions for the MPI version of the overseer.

#tags for worker reporting to master
TAG_DONE_PAIR = 1
TAG_REPORT_SUCCESS=2
#tags for master reporting to worker
TAG_WORKER_COMMAND=3
#the stop command
COMMAND_STOP = 'stop'
