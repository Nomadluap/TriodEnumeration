NCPUS=40
TIME=6h
sqsub -q mpi -r $TIME -n $NCPUS -o "out.%J" python overseer.py
