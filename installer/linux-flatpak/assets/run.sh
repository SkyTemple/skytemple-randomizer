#!/bin/sh
# Simple runner script for the app, that makes sure some host configuration doesn't leak into the app.
export PYTHONNOUSERSITE=1
export RUNNING_IN_FLATPAK=1
exec skytemple_randomizer gui "$@"
