from pydantic import BaseModel as PydanticBaseModel
import humps

class BaseModel(PydanticBaseModel):
    '''Base configuration model with camelCase fields'''
    class Config:
        allow_population_by_field_name = True
        alias_generator = humps.camelize