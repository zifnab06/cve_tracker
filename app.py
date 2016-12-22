#!/usr/bin/python3

import json
import os
import sys

import utils

from flask import Flask, jsonify, render_template, request

dbfile = "sqlite.db"

db_version = 3
forceDBUpdate = False

app = Flask(__name__)

import local_config

app.config.from_object(local_config)

if not os.path.isfile(dbfile):
  print("No database found. Creating one...")
  utils.createDB()

if utils.getDBVersion() < db_version:
  print("Database version out of date, updating...")
  utils.updateDB()
  utils.getKernelTableFromGithub()

status_ids = utils.getStatusIDs()
allCVEs = utils.getCVEs()
kernels = utils.getKernelsFromDB()


@app.route("/")
@app.route("/<string:k>")
def index(k=None):
  if k:
    kernel = utils.getKernelByRepo(k)
    patches = utils.getPatchesByRepo(k)
    patched = utils.getNumberOfPatchedByRepoId(k)
    return render_template('kernel.html', kernel = kernel, patched = patched, cves = allCVEs, status_ids = status_ids, patches = patches)
  else:
    return render_template('index.html', kernels = kernels)

@app.route("/update", methods=['POST'])
def update():
  r = request.get_json()
  k = r['kernel_id'];
  c = r['cve_id'];
  s = r['status_id'];
  utils.updatePatchStatus(k, c, s)
  patched = utils.getNumberOfPatchedByRepoId(k)
  return jsonify({'error': 'success', 'patched': patched})


