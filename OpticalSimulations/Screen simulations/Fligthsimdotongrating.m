%Flight simulator difference between dot and no dot with gradiant backround in
%Estimation of the receptive field: half width 5.4 degree
%Fig. 6

xdim =-20:20;
ydim =-20:20;
[aceptanceangle,aceptancestrength] = Gaussianreceptivefield([0 0],5.4,1,xdim,ydim);

%How receptive field shows in virtual screen; the screen is 2.5 cm away and
%2.5*2.5 cm size with 500*500 pixels 
mappos =[-50000/2 50000/2 50000 ;50000/2 50000/2 50000; -50000/2 -50000/2 50000]/2;
mapsize =[5000 5000];

[Map] = Mapper([0 0 0],[0 0 1],aceptanceangle,aceptancestrength,mappos, mapsize);
% pcolor(Map)
BackImage=zeros(5000,5000)+0.5;
d_ang=atan(2.5/5000/2.5)/pi*180;
one_bar=round(1/d_ang);
divv = mod((1:5000)+65,2*one_bar);
BackImage(:,divv> one_bar) =1;
DotImage = BackImage;
[X,Y] = meshgrid(1:5000,1:5000);
circrad= 0.95/2/d_ang;
DotImage((X-2500).^2+(Y-2500).^2<(circrad)^2)=0.5;
Backvalue = sum(BackImage.*Map,'all')
Dotvalue = sum(DotImage.*Map,'all')