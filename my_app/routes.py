from flask import Flask, render_template, request, redirect, jsonify
import sqlalchemy as sa
from sqlalchemy.orm import load_only
from sqlalchemy import func

from my_app.forms import MaterialForm, CoatingForm, ToolForm
from my_app import app, db
from my_app.models import Materials, Toolsdate, Coating, Experiments, RecomededSpeed, Adhesive, Coefficients, \
    MaterialType


@app.route('/')
def select_parameters():
    unique_materials = RecomededSpeed.query.with_entities(RecomededSpeed.Material).distinct().all()
    unique_tools = RecomededSpeed.query.with_entities(RecomededSpeed.Tool).distinct().all()
    unique_coatings = RecomededSpeed.query.with_entities(RecomededSpeed.Coating).distinct().all()

    return render_template('home.html', unique_materials=unique_materials, unique_tools=unique_tools,
                           unique_coatings=unique_coatings)


@app.route('/recommended_speed', methods=['POST', 'GET'])
def recomended_speeds():
    if request.method == 'POST':
        material = request.form['material']
        tool = request.form['tool']
        coating = request.form['coating']
        filters = {
            RecomededSpeed.Material: material,
            RecomededSpeed.Tool: tool,
        }
        if coating != 'None':
            filters[RecomededSpeed.Coating] = coating

        recomended_speed = RecomededSpeed.query.filter_by(**filters).options(
            load_only(RecomededSpeed.Material, RecomededSpeed.Tool, RecomededSpeed.Coating,
                      RecomededSpeed.SpindleSpeed, RecomededSpeed.FeedTable, RecomededSpeed.Durability)
        ).order_by(sa.desc(RecomededSpeed.Durability)).all()

    else:
        recomended_speed = RecomededSpeed.query.options(
            load_only(RecomededSpeed.Material, RecomededSpeed.Tool, RecomededSpeed.Coating,
                      RecomededSpeed.SpindleSpeed, RecomededSpeed.FeedTable, RecomededSpeed.Durability)
        ).all()

    return render_template('recomended_speed.html', recomended_speed=recomended_speed)


@app.route('/add', methods=['POST', 'GET'])
def add():
    material_form = MaterialForm()
    coating_form = CoatingForm()
    tool_form = ToolForm()

    if request.method == 'POST':
        try:
            if material_form.submit.data and material_form.validate_on_submit():
                if material_form.new_type.data:
                    existing_type = MaterialType.query.filter_by(name=material_form.new_type.data).first()
                    if existing_type:
                        type_id = existing_type.id
                    else:
                        new_material_type = MaterialType(name=material_form.new_type.data)
                        db.session.add(new_material_type)
                        db.session.commit()
                        type_id = new_material_type.id
                else:
                    type_id = material_form.type_id.data

                if type_id == 0:
                    material_form.type_id.errors.append('Пожалуйста, выберите тип материала или добавьте новый.')
                    render_template('add.html', material_form=material_form, coating_form=coating_form,
                                    tool_form=tool_form)

                new_material = Materials(
                    Name=material_form.name.data,
                    PropPhysics=material_form.prop_physics.data,
                    Structure=material_form.structure.data,
                    Properties=material_form.properties.data,
                    Gost=material_form.gost.data,
                    type_id=type_id  # Сохранение типа материала
                )
                db.session.add(new_material)
                db.session.commit()
                return redirect('/add')

            if coating_form.submit.data and coating_form.validate_on_submit():
                new_coating = Coating(
                    Name=coating_form.name.data,
                    MaterialCoating=coating_form.material_coating.data,
                    TypeApplication=coating_form.type_application.data,
                    MaxThickness=coating_form.max_thickness.data,
                    NanoHardness=coating_form.nanohardness.data,
                    TemratureResistance=coating_form.temperature_resistance.data,
                    KoefficientFriction=coating_form.koefficient_friction.data,
                    ColorCoating=coating_form.color_coating.data
                )
                db.session.add(new_coating)
                db.session.commit()
                return redirect('/add')

            if tool_form.submit.data and tool_form.validate_on_submit():
                new_tool = Toolsdate(
                    Name=tool_form.name.data,
                    MaterialTool=tool_form.material_tool.data,
                    NumberTeeth=tool_form.number_teeth.data,
                    Diameter=tool_form.diameter.data
                )
                db.session.add(new_tool)
                db.session.commit()
                return redirect('/add')

        except Exception as e:
            return f'Ошибка: {e}'

    return render_template('add.html', material_form=material_form, coating_form=coating_form, tool_form=tool_form)


@app.route('/materials', methods=['GET', 'POST'])
def materials_table():
    # Получаем все типы материалов для выпадающего списка
    material_types = MaterialType.query.all()

    # Параметры фильтрации и поиска
    selected_type_id = request.args.get('type_id')
    search_query = request.args.get('search_query', '')

    # Базовый запрос
    materials_query = Materials.query

    # Фильтрация по типу материала, если выбран
    if selected_type_id and selected_type_id != 'all':
        materials_query = materials_query.filter_by(type_id=selected_type_id)

    # Поиск по названию материала
    if search_query:
        materials_query = materials_query.filter(Materials.name.ilike(f'%{search_query}%'))

    # Получаем отсортированный список материалов
    materials = materials_query.order_by(Materials.name).all()

    return render_template('materials.html', materials=materials, material_types=material_types,
                           selected_type_id=selected_type_id, search_query=search_query)


@app.route('/materials/search')
def search_materials():
    search_query = request.args.get('search_query', '')
    type_id = request.args.get('type_id', 'all')

    materials = Materials.query
    # Ищем материалы, соответствующие запросу
    if type_id != 'all':
        materials = materials.filter_by(type_id=type_id)
    if search_query:
        filtered_materials = [material for material in materials.all() if search_query.lower() in material.name.lower()]
    else:
        filtered_materials = materials.all()

    # Преобразуем результат в список словарей
    materials_list = [{
        'id': material.id,
        'name': material.name,
        'prop_physics': material.prop_physics,
        'structure': material.structure,
        'properties': material.properties,
        'gost': material.gost
    } for material in filtered_materials]

    return jsonify(materials_list)

@app.route('/materials/by_type/<int:type_id>')
def get_materials_by_type(type_id):
    # Получаем материалы, соответствующие выбранному типу
    materials = Materials.query.filter_by(type_id=type_id).all()
    # Преобразуем материалы в список словарей
    materials_list = [{'id': material.id, 'name': material.name} for material in materials]
    return jsonify(materials_list)


@app.route('/calculate')
def calculate():
    cutting_speed_value = request.args.get('cutting_speed', '0')  # Получаем значение как строку
    try:
        cutting_speed = float(cutting_speed_value)  # Пробуем преобразовать в float
    except ValueError:
        cutting_speed = 0  # В случае ошибки устанавливаем значение по умолчанию
        print(f"Некорректное значение cutting_speed: {cutting_speed_value}")

    feed_per_tooth_value = request.args.get('feed_per_tooth', '0')
    try:
        feed_per_tooth = float(feed_per_tooth_value)
    except ValueError:
        feed_per_tooth = 0
        print(f"Некорректное значение feed_per_tooth: {feed_per_tooth_value}")

    material_id = request.args.get('material_id')
    tool_id = request.args.get('tool_id')
    coating_id = request.args.get('coating_id')


    # Получаем коэффициенты из базы данных
    coefficient = Coefficients.query.filter_by(
        material_id=material_id,
        tool_id=tool_id,
        coating_id=coating_id
    ).first()

    # Если коэффициенты не найдены, возвращаем пустой результат
    if not coefficient:
        return jsonify({
            'cutting_force': 0,
            'cutting_temperature': 0,
            'tool_life': 0
        })

    # Показатели степени (известны и фиксированы)
    a_force = -0.12
    b_force = 0.95
    a_temp = 0.4
    b_temp = 0.24
    a_life = -0.2
    b_life = -0.15

    # Расчет силы резания
    cutting_force = coefficient.cutting_force_coefficient * (cutting_speed ** a_force) * (feed_per_tooth ** b_force)

    # Расчет температуры резания
    cutting_temperature = coefficient.cutting_temperature_coefficient * (cutting_speed ** a_temp) * (feed_per_tooth ** b_temp)

    # Расчет стойкости инструмента
    tool_life = coefficient.durability_coefficient * (cutting_speed ** a_life) * (feed_per_tooth ** b_life)

    return jsonify({
        'cutting_force': cutting_force,
        'cutting_temperature': cutting_temperature,
        'tool_life': tool_life
    })




@app.route('/materials/<int:id>/delete')
def delete_materials(id):
    delete_str = Materials.query.get_or_404(id)
    try:
        db.session.delete(delete_str)
        db.session.commit()
        return redirect('/materials')
    except:
        return 'Ошибка при удалении'


@app.route('/materials/<int:id>/update', methods=['GET', 'POST'])
def materials_update(id):
    materials = Materials.query.get_or_404(id)
    if request.method == 'POST':
        materials.name = request.form['name']
        materials.prop_physics = request.form['NameP']
        materials.structure = request.form['NameX']
        materials.properties = request.form['NamePr']
        materials.gost = request.form['NameGost']
        try:
            db.session.commit()
            return redirect('/materials')
        except:
            return 'Ошибка'

    return render_template('materials_update.html', materials=materials)


@app.route("/material/<int:id>/info")
def mat_info(id):
    material = Materials.query.get_or_404(id)
    return render_template('mat_info.html', material=material)


@app.route('/coatings')
def caotings():
    coatings = Coating.query.order_by(Coating.Name).all()
    return render_template('coating.html', coatings=coatings)


@app.route('/coating/<int:id>/delete')
def delete_coating(id):
    delete_str = Coating.query.get_or_404(id)
    try:
        db.session.delete(delete_str)
        db.session.commit()
        return redirect('/coatings')
    except:
        return 'Ошибка при удалении'


@app.route('/coating/<int:id>/update', methods=['GET', 'POST'])
def coating_update(id):
    coatings = Coating.query.get(id)
    if request.method == 'POST':
        coatings.name = request.form['Name1']
        coatings.MaterialCoating = request.form['Name2']
        coatings.TypeApplication = request.form['Name3']
        coatings.MaxThickness = request.form['Name4']
        coatings.NanoHardness = request.form['NameNano']
        coatings.TemratureResistance = request.form['NameResistnce']
        coatings.KoefficientFriction = request.form['NameKoef']
        coatings.ColorCoating = request.form['Color']

        try:
            db.session.commit()
            return redirect('/coatings')
        except:
            return 'Ошибка'

    return render_template('coating_update.html', coating=coatings)


@app.route("/coating/<int:id>/info")
def coat_info(id):
    coating = Coating.query.get_or_404(id)
    return render_template('coat_info.html', coating=coating)


@app.route('/tools')
def tools_table():
    tools = Toolsdate.query.order_by(Toolsdate.Name).all()
    return render_template('tools.html', tools=tools)


@app.route('/tool/<int:id>/delete')
def delete_tool(id):
    delete_str = Toolsdate.query.get_or_404(id)
    try:
        db.session.delete(delete_str)
        db.session.commit()
        return redirect('/tools')
    except:
        return 'Ошибка при удалении'


@app.route('/tool/<int:id>/update', methods=['GET', 'POST'])
def tool_update(id):
    tool = Toolsdate.query.get(id)
    if request.method == 'POST':
        tool.name = request.form['Name5']
        tool.MaterialTool = request.form['Name6']
        tool.NumberTeeth = request.form['Name8']
        tool.Diameter = request.form['Name9']
        try:
            db.session.commit()
            return redirect('/tools')
        except:
            return 'Ошибка'

    return render_template('tool_update.html', tool=tool)


@app.route("/tool/<int:id>/info")
def tools_info(id):
    tool = Toolsdate.query.get_or_404(id)
    return render_template('tool_info.html', tool=tool)


@app.route('/experiments')
def experiments_table():
    material_filter = request.args.get('material', '')
    coating_filter = request.args.get('coating', '')
    spindle_min = request.args.get('spindle_min')
    spindle_max = request.args.get('spindle_max')
    feed_min = request.args.get('feed_min')
    feed_max = request.args.get('feed_max')
    sort_by = request.args.get('sort_by')
    order = request.args.get('order', 'asc')

    experiments_query = Experiments.query

    if material_filter:
        experiments_query = experiments_query.filter(Experiments.Material.ilike(f'%{material_filter}%'))

    if coating_filter:
        experiments_query = experiments_query.filter(Experiments.Coating.ilike(f'%{coating_filter}%'))

    if spindle_min:
        experiments_query = experiments_query.filter(Experiments.SpindleSpeed >= spindle_min)

    if spindle_max:
        experiments_query = experiments_query.filter(Experiments.SpindleSpeed <= spindle_max)

    if feed_min:
        experiments_query = experiments_query.filter(Experiments.FeedTable >= feed_min)

    if feed_max:
        experiments_query = experiments_query.filter(Experiments.FeedTable <= feed_max)

    if sort_by:
        if order == 'desc':
            experiments_query = experiments_query.order_by(sa.desc(getattr(Experiments, sort_by)))
        else:
            experiments_query = experiments_query.order_by(sa.asc(getattr(Experiments, sort_by)))

    experiments = experiments_query.all()

    return render_template('experiment.html', experiment=experiments, sort_by=sort_by, order=order,
                           request_args=request.args)


@app.route("/experiments/<int:id>/info")
def experiments_info(id):
    experiment = Experiments.query.get_or_404(id)
    return render_template('experiment_info.html', experiment=experiment)


@app.route("/adhesive")
def adhesive():
    adhesive = Adhesive.query.all()
    return render_template('adhesive.html', adhesive=adhesive)


@app.route("/expected_parameters", methods=['GET', 'POST'])
def expected_parameters():
    materials = Materials.query.all()
    tools = Toolsdate.query.all()
    coatings = Coating.query.all()
    material_types = MaterialType.query.all()

    selected_material = None
    selected_tool = None
    selected_coating = None
    coefficient = None


    return render_template(
        'expected_parameters.html',
        materials=materials,
        tools=tools,
        coatings=coatings,
        coefficient=coefficient,
        selected_material=selected_material,
        selected_tool=selected_tool,
        selected_coating=selected_coating,
        material_types=material_types
    )

@app.route('/update_graph_data', methods=['POST'])
def update_graph_data():
    data = request.json
    material_id = data.get('material_id')
    tool_id = data.get('tool_id')
    coating_id = data.get('coating_id')

    tool = Toolsdate.query.get(tool_id)
    diameter = tool.Diameter
    count_of_teeth = tool.NumberTeeth

    coefficient = Coefficients.query.filter_by(
        material_id=material_id,
        tool_id=tool_id,
        coating_id=coating_id
    ).first()

    if not coefficient:
        app.config['GRAPH_DATA'] = {}
    else:
        app.config['GRAPH_DATA'] = {
            'cutting_force_coefficient': coefficient.cutting_force_coefficient,
            'cutting_temperature_coefficient': coefficient.cutting_temperature_coefficient,
            'durability_coefficient': coefficient.durability_coefficient,
            'diameter': diameter,
            'teeth_count': count_of_teeth,
        }

    return jsonify({'status': 'success'})

@app.route('/update_dash_values', methods=['GET', 'POST'])
def update_dash_values():
    # Получаем значения слайдеров от Dash
    dash_values = app.config.get('DASH_SLIDER_VALUES', {})
    return jsonify(dash_values)
