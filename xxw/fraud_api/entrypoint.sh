#!/bin/bash
gunicorn src.main:app -b 0.0.0.0:5000 -k meinheld.gmeinheld.MeinheldWorker