from flask_wtf import FlaskForm
from wtforms import SubmitField,IntegerField,validators
from wtforms.validators import DataRequired


class ElectionForm (FlaskForm):
    nbInscrits=IntegerField("Nombre d'inscrits",validators=[DataRequired("Entrer le nombre de votants ")])
    nbCandidats=IntegerField("Nombre de candidats",validators=[DataRequired("Entrer le nombre de candidats")])
    nbBureaux=IntegerField("Nombre de Bureaux",validators=[DataRequired("Entrer le nombre de bureaux")])
    nbScrutateurs=IntegerField("Nombre de scrutateurs",validators=[DataRequired("Entrer le nombre de scrutateurs")])
    submit=SubmitField("Lancer")