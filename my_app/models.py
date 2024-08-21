import sqlalchemy as sa
import sqlalchemy.orm as so
from my_app import db
import math


class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(sa.String(64), index=True, unique=True)
    PropPhysics = db.Column(sa.String(64))
    Structure = db.Column(sa.Text)
    Properties = db.Column(sa.String(120))
    Gost = db.Column(sa.String(64))

    experiment = so.relationship('Experiments', back_populates='mat_info')
    recomend = so.relationship('RecomededSpeed', back_populates='mat_info')
    adhesive = so.relationship('Adhesive', back_populates='mat_info')

    def __repr__(self):
        return '<Material {}>'.format(self.id)


class ToolGeometry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('toolsdate.id'))
    FrontAngle = db.Column(sa.Float)
    SpiralAngle = db.Column(sa.Float)
    FRearAngle = db.Column(sa.Float)
    SRearAngle = db.Column(sa.Float)
    MainRearAngle = db.Column(sa.Float)
    AngularPitch = db.Column(sa.String(32))

    tool = db.relationship('Toolsdate', back_populates='geometry')


class Toolsdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(sa.String(64), index=True, unique=True)
    MaterialTool = db.Column(sa.String(64))
    NumberTeeth = db.Column(db.Integer, nullable=False)
    Diameter = db.Column(db.Float, nullable=False)
    geometry = db.relationship('ToolGeometry', back_populates='tool')

    experiment = so.relationship('Experiments', back_populates='tools_info')
    recomend = so.relationship('RecomededSpeed', back_populates='tools_info')


class Coating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(sa.String(64), index=True, unique=True)
    MaterialCoating = db.Column(sa.String(64))
    ColorCoating = db.Column(sa.String(32))
    TypeApplication = db.Column(sa.String(64))
    MaxThickness = db.Column(sa.String(32))
    NanoHardness = db.Column(sa.String(32))
    TemratureResistance = db.Column(sa.Float)
    KoefficientFriction = db.Column(sa.Float)

    experiment = so.relationship('Experiments', back_populates='coat_info')
    recomend = so.relationship('RecomededSpeed', back_populates='coat_info')
    adhesive = so.relationship('Adhesive', back_populates='coat_info')

    def __repr__(self):
        return '<Coating {}>'.format(self.id)


class Csv_Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename_strengh = db.Column(sa.String(128), nullable=False, unique=True)
    filename_temrature = db.Column(sa.String(128), nullable=False, unique=True)
    path = db.Column(sa.String(256), nullable=False, unique=True)
    path_graphik_s = db.Column(sa.String(256))
    path_graphik_t = db.Column(sa.String(256))

    experiment = so.relationship('Experiments', back_populates='csv_f')


class Experiments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Material = db.Column(sa.String(64), db.ForeignKey(Material.Name))
    Tool = db.Column(sa.String(64), db.ForeignKey(Toolsdate.Name))
    Coating = db.Column(sa.String(64), db.ForeignKey(Coating.Name))
    SpindleSpeed = db.Column(db.Float)
    FeedTable = db.Column(db.Float)
    DepthCut = db.Column(db.Float)
    WidthCut = db.Column(db.Float)
    LengthPath = db.Column(db.Float)
    Durability = db.Column(db.Float)
    csv_id = db.Column(db.Integer, db.ForeignKey(Csv_Files.id))

    tools_info = so.relationship('Toolsdate', foreign_keys=[Tool], back_populates='experiment')
    coat_info = so.relationship('Coating', foreign_keys=[Coating], back_populates='experiment')
    mat_info = so.relationship('Material', foreign_keys=[Material], back_populates='experiment')
    csv_f = so.relationship('Csv_Files', foreign_keys=[csv_id], back_populates='experiment')

    @property
    def cutter_speed(self):
        if self.tools_info:
            d = self.tools_info.Diameter
            return math.pi * d * self.SpindleSpeed / 1000
        else:
            return None

    @property
    def feed_of_teeth(self):
        if self.tools_info:
            z = self.tools_info.NumberTeeth
            return self.FeedTable / (z * self.SpindleSpeed)

    def __repr__(self):
        return '<Experiments {}>'.format(self.id)


class RecomededSpeed(db.Model):
    Material = db.Column(sa.String(64), db.ForeignKey(Material.Name), nullable=False)
    Tool = db.Column(sa.String(64), db.ForeignKey(Toolsdate.Name), nullable=False)
    Coating = db.Column(sa.String(64), db.ForeignKey(Coating.Name), nullable=False)
    SpindleSpeed = db.Column(db.Integer)
    FeedTable = db.Column(db.Float)
    Roughness = db.Column(db.Float)
    Hardening = db.Column(db.Float)
    Durability = db.Column(db.Float)
    Microhardness = db.Column(db.Float)

    tools_info = so.relationship('Toolsdate', foreign_keys=[Tool], back_populates='recomend')
    coat_info = so.relationship('Coating', foreign_keys=[Coating], back_populates='recomend')
    mat_info = so.relationship('Material', foreign_keys=[Material], back_populates='recomend')

    __table_args__ = (
        sa.PrimaryKeyConstraint('Material', 'Tool', 'Coating', name='recomended_speed_pk'),
    )

    @property
    def cutter_speed(self):
        if self.tools_info:
            d = self.tools_info.Diameter
            return math.pi * d * self.SpindleSpeed / 1000
        else:
            return None

    @property
    def feed_of_teeth(self):
        if self.tools_info:
            z = self.tools_info.NumberTeeth
            return self.FeedTable / (z * self.SpindleSpeed)


class Adhesive(db.Model):
    material = db.Column(sa.String(64), db.ForeignKey(Material.Name), nullable=False)
    coating = db.Column(sa.String(64), db.ForeignKey(Coating.Name), nullable=False)
    temperature = db.Column(sa.Integer, nullable=False)
    bond_strength_adhesive = db.Column(sa.Float, nullable=False)
    normal_shear_strength = db.Column(sa.Float, nullable=False)

    mat_info = so.relationship('Material', foreign_keys=[material], back_populates='adhesive')
    coat_info = so.relationship('Coating', foreign_keys=[coating], back_populates='adhesive')
    @property
    def koefficient_shear(self):
        return self.bond_strength_adhesive / self.normal_shear_strength

    __table_args__ = (
        sa.PrimaryKeyConstraint('material', 'coating', 'temperature', name='adhesive_pk'),
    )
