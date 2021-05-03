function E=fldfoc(f,D,N,lamb,n0,alf)
global xs ys
x=linspace(-D/2,D/2,N);
dx=x(2)-x(1);

h1=f*tan(alf);    %distance along x between the positionof the focal point and x=y=0
rfq=(xs-h1).^2+ys.^2+f^2;   %squared distance from entrance plane to focal point
k0=2*pi/lamb;  %k0
k0n0=k0*n0;    %note that n0 is a local variable, differing from that of the main prgr.
%k0q=k0^2;
kn0q=k0n0^2;

Nd2=N/2;
Nqh=((N+1)*0.5)^2;
E=1+zeros(N,N);   %the field is made equal to unity for all points, 
                %the part outside the lens is put equal to 0 below
for m1=Nd2+1:N
    hh=Nqh-(m1-0.5-Nd2)^2;
    mh=fix(hh^0.5+0.5)+1+Nd2;
    m1m=N-m1+1;
    for m2=mh:N
        m2m=N-m2+1;
        E(m1,m2)=0;
        E(m1,m2m)=0;
        E(m1m,m2)=0;
        E(m1m,m2m)=0;
    end
end
rf=rfq.^0.5;   %rf contains the distances between points in the plane just 
            %behind the lens and the chosen focal point
E=E.*exp(-1i*k0n0*rf);   %if a ray picture would have been used all ray would 
                    %be in phase in the focal point
  % the part below takes into account propagation of SVE E in the plane
  % just behind the lens to the focal plane, by 1 step (length f) with FTBPM
dk=2*pi/(N*dx);

Ma=linspace(0,N-1,N)-Nd2;
k_x=Ma*dk;   %after fft and fftshift the DC component corresp. to (Nd2+1,Nd2+1)
%k_xq=k_x.^2;
%k_zq=zeros(N,N);
[k_xq,k_yq]=meshgrid(k_x.^2);
k_zq=kn0q-k_xq-k_yq;
k_z=real(k_zq.^0.5)-k0n0;
clear k_zq
Et=fft2(E);
    %sum(sum(abs(Et).^2))/S1/256
    Et=fftshift(Et);
    Et=Et.*exp(1i*k_z*f);
    Et=fftshift(Et);
    E=ifft2(Et);
