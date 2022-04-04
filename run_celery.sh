#!/bin/sh
celery -A Argminer worker -l info --autoscale=10,1 -B