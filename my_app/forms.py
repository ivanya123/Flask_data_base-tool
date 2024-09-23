from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional

from my_app.models import MaterialType

class MaterialForm(FlaskForm):
    name = StringField('Название материала', validators=[DataRequired()])
    prop_physics = StringField('Физико-механические свойства')
    structure = StringField('Химический состав')
    properties = StringField('Свойства')
    gost = StringField('ГОСТ')
    type_id = SelectField('Тип материала', coerce=int, validators=[DataRequired()])  # Поле для выбора типа материала
    new_type = StringField('Добавить новый тип материала', validators=[Optional()])
    submit = SubmitField('Добавить материал')

    def __init__(self, *args, **kwargs):
        super(MaterialForm, self).__init__(*args, **kwargs)
        self.type_id.choices = [(mt.id, mt.name) for mt in MaterialType.query.all()]


class CoatingForm(FlaskForm):
    name = StringField('Название покрытия', validators=[DataRequired()])
    material_coating = StringField('Материал покрытия')
    type_application = StringField('Способ нанесения')
    max_thickness = StringField('Максимальная толщина')
    nanohardness = StringField('Микротвердость')
    temperature_resistance = FloatField('Температурная устойчивость', validators=[NumberRange(min=0)])
    koefficient_friction = FloatField('Коэффициент трения', validators=[NumberRange(min=0)])
    color_coating = StringField('Цвет покрытия')
    submit = SubmitField('Добавить покрытие')


class ToolForm(FlaskForm):
    name = StringField('Название инструмента', validators=[DataRequired()])
    material_tool = StringField('Материал инструмента')
    number_teeth = IntegerField('Количество зубьев', validators=[DataRequired(), NumberRange(min=1)])
    diameter = FloatField('Диаметр', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Добавить инструмент')
