from my_app import db,app
from my_app.models import Csv_Files, Experiments, RecomededSpeed, Material,Toolsdate,Coating, Adhesive
import csv


app.app_context().push()


# with open('adhesive.csv', encoding='utf-8') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         material = row['material'].strip()
#         coating = row['coating'].strip()
#         temperature = row['temperature']
#         bond_strength_adhesive = row['tpp']
#         normal_shear_strength = row['prn']
#
#         adhesive = Adhesive(material=material,
#                             coating=coating,
#                             temperature=temperature,
#                             bond_strength_adhesive=bond_strength_adhesive,
#                             normal_shear_strength=normal_shear_strength)
#
#         db.session.add(adhesive)
#         db.session.commit()
#
# all_adhesive = Adhesive.query.all()
# for adhesive in all_adhesive:
#     db.session.delete(adhesive)

list_data = [(101.05, 1063),
             (118.94, 991),
             (129.47, 924),
             (137.89, 907),
             (141.05, 881)]

adhesive_vt41 = Adhesive.query.filter_by(material='ВТ41').filter_by(coating='nACRo+TiB2')
k=0
for adhesive in adhesive_vt41:
    adhesive.bond_strength_adhesive = list_data[k][0]
    adhesive.normal_shear_strength = list_data[k][1]
    db.session.commit()
    k += 1





