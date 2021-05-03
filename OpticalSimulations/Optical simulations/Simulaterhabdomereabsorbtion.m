%Fig. S44-S46
%calculates the field just behind a lens using ray tracing,  
%aplied; the optical axis of the lens is the z-axis

close all
% clear;
global xs ys 
n=[1 1.45 1.34]; %reflective index: air, inside lens, inside crystal cone
lamb=0.45;  %in micron   the vacuum wavelength
k0=2*pi/lamb;    %wavenumber, in vacuum
k2=(k0*n(3))^2;         %introduced for computational efficiency, quantity for BPM
N=512;         %for FFT BPM 
Nd2=N/2;  %integer, N should be even  

    

n1=1.363;  %core index, values of Stavenga
n2=1.34;   %cladding index
a=1.6/2;  %radius of wg
V=2*pi*a*(n1^2-n2^2)^0.5/lamb; %used for modal fld calculation
%1st ray tracing through the lens

num=31;   %number of points along x; during ray tracing y=0 is (here) assumed
A=[11 11 8 16];  %fruit fly; A=[r1 |r2| thickness lens-diameter (diaphragma)]  r2<0; comment I
D=A(4);  %lens diameter
Xmx=A(4)/2; %window for BPM x=(-Xmx,Xmx) 
dz=0.125;   %stepsize delta z
dzc=17;  %distance from end of lens, f at dz=21.33 drosoph
Af=1000000;  %distance of source point, for parallel bundel just take a large number
angl=0;      %defines the angle of the source point (degrees)
zvp=-Af*cos(angl*pi/180);
xvp=Af*sin(angl*pi/180);


kappa = 0.005/2; %1/um Absorbance of the rhabdomere
  Ftransout =1; %Transmittance outside rhabdomere 
  e=0.3; % these two lines to introdice a second rhabdomere at distance e
%         % (boundary to boundary); together with the 4 lines in the loop below
%         %and the expression for m1M below

movr = 0; %Distance rhabdomere from center [um]

rvp=[xvp 0 zvp];     %source point

rmx=A(4)/2;  %maximum x and y values used for the incoming field, the field coming from outside a radius
           %of A(4)/2 (defining the aperture) is later put equal to zero
           %(if necessary)
           %a too large value of rmx may lead to total internalreflecttion
           %at the 2nd lens surface (even if rmx< lens radius
           %  comment II
           
xing=linspace(-rmx,rmx,num);   %xing defines grid for incoming rays
[rsf2,euit,fi,E]=calcraysE3(xing,xing,rvp,n,A,k0); %rsf2(1:num,1:3) position of rays (x,y,z) 
% at the output;  fi(1:num) complex phase; euit(1:num,1:3): unit vector giving ray
% direction; this quantity is not used below but could be useful 
%note that the wavelenght (and so k0) does not play any role in ray
%tracing, we use ko for simplicity

%Next lines calculate distances to nearest point: separated up/down and
%left right
rsf2m =reshape(rsf2,length(xing),length(xing),3);

distt = NaN(length(E),3);%Area around the ray

numx=size(xing,2);
numy=size(xing,2);
%Calculate ray area using cross product. Note calculates using points
%around the actualpoint
for m1=2:numx-1
    for m2=2:numy-1
    index =(m1-1)*numx+m2; %index in the final list
    distt(index,:)=cross(squeeze(rsf2m(m2+1,m1,:))-squeeze(rsf2m(m2-1,m1,:)),squeeze((rsf2m(m2,m1+1,:)))-squeeze(rsf2m(m2,m1-1,:)));
     
    end
end
area = reshape(sqrt(abs(distt(:,3))/4),length(xing),length(xing));%Calculate actual area
areat = NaN(length(E),1); %Store corrected areas
%Fills in the missing area values on the edges
for m1=1:numx
    for m2=1:numy
     index =(m1-1)*numx+m2; %index in the final list
     if(isnan(area(m2,m1)))%if not inside calculated area
         %First check if in perimeter
         if(m1==1)
            areat(index) =area(m2,m1+1);   
         elseif( m1==numx)
             areat(index) =area(m2,m1-1);   
         elseif( m2==1)
             areat(index) =area(m2+1,m1);
         elseif( m2==numy)
             areat(index) =area(m2-1,m1);
         %Check if neighbouring ray area has been calculate
         elseif(~isnan(area(m2,m1-1)))
              areat(index) =area(m2,m1-1);   
         elseif(~isnan(area(m2,m1+1)))
              areat(index) =area(m2,m1+1);   
         elseif(~isnan(area(m2+1,m1)))
              areat(index) =area(m2+1,m1);   
         elseif(~isnan(area(m2-1,m1)))
              areat(index) =area(m2-1,m1);   
         else
            areat(index) =NaN; %Not even near lense
         end
     else
          areat(index) =area(m2,m1); %Normally inside lens
     end
     
    end
end

outtakes=isnan(E); %These lines takes out the rays which got outside the lens
rsf2(outtakes,:) =[]; %These lines takes out the rays which got outside the lens
euit(outtakes,:) =[]; %These lines takes out the rays which got outside the lens
fi(outtakes) =[]; %These lines takes out the rays which got outside the lens
E(outtakes) =[]; %These lines takes out the rays which got outside the lens
areat(outtakes) =[];%These lines takes out the rays which got outside the lens
fi=fi-min(fi);   %to get easonable values for fi


%Test; position focal point behind right vertex
k=k0*n(3);       %k value for index n(3), used in BPM
% mr=2;            %2 corresponds to near axis propagation, 2<=mr<=num may be considered
% A=(fi(1)-fi(mr))/k;
% ddx=rsf2(mr,1)-rsf2(1,1);
% F=(ddx^2-A^2)/(2*A)    %comment V

%correction for unequal spacing of the rays: smal distance between
%rays-->larger intensity
%[idx,d] = knnsearch(rsf2, rsf2, 'k', 3); %search nearest neighbour ray
dxh=areat; %distance to nearest ray
dxi=1./dxh'.^0.5; 
E=E.*dxi;               %Comment VI
%E=E/max(E);  %to get reasonable values for E
E =E*Af*(xing(2)-xing(1)); %Scaling the E to resonable without losing accuracy, when changing angle

 figure(1)  %plot

 hold on
%plot(rsf2(:,1),rsf2(:,2),'ko')
plot3(rsf2(:,1),rsf2(:,2),fi,'k.')
plot3(rsf2(:,1),rsf2(:,2),E,'r.')
hold off
title('ray positions behind the lens: fi (black) and field E (red)')
xlabel('x/micrometer')
ylabel('y/micrometer')
%calculation of circularly simmetrical field for BPM
fiB=zeros(N);  %allocation of memory
EB=fiB;        %allocation of memory

x=linspace(-Xmx,Xmx,N);
dx=x(2)-x(1);
%Rq=max(rsf2(:,1))^2;   %squared max value of x of nonzero field
             %building the field for BPM using interpolation
clear Es fis;
Es =scatteredInterpolant(rsf2(:,1),rsf2(:,2),E','natural','none');%interpolation function for E
fis =scatteredInterpolant(rsf2(:,1),rsf2(:,2),fi','natural','none');%interpolation function for fi
%loop through whole area and interpolate values for E and fiB      

[Xg,Yg] = meshgrid(1:N,1:N);   
Xg =Xg(:);
Yg=Yg(:);
EB(sub2ind(size(EB), Yg, Xg)) = Es(x(Xg),x(Yg));
fiB(sub2ind(size(fiB), Yg, Xg)) = fis(x(Xg),x(Yg));

EB(isnan(EB)) =0; %set outside values to 0
fiB(isnan(fiB)) =0;%set outside values to 0
clear E
EB=EB.*exp(1i*fiB);
E=EB;   %E: normal notation for field in our BPM software
clear EB fiB 

dk=2*pi/(N*dx);
M=linspace(0,N-1,N);

Ma=M-Nd2+0.5;

k_x=(Ma-0.5)*dk;
k_xq=k_x.^2;
k_zq=zeros(N,N);
for m1=1:N
    
    for m2=1:N
         k_zq(m1,m2)=k2-k_xq(m1)-k_xq(m2);  
    end
end
k_z=k_zq.^0.5;  %k_z values for various Fourier components
clear k_zq

[xs,ys]=meshgrid(x,x);
figure
hold on
pcolor(xs,ys,abs(E));
shading interp
title('field |E| just behind the lens')
colorbar
hold off



% below the BPM part as a test to the calculated field behind the lens
% note: here no absorbers at the boundaries are applied
Et=fft2(E);
Et=fftshift(Et);
Et1=Et;

Et=Et1.*exp(1i*k_z*dzc);
Et=fftshift(Et);
E=ifft2(Et);
    
    
figure
hold on
pcolor(xs,ys,abs(E));
shading interp
d=sum(sum(((xs.^2+ys.^2).^0.5).*abs(E).^2)/sum(sum(abs(E).^2)))  %measure for width of beam
tt=['field at z=' num2str(dzc) ' d=' num2str(d)];
title(tt)
colorbar
hold off

      
 %Field ready
 x=linspace(-D/2,D/2,N);
[xs,ys]=meshgrid(x);
dx=x(2)-x(1);  %equal to the assumed stepsize along y, dy
dxq=dx^2;   

%modal field for analysis, may also be used for testing purposes
rq=xs.^2+ys.^2;
Ne=clcfibfundN(n1,n2,V);    %program calculates the effective index of fundamental mode
ss=['modal index: ' num2str(Ne)]
r(1:Nd2)=x(Nd2+1:N);
figure
Efi=clcfld(n1,n2,Ne,V,r,a);   %the radial dependence of the rotationally invariant modal field
plot(r,Efi)
title('modal field, fundamental mode E(r)')
hold off
Em=spline(r,Efi,rq.^0.5);   %the 2D cross section of the field is calculated
Em=Em/(dxq*sum(sum(abs(Em).^2)))^0.5; %normalizing for inner product:
                                     %dxq*sum(sum(abs(Em).^2)
     
%The Aperature if needed
% apdist =movr+a; %Aperature centre position
% for m1 = 1:2/dz
%       Et=fft2(E);   %FT
%     Et=fftshift(Et); %shift to get a logical labeling:  k_x=k_y=0 corresp. to (Nd2+1,Nd2+1)
%     Et=Et.*exp(1i*k_z*dz);
%     Et=fftshift(Et); %back shift
%     E=ifft2(Et);     %inverse transform
%     E((xs+2.5-apdist).^2+(ys).^2 > 2.5^2) = E((xs+2.5-apdist).^2+(ys).^2 > 2.5^2)*0.8; %This puts aperature to distal end of the rhabdomere
% end                                    
%BPM parameters needed or of help in the computations

n0=(n1+n2)/2;  %average index
k0=2*pi/lamb;  %k0, the wavenumber
k0n0=k0*n0;  %for speed, the product is needed several times
k0q=k0^2;
rq=xs.^2+ys.^2;

% k_z values for propagation of plane waves
kn0q=k0n0^2;
dk=2*pi/(N*dx);    %delta(k)
%Nd2=N/2;
Ma=linspace(0,N-1,N)-Nd2;  %used to define an array for the  k_x and k_y values
k_x=Ma*dk;   %after Matlab commands fft and fftshift the DC component k_x=k_y=0 corresp. to (Nd2+1,Nd2+1)
k_xq=k_x.^2;
k_zq=zeros(N,N);  %allocating memory
Fexp=zeros(N,N);
for m1=1:N
    for m2=1:N
         k_zq(m1,m2)=kn0q-k_xq(m1)-k_xq(m2);  
    end
end
k_z=real(k_zq.^0.5)-k0n0;   
clear k_zq   %saves memorie

%index factor on propagating
n1q=n1^2;
n2q=n2^2;
hf=k0*(n2q-n0^2)/(2*n0)*dz;  %help quantity for Q_2 operator
Fexp(1:N,1:N)=exp(1i*hf); %exp index factor for background, part with index n2
                           %Fexp entries for core of rhabdomere are defined
                           %below

%assumed smooth length
smdx=0.02; %1/4 of difference in index at r=a+smdx (see notes in doc-file)
msm=2*round(0.5*a*log(3)/smdx);  %for function 1/(1+(x/a)^msm)
G=100; 
xsmmx=a+smdx*log(G)/log(3); % x value for which (1+(x/a)^msm)=100
mmx=round(xsmmx/dx)+1;    % safe number of discretization points around the core
                           %to apply the effect of the smoothed core index
msmd2=msm/2;   %needed below

ap=a^msm;
%aq=(a-dx/2)^2;
%aq=a^2;
Ffilt=zeros(N,N);

  Ftrans = exp(-kappa*dz);

%Movement of the rhabdomere
M2mov =round(movr/dx);
for m1=Nd2+1:Nd2+1+mmx
      m1m=N-m1+1;
       m1M=m1m+M2e;     %
    for m2=Nd2+1:Nd2+1+mmx
        rp=rq(m1,m2)^msmd2;   %msm/2 because rq is already squared
        Hsm=1/(1+rp/ap);
        nq=n2q+(n1q-n2q)*Hsm;
        hf=k0*(nq-n0^2)/(2*n0)*dz;
        trans = Ftransout+(Ftrans-Ftransout)*Hsm;
        h1=exp(1i*hf)*trans;    %+ or -?
        
        Fexp(m1,m2+M2mov)=h1;    %clculation of exp(iQ_2dz), 4 points for symmetry reasons
        m2m=N-m2+1;
        Fexp(m1,m2m+M2mov)=h1;
        Fexp(m1m,m2m+M2mov)=h1;
        Fexp(m1m,m2+M2mov)=h1;
        
        Ffilt(m1,m2+M2mov)=Hsm;  %needed for analysis of power fraction in core of rhabdomere
        Ffilt(m1,m2m+M2mov)=Hsm;  
        Ffilt(m1m,m2m+M2mov)=Hsm;
        Ffilt(m1m,m2+M2mov)=Hsm;

    end
end
xsss=['power fraction of mode in core: ' num2str(sum(sum(Ffilt.*Em.^2))*dxq)]

%testfig for Ffilt
% figure(8)
% pcolor(xs,ys,Fexp);
% shading interp
% hold on
% 
% colorbar

%absorbers at boundary with width 1/wa of total width
wa=1/10;
nwa=round(N*wa+0.51);   %number of points involved
%filter function
xa=linspace(0,nwa*dx,nwa+1);
nwa=nwa+1;
mh=N-nwa+1;
as=0.002/dz;  %0.002 performs rather well, number could be changed for certain cases
fa=as*(1+cos(pi*xa/xa(nwa)));  %smoothly vaying aborption is introduced, near computational boundaries
fa=exp(-fa);
fainv =fa(nwa:-1:1);
%the effect of aborption at the boundaries is incorperated in Fexp
for m1=1:N
    Fexp(m1,1:nwa)=fa.*Fexp(m1,1:nwa);
    Fexp(1:nwa,m1)=fa'.*Fexp(1:nwa,m1);
    
    %fa=fa(nwa:-1:1);
    Fexp(m1,mh:N)=fainv.*Fexp(m1,mh:N);
    Fexp(mh:N,m1)=fainv'.*Fexp(mh:N,m1);

end


H1=sum(sum(abs(E).^2))*dxq;
H1=1/H1^0.5;
%  E=E*H1;  %field normalization
%Nstfld=sum(sum(abs(E).^2))*dxq;  %test for 1

% figure
% pcolor(xs,ys,abs(E));
% shading interp
% hold on
% contour(xs,ys,abs(E),5,'k')
% colorbar
% plot(0,0,'w+','markersize',18)
% 
% title('field in focal plane of lens ')
% hold off

% figure(1)
% plot(xs(Nd2,:),abs(E(Nd2,:)))
% hold on
% figure(4)
% plot(xs(Nd2,:),angle(E(Nd2,:)))
%
%
% H1=sum(sum(Em.*conj(E)))*dxq;
% EdecEm=abs(H1)^2      %power in mode
% % sum(sum(E.*conj(E)))*dxq  %totla power in starting field
% %
% figure(2)
% pcolor(xs,ys,abs(E));
% shading interp
% hold on
% contour(xs,ys,abs(E),5,'k')
% colorbar
% hold off
% % %

Nst=640; %with dz=0.125 this correspond to 80 micrometer
% Pmod(1:Nst)=0;   %part of field that is modal
% Pfld(1:Nst)=0;    %total field
Pcr(1:Nst)=0; %memory allocation
Pmod=Pcr;  %

for m1=1:Nst
    Et=fft2(E);   %FT
    Et=fftshift(Et); %shift to get a logical labeling:  k_x=k_y=0 corresp. to (Nd2+1,Nd2+1)
    Et=Et.*exp(1i*k_z*dz);
    Et=fftshift(Et); %back shift
    E=ifft2(Et);     %inverse transform
    E=Fexp.*E;       %application of effect of core index (sometimes called lens formula and absorption at boundary
    HE=abs(E).^2;    %for evaluation of power fraction in core
    %Pfld(m1)=sum(sum(HE))*dxq;
    Pcr(m1)=sum(sum(Ffilt.*HE))*dxq;
    H1=sum(sum(Em.*conj(E)))*dxq;
    Pmod(m1)=abs(H1)^2;
end

figure
pcolor(xs,ys,abs(E));
shading interp
hold on
contour(xs,ys,abs(E),'k')
plot(0,0,'w+','markersize',18)
colorbar
title(['propagation length = ' num2str(Nst*dz) ' \mum'])
hold off

%power curves
figure
z=linspace(1,Nst,Nst)*dz;
plot(z,Pcr,'k','linewidth',2)
title(['L = ' num2str(Nst*dz) '  P_c_o_r_e (z)'])
axis([0 Nst*dz 0 max(Pcr)]);
figure
plot(z,Pmod,'k','linewidth',2)
title(['L = ' num2str(Nst*dz) '  P_m_o_d (z)'])
axis([0 Nst*dz 0 max(Pmod)]);
AbPower =sum(Pcr* (1-exp(-kappa*2*dz)));
ssss=['Absorbtion: ' num2str(AbPower)]



