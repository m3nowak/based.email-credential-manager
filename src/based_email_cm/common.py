from pydantic import BaseModel as PydanticBaseModel
import humps

class BaseModel(PydanticBaseModel):
    '''Base configuration model with camelCase fields'''
    class Config:
        allow_population_by_field_name = True
        alias_generator = humps.camelize

def nats_kv_bucket(bucket_name:str, key_name:str):
    def decorator(cls):
        class NewModel(cls):
            class Config(cls.Config):
                schema_extra = {
                    'natsKvBucket': bucket_name,
                    'natsKvKey': key_name
                }
        return NewModel
    return decorator
