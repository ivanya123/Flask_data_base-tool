from flask import render_template, request, redirect, jsonify, flash, url_for
from sqlalchemy.orm import joinedload

from my_app import app, db
from my_app.forms import MaterialForm, CoatingForm, MillingGeometryForm, TurningGeometryForm, DrillGeometryForm, \
    ExperimentForm, ToolForm
from my_app.models import Materials, Tools, Coating, Experiments, RecommendationParameters, Adhesive, Coefficients, \
    MaterialType, MillingGeometry, WearTables, DrillGeometry, TurningGeometry


@app.route('/')
def select_parameters():
    unique_materials = Materials.query.join(RecommendationParameters).distinct().all()
    unique_tools = Tools.query.join(RecommendationParameters).distinct().all()
    unique_coatings = Coating.query.join(RecommendationParameters).distinct().all()

    return render_template('home.html', unique_materials=unique_materials, unique_tools=unique_tools,
                           unique_coatings=unique_coatings)


@app.route('/recommended_speed', methods=['POST', 'GET'])
def recommended_speed():
    # Получаем значения фильтров из параметров запроса
    material_id = request.args.get('material_id', type=int)
    coating_id = request.args.get('coating_id', type=int)
    tool_id = request.args.get('tool_id', type=int)

    # Получаем списки для выпадающих списков
    materials = Materials.query.join(RecommendationParameters).distinct().all()
    coatings = Coating.query.join(RecommendationParameters).distinct().all()
    tools = Tools.query.join(RecommendationParameters).distinct().all()

    # Формируем запрос с учетом фильтров
    query = RecommendationParameters.query.options(
        joinedload(RecommendationParameters.material),
        joinedload(RecommendationParameters.tool),
        joinedload(RecommendationParameters.coating))
    if material_id:
        query = query.filter_by(material_id=material_id)
    if coating_id:
        query = query.filter_by(coating_id=coating_id)
    if tool_id:
        query = query.filter_by(tool_id=tool_id)

    recomended_speed = query.all()

    return render_template('recommend_speed.html',
                           recomended_speed=recomended_speed,
                           materials=materials,
                           coatings=coatings,
                           tools=tools,
                           selected_material_id=material_id,
                           selected_coating_id=coating_id,
                           selected_tool_id=tool_id)


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


@app.route("/material/<int:material_id>/info")
def mat_info(material_id):
    material = Materials.query.get_or_404(material_id)
    return render_template('mat_info.html', material=material)


@app.route('/coatings')
def coatings():
    search_query = request.args.get('search_query', '')
    coatings = Coating.query.order_by(Coating.name)
    if search_query:
        coatings = [coating for coating in coatings.all() if search_query.lower() in coating.name.lower()]
    else:
        coatings = coatings.all()
    return render_template('coating.html', coatings=coatings, search_query=search_query)


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
    return render_template('coat_info.html', coating=coating)


@app.route('/tools')
def tools():
    # Получаем параметры запроса
    tool_type = request.args.get('tool_type', 'all')
    search_query = request.args.get('search_query', '')

    # Оптимизация запроса с подгрузкой связанных геометрий
    query = Tools.query.options(
        db.joinedload(Tools.milling_geometry),
        db.joinedload(Tools.turning_geometry),
        db.joinedload(Tools.drill_geometry)
    )

    # Фильтрация по типу инструмента
    if tool_type != 'all':
        query = query.filter(Tools.tool_type == tool_type)

    # Поиск по названию
    if search_query:
        tools = [tool for tool in query.all() if search_query.lower() in tool.name.lower()]
    else:
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
    tool = Tools.query.get_or_404(tool_id)

    # Определяем, какую форму использовать в зависимости от типа инструмента
    if tool.tool_type == 'milling':
        form = MillingGeometryForm()
    elif tool.tool_type == 'turning':
        form = TurningGeometryForm()
    elif tool.tool_type == 'drilling':
        form = DrillGeometryForm()
    else:
        form = ToolForm()

    if request.method == 'GET':
        # Предзаполняем форму данными инструмента
        form.name.data = tool.name
        form.material_tool.data = tool.material_tool
        form.name_easy.data = tool.name_easy
        form.is_indexable.data = tool.is_indexable  # Убедитесь, что поле называется `is_insert` или `is_indexable`

        # Предзаполняем данные геометрии инструмента
        if tool.tool_type == 'milling' and tool.milling_geometry:
            form.type_milling.data = tool.milling_geometry.type_milling
            form.diameter.data = tool.milling_geometry.diameter
            form.diameter_shank.data = tool.milling_geometry.diameter_shank
            form.length.data = tool.milling_geometry.length
            form.length_work.data = tool.milling_geometry.length_work
            form.number_teeth.data = tool.milling_geometry.number_teeth
            form.type_shank.data = tool.milling_geometry.type_shank
            form.spiral_angle.data = tool.milling_geometry.spiral_angle
        elif tool.tool_type == 'turning' and tool.turning_geometry:
            form.turning_type.data = tool.turning_geometry.turning_type
            form.front_angle.data = tool.turning_geometry.front_angle
            form.main_rear_angle.data = tool.turning_geometry.main_rear_angle
            form.sharpening_angle.data = tool.turning_geometry.sharpening_angle
            form.cutting_angle.data = tool.turning_geometry.cutting_angle
            form.aux_rear_angle.data = tool.turning_geometry.aux_rear_angle
        elif tool.tool_type == 'drilling' and tool.drill_geometry:
            form.drill_type.data = tool.drill_geometry.drill_type
            form.diameter.data = tool.drill_geometry.diameter
            form.screw_angle.data = tool.drill_geometry.screw_angle
            form.top_angle.data = tool.drill_geometry.top_angle
            form.front_angle.data = tool.drill_geometry.front_angle
            form.rear_angle.data = tool.drill_geometry.rear_angle
            form.transverse_edge_angle.data = tool.drill_geometry.transverse_edge_angle

    elif form.validate_on_submit():
        # Обновляем основные поля инструмента
        tool.name = form.name.data
        tool.material_tool = form.material_tool.data
        tool.name_easy = form.name_easy.data
        tool.is_indexable = form.is_indexable.data  # Убедитесь, что поле называется правильно

        # Обновляем данные геометрии инструмента
        if tool.tool_type == 'milling':
            if not tool.milling_geometry:
                tool.milling_geometry = MillingGeometry()
            tool.milling_geometry.type_milling = form.type_milling.data
            tool.milling_geometry.diameter = form.diameter.data
            tool.milling_geometry.diameter_shank = form.diameter_shank.data
            tool.milling_geometry.length = form.length.data
            tool.milling_geometry.length_work = form.length_work.data
            tool.milling_geometry.number_teeth = form.number_teeth.data
            tool.milling_geometry.type_shank = form.type_shank.data
            tool.milling_geometry.spiral_angle = form.spiral_angle.data
        elif tool.tool_type == 'turning':
            if not tool.turning_geometry:
                tool.turning_geometry = TurningGeometry()
            tool.turning_geometry.turning_type = form.turning_type.data
            tool.turning_geometry.front_angle = form.front_angle.data
            tool.turning_geometry.main_rear_angle = form.main_rear_angle.data
            tool.turning_geometry.sharpening_angle = form.sharpening_angle.data
            tool.turning_geometry.cutting_angle = form.cutting_angle.data
            tool.turning_geometry.aux_rear_angle = form.aux_rear_angle.data
        elif tool.tool_type == 'drilling':
            if not tool.drill_geometry:
                tool.drill_geometry = DrillGeometry()
            tool.drill_geometry.drill_type = form.drill_type.data
            tool.drill_geometry.diameter = form.diameter.data
            tool.drill_geometry.screw_angle = form.screw_angle.data
            tool.drill_geometry.top_angle = form.top_angle.data
            tool.drill_geometry.front_angle = form.front_angle.data
            tool.drill_geometry.rear_angle = form.rear_angle.data
            tool.drill_geometry.transverse_edge_angle = form.transverse_edge_angle.data

        try:
            db.session.commit()
            flash('Инструмент успешно обновлен!', 'success')
            return redirect(url_for('tools_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении инструмента: {e}', 'danger')
    else:
        if request.method == 'POST':
            flash('Пожалуйста, исправьте ошибки в форме.', 'danger')

    return render_template('tool_update.html', form=form, tool=tool)


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

    experiments_query = Experiments.query.options(joinedload(Experiments.material), joinedload(Experiments.coating),
                                                  joinedload(Experiments.tool)).all()

    # Фильтрация уже в Python
    if material_filter:
        experiments_query = [exp for exp in experiments_query if material_filter.lower() in exp.material.name.lower()]

    if coating_filter:
        experiments_query = [exp for exp in experiments_query if coating_filter.lower() in exp.coating.name.lower()]

    if spindle_min:
        experiments_query = [exp for exp in experiments_query if exp.spindle_speed >= float(spindle_min)]

    if spindle_max:
        experiments_query = [exp for exp in experiments_query if exp.spindle_speed <= float(spindle_max)]

    if feed_min:
        experiments_query = [exp for exp in experiments_query if exp.feed_table >= float(feed_min)]

    if feed_max:
        experiments_query = [exp for exp in experiments_query if exp.feed_table <= float(feed_max)]

    if sort_by:
        reverse = (order == 'desc')
        experiments_query = sorted(experiments_query, key=lambda x: getattr(x, sort_by), reverse=reverse)

    return render_template('experiment.html',
                           experiment=experiments_query,
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
    uniq_material = Materials.query.join(Adhesive).distinct().all()
    uniq_coating = Coating.query.join(Adhesive).distinct().all()
    uniq_temperature = Adhesive.query.with_entities(Adhesive.temperature).distinct().all()

    selected_material = request.args.get('material_id')
    selected_coating = request.args.get('coating_id')
    selected_temperature = request.args.get('temperature')

    query = Adhesive.query

    if selected_material:
        selected_material = int(selected_material)  # Преобразуем в целое число
        query = query.filter(Adhesive.material_id == selected_material)
    else:
        selected_material = None

    if selected_coating:
        selected_coating = int(selected_coating)  # Преобразуем в целое число
        query = query.filter(Adhesive.coating_id == selected_coating)
    else:
        selected_coating = None

    if selected_temperature:
        selected_temperature = float(selected_temperature)  # Преобразуем в число с плавающей точкой
        query = query.filter(Adhesive.temperature == selected_temperature)
    else:
        selected_temperature = None

    adhesive_table = query.all()

    return render_template('adhesive.html',
                           adhesive=adhesive_table,
                           materials=uniq_material,
                           coatings=uniq_coating,
                           uniq_temperature=uniq_temperature,
                           selected_temperature=selected_temperature,
                           selected_coating=selected_coating,
                           selected_material=selected_material)


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
    diameter = tool.milling_geometry.diameter if tool.milling_geometry else None
    count_of_teeth = tool.milling_geometry.number_teeth if tool.milling_geometry else None

    coefficient: Coefficients = Coefficients.query.filter_by(
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
            'coating_id': coating_id,
            'material_name': coefficient.material.name,
            'tool_id': tool_id
        }

    # Получаем рекомендуемые режимы резания
    recommended = RecommendationParameters.query.filter_by(
        material_id=material_id,
        tool_id=tool_id,
        coating_id=coating_id
    ).first()

    if recommended:
        # Вычисляем дополнительные параметры
        cutting_speed = recommended.cutter_speed
        feed_per_tooth = recommended.feed_of_teeth
        cutting_force = recommended.Fz
        temperature = recommended.temperature
        durability = recommended.durability_

        recommended_data = {
            'spindle_speed': recommended.spindle_speed,
            'feed_rate': recommended.feed_table,
            'cutting_speed': round(cutting_speed, 2) if cutting_speed else None,
            'feed_per_tooth': round(feed_per_tooth, 3) if feed_per_tooth else None,
            'cutting_force': round(cutting_force, 2) if cutting_force else None,
            'temperature': round(temperature, 2) if temperature else None,
            'durability': round(durability, 2) if isinstance(durability, (int, float)) else durability
        }
    else:
        recommended_data = None

    return jsonify({'status': 'success', 'recommended_data': recommended_data})
