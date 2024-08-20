from flask import Flask, render_template, request, redirect
from my_app import app, db
from my_app.models import Material, Toolsdate, Coating, Experiments, RecomededSpeed, Adhesive
import sqlalchemy as sa


@app.route('/')
def select_parameters():
    unique_materials = RecomededSpeed.query.with_entities(RecomededSpeed.Material).distinct().all()
    unique_tools = RecomededSpeed.query.with_entities(RecomededSpeed.Tool).distinct().all()
    unique_coatings = RecomededSpeed.query.with_entities(RecomededSpeed.Coating).distinct().all()

    return render_template('home.html', unique_materials=unique_materials, unique_tools=unique_tools,
                           unique_coatings=unique_coatings)


@app.route('/recommended_speed', methods=['POST', 'GET'])
def recomended_speeds():
    recomended_speed = None
    if request.method == 'POST':
        material = request.form['material']
        tool = request.form['tool']
        coating = request.form['coating']
        if coating != 'None':
            recomended_speed = RecomededSpeed.query.filter_by(Material=material,
                                                              Tool=tool,
                                                              Coating=coating).all()
        else:
            recomended_speed = RecomededSpeed.query.filter_by(Material=material,
                                                              Tool=tool).order_by(
                sa.desc(RecomededSpeed.Durability)).all()

    if request.method == 'GET':
        recomended_speed = RecomededSpeed.query.all()

    return render_template('recomended_speed.html', recomended_speed=recomended_speed)


@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        try:
            if 'Button_1' in request.form:
                # Обработка данных для первой формы
                name_material = request.form.get('Name')
                physic_material = request.form.get('NameP')
                construct_material = request.form.get('NameX')
                properties_material = request.form.get('NamePr')
                gost = request.form.get('NameGost')

                new_material = Material(Name=name_material, PropPhysics=physic_material, Structure=construct_material,
                                        Properties=properties_material, Gost=gost)

                db.session.add(new_material)
                db.session.commit()
                return redirect('/add')

            if 'Button_2' in request.form:
                # Обработка данных для второй формы
                name_coating = request.form.get('Name1')
                coating_material = request.form.get('Name2')
                type_application = request.form.get('Name3')
                max_thikness = request.form.get('Name4')
                nanohardness = request.form.get('NameNano')
                tempresist = request.form.get('NameResistnce')
                koefficient = request.form.get('NameKoef')
                color = request.form.get('Color')

                new_coating = Coating(Name=name_coating, MaterialCoating=coating_material,
                                      TypeApplication=type_application,
                                      MaxThickness=max_thikness, NanoHardness=nanohardness,
                                      TemratureResistance=tempresist,
                                      KoefficientFriction=koefficient, ColorCoating=color)

                db.session.add(new_coating)
                db.session.commit()
                return redirect('/add')

            if 'Button_3' in request.form:
                # Обработка данных для третьей формы
                name_tool = request.form.get('Name5')
                material_tool = request.form.get('Name6')
                number_teeth = int(request.form.get('Name8'))
                diameter = float(request.form.get('Name9'))

                new_tool = Toolsdate(Name=name_tool, MaterialTool=material_tool,
                                     NumberTeeth=number_teeth, Diameter=diameter)

                db.session.add(new_tool)
                db.session.commit()
                return redirect('/add')
        except Exception as e:
            return f'Ошибка: {e}'

    return render_template('add.html')


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
