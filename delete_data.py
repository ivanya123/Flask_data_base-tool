import os
from typing import Any

from my_app import db,app
from my_app.models import Csv_Files, Experiments, RecommendedSpeed, Material,Toolsdate,Coating
import pandas as pd
import matplotlib.pyplot as plt
import shutil
app.app_context().push()


exp = Experiments.query.all()
csv = Csv_Files.query.all()
print(csv)




#for i in range(1,len(exp)):
#    exper = Experiments.query.get_or_404(i)
#    csv_data = Csv_Files.query.get_or_404(i)
#    db.session.delete(exper)
#    db.session.delete(csv_data)
#    db.session.commit()



