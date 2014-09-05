# README #

This is the triodEnumerator. This branch of the program makes extensive use of
classes, and is therefore much easier to read than the previous version.

## How To Run ##
The program assumes an MPI-enabled system with Python 2.7.* and mpi4py
installed. On Sharcnet systems, the command `module load python/intel/2.7.5`
will have to be executed before the program can be run. 

Once the python modules have been loaded, the program may be run with the
mpirun command, specifying `overseer.py` as the executable. For example:
`mpirun -n 128 overseer.py`


