function [rsf2,euit,fi,E]=calcraysE3(xing,ying,rvp,n,A,k)
global  rc ec 
%This is a 3D lens tracing version
%rc is the considered position of a certain ray, ec its direction length
%unity; both in 3D
% at the output;  fi(1:num) complex phase; euit(1:num,1:3): unit vector giving ray
% direction; this quantity is not used below but could be useful 
%note that the wavelenght (and so k0) does not play any role in ray
%tracing, we use ko for simplicity
numx=size(xing,2);
numy=size(ying,2);

nr=n(2:3)./n(1:2);  %introduced for efficiency
nrinv=1./nr;  %introduced for efficiency
nrinv2=nrinv.^2;
kn=k*n;    %efficient, for phase calc.s

   

rsf2=zeros(numx*numy,3); %allocation of memory, position of rays at output
euit=zeros(numx*numy,3);              %allocation of memory, direction of rays at output
E(1:numx*numy)=0;       %allocation of memory, field
fi=E;                   %allocation of memory, complex phase
r1q=A(1)^2;     %introduced for efficiency
r2q=A(2)^2;     %introduced for efficiency
lgth0=sum(rvp.^2)^0.5;   %distance of source point to origin, introduced for efficiency

for m1=1:numx
    for m2=1:numy
    index =(m1-1)*numx+m2; %index in the final list
    xs=xing(m1);
    ys=xing(m2);
    rc=[xs ys 0];  %grid point at plane in front of lens, at z=0
    r2=sum(rc.^2);
    
    eh=rc-rvp;
    lgth=sum(eh.^2)^0.5;
    ec=eh/lgth;  %unit vector of ray
    E(index)=ec(3)^0.5/lgth;      % comment III
    fi(index)=(lgth-lgth0)*kn(1); %-lgth0 to get not too high values for fi
    t=zksnp1(A);            %calculation of inteserction point with front lens
    rc=rc+t*ec;            %point on 1st lens surface, t is the path length
    
    if(sqrt(rc(1)^2+rc(2)^2)>A(4)/2) %set everything to NaN if goes outside of the lens
        E(index) =NaN;
        fi(index) =NaN;
        rsf2(index,:) = [NaN NaN NaN];
        euit(index,:) =[NaN NaN NaN];
        continue;
    end
    fi(index)=fi(index)+t*kn(1);
    h1=1/(r1q-r2)^0.5;
    dfx=rc(1)*h1;
    dfy=rc(2)*h1;
    ec=rfrl1(dfx,dfy,nrinv(1),nrinv2(1));  %refraction at sf1; comment IV
    t=zksnp2(A);
%     if abs(imag(t))>0
%         t
%         r2^0.5
%     end
    rc=rc+t*ec;         %%point on 2nd lens surface
    fi(index)=fi(index)+t*kn(2);
    rr2=rc(1)^2+rc(2)^2;
    h1=1/(r2q-rr2)^0.5;
    dfx=-rc(1)*h1;
    dfy=-rc(2)*h1;
    ec=rfrl1(dfx,dfy,nrinv(2),nrinv2(2));  %similar as above; comment IV
    t=(A(3)-rc(3))/ec(3);
    rc=rc+t*ec;
    fi(index)=fi(index)+t*kn(3);
    rsf2(index,:)=[rc(1) rc(2) A(3)];  % z-value A(3) = lens thickness
    euit(index,:)=ec;
    end
    
end


