import os
from typing import Any, List, Tuple

from my_app import db,app
from my_app.models import Csv_Files, Experiments, RecomededSpeed, Materials,Toolsdate,Coating
import pandas as pd
import matplotlib.pyplot as plt
import shutil

app.app_context().push()


def claer_list(list_files):
  new_list = []
  for i in list_files:
    if ('ЛИНИИ' not in i) and ('КОЭФФИЦИЕНТЫ' not in i) and (('53' in i) or ('0' in i)):
      new_list.append(i)
  return sorted(new_list)


def corteg(list_files):
    list_corteg = []
    b = int(len(list_files)/2)
    for i in list_files[:b]:
        for j in list_files[b:]:
            if i == j.replace('Температура','Силы'):
                list_corteg.append((path+i,path+j))
    return list_corteg

def coating_1(string):
  list_coating = ['naco3+tib2', 'nacro+tib2', 'naco3', 'nacro','uncoated','altincrn3', 'alticrn3', 'tib2', 'Tib2']
  if list_coating[0] in string:
    return 'nACo3+TiB2'
  elif list_coating[1] in string:
    return 'nACRo+TiB2'
  elif list_coating[2] in string:
    return 'nACo3'
  elif list_coating[3] in string:
    return 'nACRo'
  elif (list_coating[5] in string) or (list_coating[6] in string):
    return 'AlTiNCrN3'
  elif (list_coating[7] in string) or (list_coating[8] in string):
    return 'TiB2'
  elif list_coating[4] in string:
    return 'Без покрытия'


def obrabotka_csv(data):
  df = pd.read_csv(data,
                   encoding = 'windows-1251',
                   sep = ';',
                   decimal = ',',
                   index_col = 0)
  list_parameters = []
  if 'vt18u' in df.columns[1]:
      material = 'ВТ18У'
  elif 'vt41' in df.columns[1]:
      material = 'ВТ41'
  elif 'hn58' in df.columns[1]:
      material = 'ХН58МБЮД-ИД'
  elif ('hn50' in df.columns[1]) or ('hn5-' in df.columns[1]):
      material = 'ХН50МВКТЮР'
  else:
      None
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
                          1,
                          4,
                          LengthPath,
                          Durability])
  return list_parameters



def process_csv_files(file_path):
    list_parameters = obrabotka_csv(file_path[0])
    save_path = os.path.join('../uploads', 'csv_files_new')
    os.makedirs(save_path, exist_ok=True)
    new_file_path_s = os.path.join(save_path, os.path.basename(file_path[0]))
    new_file_path_t = os.path.join(save_path, os.path.basename(file_path[1]))
    shutil.copyfile(file_path[0], new_file_path_s)
    shutil.copyfile(file_path[1], new_file_path_t)

    csv_file = Csv_Files(filename_strengh = os.path.basename(file_path[0]),  path = new_file_path_s, filename_temrature=os.path.basename(new_file_path_t))
    db.session.add(csv_file)
    db.session.commit()
    id_csv_filter = Csv_Files.query.filter_by(filename_strengh = os.path.basename(file_path[0])).first()
    id_csv = id_csv_filter.id
    path_gr_s = graphiks(file_path[0], id_csv)
    path_gr_t = graphikt(file_path[1], id_csv)
    print(path_gr_s)
    print(path_gr_t)
    id_csv_filter.path_graphik_s = path_gr_s
    id_csv_filter.path_graphik_t = path_gr_t
    db.session.commit()
    id_csv_filter = Csv_Files.query.filter_by(filename_strengh=os.path.basename(file_path[0])).first()
    list_parameters.append(id_csv)
    material = Materials.query.filter_by(Name = list_parameters[0]).first()
    tool = Toolsdate.query.filter_by(Name = list_parameters[1]).first()
    coating = Coating.query.filter_by(Name = list_parameters[2]).first()

    experiment = Experiments(Material=material.name,
                             Tool=tool.name,
                             Coating=coating.name,
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


def graphiks(path, csv_id):
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
    path_file = str(csv_id) + 'strengh.png'
    plt.savefig(save_path + '/' + path_file)
    plt.close()
    path_file = save_path.replace('\\', '/')+ '/'+ path_file
    return path_file.replace('my_app/static', '')

def graphikt(path, csv_id):
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
    path_file = str(csv_id) + 'temp.png'
    plt.savefig(save_path + '/' + path_file)
    plt.close()
    path_file = save_path.replace('\\', '/') + '/' + path_file
    return path_file.replace('my_app/static', '')


path = 'uploads/csv_files/'
onlyfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

k = claer_list(onlyfiles)
r = corteg(k)
for cor_file in r:
    process_csv_files(cor_file)





