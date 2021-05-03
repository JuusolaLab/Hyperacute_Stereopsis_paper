function t=zksnp1(A)
%determines t (real number) such that v=rc+t*ec intersects z=A(1)-(A(1)^2-x^2-y^2)^0.5
%1st determine a,b,c of at^2+bt+c=0
global rc ec 

c=rc(1)^2+rc(2)^2;
b=2*(-A(1)*ec(3)+rc(1)*ec(1)+rc(2)*ec(2)); 
a=1; %sum(ec.^2);

t=(-b-(b^2-4*a*c)^0.5)/(2*a);