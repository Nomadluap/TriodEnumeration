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


class EmptyMappingIterator(MappingIterator):
    '''
    A mapping iterator which does not return full mappings. Returns nothing.
    '''
    def __init__(self):
        pass

    def next(self):
        raise StopIteration


class FullMappingIterator(MappingIterator):
    '''
    A mapping iterator which returns mappings based on an existing mapping. This
    iterator simply returns its constructor mapping.
    '''
    def __init__(self, mapping):
        if type(mapping) is not Mapping:
            raise TypeError("mapping must be of type 'Mapping'")
        self.mapping = mapping
        self.hasReturned = False

    def next(self):
        if not self.hasReturned:
            self.hasReturned = True
            return self.mapping
        else:
            raise StopIteration


class BasicEmptyMapIterator(EmptyMappingIterator):
    '''
    An empty mapping iterator which returns a mapping for each point in the
    codomain. Each mapping returned contains only this point as the basepoint.
