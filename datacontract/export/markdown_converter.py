from typing import Dict

from pydantic import BaseModel

from datacontract.export.exporter import Exporter
from datacontract.model.data_contract_specification import (
    DataContractSpecification,
    Definition,
    Field,
    Model,
    Server,
    ServiceLevel,
)


class MarkdownExporter(Exporter):
    """Exporter implementation for converting data contracts to Markdown."""

    def export(
        self,
        data_contract: DataContractSpecification,
        model: Model,
        server: str,
        sql_server_type: str,
        export_args: dict,
    ) -> str:
        """Exports a data contract to Markdown format."""
        return to_markdown(data_contract)


def to_markdown(data_contract: DataContractSpecification) -> str:
    """
    Convert a data contract to its Markdown representation.

    Args:
        data_contract (DataContractSpecification): The data contract to convert.

    Returns:
        str: The Markdown representation of the data contract.
    """
    markdown_parts = [
        f"# {data_contract.id}",
        "## Info",
        obj_attributes_to_markdown(data_contract.info),
        "",
        "## Servers",
        servers_to_markdown(data_contract.servers),
        "",
        "## Terms",
        obj_attributes_to_markdown(data_contract.terms),
        "",
        "## Models",
        models_to_markdown(data_contract.models),
        "",
        "## Definitions",
        definitions_to_markdown(data_contract.definitions),
        "",
        "## Service levels",
        service_level_to_markdown(data_contract.servicelevels),
    ]
    return "\n".join(markdown_parts)


def obj_attributes_to_markdown(obj: BaseModel, excluded_fields: set = set()) -> str:
    if not obj:
        return ""
    obj_model = obj.model_dump(exclude_unset=True, exclude=excluded_fields)
    description = obj_model.pop("description", None)
    attributes = [
        (f"• `{attr}`" if value is True else f"• **{attr}:** {value}") for attr, value in obj_model.items() if value
    ]
    return f"*{description_to_markdown(description)}*<br>{'<br>'.join(attributes)}"


def servers_to_markdown(servers: Dict[str, Server]) -> str:
    if not servers:
        return ""
    markdown_parts = [
        "| Name | Type | Attributes |",
        "| ---- | ---- | ---------- |",
    ]
    for server_name, server in servers.items():
        markdown_parts.append(
            f"| {server_name} | {server.type or ''} | {obj_attributes_to_markdown(server, {'type'})} |"
        )
    return "\n".join(markdown_parts)


def models_to_markdown(models: Dict[str, Model]) -> str:
    return "\n".join(model_to_markdown(model_name, model) for model_name, model in models.items())


def model_to_markdown(model_name: str, model: Model) -> str:
    """
    Generate Markdown representation for a specific model.

    Args:
        model_name (str): The name of the model.
        model (Model): The model object.

    Returns:
        str: The Markdown representation of the model.
    """
    parts = [
        f"### {model_name}",
        f"*{description_to_markdown(model.description)}*",
        "",
        "| Field | Type | Attributes |",
        "| ----- | ---- | ---------- |",
    ]

    # Append generated field rows
    parts.append(fields_to_markdown(model.fields))
    return "\n".join(parts)


def fields_to_markdown(
    fields: Dict[str, Field],
    level: int = 0,
) -> str:
    """
    Generate Markdown table rows for all fields in a model.

    Args:
        fields (Dict[str, Field]): The fields to process.
        level (int): The level of nesting for indentation.

    Returns:
        str: A Markdown table rows for the fields.
    """

    return "\n".join(field_to_markdown(field_name, field, level) for field_name, field in fields.items())


def field_to_markdown(field_name: str, field: Field, level: int = 0) -> str:
    """
    Generate Markdown table rows for a single field, including nested structures.

    Args:
        field_name (str): The name of the field.
        field (Field): The field object.
        level (int): The level of nesting for indentation.

    Returns:
        str: A Markdown table rows for the field.
    """
    tabs = "&numsp;" * level
    arrow = "&#x21b3;" if level > 0 else ""
    column_name = f"{tabs}{arrow} {field_name}"

    attributes = obj_attributes_to_markdown(field, {"type", "fields", "items", "keys", "values"})

    rows = [f"| {column_name} | {field.type} | {attributes} |"]

    # Recursively handle nested fields, array, map
    if field.fields:
        rows.append(fields_to_markdown(field.fields, level + 1))
    if field.items:
        rows.append(field_to_markdown("items", field.items, level + 1))
    if field.keys:
        rows.append(field_to_markdown("keys", field.keys, level + 1))
    if field.values:
        rows.append(field_to_markdown("values", field.values, level + 1))

    return "\n".join(rows)


def definitions_to_markdown(definitions: Dict[str, Definition]) -> str:
    if not definitions:
        return ""
    markdown_parts = [
        "| Name | Type | Domain | Attributes |",
        "| ---- | ---- | ------ | ---------- |",
    ]
    for definition_name, definition in definitions.items():
        markdown_parts.append(
            f"| {definition_name} | {definition.type or ''} | {definition.domain or ''} | {obj_attributes_to_markdown(definition, {'name', 'type', 'domain'})} |",
        )
    return "\n".join(markdown_parts)


def service_level_to_markdown(service_level: ServiceLevel | None) -> str:
    if not service_level:
        return ""
    result = [""]
    if service_level.availability:
        result.extend(
            [
                "### Availability",
                obj_attributes_to_markdown(service_level.availability),
                "",
            ]
        )
    if service_level.retention:
        result.extend(
            [
                "### Retention",
                obj_attributes_to_markdown(service_level.retention),
                "",
            ]
        )
    if service_level.latency:
        result.extend(
            [
                "### Latency",
                obj_attributes_to_markdown(service_level.latency),
                "",
            ]
        )
    if service_level.freshness:
        result.extend(
            [
                "### Freshness",
                obj_attributes_to_markdown(service_level.freshness),
                "",
            ]
        )
    if service_level.frequency:
        result.extend(
            [
                "### Frequency",
                obj_attributes_to_markdown(service_level.frequency),
                "",
            ]
        )
    if service_level.support:
        result.extend(
            [
                "### Support",
                obj_attributes_to_markdown(service_level.support),
                "",
            ]
        )
    if service_level.backup:
        result.extend(
            [
                "### Backup",
                obj_attributes_to_markdown(service_level.backup),
                "",
            ]
        )
    return "\n".join(result)


def description_to_markdown(description: str | None) -> str:
    return (description or "No description.").replace("\n", "<br>")
