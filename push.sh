#!/usr/bin/env bash
sudo git add .
sudo git commit -m "$1"
sudo gir push origin master
