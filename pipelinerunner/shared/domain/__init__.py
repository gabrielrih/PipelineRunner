# shared/domain/exceptions.py

class SharedException(Exception):
    """Exceção base para o módulo shared"""
    pass


class RepositoryException(SharedException):
    """Exceção base para erros de repositório"""
    pass


class EntityNotFoundException(RepositoryException):
    """Entidade não encontrada"""
    def __init__(self, entity_type: str, identifier: str):
        super().__init__(f"{entity_type} '{identifier}' not found")
        self.entity_type = entity_type
        self.identifier = identifier


class DuplicateEntityException(RepositoryException):
    """Entidade duplicada"""
    def __init__(self, entity_type: str, identifier: str):
        super().__init__(f"{entity_type} '{identifier}' already exists")
        self.entity_type = entity_type
        self.identifier = identifier


class SerializationException(RepositoryException):
    """Erro ao serializar/deserializar"""
    pass


class FileSystemException(RepositoryException):
    """Erro ao acessar sistema de arquivos"""
    pass
