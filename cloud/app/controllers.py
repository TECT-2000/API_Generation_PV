from random import randint
import copy
from pdf2image import convert_from_path
import json
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# Creation of all set of partion
def createPartition(scrut_list):
    allParts = list()
    i = 1
    while i <= len(scrut_list):
        parts = createPart(scrut_list, i)
        allParts.extend(parts)
        i += 1
    return allParts


# creation of all set part of a partition with a specific number of element
def createPart(E, n):
    L = list()
    scrut_list = list()
    scrut_list += E

    if n == 1:
        for k, scrutateur in enumerate(scrut_list):
            temp = list()
            temp.append(scrutateur)
            L.append(temp)
        return L
    else:

        # We pop the first element of the list
        first = scrut_list[0]
        del scrut_list[0]

        L_temp = createPart(scrut_list, n - 1)

        for k, elt in enumerate(L_temp):
            L_temp[k].insert(0, first)
            L.append(L_temp[k])

        if len(E) >= n:
            L_temp = createPart(scrut_list, n)
            for k, elt in enumerate(L_temp):
                L.extend(L_temp)
        return L


# generation of Fraud List
def generateFraudForVoteOffice(scrut_list):
    listFraud = list()
    if len(scrut_list) == 0:
        return listFraud
    else:

        scrut_temp = list()
        scrut_temp += scrut_list

        # We create partition with list of scrutators
        partList = createPartition(scrut_temp)

        # We get the index of fraud part
        indexofFraudElt = randint(0, len(partList) - 1)

        # we add the corresponding elt into listFraud list
        fraudElt = partList[indexofFraudElt]

        # We choose to add it or not to list of fraud part
        if randint(0, 1) == 1:
            listFraud.append(fraudElt)

        # remove all scrutators of fraudElt in scrut_list
        if len(fraudElt) > 0:
            for elt in fraudElt:
                scrut_temp.remove(elt)

        # We generate the rest of fraud element and add them to our listFraud list
        L = generateFraudForVoteOffice(scrut_temp)
        if (len(L) > 0):
            listFraud.extend(L)

        return listFraud

    # distribution of number of voters


def votersDistributions(nbInscrits, nbBureaux):
    voters = list()
    nbIns = nbInscrits
    nbBRestant = nbBureaux - 1
    for i in range(nbBureaux):
        if (i < nbBureaux - 1):
            voters.append(randint(1, nbIns - nbBRestant))
            nbIns -= voters[i]
            nbBRestant -= 1
        else:
            voters.append(nbIns)
    return voters


# Create all scrutators
def creationScrutators(nbScrutateurs):
    scrut_list = list()
    for i in range(nbScrutateurs):
        scrut_list.append("Scrutateur " + str(i + 1))
    return scrut_list


def randomSequence(NbElt, MaxVal):
    temp = list()
    for i in range(NbElt):
        val = randint(0, MaxVal)
        while val in temp:
            val = randint(0, MaxVal)
        temp.append(val)
    return temp


# this method distribute all scrutators to every candidate
def scrutatorsDistribution(nbCandidats, nbScrutateurs, nbBureaux):
    dist = list()
    nbS = nbScrutateurs
    if nbScrutateurs == nbCandidats * nbBureaux:
        for i in range(nbCandidats):
            dist.append(range(nbBureaux + 1))
    else:
        distNbreScrutateur = list()
        for i in range(nbCandidats):
            distNbreScrutateur.append(0)

        for j in range(nbScrutateurs):
            flag = False
            while not flag:
                pos = randint(0, nbCandidats - 1)
                if distNbreScrutateur[pos] < 3:
                    distNbreScrutateur[pos] += 1
                    flag = True

        for k, val in enumerate(distNbreScrutateur):
            BureauxRepresentes = list()
            if val > 0:
                BureauxRepresentes = randomSequence(val, nbBureaux - 1)
            dist.append(BureauxRepresentes)
    return dist


# this method is used to distribute .... per candidate
def nbVoixParCandidats(nbVotants, nbCandidats):
    nbVoix = list()
    nbV = nbVotants
    for i in range(nbCandidats):
        if nbV > 1:
            nb = randint(1, nbV)
            nbVoix.append(nb)
            nbV -= nb
        else:
            nbVoix.append(1)
    return nbVoix


# this method is used to produce a true PV for a specific Bureau
def generateTruePV(indBureau, votantsParBureaux, scrutateursParCandidat, listScrutateurs, nbCandidats, signataire):
    PV = dict()
    PV["nomBureau"] = "Bureau " + str(indBureau + 1)
    PV["nbVotants"] = votantsParBureaux[indBureau]
    PV["Signataire"] = signataire

    candidates = list()
    nbBulletinsNull = (votantsParBureaux[indBureau] * 5) // 100
    nbVotants = votantsParBureaux[indBureau] - nbBulletinsNull
    nbVoixParCandidat = nbVoixParCandidats(nbVotants, nbCandidats)
    for i in range(nbCandidats):
        candidat = dict()
        candidat["candidat"] = "Candidat " + str(i + 1)
        candidat["nbVoix"] = nbVoixParCandidat[i]
        if indBureau in scrutateursParCandidat[i]:
            candidat["scrutateur"] = listScrutateurs[0]
            del listScrutateurs[0]
        else:
            candidat["scrutateur"] = ""
        candidates.append(candidat)
    candidat = dict()
    candidat["candidat"] = "Bulletin null "
    candidat["nbVoix"] = nbBulletinsNull
    candidates.append(candidat)
    PV["candidats"] = candidates

    return PV


def isHistoFraudContainElt(HistoFraude, fraudElt):
    result = False
    gagnant = -1
    for histoFraud in HistoFraude:
        listH = histoFraud["fraud"]
        if len(listH) == len(fraudElt):
            temp = [elt for elt in listH if elt in fraudElt]
            if len(temp) == len(fraudElt):
                result = True
                gagnant = histoFraud["gagnant"]
                break
    return result, gagnant


def writePVsToOutputFile(allPVs):
    # write datas into Bureau Folder
    for i in range(len(allPVs)):
        dir_path = os.getcwd()
        bureau_path = dir_path + "/Bureaux/Bureau_{}/JSON/".format(i + 1)

        # Write allPVs
        for j, pvList in enumerate(allPVs[i]):
            if j == len(allPVs[i]) - 1 or (len(allPVs[i][j]["candidats"][j]["scrutateur"]) > 0):
                candidat_path = dir_path + "/Candidats/Candidat_{}/JSON/".format(j + 1)
                bureau_filename = bureau_path
                candidat_filename = candidat_path
                if j < len(allPVs[i]) - 1:
                    bureau_filename += "PV_{}_{}.json".format(i + 1, j + 1)
                    candidat_filename += "candidat_{}_{}.json".format(j + 1, i + 1)
                    writeIntoJsonFile(candidat_path, candidat_filename, allPVs[i][j])
                else:
                    bureau_filename += "PV_ELECAM.json"
                    candidat_path = dir_path + "/Candidats/ELECAM/JSON/"
                    candidat_filename = candidat_path + "Elecam_{}.json".format(i + 1)
                    writeIntoJsonFile(candidat_path, candidat_filename, allPVs[i][j])
                writeIntoJsonFile(bureau_path, bureau_filename, allPVs[i][j])


def generatePDFFile(allPVs):
    for i in range(len(allPVs)):
        dir_path = os.getcwd()
        bureau_path = dir_path + "/Bureaux/Bureau_{}/PDF/".format(i + 1)

        # Write allPVs
        for j, pvList in enumerate(allPVs[i]):
            if j == len(allPVs[i]) - 1 or (len(allPVs[i][j]["candidats"][j]["scrutateur"]) > 0):
                candidat_path = dir_path + "/Candidats/Candidat_{}/PDF/".format(j + 1)
                bureau_filename = bureau_path
                candidat_filename = candidat_path
                if j < len(allPVs[i]) - 1:
                    bureau_filename += "PV_{}_{}.pdf".format(i + 1, j + 1)
                    candidat_filename += "candidat_{}_{}.pdf".format(j + 1, i + 1)
                    writeIntoPDFFile(candidat_path, candidat_filename, allPVs[i][j])
                else:
                    bureau_filename += "PV_ELECAM.pdf"
                    candidat_path = dir_path + "/Candidats/ELECAM/PDF/"
                    candidat_filename = candidat_path + "Elecam_{}.pdf".format(i + 1)
                    writeIntoPDFFile(candidat_path, candidat_filename, allPVs[i][j])
                writeIntoPDFFile(bureau_path, bureau_filename, allPVs[i][j])


def writeIntoJsonFile(dir_path, filename, data):
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError:
            print("Creation of the directory %s failed" % dir_path)
        else:
            print("Successfully created the directory %s" % dir_path)
    else:
        print("Directory already exist")

    dir_path += filename
    jsonDump = json.dumps(data)
    f = open(filename, "w")
    f.write(jsonDump)
    f.close()


def writeIntoPDFFile(dir_path, filename, data):
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError:
            print("Creation of the directory %s failed" % dir_path)
        else:
            print("Successfully created the directory %s" % dir_path)
    else:
        print("Directory already exist")

    # print(data)
    dir_path += filename
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30,
                            bottomMargin=18)
    doc.pagesize = landscape(A4)
    # container for the 'Flowable' objects
    elements = []

    dataEntete = [["bureau", data['nomBureau']],
                  ["Nombre d'électeurs", str(data["nbVotants"])]]
    dataVoix = [["Noms des candidats", "Nombre de voies"]]
    dataSignature = [["Scrutateurs", "Signature"]]

    for i in range(len(data['candidats'])):
        row = [str(data['candidats'][i]['candidat']), str(data['candidats'][i]['nbVoix'])]
        dataVoix.append(row)
        if i != len(data["candidats"]) - 1:
            row = [str(data['candidats'][i]['scrutateur']), str(data['candidats'][i]['scrutateur'])]
            dataSignature.append(row)

    styleEntete = TableStyle([('ALIGN', (1, 1), (-2, -2), 'RIGHT'),
                              ('TEXTCOLOR', (1, 1), (-2, -2), colors.red),
                              ('VALIGN', (0, 0), (0, -1), 'TOP'),
                              ('TEXTCOLOR', (0, 0), (0, -1), colors.blue),
                              ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
                              ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),
                              ('TEXTCOLOR', (0, -1), (-1, -1), colors.green),
                              ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                              ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                              ])

    # Configure style and word wrap
    s = getSampleStyleSheet()
    s = s["BodyText"]
    s.leading = 15
    s.wordWrap = 'CJK'

    data2Entete = [[Paragraph(cell, s) for cell in row] for row in dataEntete]
    data2Voix = [[Paragraph(cell, s) for cell in row] for row in dataVoix]
    data2Signature = [[Paragraph(cell, s) for cell in row] for row in dataSignature]

    tableauEntete = Table(data2Entete)
    tableauEntete.setStyle(styleEntete)
    elements.append(tableauEntete)

    elements.append(Spacer(80, 100))

    tableauVoix = Table(data2Voix)
    tableauVoix.setStyle(styleEntete)
    elements.append(tableauVoix)

    elements.append(Spacer(80, 100))

    tableauSignature = Table(data2Signature)
    tableauSignature.setStyle(styleEntete)
    elements.append(tableauSignature)

    doc.build(elements)

    images = convert_from_path(filename, 500)
    for image in images:
        image.save(filename.replace('.pdf', ".png"), "png")


def generationPV(nbInscrits, nbBureaux, nbScrutateurs, nbCandidats):
    votantsParBureaux = votersDistributions(nbInscrits, nbBureaux)
    listScrutateurs = creationScrutators(nbScrutateurs)
    scrutateursParCandidat = scrutatorsDistribution(nbCandidats, nbScrutateurs, nbBureaux)

    truePVs = list()
    allPVs = list()
    HistoFraude = list()

    for indBureau in range(nbBureaux):

        TruePV = generateTruePV(indBureau, votantsParBureaux, scrutateursParCandidat, listScrutateurs, nbCandidats,
                                indBureau)
        truePVs.append(TruePV)

        # The last candidate is Elecam
        candidatesPVs = list()
        for j in range(nbCandidats + 1):
            candPV = copy.deepcopy(TruePV)
            candidatesPVs.append(candPV)

        # if there's a fraud
        if randint(0, 1) == 1:

            # we get all candidates represent in this Bureau
            scrutPresent = list()
            for cand in range(nbCandidats):
                if indBureau in scrutateursParCandidat[cand]:
                    scrutPresent.append(cand)
            listFraud = generateFraudForVoteOffice(scrutPresent)

            # print("-------------- Bureau "+str(i)+" --------------------")
            # print(listFraud)
            # print("-----------------------------------------------------")
            for elt in listFraud:
                if len(elt) == 1:
                    fakePV = candidatesPVs[elt[0]]
                    nb = randint(1, 100)
                    fakePV["candidats"][elt[0]]["nbVoix"] += nb
                elif len(elt) >= 2:
                    result, gagnant = isHistoFraudContainElt(HistoFraude, elt)
                    commonPV = copy.deepcopy(TruePV)
                    if not result:
                        gagnant = randint(0, len(elt) - 1)
                        gagnant = elt[gagnant]
                        histoElt = dict()
                        histoElt["fraud"] = elt
                        histoElt["gagnant"] = gagnant
                        HistoFraude.append(histoElt)

                    for candidat in elt:
                        if candidat != gagnant:
                            # print("ggggg : "+str(gagnant)+" and candidat = "+str(candidat))
                            nb = commonPV["candidats"][candidat]["nbVoix"] // 2
                            commonPV["candidats"][candidat]["nbVoix"] -= nb
                            commonPV["candidats"][gagnant]["nbVoix"] += nb

                    # distribution of commonPV to all candidates
                    # print(listFraud)
                    # print("gagnant "+str(gagnant))
                    # print("True PV Candidates")
                    # print(TruePV)
                    # print("CommonPV ")
                    # print(commonPV)
                    # print("Candidates PV")
                    for candidat in elt:
                        fakePV = candidatesPVs[candidat]
                        candidatesPVs[candidat] = commonPV

        # if Elecam's frauded
        if randint(0, 1) == 1:
            fakePV = candidatesPVs[len(candidatesPVs) - 1]
            gagnant = randint(0, nbCandidats - 1)
            for candidat in range(nbCandidats):
                if candidat != gagnant:
                    nb = (fakePV["candidats"][candidat]["nbVoix"] * 3) // 100
                    fakePV["candidats"][candidat]["nbVoix"] -= nb
                    fakePV["candidats"][gagnant]["nbVoix"] += nb
        allPVs.append(candidatesPVs)

    print(allPVs)
    # write result into output file (csv and json)
    writePVsToOutputFile(allPVs)
    generatePDFFile(allPVs)
