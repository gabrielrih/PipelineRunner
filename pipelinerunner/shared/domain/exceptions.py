class SharedException(Exception):
    pass


class RepositoryException(SharedException):
    pass


class SerializationException(RepositoryException):
    pass


class FileSystemException(RepositoryException):
    pass
