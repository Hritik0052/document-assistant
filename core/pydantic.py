from pydantic import BaseModel, ValidationError


class FormError(Exception):
    def __init__(self, errors: dict[str, str]):
        self.errors = errors
        super().__init__(errors)


def parse_form(schema: type[BaseModel], data) -> BaseModel:
    payload = {}
    for key in schema.model_fields:
        value = data.get(key)
        if value is not None:
            payload[key] = value
    try:
        return schema.model_validate(payload)
    except ValidationError as exc:
        errors: dict[str, str] = {}
        for error in exc.errors():
            loc = error.get('loc') or ('form',)
            field = str(loc[0])
            errors.setdefault(field, error['msg'])
        raise FormError(errors) from exc
