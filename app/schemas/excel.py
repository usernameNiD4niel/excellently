from marshmallow import Schema, fields, validate

class FormulaSchema(Schema):
    """Schema for formula validation."""
    columns = fields.List(fields.Str(), required=True)
    formula = fields.Str(required=True)

class ExcelFormulaRequestSchema(Schema):
    """Schema for Excel formula request validation."""
    formula = fields.List(fields.Nested(FormulaSchema), required=True)

# Create schema instances
excel_formula_schema = ExcelFormulaRequestSchema() 