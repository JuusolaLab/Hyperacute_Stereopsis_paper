function [Map] = MultipleFields(MU,hw,amplitude,xdim,ydim,lenspos,lensnormal,mappos, mapsize)
%MU [x y] direction of the centre of receptive field
%hw halfwidth of receptive field
%amplitude max value of receptive field
%xdim x angles
%ydim y angles
%lenspos [x y z] lens center x sideway, y up, z forward
%lensnormal [x y z] lens direction
%aceptanceangle [xangle yangle] two colums for angles
%aceptancestrength strength of aceptance angle
%mappos [x y z] [top-left; top-rigt; bottom-left] position of map 
%smapsize [xsize ysize] size of the map
%Map outputs map position
numcells = size(MU,1);
Map = zeros(mapsize(2),mapsize(1),numcells);
for i = 1:numcells
    [aceptanceangle,aceptancestrength] = Gaussianreceptivefield(MU(i,:),hw(i),amplitude(i),xdim,ydim);
    Map(:,:,i) = Mapper(lenspos(i,:),lensnormal(i,:),aceptanceangle,aceptancestrength,mappos, mapsize);
end
end

