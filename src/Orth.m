function Orth( filename )
%This function takes in  file with the locations of features in images
%and creates a 3d point cloud with the features

%read in the file
file = fopen(filename, 'r');
line = fgets(file);
line = strsplit(line)
%get the number of camers, points, and observations from the first line
camTotal = int32(str2num(char(line(1))));
pointTotal = int32(str2num(char(line(2))))
obsTotal = int32(str2num(char(line(3))))

%set up W matrix
W = zeros(camTotal*2,pointTotal);
for i=1:obsTotal
    curr = strsplit(fgets(file));
    cam = int32(str2num(char(curr(1))));
    point = int32(str2num(char(curr(2))));
    x = str2num(char(curr(3)));
    y = str2num(char(curr(4)));
    W(cam+1, point+1) = x;
    W(camTotal+cam+1, point+1) = y;
end

%Get rid of the 0 entries in the W matrix
Wnew = zeros(camTotal*2, 1);
count = 1;
for i=1:pointTotal
    check = ismember(0, W(:,i));
    if(check == 0)
        Wnew(:,count) = W(:,i);
        count = count+1;
    end
end

%Subtract the mean of each row
W= Wnew;
[r, c] = size(W);
WPrime = W;
for i=1:r
    mean(W(i,:));
    WPrime(i,:) = W(i,:)-mean(W(i,:));
end

%take svd and get first 3 entries fo each matrix
[O1, Sig, O2] = svd(WPrime);
O2 = O2';

O1Prime = O1(:, 1:3);
Sigma = sqrt(Sig(1:3, 1:3));
O2Prime = O2(1:3,:);

Rht = O1Prime*Sigma;
Sht = Sigma*O2Prime;

%I = G*c
A = ones(camTotal2, 1);
B = zeros(camTotal, 1);
c = [A;B];

Gii = zeros(camTotal, 6);
Gjj = zeros(camTotal, 6);
Gij = zeros(camTotal, 6);
for i=1:camTotal
    Gii(i,:) = g(Rht(i,:), Rht(i,:));
    Gjj(i,:) = g(Rht(camTotal+i,:), Rht(camTotal+i,:));
    Gij(i,:) = g(Rht(i,:),Rht(camTotal+i,:));
end;

G = [Gii; Gjj];
G = [G; Gij];
G = pinv(G);

[Gr, Gc] = size(G)
[cr, cc] = size(c)

I= G*c;
%get L matrix used to find Q
L = [I(1), I(2), I(3); I(2), I(4), I(5); I(3), I(5), I(6)]
    
%Check Postive Definiteness
L = (L+L')/2;
[U, S] = eigs(L);
S(find(S<0)) = 0.0000001;

Q = U*sqrt(S);

R = Rht*Q;
S = inv(Q)*Sht;

%Align
i = R(1,:)'/norm(R(1,:)');
j = R(camTotal+1,:)'/norm(R(camTotal+1,:)');
k = cross(i,j)/norm(cross(i,j));
RPrime = [i,j,k];
R=R*RPrime;
S=inv(RPrime)*S;


%Print to textfile and make point cloud
Sx = S(1,:);
Sy = S(2,:);
Sz = S(3,:);

fileId = fopen('coords.txt', 'w');
fprintf(fileId, '%f %f %f \n', Sx, Sy, Sz);

scatter3(Sx, Sy, Sz, 'filled');

end
