#
# This script fetches the latest Pseudopupil analysis suite
# from PyPi and Github and creates few README.md pages
#

datenow=$(date)


# ## Uncomment to make a separate folder with zips 
## 
# ## SOURCE CODE ARHIVES/ ZIPS
# mkdir source_zips
# cd source_zips
# 
# pkg=movemeter
# 
# wget https://github.com/jkemppainen/$pkg/archive/master.zip
# mv master.zip $pkg.zip
# 
# pkg=tk_steroids
# 
# wget https://github.com/jkemppainen/$pkg/archive/master.zip
# mv master.zip $pkg.zip
# 
# pkg=pupil-analysis
# 
# wget https://github.com/jkemppainen/$pkg/archive/master.zip
# mv master.zip $pkg.zip
# 
# pkg=roimarker
# 
# wget https://github.com/jkemppainen/$pkg/archive/master.zip
# mv master.zip $pkg.zip
# 
# pkg=python-biosystfiles
# 
# wget https://github.com/jkemppainen/$pkg/archive/master.zip
# mv master.zip $pkg.zip
# 
# cat > README.md <<- EOM
# # Source code archives
# 
# The zip files here contain the project full sources fetched from Github on $datenow.
# 
# * $(zipgrep "__version__ = " pupil-analysis.zip)
# * $(zipgrep "__version__ = " movemeter.zip)
# * $(zipgrep "__version__ = " tk_steroids.zip)
# * $(zipgrep "__version__ = " roimarker.zip)
# 
# EOM
# 
# ## FILES NEEDED FOR PIP INSTALL

mkdir wheels
cd wheels
# 
pip download --no-deps pupil-analysis
pip download --no-deps movemeter
pip download --no-deps tk-steroids
pip download --no-deps roimarker
pip download --no-deps python-biosystfiles

# echo "" >> README.md

cat > README.md <<- EOM
# Python wheel packages

For all platforms. Fetched from PyPi on $datenow.

## Installation

$(printf '```')
$(printf "pip install $(ls -1  *.whl | tr '\n' ' ' )")
$(printf '```')

### Offline

If installing on a system without internet connection,
you can download 3rd party dependencies on an identitical system
(same OS, same Python version) by

$(printf '```')
$(printf "pip download $(ls -1  *.whl | tr '\n' ' ' )")
$(printf '```')


EOM

cd ..

wheels="$(ls -1  wheels/*.whl | tr '\n' ' ')"
wheels=${wheels//"wheels/"/}

cat > README.md <<- EOM
# Motion analysis (X-ray and Deep Pseudopupil)

This subrepository contains the Python based motion and deep pseudopupil
analysis suite used in the
*Binocular Mirror-Symmetric Microsaccadic Sampling of Hyperacute 3D-Vision* paper.

It consist of two parts
* **movemeter** - To analyse the X-ray microsaccade data
* **pupil-analysis** - To analyse the deep pseudopupil microsaccades and the rhabdomere orientation

In addition to *movemeter*, we also used our MATLAB based implementation for motion analysis (*xraymovement2.m*).


## Installing

Select one of the following methods.

### A) All-in-one installer (Windows only)

For Windows, all-in-one installer is provided in
[Releases](https://github.com/JuusolaLab/Hyperacute_Stereopsis_paper/releases).

1) Download and run *Pupil_Analysis_0.X.Y.exe*
2) Launch icons appear in the Windows Start menu after

Different versions can coexist side-by-side. Use Windows *Apps & features* to uninstall.
Internet connection not required.


### B) From PyPi

[The Python Package](https://pypi.org/) index is guaranteed to have at least as recent
versions as provided here, and installing is simple

$(printf '```')
pip install pupil-analysis
$(printf '```')


### C) From static wheels

To install from the static wheels provided here,
download the *wheel* folder and in it, run

$(printf '```')
$(printf "pip install $wheels")
$(printf '```')

[See for more details](wheels/README.md)


## Launching

After the Windows installer, launch icons *Movemeter* and *Pupil Analysis* appear in the Start menu.

For other installation methods

$(printf '```python')
python -m pupilanalysis.tkgui
$(printf '```')

and

$(printf '```python')
python -m movemeter.tkgui
$(printf '```')


## Contributing

Problems can be reported
[here](https://github.com/JuusolaLab/Hyperacute_Stereopsis_paper/issues)
or on the repositories of the individual projects (movemeter, pupilanalysis).
Pull requests are welcomed!

EOM


