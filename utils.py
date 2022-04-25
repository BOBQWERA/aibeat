class BadIter:
    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration