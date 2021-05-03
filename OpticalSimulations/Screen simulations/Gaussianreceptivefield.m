function [aceptanceangle,aceptancestrength] = Gaussianreceptivefield(MU,hw,amplitude,xdim,ydim)
%Makes 2d gaussian receptive field based on angles
%MU [x y] direction of the centre of receptive field
%hw halfwidth of receptive field
%amplitude max value of receptive field
%xdim x angles
%ydim y angles
%aceptanceangle [x y] angles for the aceptance surface
%aceptancestrength strength for each aceptanceangle point
[Y,X] = meshgrid(ydim,xdim);% makes gride
aceptanceangle = [Y(:) X(:)];
var = (hw/2.355)^2;
SIGMA = [var 0; 0 var]; 
aceptancestrength =mvnpdf(aceptanceangle,MU,SIGMA); % makes 2d receptive field
aceptancestrength = aceptancestrength/max(max(aceptancestrength))*amplitude; % scales peak value of receptive field
