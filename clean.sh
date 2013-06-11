#!/bin/bash

kill $(ps aux | grep '[p]ython control.py start' | awk '{print $2}')
kill $(ps aux | grep '[p]ython run.py' | awk '{print $2}')
kill $(ps aux | grep '[p]ython cli.py' | awk '{print $2}')
