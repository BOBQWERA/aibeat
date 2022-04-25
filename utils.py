class BadIter:
    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

if __name__ == "__main__":
    for i in BadIter():
        print(i)