from flask import Flask, render_template, request, redirect
import sqlalchemy as sa
from sqlalchemy.orm import load_only

from my_app.forms import MaterialForm, CoatingForm, ToolForm
from my_app import app, db
from my_app.models import Material, Toolsdate, Coating, Experiments, RecomededSpeed, Adhesive, Coefficients

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
                new_material = Material(
                    name=material_form.name.data,
                    prop_physics=material_form.prop_physics.data,
                    structure=material_form.structure.data,
                    properties=material_form.properties.data,
                    gost=material_form.gost.data,
                    type_id=material_form.type_id.data  # Сохранение типа материала
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


@app.route('/materials')
def materials_table():
    materials = Material.query.order_by(Material.Name).all()
    return render_template('materials.html', materials=materials)


@app.route('/materials/<int:id>/delete')
def delete_materials(id):
    delete_str = Material.query.get_or_404(id)
    try:
        db.session.delete(delete_str)
        db.session.commit()
        return redirect('/materials')
    except:
        return 'Ошибка при удалении'


@app.route('/materials/<int:id>/update', methods=['GET', 'POST'])
def materials_update(id):
    materials = Material.query.get_or_404(id)
    if request.method == 'POST':
        materials.Name = request.form['Name']
        materials.PropPhysics = request.form['NameP']
        materials.Structure = request.form['NameX']
        materials.Properties = request.form['NamePr']
        materials.Gost = request.form['NameGost']
        try:
            db.session.commit()
            return redirect('/materials')
        except:
            return 'Ошибка'

    return render_template('materials_update.html', materials=materials)


@app.route("/material/<int:id>/info")
def mat_info(id):
    material = Material.query.get_or_404(id)
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
        coatings.Name = request.form['Name1']
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
        tool.Name = request.form['Name5']
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
    materials = Material.query.all()
    tools = Toolsdate.query.all()
    coatings = Coating.query.all()

    selected_material = None
    selected_tool = None
    selected_coating = None
    coefficient = None

    if request.method == 'POST':
        selected_material = int(request.form.get('material'))
        selected_tool = int(request.form.get('tool'))
        selected_coating = int(request.form.get('coating'))

        # Извлекаем коэффициенты из базы данных на основе выбранных параметров
        coefficient = Coefficients.query.filter_by(
            material_id=selected_material,
            tool_id=selected_tool,
            coating_id=selected_coating
        ).first()



        if not coefficient:
            error = "Не найдены коэффициенты для выбранных параметров."
            return render_template(
                'expected_parameters.html',
                materials=materials,
                tools=tools,
                coatings=coatings,
                selected_material=selected_material,
                selected_tool=selected_tool,
                selected_coating=selected_coating,
                error=error
            )


    return render_template(
        'expected_parameters.html',
        materials=materials,
        tools=tools,
        coatings=coatings,
        coefficient=coefficient,
        selected_material=selected_material,
        selected_tool=selected_tool,
        selected_coating=selected_coating
    )
