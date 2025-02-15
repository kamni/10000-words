"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

class Singleton(type):
    """
    Create a singleton that prevents multiple instantiations.

    Metaclass that is useful for connections
    where we don't want more than one instance (e.g., database connections).
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    @classmethod
    def destroy(metacls, cls):
        """
        Destroy an instance of a singleton class so it can be reinitialized

        Usage: Singleton.destroy(SomeClass)
        """
        if cls in metacls._instances:
            del metacls._instances[cls]

    @classmethod
    def destroy_all(cls):
        """
        Nuke everything
        """
        cls._instances = {}
