#!/bin/bash
gunicorn src.app:app -b 0.0.0.0:10160 -k meinheld.gmeinheld.MeinheldWorker -w 5