# Motion analysis (X-ray and Deep Pseudopupil)

This subrepository contains the Python based motion and deep pseudopupil
analysis suite used in the
*Binocular Mirror-Symmetric Microsaccadic Sampling of Hyperacute 3D-Vision* paper.

It consist of two parts
* **movemeter** - To analyse the X-ray microsaccade data
* **gonio-analysis** - To analyse the deep pseudopupil microsaccades and the rhabdomere orientation

In addition to *movemeter*, we also used our MATLAB based implementation for motion analysis (*xraymovement2.m*).


## Installing

Select one of the following methods.

### A) All-in-one installer (Windows only)

For Windows, all-in-one installer is provided in
[Releases](https://github.com/JuusolaLab/Hyperacute_Stereopsis_paper/releases).

1) Download and run *Gonio_Analysis_0.X.Y.exe*
2) Launch icons appear in the Windows Start menu after

Different versions can coexist side-by-side. Use Windows *Apps & features* to uninstall.
Internet connection not required.


### B) From PyPi

[The Python Package](https://pypi.org/) index is guaranteed to have at least as recent
versions as provided here, and installing is simple

```
pip install gonio-analysis
```


### C) From static wheels

To install from the static wheels provided here,
download the *wheel* folder and in it, run

```
pip install gonio_analysis-0.5.0-py3-none-any.whl movemeter-0.4.2-py3-none-any.whl python_biosystfiles-0.0.1-py3-none-any.whl roimarker-0.2.0-py3-none-any.whl tk_steroids-0.6.1-py3-none-any.whl 
```

[See for more details](wheels/README.md)


## Launching

After the Windows installer, launch icons *Movemeter* and *Gonio Analysis* appear in the Start menu.

For other installation methods

```python
python -m gonioanalysis.tkgui
```

and

```python
python -m movemeter.tkgui
```


## Contributing

Problems can be reported
[here](https://github.com/JuusolaLab/Hyperacute_Stereopsis_paper/issues)
or on the repositories of the individual projects (movemeter, gonioanalysis).
Pull requests are welcomed!

