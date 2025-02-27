"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Any

from pydantic import BaseModel, ConfigDict


class HashableMixin:
    """
    Implement hashing for models.

    By default, the `id` is used for uniqueness;
    but for models that have an optional id,
    you have to override the `unique_fields` property.

    NOTE: Pydantic has its own hash, but only if the instance is frozen,
    i.e., it can't be updated. This is why we're implementing our own hash.
    """

    def __eq__(self, other: Any) -> bool:
        return hash(self) == hash(other)

    def __hash__(self):
        attrs = self.model_dump()
        unique_values = {
            field: attrs[field]
            for field in self.unique_fields
        }
        hashstr = f'{self.__class__.__qualname__}-{unique_values}'
        return hash(hashstr)

    @property
    def unique_fields(self):
        """
        List of field names that make a model unique.
        """

        try:
            assert 'id' in self.model_dump(exclude_unset=True)
            return ['id']
        except AssertionError:
            raise NotImplementedError


class GlobalBaseModel(BaseModel):
    """
    Use this base for all pydantic models
    """
    model_config = ConfigDict(use_enum_values=True)
