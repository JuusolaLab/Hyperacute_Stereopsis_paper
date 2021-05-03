function t=zksnp2(A)
%determines t such that v=rc+t*ec intersects f=A3+(A2^2-r^2)^0.5-A2
%1st determine a,b,c of at^2+bt+c=0
global rc ec 

B=(rc(3)-A(3)+A(2));
c=B^2-A(2)^2+rc(1)^2+rc(2)^2;
b=2*(B*ec(3)+ec(1)*rc(1)+ec(2)*rc(2));
a=sum(ec.^2);

t=(-b+(b^2-4*a*c)^0.5)/(2*a);