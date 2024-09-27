from my_app import db,app
from my_app.models import CsvFiles, Experiments, RecommendationParameters, Materials,Tools,Coating, Adhesive
import csv
import random


app.app_context().push()


# with open('adhesive.csv_files', encoding='utf-8') as csvfile:
#     reader = csv_files.DictReader(csvfile)
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

# random.randint(160, 180)
roughness = [0.8, 1.0, 1.6]
recomeded_speed = RecommendationParameters.query.all()

for rec in recomeded_speed:
    rec.roughness = random.choice(roughness)
    db.session.commit()






