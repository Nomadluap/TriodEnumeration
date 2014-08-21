'''
mappingIterators.py - classes which facilitate iterating over different types of
mappings.

There are two distinct types of mapping iterators in this file: empty mapping
iterators and full mapping iterators.

Empty mapping iterators are intended for the overseer thread and are generally
in charge of generating pairs of empty maps which will eventually get sent to
worker threads.

Full mapping iterators are intended to be utilized inside worker threads in
order to complete the empty mappings given to them by the overseer thread. 
'''
from config import N, M, T
from mapping import Mapping, Vertex


class MappingIterator(object):
    '''
    The base class for all mapping iterators. This class returns no mapppings.
    '''
    def __init__(self):
        pass

    def next(self):
        raise StopIteration
