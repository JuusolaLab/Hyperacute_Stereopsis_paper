function [Map] = Mapper(lenspos,lensnormal,aceptanceangle,aceptancestrength,mappos, mapsize)
%Maps the receptive field to virtual surface
%lenspos [x y z] lens center x sideway, y up, z forward
%lensnormal [x y z] lens direction
%aceptanceangle [xangle yangle] two colums for angles
%aceptancestrength strength of aceptance angle
%mappos [x y z] [top-left; top-rigt; bottom-left] position of map 
%smapsize [xsize ysize] size of the map
%Map outputs map position
xside =mappos(2,:)-mappos(1,:);
xlength =norm(xside);
xside =xside/norm(xside);

yside =mappos(3,:)-mappos(1,:);
ylength =norm(yside);
yside =yside/norm(yside);

mapnormal =cross(xside,yside);%Calculate normal of the Map

%double check that vectors are unit vectors;
mapnormal =mapnormal/norm(mapnormal);
lensnormal =lensnormal/norm(lensnormal);
tanacept = tan(aceptanceangle/180*pi);
numpoints =length(aceptancestrength);

%calculate normal directions between lens and 
raynormalb = cross([0 1 0], lensnormal);
raynormalv = cross(lensnormal, raynormalb);

%Calculate rays for raytracing
raydirection =lensnormal + raynormalb.*tanacept(:,1)+raynormalv.*tanacept(:,2);
raylength =vecnorm(raydirection',2);
raydirection= raydirection./[raylength' raylength' raylength'];

%Calculate intersection point between rays and map
d=dot(mappos(1,:)-lenspos,mapnormal)./dot(raydirection,repmat(mapnormal,numpoints,1),2);
intersectionpoints = lenspos +raydirection.*d;

%Transform intersection points to map points
xdir = dot(repmat(xside,numpoints,1), intersectionpoints-mappos(1,:),2)/xlength*mapsize(1);
ydir = dot(repmat(yside,numpoints,1), intersectionpoints-mappos(1,:),2)/ylength*mapsize(2);

%Search nearest intersection points for each intersection point
[Indnp] = knnsearch(intersectionpoints,intersectionpoints,'K',5);

%Calculate the area three ways using points
cdist1=cross(intersectionpoints(Indnp(:,2),:)-intersectionpoints(Indnp(:,3),:),intersectionpoints(Indnp(:,4),:)-intersectionpoints(Indnp(:,5),:));
cdist2=cross(intersectionpoints(Indnp(:,2),:)-intersectionpoints(Indnp(:,4),:),intersectionpoints(Indnp(:,3),:)-intersectionpoints(Indnp(:,5),:));
cdist3=cross(intersectionpoints(Indnp(:,2),:)-intersectionpoints(Indnp(:,5),:),intersectionpoints(Indnp(:,3),:)-intersectionpoints(Indnp(:,4),:));

%Search for largest area
cdistf = max([abs(cdist1(:,3)) abs(cdist2(:,3)) abs(cdist3(:,3))],[],2);
%cdistf = max([sqrt(cdist1(:,1).^2+cdist1(:,2).^2+cdist1(:,3).^2) sqrt(cdist2(:,1).^2+cdist2(:,2).^2+cdist2(:,3).^2) sqrt(cdist3(:,1).^2+cdist3(:,2).^2+cdist3(:,3).^2)],[],2);
%cdistf =sqrt(cdist1(:,1).^2+cdist1(:,2).^2+cdist1(:,3).^2);
OutsideVal = isnan(xdir) | isnan(ydir) | (cdistf == 0)| (d<0); 
xdir(OutsideVal) =[];
ydir(OutsideVal) =[];
cdistf(OutsideVal) =[];
aceptancestrength(OutsideVal) =[];
%Interpolate the map
maxx =ceil(max(xdir));
if(maxx >mapsize(1))
    maxx =mapsize(1);
end
minx =floor(min(xdir));
if(minx <1)
    minx =1;
end
maxy = ceil(max(ydir));
if(maxy >mapsize(2))
    maxy =mapsize(2);
end
miny = floor(min(ydir));
if(miny <1)
    miny =1;
end

Field =scatteredInterpolant(xdir,ydir,aceptancestrength./cdistf*4,'linear','none');%interpolation function for E

Map =zeros(mapsize(2),mapsize(1));
[Xg,Yg] = meshgrid(minx:maxx,miny:maxy);
Xg =Xg(:);
Yg=Yg(:);
Map(sub2ind(size(Map), Yg, Xg))=Field(Xg,Yg);
Map(isnan(Map)) =0;