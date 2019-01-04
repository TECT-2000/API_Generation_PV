from os import uname_result

from app import app
from app.forms import ElectionForm
from flask import render_template,request,flash,jsonify,redirect,url_for
from .controllers import generationPV
import os
import json,urllib.request
import requests

@app.route("/",methods=['GET'])
def index():
    form=ElectionForm()
    return render_template('accueil.html',form=form)


@app.route('/generation/',methods=['POST'])
def generation():

    nbInscrits=int(request.form['nbInscrits'])
    nbCandidats=int(request.form['nbCandidats'])
    nbBureaux=int(request.form['nbBureaux'])
    nbScrutateurs=int(request.form['nbScrutateurs'])
    if(nbInscrits<nbBureaux):
        flash("erreur : Nombre d'inscrits inférieur au nombre de bureaux")
        #return redirect("/")
        response=jsonify({"code" :"0","error": "Nombre d'inscrits inférieur au nombre de bureaux"})
        response.status_code=404
        return response
    generationPV(nbInscrits, nbBureaux, nbScrutateurs, nbCandidats)
    response=jsonify({"code":"success",'url':os.getcwd()})
    response.status_code=200
    #return response
    return redirect(url_for('envoi'))
    #return render_template('fin.html')

@app.route("/envoi_blockchain/")
def envoi():
    url=os.getcwd()
    r=urllib.request.urlopen("http://localhost:6000/stockage?url="+url).read()
    return r


