/*
*   This code generates the position coordinates x_i, y_i, z_i, i=1,npart,
*   for the npart spheres in a fractal aggregate.   The fractal scaling
*   is given by 
*
*      npart = k0 (Rg/a)^df
*      
*   where k0: structure factor, df: fractal dimension,, a: sphere radius,
*   Rg: radius of gyration:
*
*   Rg^2 = (1/npart) sum r_i^2
*
*   with r_i: distance from ith sphere to center of mass of cluster.
*
*   The code uses a pseudo-random algorithm to mimick cluster-cluster 
*   aggregation, subject to the constraint that the fractal scaling is
*   identically satisfied for the cluster.   
*
*   input parameters:  all should be obvious except nsamp:  this is the 
*   initial number of spheres from which the npart--sized custer will be
*   generated.   nsamp should be >= npart.   I've used nsamp around 
*   1 - 2 * npart.   
*
*   iccmod=0: the code uses a cluster-cluster algorithm.
*   iccmod=1: the original DLA algorithm:  one sphere at a time
*   is added to the cluster.    Not realisti*of typical soot dynamics.
*/

#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include <fstream>

const int npd = 5000;

int main() {
	int npart, nsamp, k0, df, iccmod;	
	std::cout << " Enter space-separated list:" << std::endl
		<< "{ npart, nsamp, k0, df, iccmod }: ";
	std::cin >> npart >> nsamp >> k0 >> df >> icmod;

	std::string fout;
	std::cout << "output file: ";
	std::cin >> fout;



}
