NCPUS=128
TIME=24h
sqsub -q mpi -r $TIME -n $NCPUS -o "out.%J" python overseer.py
