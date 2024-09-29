from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Optional

from my_app.models import MaterialType, Insert


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
    name = StringField('Введите код инструмента', validators=[DataRequired()])
    material_tool = StringField('Материал инструмента')
    name_easy = StringField('Название инструмента', validators=[DataRequired()])
    tool_type = SelectField('Тип инструмента', coerce=str, validators=[DataRequired()],
                            choices=[('milling', 'Фреза'), ('turning', 'Токарный инструмент'), ('drilling', 'Сверло')])
    is_insert = BooleanField('Составной инструмент(с пластинами)',
                             default=True, false_values=None)
    submit = SubmitField('Добавить инструмент')


class MillingGeometryForm(FlaskForm):
    tool_type = 'milling'
    name = StringField('Введите код инструмента', validators=[DataRequired()])
    material_tool = StringField('Материал инструмента')
    name_easy = StringField('Название инструмента', validators=[DataRequired()])
    is_insert = BooleanField('Составной инструмент(с пластинами)',
                             default=True, false_values=None)
    insert = StringField('Название пластины')


    diameter = FloatField('Диаметр', validators=[NumberRange(min=0)])
    number_teeth = IntegerField('Количество зубьев', validators=[NumberRange(min=0)])
    front_angle = FloatField('Передний угол', validators=[NumberRange(min=0)])
    spiral_angle = FloatField('Угол винтовой канавки', validators=[NumberRange(min=0)])
    f_rear_angle = FloatField('Задний угол', validators=[NumberRange(min=0)])
    s_rear_angle = FloatField('Вспомогательный задний угол', validators=[NumberRange(min=0)])
    main_rear_angle = FloatField('Основной задний угол', validators=[NumberRange(min=0)])
    angular_pitch = StringField('Винтовая линия')
    submit = SubmitField('Добавить инструмент')

    def __init__(self, *args, **kwargs):
        super(MillingGeometryForm, self).__init__(*args, **kwargs)
        self.insert.choices = [(i.id, i.name) for i in Insert.query.all()]

class TurningGeometryForm(FlaskForm):
    tool_type = 'turning'
    name = StringField('Введите код инструмента', validators=[DataRequired()])
    material_tool = StringField('Материал инструмента')
    name_easy = StringField('Название инструмента', validators=[DataRequired()])
    is_insert = BooleanField('Составной инструмент(с пластинами)',
                             default=True, false_values=None)
    insert = StringField('Название пластины', validators=[DataRequired()])
    turning_type = StringField('Тип токарного инструмента', validators=[DataRequired()])
    front_angle = FloatField('Передняя угол', validators=[NumberRange(min=0)])
    main_rear_angle = FloatField('Задний угол', validators=[NumberRange(min=0)])
    sharpening_angle = FloatField('Угол заострения', validators=[NumberRange(min=0)])
    cutting_angle = FloatField('Угол резания', validators=[NumberRange(min=0)])
    aux_rear_angle = FloatField('Вспомогательный задний угол', validators=[NumberRange(min=0)])
    submit = SubmitField('Добавить инструмент')
class DrillGeometryForm(FlaskForm):
    tool_type = 'turning'
    name = StringField('Введите код инструмента', validators=[DataRequired()])
    material_tool = StringField('Материал инструмента')
    name_easy = StringField('Название инструмента', validators=[DataRequired()])
    is_insert = BooleanField('Составной инструмент(с пластинами)',
                             default=True, false_values=None)
    insert = StringField('Название пластины', validators=[DataRequired()])
    drill_type = StringField('Тип сверла', validators=[DataRequired()])
    diameter = FloatField('Диаметр', validators=[NumberRange(min=0)])
    screw_angle = FloatField('Угол винтовой линии', validators=[NumberRange(min=0)])
    top_angle = FloatField('Угол при вершине', validators=[NumberRange(min=0)])
    front_angle = FloatField('Передний угол', validators=[NumberRange(min=0)])
    rear_angle = FloatField('Задний угол', validators=[NumberRange(min=0)])
    transverse_edge_angle = FloatField('Поперечнй угол уромки', validators=[NumberRange(min=0)])
    submit = SubmitField('Добавить инструмент')