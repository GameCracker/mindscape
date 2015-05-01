# mindscape

## Install
- Install **MuseSDK** from [MuseIO Developer] (https://sites.google.com/a/interaxon.ca/muse-developer-site/download).
- Install **liblo** from [liblo Sourceforge] (http://liblo.sourceforge.net/README.html).
- Install **mne** by:
<br>
'pip install mne --upgrade'
<br>
See [mne site] (http://martinos.org/mne/stable/getting_started.html) if you got any error. 
Or, if you don't need Alpha wave calibration, **comment out line 4, line 54 - 124** in file **'osc_server/osc_server.py'**.
- Install **numpy**, See [numpy site] (http://docs.scipy.org/doc/numpy/user/install.html) if you got any error. 
Or, if you don't need Alpha wave calibration, **comment out line 3, line 54 - 124**in file **'osc_server/osc_server.py'**.

## Run 
- Turn on Muse, pair Muse with your computer via Bluetooth.
- Pair and connect Muse by run:
<br>
'./muse.sh'
- To streaming data and calibration, sending data to Unity, run:
<br>
'./run.sh'
