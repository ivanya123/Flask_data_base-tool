from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField, SelectField, BooleanField, FormField, Form, \
    DateField, FieldList
from wtforms.validators import DataRequired, NumberRange, Optional
from datetime import date

from my_app.models import MaterialType, Materials, Coating, Tools


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
    is_indexable = BooleanField('Составной инструмент(с пластинами)',
                                default=False, false_values=None)
    insert = StringField('Название пластины')

    type_milling = StringField('Тип фрезы', validators=[DataRequired()])
    diameter = FloatField('Диаметр', validators=[NumberRange(min=0)])
    diameter_shank = FloatField('Диаметр хвостовика', validators=[NumberRange(min=0)])
    length = FloatField('Длина', validators=[NumberRange(min=0)])
    length_work = FloatField('Длина рабочей части', validators=[NumberRange(min=0)])
    number_teeth = IntegerField('Количество зубьев', validators=[NumberRange(min=0)])
    type_shank = StringField('Тип хостовика', validators=[DataRequired()])  # Поле для выбора типа хвостовика
    spiral_angle = FloatField('Угол наклона стружечных канавок', validators=[NumberRange(min=0)])

    submit = SubmitField('Добавить инструмент')


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


class WearForm(Form):
    length = FloatField('Пройденный путь', validators=[DataRequired(), NumberRange(min=0)])
    wear = FloatField('Износ', validators=[DataRequired(), NumberRange(min=0)])


class ExperimentForm(FlaskForm):
    material_id = SelectField('Материал', coerce=int, validators=[DataRequired()])
    tool_id = SelectField('Инструмент', coerce=int, validators=[DataRequired()])
    coating_id = SelectField('Покрытие', coerce=int, validators=[DataRequired()])
    spindle_speed = FloatField('Скорость шпинделя', validators=[DataRequired()])
    feed_table = FloatField('Подача стола', validators=[DataRequired()])
    depth_cut = FloatField('Глубина резания', validators=[DataRequired()])
    width_cut = FloatField('Ширина резания', validators=[DataRequired()])
    length_path = FloatField('Длина пути', validators=[DataRequired()])
    durability = FloatField('Долговечность', validators=[DataRequired()])
    date_conducted = DateField(
        'Дата проведения эксперимента',
        default=date.today,
        format='%Y-%m-%d',
        validators=[DataRequired()]
    )
    wear_data = FieldList(FormField(WearForm), label='Данные износа')

    submit = SubmitField('Добавить эксперимент')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.material_id.choices = [(mt.id, mt.name) for mt in Materials.query.all()]
        self.tool_id.choices = [(t.id, t.name) for t in Tools.query.all()]
        self.coating_id.choices = [(c.id, c.name) for c in Coating.query.all()]


