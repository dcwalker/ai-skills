"""Concrete plugin implementations. Each function registers itself with
plugin_registry via the @register decorator when this module is imported."""

from app.plugin_registry import register


@register("csv-export")
def export_csv(data):
    return ",".join(str(v) for v in data)


@register("json-export")
def export_json(data):
    import json
    return json.dumps(data)
