from flask import render_template, request, redirect, jsonify, flash
import sqlalchemy as sa

from my_app.forms import MaterialForm, CoatingForm, MillingGeometryForm, TurningGeometryForm, DrillGeometryForm, \
    ExperimentForm
from my_app import app, db
from my_app.models import Materials, Tools, Coating, Experiments, RecommendationParameters, Adhesive, Coefficients, \
    MaterialType, MillingGeometry, TurningGeometry, DrillGeometry, WearTables


@app.route('/')
def select_parameters():
    unique_materials = Materials.query.join(RecommendationParameters).distinct().all()
    unique_tools = Tools.query.join(RecommendationParameters).distinct().all()
    unique_coatings = Coating.query.join(RecommendationParameters).distinct().all()

    return render_template('home.html', unique_materials=unique_materials, unique_tools=unique_tools,
                           unique_coatings=unique_coatings)


@app.route('/recommended_speed', methods=['POST', 'GET'])
def recomended_speeds():
    if request.method == 'POST':
        print(request.form)
        material = int(request.form['material'])
        tool = int(request.form['tool'])
        coating = int(request.form['coating']) if request.form['coating'] != 'None' else "None"
        filters = {
            'material_id': material,
            'tool_id': tool,
        }
        if coating != 'None':
            filters['coating_id'] = coating

        recommendation_parameters = RecommendationParameters.query.filter_by(
            **filters
        ).order_by(
            sa.desc(RecommendationParameters.durability)).all()

    else:
        recommendation_parameters = RecommendationParameters.query.all()

    return render_template('recomended_speed.html', recomended_speed=recommendation_parameters)


@app.route('/add', methods=['POST', 'GET'])
def add():
    material_form = MaterialForm()
    coating_form = CoatingForm()
    milling_geometry_form = MillingGeometryForm()
    turning_form = TurningGeometryForm()
    drill_form = DrillGeometryForm()

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
                                    tool_form=milling_geometry_form)

                new_material = Materials(
                    name=material_form.name.data,
                    prop_physics=material_form.prop_physics.data,
                    structure=material_form.structure.data,
                    properties=material_form.properties.data,
                    gost=material_form.gost.data,
                    type_id=type_id  # Сохранение типа материала
                )
                db.session.add(new_material)
                db.session.commit()
                return redirect('/add')

            if coating_form.submit.data and coating_form.validate_on_submit():
                new_coating = Coating(
                    name=coating_form.name.data,
                    material_coating=coating_form.material_coating.data,
                    type_application=coating_form.type_application.data,
                    max_thickness=coating_form.max_thickness.data,
                    nano_hardness=coating_form.nanohardness.data,
                    temperature_resistance=coating_form.temperature_resistance.data,
                    coefficient_friction=coating_form.koefficient_friction.data,
                    color_coating=coating_form.color_coating.data
                )
                db.session.add(new_coating)
                db.session.commit()
                return redirect('/add')

            if milling_geometry_form.submit.data:
                if milling_geometry_form.validate_on_submit():
                    new_tool = Tools(
                        name=milling_geometry_form.name.data,
                        name_easy=milling_geometry_form.name_easy.data,
                        tool_type=milling_geometry_form.tool_type,
                        material_tool=milling_geometry_form.material_tool.data,
                        is_indexable=milling_geometry_form.is_indexable.data
                    )
                    new_milling_geometry = MillingGeometry(
                        type_milling=milling_geometry_form.type_milling.data,
                        diameter=milling_geometry_form.diameter.data,
                        diameter_shank=milling_geometry_form.diameter_shank.data,
                        length=milling_geometry_form.length.data,
                        length_work=milling_geometry_form.length_work.data,
                        number_teeth=milling_geometry_form.number_teeth.data,
                        spiral_angle=milling_geometry_form.spiral_angle.data,
                        type_shank=milling_geometry_form.type_shank.data
                    )

                    new_tool.milling_geometry = new_milling_geometry
                    db.session.add(new_tool)
                    db.session.commit()
                    return redirect('/add')
                else:
                    return 'Не пройдена валидация'

        except Exception as e:
            return f'Ошибка: {e}'

    return render_template('add.html', material_form=material_form, coating_form=coating_form,
                           milling_geometry_form=milling_geometry_form, turning_form=turning_form,
                           drill_form=drill_form)


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
    cutting_temperature = coefficient.cutting_temperature_coefficient * (cutting_speed ** a_temp) * (
            feed_per_tooth ** b_temp)

    # Расчет стойкости инструмента
    tool_life = coefficient.durability_coefficient * (cutting_speed ** a_life) * (feed_per_tooth ** b_life)

    return jsonify({
        'cutting_force': cutting_force,
        'cutting_temperature': cutting_temperature,
        'tool_life': tool_life
    })


@app.route('/materials/<int:materaial_id>/delete')
def delete_materials(materaial_id):
    delete_str = Materials.query.get_or_404(materaial_id)
    try:
        db.session.delete(delete_str)
        db.session.commit()
        return redirect('/materials')
    except Exception:
        return 'Ошибка при удалении'


@app.route('/materials/<int:material_id>/update', methods=['GET', 'POST'])
def materials_update(material_id):
    material_form = MaterialForm()
    material = Materials.query.get_or_404(material_id)
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
                    return render_template('materials_update.html',
                                           material=material,
                                           material_form=material_form)

                material.name = material_form.name.data
                material.prop_physics = material_form.prop_physics.data
                material.structure = material_form.structure.data
                material.properties = material_form.properties.data
                material.gost = material_form.gost.data
                material.type_id = type_id

                db.session.commit()
                return redirect('/materials')
        except Exception as e:
            return f'Ошибка: {e}'

    material_form.type_id.data = material.type_id
    return render_template('materials_update.html',
                           material=material,
                           material_form=material_form)


@app.route("/material/<int:materaial_id>/info")
def mat_info(material_id):
    material = Materials.query.get_or_404(material_id)
    return render_template('material.html', material=material)


@app.route('/coatings')
def caotings():
    coatings = Coating.query.order_by(Coating.name).all()
    return render_template('coating.html', coatings=coatings)


@app.route('/coating/<int:coating_id>/delete')
def delete_coating(coating_id):
    delete_str = Coating.query.get_or_404(coating_id)
    try:
        db.session.delete(delete_str)
        db.session.commit()
        return redirect('/coatings')
    except:
        return 'Ошибка при удалении'


@app.route('/coating/<int:coating_id>/update', methods=['GET', 'POST'])
def coating_update(coating_id):
    coating = Coating.query.get(coating_id)
    coating_form = CoatingForm()
    if request.method == 'POST':
        try:
            if coating_form.submit.data and coating_form.validate_on_submit():
                coating.name = coating_form.name.data
                coating.material_coating = coating_form.material_coating.data
                coating.max_thickness = coating_form.max_thickness.data
                coating.nanohardness = coating_form.nanohardness.data
                coating.temperature_resistance = coating_form.temperature_resistance.data
                coating.koefficient_friction = coating_form.koefficient_friction.data
                coating.color_coating = coating_form.color_coating.data

                db.session.commit()
                return redirect('/coatings')
            else:
                return render_template('coating_update.html', coating=coating, coating_form=coating_form)
        except Exception as e:
            return f'Ошибка: {e}'

    return render_template('coating_update.html', coating=coating, coating_form=coating_form)


@app.route("/coating/<int:coating_id>/info")
def coat_info(coating_id):
    coating = Coating.query.get_or_404(coating_id)
    return render_template('coating.html', coating=coating)


@app.route('/tools')
def tools():
    # Получаем параметры запроса
    tool_type = request.args.get('tool_type', 'all')
    search_query = request.args.get('search_query', '')

    # Базовый запрос
    query = Tools.query

    # Фильтрация по типу инструмента
    if tool_type != 'all':
        query = query.filter(Tools.tool_type == tool_type)

    # Поиск по названию
    if search_query:
        query = query.filter(Tools.name.ilike(f'%{search_query}%'))

    # Оптимизация запроса с подгрузкой связанных геометрий
    query = query.options(
        db.joinedload(Tools.milling_geometry),
        db.joinedload(Tools.turning_geometry),
        db.joinedload(Tools.drill_geometry)
    )

    # Загружаем все инструменты
    tools = query.all()

    return render_template('tools.html', tools=tools, selected_tool_type=tool_type, search_query=search_query)


@app.route('/tool/<int:tool_id>/delete')
def delete_tool(tool_id):
    delete_str = Tools.query.get_or_404(tool_id)
    tool_geometry = [getattr(delete_str, 'milling_geometry'),
                     getattr(delete_str, 'turning_geometry'),
                     getattr(delete_str, 'drill_geometry')]

    try:
        db.session.delete(delete_str)
        for geom in tool_geometry:
            if geom:
                db.session.delete(geom)
        db.session.commit()
        return redirect('/tools')
    except:
        return 'Ошибка при удалении'


@app.route('/tool/<int:tool_id>/update', methods=['GET', 'POST'])
def tool_update(tool_id):
    tool = Tools.query.get(tool_id)
    if request.method == 'POST':
        tool.name = request.form['Name5']
        tool.material_tool = request.form['Name6']
        tool.number_teeth = request.form['Name8']
        tool.diameter = request.form['Name9']
        try:
            db.session.commit()
            return redirect('/tools')
        except:
            return 'Ошибка'

    return render_template('tool_update.html', tool=tool)


@app.route("/tool/<int:tool_id>/info")
def tools_info(tool_id):
    tool = Tools.query.get_or_404(tool_id)
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
        experiments_query = experiments_query.filter(Experiments.material.ilike(f'%{material_filter}%'))

    if coating_filter:
        experiments_query = experiments_query.filter(Experiments.coating.ilike(f'%{coating_filter}%'))

    if spindle_min:
        experiments_query = experiments_query.filter(Experiments.spindle_speed >= spindle_min)

    if spindle_max:
        experiments_query = experiments_query.filter(Experiments.spindle_speed <= spindle_max)

    if feed_min:
        experiments_query = experiments_query.filter(Experiments.feed_table >= feed_min)

    if feed_max:
        experiments_query = experiments_query.filter(Experiments.feed_table <= feed_max)

    if sort_by:
        if order == 'desc':
            experiments_query = experiments_query.order_by(sa.desc(getattr(Experiments, sort_by)))
        else:
            experiments_query = experiments_query.order_by(sa.asc(getattr(Experiments, sort_by)))

    experiments = experiments_query.all()

    return render_template('experiment.html',
                           experiment=experiments,
                           sort_by=sort_by,
                           order=order,
                           request_args=request.args)


@app.route('/experiment/add', methods=['GET', 'POST'])
def add_experiment():
    form = ExperimentForm()
    if request.method == 'POST':
        total_enries = len([key for key in request.form.keys() if 'wear_data-' in key and '-length' in key])
        form.wear_data.min_entries = total_enries
        form = ExperimentForm(request.form)

        if form.validate():
            new_experiment = Experiments(
                material_id=form.material_id.data,
                tool_id=form.tool_id.data,
                coating_id=form.coating_id.data,
                spindle_speed=form.spindle_speed.data,
                feed_table=form.feed_table.data,
                depth_cut=form.depth_cut.data,
                width_cut=form.width_cut.data,
                length_path=form.length_path.data,
                durability=form.durability.data,
                data_experiment=form.date_conducted.data
            )
            db.session.add(new_experiment)
            db.session.flush()
            for wear_form in form.wear_data.entries:
                wear_entry = WearTables(
                    experiment_id=new_experiment.id,
                    length=wear_form.form.length.data,
                    wear=wear_form.form.wear.data
                )
                db.session.add(wear_entry)
            db.session.commit()

            flash(f'Добавлен новый эксперимент: Номер - {new_experiment.id}', 'success')
        else:
            print(form.errors)
    return render_template('add_experiment.html', form=form)




@app.route("/experiments/<int:experiment_id>/info")
def experiments_info(experiment_id):
    experiment = Experiments.query.get_or_404(experiment_id)
    return render_template('experiment_info.html', experiment=experiment)


@app.route("/adhesive")
def adhesive():
    adhesive_table = Adhesive.query.all()
    return render_template('adhesive.html', adhesive=adhesive_table)


@app.route("/expected_parameters", methods=['GET', 'POST'])
def expected_parameters():
    materials = Materials.query.all()
    tools = Tools.query.all()
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

    tool = Tools.query.get(tool_id)
    diameter = tool.milling_geometry.diameter
    count_of_teeth = tool.milling_geometry.number_teeth

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
