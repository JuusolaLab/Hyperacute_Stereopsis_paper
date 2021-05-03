%This script is for calculating reseptive fields of neural superposition rhabdomeres in virtual screen 
%Fig S52
%Rhabdomere parameters in rest
rotangle = atan(0.39/1.4);
RotM =[cos(rotangle) -sin(rotangle); sin(rotangle) cos(rotangle)];

MU = RotM*[2.05 -1.50; 1.89 0.19; 2.39 2.28; 0.39 1.4; -1.56 1.00; -1.89 -0.722; 0 0]'*-3*0.85;
MU =MU';
hw = [5.2; 4.6; 4.8; 4.5; 4.6; 5.1; 3.12];
amplitude = [8.6; 8.3; 7.8;8.3;8.3;8.8;7.15];
%parameters of the lens array
lenspos =[13.8432199057168,-7.97463357383556,-0.697356732085874; 13.8432199057168,7.97463357383556,-0.697356732085874 ; 13.8432199057168,23.8632089447944,-2.08742695662199; 0,15.9796999032600,-0.697688765171388; -13.8432199057168,7.97463357383556,-0.697356732085874; -13.8432199057168,-7.97463357383556,-0.697356732085874; 0 0 0];
lensnorm = [ 0.0755030520101178,-0.0434948789073477,0.996196509051298; 0.0755030520101178,0.0434948789073477,0.996196509051298; 0.0755030520101178,0.130153614430632,0.988614852097519; 0,0.0871557427476582,0.996194698091746; -0.0755030520101178,0.0434948789073477,0.996196509051298; -0.0755030520101178,-0.0434948789073477,0.996196509051298; 0 0 1];
xdim =-20:20;
ydim =-20:20;
%How receptive field shows in virtual screen; the screen is 5 cm away and
%2.5*2.5 cm size with 500*500 pixels
mappos =[-50000/2 50000/2 50000 ;50000/2 50000/2 50000; -50000/2 -50000/2 50000];
mapsize =[500 500];
%Calculate receptive fields at the virtual screen
[Map] = MultipleFields(MU,hw,amplitude,xdim,ydim,lenspos,lensnorm,mappos, mapsize);

sMap = sum(Map,3);
%imagesc(sMap);
figure;
hold on
contour(squeeze(Map(:,:,1)),1,'r')
contour(squeeze(Map(:,:,2)),1,'g')
contour(squeeze(Map(:,:,3)),1,'b')
contour(squeeze(Map(:,:,4)),1,'y')
contour(squeeze(Map(:,:,5)),1,'m')
contour(squeeze(Map(:,:,6)),1,'c')
contour(squeeze(Map(:,:,7)),1,'k')
hold off
