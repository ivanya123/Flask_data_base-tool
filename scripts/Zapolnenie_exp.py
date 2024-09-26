import sqlalchemy as sa
import sqlalchemy.orm as so
from my_app import db, app
from my_app.models import Material, Coating, Toolsdate, Experiments, Csv_Files, RecomededSpeed
import os
import pandas as pd
import shutil
import matplotlib.pyplot as plt



app.app_context().push()
# onlyfiles = [f for f in os.listdir("D:/Скомпонованные данные/Финальные данные по 4 этапу/Titan/") if os.path.isfile(os.path.join('D:/Скомпонованные данные/Финальные данные по 4 этапу/Titan/', f))]
# path = 'D:/Скомпонованные данные/Финальные данные по 4 этапу/Titan/'

def corteg_path(path):
    list_path = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    files_s = []
    files_t = []
    for i in list_path:
        if ("Силы" in i) and ('КОЭФФИЦИЕНТЫ' not in i) and ('ЛИНИИ' not in i) and ('Титан.csv' not in i):
            files_s.append(f'{path}{i}')
    for i in list_path:
        if ("Температура" in i) and ('КОЭФФИЦИЕНТЫ' not in i) and ('ЛИНИИ' not in i) and ('Титан.csv' not in i):
            files_t.append(f'{path}{i}')
    corteg_files = []
    for i in range(len(files_s)):
        corteg_files.append((files_s[i], files_t[i]))

    return corteg_files

def coating_1(string):
  list_coating = ['naco3+tib2', 'nacro+tib2', 'naco3', 'nacro','uncoated']
  if list_coating[0] in string:
    return 'nACo3+TiB2'
  elif list_coating[1] in string:
    return 'nACRo+TiB2'
  elif list_coating[2] in string:
    return 'nACo3'
  elif list_coating[3] in string:
    return 'nACRo'
  elif list_coating[4] in string:
    return 'Без покрытия'

def obrabotka_csv(data):
  df = pd.read_csv(data,
                   encoding = 'windows-1251',
                   sep = ';',
                   decimal = ',',
                   index_col=0)
  list_parameters = []
  material = df.columns[1].split(',')[0].replace('v','В').replace('t','Т').replace('u','У')
  coating = coating_1(df.columns[1].split(',')[1])
  spindelSpeed = float(df.columns[1].split(',')[3].replace('.csv',''))
  TableFeed = float(df.columns[1].split(',')[2])
  LengthPath = df['L, мм'].iloc[-1]
  Durability = LengthPath/TableFeed
  list_parameters.extend([material,
                          'Фреза 6157-7005',
                          coating,
                          spindelSpeed,
                          TableFeed,
                          1.5,
                          5,
                          LengthPath,
                          Durability])
  return list_parameters


def process_csv_files(file_path):
    list_parameters = obrabotka_csv(file_path[0])
    save_path = os.path.join('../uploads', 'csv_files')
    os.makedirs(save_path, exist_ok=True)
    new_file_path_s = os.path.join(save_path, os.path.basename(file_path[0]))
    new_file_path_t = os.path.join(save_path, os.path.basename(file_path[1]))

    shutil.copyfile(file_path[0], new_file_path_s)
    shutil.copyfile(file_path[1], new_file_path_t)

    csv_file = Csv_Files(filename_strengh = os.path.basename(file_path[0]),  path = new_file_path_s, filename_temrature=new_file_path_t)
    db.session.add(csv_file)
    db.session.commit()
    id_csv_filter = Csv_Files.query.filter_by(filename_strengh = os.path.basename(file_path[0])).first()
    id_csv = id_csv_filter.id
    list_parameters.append(id_csv)
    material = Material.query.filter_by(Name = list_parameters[0]).first()
    print(material.Name)
    tool = Toolsdate.query.filter_by(Name = list_parameters[1]).first()
    coating = Coating.query.filter_by(Name = list_parameters[2]).first()

    experiment = Experiments(Material=material.Name,
                             Tool=tool.Name,
                             Coating=coating.Name,
                             SpindleSpeed=list_parameters[3],
                             FeedTable=list_parameters[4],
                             DepthCut=list_parameters[5],
                             WidthCut=list_parameters[6],
                             LengthPath=list_parameters[7],
                             Durability=list_parameters[8],
                             csv_id = id_csv_filter.id)


    db.session.add(experiment)
    db.session.commit()
    return csv_file, list_parameters

#Построение графиков и добавление их в базу данных.
def graphiks(path):
    df = pd.read_csv(path,
                       encoding='windows-1251',
                       sep=';',
                       decimal=',',
                       index_col=0
                       )
    x = df['L, мм']
    y1 = df.iloc[:, 1]  # Второй столбец
    y2 = df.iloc[:, -1]  # Последний столбец

    plt.figure(figsize=(10, 6))

    # Построить графики
    plt.plot(x, y1, label='Силы', color='blue', linestyle='-')
    plt.plot(x, y2, label='Линейная апроксимация', color='red', linestyle='-')

    # Добавить подписи к осям и заголовок
    plt.xlabel('L, мм', fontsize=12)
    plt.ylabel('F$_{z}$, Н', fontsize=12)
    plt.title('Изменение тангенциальной составляющей усилий резания во время обработки', fontsize=14)

    # Добавить легенду
    plt.legend()

    plt.grid(True)

    save_path = os.path.join('../my_app/static', 'graphik')
    os.makedirs(save_path, exist_ok=True)
    print(os.path.basename(path))
    csv_files = Csv_Files.query.filter_by(filename_strengh=os.path.basename(path)).first()
    id_files = csv_files.id
    path_file = str(id_files) + 'strengh.png'
    plt.savefig(save_path + '/' + path_file)
    plt.close()
    path_file = save_path.replace('\\', '/')+ '/'+ path_file
    csv_files.path_graphik_s = path_file.replace('my_app/static/','')
    return path_file


def graphikt(path):
    df = pd.read_csv(path,
                     encoding='windows-1251',
                     sep=';',
                     decimal=',',
                     index_col=0
                     )
    x = df['L, мм']
    y1 = df.iloc[:, 1]  # Второй столбец
    y2 = df.iloc[:, -1]  # Последний столбец

    plt.figure(figsize=(10, 6))

    # Построить графики
    plt.plot(x, y1, label='Температура', color='blue', linestyle='-')
    plt.plot(x, y2, label='Линейная апроксимация', color='red', linestyle='-')

    # Добавить подписи к осям и заголовок
    plt.xlabel('L, мм', fontsize=12)
    plt.ylabel('T, °C', fontsize=12)
    plt.title('Изменение температуры во время обработки', fontsize=14)

    # Добавить легенду
    plt.legend()
    plt.grid(True)

    save_path = os.path.join('../my_app/static', 'graphik')
    os.makedirs(save_path, exist_ok=True)
    final_path = str(save_path + '/' + os.path.basename(path))
    csv_files = Csv_Files.query.filter_by(filename_temrature=os.path.basename(final_path)).first()
    id_files = csv_files.id
    path_file = str(id_files) + 'temp.png'
    plt.savefig(save_path + '/' + path_file)
    plt.close()
    path_file = save_path.replace('\\', '/')+ '/' + path_file
    csv_files.path_graphik_t = path_file.replace('my_app/static/', '')
    return path_file




path = 'uploads/csv_files/'
list_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def corteg(list_files):
    list_corteg = []
    for i in list_files[:]:
        for j in list_files[11:]:
            if i == j.replace('Температура', 'Силы'):
                list_corteg.append((i,j))
    return list_corteg

r = corteg(list_files)
print(r)
#for i in r:
#    try:
#        path_s = graphiks(path + i[0])
#        path_t = graphikt(path + i[1])
#    except ValueError as e:
#        print(e)
#    db.session.commit()
#
#
#csv_all = Csv_Files.query.all()
#
#for i in csv_all:
#    print(f'{i.path_graphik_t}--{i.path_graphik_s}')









