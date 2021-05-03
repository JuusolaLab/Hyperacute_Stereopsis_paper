function N=clcfibfundN(n1,n2,V)
%program calculates the effective index of fundamental mode
aant=1000;
Vq=V^2;
n1q=n1^2;
n2q=n2^2;
p=n2q/n1q;
Aq=Vq/(n1q-n2q);
%A=Aq^0.5;   %2*pi*a/lambda
umx=min(V,3.84);
u=linspace(1e-8,umx,aant);
uq=u.^2;
wq=Vq-uq;
w=wq.^0.5;
J1=besselj(1,u);
J0=besselj(0,u);
Y1=J0./(u.*J1)-1./uq;
K0=besselk(0,w);
K1=besselk(1,w);
X1=-K0./(w.*K1)-1./wq;
hF=0.25*(1-p)^2*X1.^2+(1./uq+1./wq).*(1./uq+p./wq);
F=-0.5*(1+p)*X1-hF.^0.5;
HF=Y1-F;
%  HF(990:1000)
%  u(990:1000)
teken=sign(HF(1));
m1=2;
while sign(HF(m1))==teken
    m1=m1+1;
end
%umin=spline((Y1-F),u,0);
u0=u(m1-1); %max(0,umin-0.1);
u1=u(m1); %min([3.84 V umin])
u=linspace(u0,u1,aant);
uq=u.^2;
wq=Vq-uq;
w=wq.^0.5;
J1=besselj(1,u);
J0=besselj(0,u);
Y1=J0./(u.*J1)-1./uq;
K0=besselk(0,w);
K1=besselk(1,w);
X1=-K0./(w.*K1)-1./wq;
hF=0.25*(1-p)^2*X1.^2+(1./uq+1./wq).*(1./uq+p./wq);
F=-0.5*(1+p)*X1-hF.^0.5;
%Y1-F
%umin=spline((Y1-F),u,0)
%N=(Vq/(1-p)-umin^2)^0.5;
HF=Y1-F;
% HF(90:100)
% u(90:100)
teken=sign(HF(1));
m1=2;
while sign(HF(m1))==teken
    m1=m1+1;
end
u1=u(m1-1);
u2=u(m1);
Fr=abs(HF(m1-1)/HF(m1));
umin=(Fr*u2+u1)/(1+Fr);
N=(n1q-umin^2/Aq)^0.5;
