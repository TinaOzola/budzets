import csv
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

CSV_FAILS = "dati.csv"
dati = []


def ieladet_datus():
    """Ielādē datus no CSV faila, ja tas eksistē."""
    global dati
    dati = []

    if os.path.exists(CSV_FAILS):
        with open(CSV_FAILS, mode="r", newline="", encoding="utf-8") as f:
            lasitajs = csv.DictReader(f)
            for rinda in lasitajs:
                dati.append({
                    "id": int(rinda["id"]),
                    "datums": rinda["datums"],
                    "tips": rinda["tips"],
                    "summa": float(rinda["summa"]),
                    "apraksts": rinda["apraksts"]
                })


def saglabat_datus():
    """Saglabā visus datus CSV failā."""
    with open(CSV_FAILS, mode="w", newline="", encoding="utf-8") as f:
        lauki = ["id", "datums", "tips", "summa", "apraksts"]
        rakstitajs = csv.DictWriter(f, fieldnames=lauki)
        rakstitajs.writeheader()
        rakstitajs.writerows(dati)


def nakamais_id():
    """Atgriež nākamo brīvo ID."""
    if not dati:
        return 1
    return max(ieraksts["id"] for ieraksts in dati) + 1


def aprekinat_kopsavilkumu(ieraksti):
    """Aprēķina ienākumus, izdevumus un bilanci."""
    ienakumi = sum(i["summa"] for i in ieraksti if i["tips"] == "Ienākums")
    izdevumi = sum(i["summa"] for i in ieraksti if i["tips"] == "Izdevums")
    bilance = ienakumi - izdevumi
    return ienakumi, izdevumi, bilance


@app.route("/")
def index():
    filtrs = request.args.get("filtrs", "Visi")

    if filtrs == "Ienākums":
        filtetie = [i for i in dati if i["tips"] == "Ienākums"]
    elif filtrs == "Izdevums":
        filtetie = [i for i in dati if i["tips"] == "Izdevums"]
    else:
        filtetie = dati

    ienakumi, izdevumi, bilance = aprekinat_kopsavilkumu(dati)

    return render_template(
        "index.html",
        dati=filtetie,
        filtrs=filtrs,
        ienakumi=ienakumi,
        izdevumi=izdevumi,
        bilance=bilance,
        kluda=""
    )


@app.route("/pievienot", methods=["POST"])
def pievienot():
    tips = request.form.get("tips", "").strip()
    summa_teksts = request.form.get("summa", "").strip()
    apraksts = request.form.get("apraksts", "").strip()
    datums = request.form.get("datums", "").strip()

    kluda = ""

    if tips not in ["Ienākums", "Izdevums"]:
        kluda = "Nepareizs ieraksta tips."
    elif not summa_teksts:
        kluda = "Lūdzu ievadi summu."
    elif not apraksts:
        kluda = "Lūdzu ievadi aprakstu."
    elif not datums:
        kluda = "Lūdzu izvēlies datumu."
    else:
        try:
            summa = float(summa_teksts)
            if summa <= 0:
                kluda = "Summai jābūt lielākai par 0."
        except ValueError:
            kluda = "Summai jābūt skaitlim."

    if kluda:
        filtrs = request.args.get("filtrs", "Visi")
        filtetie = dati
        ienakumi, izdevumi, bilance = aprekinat_kopsavilkumu(dati)
        return render_template(
            "index.html",
            dati=filtetie,
            filtrs=filtrs,
            ienakumi=ienakumi,
            izdevumi=izdevumi,
            bilance=bilance,
            kluda=kluda
        )

    ieraksts = {
        "id": nakamais_id(),
        "datums": datums,
        "tips": tips,
        "summa": summa,
        "apraksts": apraksts
    }

    dati.append(ieraksts)
    saglabat_datus()
    return redirect(url_for("index"))


@app.route("/dzest/<int:ieraksta_id>", methods=["POST"])
def dzest(ieraksta_id):
    global dati
    dati = [i for i in dati if i["id"] != ieraksta_id]
    saglabat_datus()
    return redirect(url_for("index"))


@app.route("/bilance")
def bilance_lapa():
    ienakumi, izdevumi, bilance = aprekinat_kopsavilkumu(dati)
    return render_template(
        "bilance.html",
        ienakumi=ienakumi,
        izdevumi=izdevumi,
        bilance=bilance
    )


if __name__ == "__main__":
    ieladet_datus()
    app.run(debug=True)
