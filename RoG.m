
% Written by Divjyot Singh
% Last Modified: February 10, 2021
% This function calculates the radius of gyration for a soot aggregate

% 'aggregate' is an N*3 array which stores the x,y,z coordinates of
% the N monomers in a soot aggregate. 'radius' is the radius of the monomer
% of the monondisperse soot aggregate. All units are nm. All variables are
% float.

% the function returns 'radiusOfGyration', which is the radius of gyration
% of a given soot aggregate. For aggregates with N>1, this function assumes
% the monomers to be point mass. This approximation is not expected to
% significantly impact the results.


function radiusOfGyration = RoG(aggregate,radius)

% This function calculates the radius of gyration of any aggregate.

Ns = size(aggregate,1);
if Ns ==1
    radiusOfGyration = sqrt(3/5)*radius;
    return
end

center = mean (aggregate, 1); % Find aggregate center of mass
x = aggregate(:,1);
y = aggregate(:,2);
z = aggregate(:,3);
x_s = (x-center(1)).^2;
y_s = (y-center(2)).^2;
z_s = (z-center(3)).^2;
Rt = sum(x_s)+sum(y_s)+sum(z_s);

radiusOfGyration = (Rt/Ns)^0.5; % Calculating the radius of gyration (This calculation treats monomers as point mass)

end

