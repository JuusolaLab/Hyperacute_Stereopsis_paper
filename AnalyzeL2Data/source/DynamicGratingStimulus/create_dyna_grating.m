x = 2;
y = 1000;
t = 14400;
thickness1 = 200;
thickness2 = 20;
speed = 3;
filename = [int2str(floor(thickness1)) 'to' int2str(floor(thickness2)) 'algrating' int2str(speed) '.mat'];
dyna_grating(x,y,t,thickness1,thickness2,speed,filename);