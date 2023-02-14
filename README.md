# sap-spear-tascar

<img src="/assets/SPEAR_logo.png" alt="SPEAR logo" width="50%"/>

Minimum working example of Tascar simulation used in the [SPEAR challenge](https://imperialcollegelondon.github.io/spear-challenge/). 
It is recommended to refer to the [Tascar manual](http://www.tascar.org/manual.pdf) for more information.
To download the SPEAR dataset and ATF needed to recreate the simulations, go [here](https://imperialcollegelondon.github.io/spear-challenge/downloads/).

This directory includes:
- *scenes-blocks*: directory including all the building blocks used to create the Tascar scenes file.
- *fct_directoryCreation.py*: create the SPEAR directory. Needs as input the path to the EasyComDataset to know the number of minutes per session.
- *fct_PathFinder.py*: function to navigate more easily through the create spear directory.
- *fct_tascarScene.py*: include the function creating the needed tascar scene file, and the function running the tascar processing to obtain the HOA file. Includes an option to add the convolution transforming the HOA file into the desired array.


## Tascar installation

To install Tascar on Linux follow the instruction on the [website](http://www.tascar.org/install.html).

To install Tascar on Mac there are also guideline on the main [website](http://www.tascar.org/install.html) but additional instructions and demos can be found in [this repo](https://github.com/alastairhmoore/tascar-on-mac-demos).

## Simulation Flowchart

![simulation flowchart](assets/TASCAR_block_b.png?raw=true)

As described on the [SPEAR challenge website](https://imperialcollegelondon.github.io/spear-challenge/simulations/) and in the above flowchart, we here create a Tascar scene outputing HOA audio files. Using the ATFs and the [*fmatconvol* function](https://github.com/alastairhmoore/jmatconvol), the HOA files are converted into the desired mic array.


### Ressources

- [TASCAR](http://www.tascar.org/)
- [EasyCom](https://arxiv.org/abs/2107.04174)
- [SPEAR](https://imperialcollegelondon.github.io/spear-challenge/)
- [SPEAR description article, IWAENC](https://imperialcollegelondon.github.io/spear-challenge/blog/2022/spear-article/)