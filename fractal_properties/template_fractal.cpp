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
#include <ctime>
#include <fstream>
#include <cmath>
#include <cstdio>
#include <random>
#include <functional>

int npd = 5000;

// ran3 returns uniform between 0 and 1
// replaced ran3 with this C++ equivalent:
// remember to ensure that everything receives the same seed as it does in the original code
std::random_device rd;
std::mt19937 gen(rd());
std::uniform_real_distribution<> unit(0.0, 1.0); // call like unit(gen);

const float PI = std::atan(1) * 4;

std::ofstream foutstream; // this is the output file

void addone(int &nptot, std::vector<std::vector<float>> &xp, int rkf1, float &df)
{
	// npd = 3000;
	std::vector<float> rp(npd);
	std::vector<int> ijp(npd);
	int itmax = 20000;

	float rgn2 = 0, rmax = 0, ri;
	for (int i = 0; i < nptot; i++)
	{
		ri = 0;
		for (int m = 0; m < 3; m++)
		{
			ri += xp[m][i] * xp[m][i];
		}
		rgn2 += ri;
		rmax = std::max(rmax, ri);
	}

	rgn2 /= nptot;
	float rgn = std::sqrt(rgn2);
	rmax = std::sqrt(ri); // why does rmax even get initialized in the for loop?

	int np3 = nptot + 1;
	float rg3 = std::pow(np3, 1 / (float)df) * 2 * rkf1;
	float rg32; // not declared in the original code before the if statement, unsure about scoping
	float rn2 = np3 * ((np3 / nptot) * rg3 * rg3 - rgn2);
	float rn = std::sqrt(rn2);

	// check if rn is too big
	if (rn > 2 + rmax)
	{
		rn = rmax + 1.8;
		rn2 = rn * rn;
		rg32 = (rn2 / (float)np3 + rgn2) * (float)nptot / (float)np3;
		rg3 = std::sqrt(rg32);
	}

	// find particles that intersect with rn
	// GOTO 20 here??
	while (true)
	{ // this accomplishes the same thing as the goto, but much more nicely i think
		
	int i = 0; // = 1 in original FORTRAN code
		for (int j = 0; j < nptot; j++)
		{
			float rj2 = 0;
			for (int k = 0; k < 3; k++)
			{
				rj2 += xp[k][j] * xp[k][j];
			}
			float rj = std::sqrt(rj2);
			float rjn = std::fabs(rj - rn);

			if (rjn <= 2)
			{
				ijp[i] = j;
				rp[i] = rj;
				i++;
			}
		}

		int nj = i - 1;
		for (int ind = 0; ind < nj; ind++)
		{
			float ran1 = unit(gen);
			int j = nj * ran1 + 1;

			// 3-way swap?
			int it = ijp[ind];
			ijp[ind] = ijp[j];
			ijp[j] = it;

			// 3-way swap?
			float rt = rp[ind];
			rp[ind] = rp[j];
			rp[j] = rt;
		}

		int it = 0; // declared here for scope reasons
		for (int ij = 0; ij < nj; ij++)
		{
			int j = ijp[ij];

			float rj = rp[ij], rj2 = rj * rj;
			if (rj + rn < 2)
			{
				continue;
			}

			float ctj = xp[2][j] / rj;			  // og: index 3
			float stj = std::sqrt(1 - ctj * ctj); // (1-ctj)(1+ctj) originally
			float phij = std::atan2(xp[1][j], xp[0][j]);
			float sphij = std::sin(phij), cphij = std::cos(phij);
			float ctp = (rn2 + rj2 - 4) / (2 * rn * rj);
			float stp = std::sqrt(1 - ctp * ctp);

			// randomly find attachment point
			// original code had do-while, equivalent to a for-loop here
			// it is declared waaaay above just for the sake of being able to use it out of scope
			// the original code doesn't seem to scope very nicely
			for (it = 0; it < itmax; it++)
			{
				float ran1 = unit(gen);
				float phi = 2 * PI * ran1;
				float zpp = rn * ctp;
				float xpp = rn * stp * std::cos(phi);
				float ypp = rn * stp * std::sin(phi);

				float z = zpp * ctj - xpp * stj;
				float x = (zpp * stj + xpp * ctj) * cphij - ypp * sphij;
				float y = (zpp * stj + xpp * ctj) * sphij + ypp * cphij;

				int icon = 0;
				for (int i = 0; i < nptot; i++)
				{
					float xi = x - xp[0][i];
					float yi = y - xp[1][i];
					float zi = z - xp[2][i];
					float ri2 = xi * xi + yi * yi + zi * zi;
					if (ri2 < 3.999)
						icon = 1;
				}
				if (icon == 0)
				{
					// originally statement label 80, i removed the GOTO
					// shift coordinates to new origin
					xp[0][np3] = x;
					xp[1][np3] = y;
					xp[2][np3] = z;
					float x0 = 0, y0 = 0, z0 = 0;
					for (int i = 0; i < 120; i++)
					{
						x0 += xp[0][i];
						y0 += xp[1][i];
						z0 += xp[2][i];
					}

					x0 /= np3;
					y0 /= np3;
					z0 /= np3;
					for (int i = 0; i < np3; i++)
					{
						xp[0][i] -= x0;
						xp[1][i] -= y0;
						xp[2][i] -= z0;
					}
					return;
				}
			}

			npd = 5000; // FORTRAN code changes npd to 3000 for some reason, just safety check
		}
		if (it > nj)
		{
			rn += 0.01;
			rn2 = rn * rn;
			rg32 = (rn2 / (float)np3 + rgn2) * nptot / (float)np3;
			rg3 = std::sqrt(rg32);

			char buffer[200];
			int n = 50; // i can't find where n is initialized, so here's a bad value
			std::snprintf(buffer, 200, "+particle %3d does not fit. new rn, rgn: %8.2f %8.2f\n", n, rn, rgn);
			foutstream << buffer;
		}
	}
}

template <typename T>
void ctos(std::vector<T> &x, std::vector<float> &r)
{
	r[0] = std::sqrt(x[0] * x[0] + x[1] * x[1] + x[2] * x[2]);
	if (r[0] == 0)
	{
		r[1] = 1;
		r[2] = 0;
	}
	else
	{
		r[1] = x[2] / r[0];
		r[2] = std::atan2(x[1], x[0]);
	}
}

template <typename T>
void rotate(int idir, float alpha, float beta, float gamma, std::vector<T> x)
{
	std::vector<float> xt(3);

	float sa = std::sin(alpha);
	float ca = std::cos(alpha);
	float sb = std::sin(beta);
	float cb = std::cos(beta);
	float sg = std::sin(gamma);
	float cg = std::cos(gamma);

	if (idir == 0)
	{
		// replace this with another for loop?
		xt[0] = (ca * cb * cg - sa * sg) * x[0] + (cb * cg * sa + ca * sg) * x[1];
		xt[1] = (-cg * sa - ca * cb * sg) * x[0] + (ca * cg - cb * sa * sg) * x[1];
		xt[2] = ca * sb * x[0] + sa * sb * x[1] + cb * x[2];
	}
	else
	{
		xt[0] = (ca * cb * cg - sa * sg) * x[0] - (cb * sg * ca + sa * cg) * x[1];
		xt[1] = (sg * ca + sa * cb * cg) * x[0] + (ca * cg - cb * sa * sg) * x[1];
		xt[2] = -cg * sb * x[0] + sg * sb * x[1] + cb * x[2];
	}

	for (int m = 0; m < 3; m++)
	{
		x[m] = xt[m];
	}
}
template <typename T>
void rotate(int idir, float &alpha, float &beta, float &gamma, std::vector<T> &x)
{
	std::vector<float> xt(3);

	float sa = std::sin(alpha);
	float ca = std::cos(alpha);
	float sb = std::sin(beta);
	float cb = std::cos(beta);
	float sg = std::sin(gamma);
	float cg = std::cos(gamma);

	if (idir == 0)
	{
		// replace this with another for loop?
		xt[0] = (ca * cb * cg - sa * sg) * x[0] + (cb * cg * sa + ca * sg) * x[1];
		xt[1] = (-cg * sa - ca * cb * sg) * x[0] + (ca * cg - cb * sa * sg) * x[1];
		xt[2] = ca * sb * x[0] + sa * sb * x[1] + cb * x[2];
	}
	else
	{
		xt[0] = (ca * cb * cg - sa * sg) * x[0] - (cb * sg * ca + sa * cg) * x[1];
		xt[1] = (sg * ca + sa * cb * cg) * x[0] + (ca * cg - cb * sa * sg) * x[1];
		xt[2] = -cg * sb * x[0] + sg * sb * x[1] + cb * x[2];
	}

	for (int m = 0; m < 3; m++)
	{
		x[m] = xt[m];
	}
}

void finmin(int isame, int &np1, std::vector<std::vector<float>> &xp, int &np2, std::vector<std::vector<float>> &xpc, int &ic1, int &ic2, float &r12)
{
	float rmin = 10000;
	for (int i = 0; i < np1; i++)
	{
		for (int j = 0; j < np2; j++)
		{
			if (isame == 0 || i != j)
			{
				float rij = 0;
				for (int m = 0; m < 3; m++)
				{
					float x12 = xp[m][i] - xpc[m][j];
					rij += x12 * x12;
				}
				if (rij < rmin)
				{
					rmin = rij;
					ic1 = i;
					ic2 = j;
				}
			}
		}
	}
	r12 = std::sqrt(rmin);
}

// void combine(int& npic, std::vector<std::vector<float>>& xpt, int& npjc, std::vector<std::vector<float>>& xpc, int& rkf1, float& df) {
template <typename T>
void combine(int &np1, std::vector<std::vector<T>> &xp, int &npc, std::vector<std::vector<float>> &xp2, float &rkf1, float &df)
{
	int nits = 10000;
	// xp(3,npd), xc(3), xpc(3, npd), xp2(3, npd), x1(3), x2(3), rc1(3), rc2(2)
	std::vector<std::vector<float>> xpc(3, std::vector<float>(npd));
	std::vector<float> xc(3), x1(3), x2(3), rc1(3), rc2(3);

	if (np1 == 1 && npc == 1)
	{
		float ct = 1 - 2 * unit(gen);
		float phi = 2 * PI * unit(gen);
		float st = sqrt(1 - ct * ct); // (1-ct)*(1+ct) in the original code, but this is slightly faster?

		xp[0][0] = st * std::cos(phi);
		xp[1][0] = st * std::sin(phi);
		xp[2][0] = ct;

		for (int m = 0; m < 3; m++)
		{
			xp[m][1] = -xp[m][0];
		}
		return;
	}
	if (npc == 1)
	{
		addone(np1, xp, rkf1, df);
		return;
	}

	int np3 = np1 + npc;
	float rgc = std::pow((float)npc, 1 / df) * 2 * rkf1;
	float rg1 = std::pow((float)np1, 1 / df) * 2 * rkf1;
	float rg3 = std::pow((float)np3, 1 / df) * 2 * rkf1;
	float c = sqrt((float)np3 * (np3 * rg3 * rg3 - np1 * rg1 * rg1 - npc * rgc * rgc) / (float)(npc * (np3 - npc)));

	float sentinel = -1E10; // used to decide if r12c forces clusters to not combine?
	for (int it = 0; it < nits; it++)
	{
		float ctc = 1 - 2 * unit(gen); // seeded with 1??
		float stc = std::sqrt(1 - ctc * ctc);
		float pc = 2 * PI * unit(gen);
		xc[0] = c * stc * std::cos(pc);
		xc[1] = c * stc * std::sin(pc);
		xc[2] = c * stc;
		for (int i = 0; i < npc; i++)
		{
			for (int m = 0; m < 3; m++)
			{
				xpc[m][i] = xp2[m][i] + xc[m];
			}
		}

		float r12;
		int ic1, ic2;

		// gripe about FORTRAN: WHY IS R12 NOT DECLARED BEFORE ITS PASSED TO FINMIN???
		finmin(0, np1, xp, npc, xpc, ic1, ic2, r12);

		if (r12 > 4.0)
			continue;

		float r1 = 0, r2 = 0;
		for (int m = 0; m < 3; m++)
		{
			x1[m] = xp[m][ic1] - xc[m];
			x2[m] = xp2[m][ic2];
			r1 += x1[m] * x1[m];
			r2 += x2[m] * x2[m];
		}
		r1 = std::sqrt(r1);
		r2 = std::sqrt(r2);

		if (std::fabs(r1 - r2) > 2)
			continue;

		ctos(x2, rc2);
		float beta = std::acos(rc2[1]);
		float alpha = rc2[2];
		rotate(0, alpha, beta, 0., x1);
		float gamma = std::atan2(x1[1], x1[0]);

		rotate(0, 0.0, 0.0, gamma, x1);
		ctos(x1, rc1);
		ctc = (rc1[0] * rc1[0] + rc2[0] * rc2[0] - 4) / (2 * rc1[0] * rc2[0]);
		if (std::fabs(ctc) > 1)
			continue;
		float tc = std::acos(ctc);
		float betac = tc - std::acos(rc1[1]);

		for (int i = 0; i < npc; i++)
		{
			rotate(0, alpha, beta, gamma, std::vector<std::reference_wrapper<float>>{xp2[0][i], xp2[0][i + 1], xp2[0][i + 2]});
			rotate(0, 0, betac, 0, std::vector<std::reference_wrapper<float>>{xp2[0][i], xp2[0][i + 1], xp2[0][i + 2]});
			rotate(1, alpha, beta, gamma, std::vector<std::reference_wrapper<float>>{xp2[0][i], xp2[0][i + 1], xp2[0][i + 2]});

			for (int m = 0; m < 3; m++)
			{
				xpc[m][i] = xp2[m][i] + xc[m];
			}
		}

		float r12c;
		finmin(0, np1, xp, npc, xpc, ic1, ic2, r12c);

		sentinel = r12c;
		if (r12c >= 2)
			break;
	}
	// write statement
	if (sentinel < 2)
		foutstream << "(clusters did not combine)\n";

	for (int i = 0; i < npc; i++)
	{
		for (int m = 0; m < 3; m++)
		{
			xp[m][i + np1] = xpc[m][i];
		}
	}

	for (int m = 0; m < 3; m++)
	{
		xc[m] = 0;
	}

	for (int i = 0; i < npc; i++)
	{
		for (int m = 0; m < 3; m++)
		{
			xc[m] += xp[m][i];
		}
	}

	for (int m = 0; m < 3; m++)
	{
		xc[m] /= (float)np3;
	}
	for (int i = 0; i < np3; i++)
	{
		for (int m = 0; m < 3; m++)
		{
			xp[m][i] -= xc[m];
		}
	}
}

void ppclus(int &nptot, int &nptotsamp, float &rkf1, float &df, int &iccmod, std::vector<std::vector<float>> &xp, int &iseed0)
{
	// these initializations are not very in line with C++, ideally, we simply initalize and then push back instead of length-initialization
	std::vector<int> iadd(npd), npc(npd), iarray(3);
	float ran3var; // not to be confused with ran3 function
	// xp is already given??
	// xp needs to have 3 elements apparently
	std::vector<std::vector<float>> /* xp(3), */ xpc(3, std::vector<float>(npd)), xpt(3, std::vector<float>(npd));

	nptotsamp = std::min(nptotsamp, npd);
	if (nptotsamp <= nptot)
	{
		nptotsamp = nptot;
	}
	while (true)
	{
		float ran = unit(gen);

		for (int i = 0; i < nptotsamp; i++)
		{
			for (int m = 0; m < 3; m++)
			{
				xpt[m].push_back(0);
			}
			iadd[i] = i;
			npc[i] = i;
		}

		if (iccmod < 0)
		{
			float xm = 0;
			for (int i = 0; i < nptot; i++)
			{
				xp[0].push_back(2 * i);
				xm += 2 * i;
			}
			xm /= nptot;
			for (int i = 0; i < nptot; i++)
			{
				xp[0][i] -= xm;
			}
			return;
		}

		int nc = nptotsamp;
		while (nc > 1)
		{
			int i, j;

			do
			{ // note: these (+1)s probably don't need to be here, since i and j simply become indices
				// C++ 0 indexing makes the +1 unnecessary
				if (iccmod == 0)
				{
					i = (int)(nc * unit(gen)) + 1;
				}
				else
				{
					i = 1;
				}
				j = (int)(nc * unit(gen)) + 1;
			} while (i == j);

			int ic = std::min(i, j), jc = std::max(i, j);
			int iaddic = iadd[ic], iaddjc = iadd[jc];
			int npic = npc[ic], npjc = npc[jc];

			for (int i = 0; i < npjc; i++)
			{
				for (int m = 0; m < 3; m++)
				{
					xpc[m][i] = xpt[m][i + iaddjc - 1];
				}
			}

			// in FORTRAN, k ranges from jc-1 to ic+1
			// since C++ is zero-indexed, jc-1 --> jc-2, ic+1 --> ic
			// same happens on the inner loop with nk
			for (int k = jc - 2; k >= ic; k--)
			{
				// I don't think nk is actually used, it's just a counter
				// there should be npc(k) iterations
				for (int nk = npc[k]; nk >= 1; nk--)
				{
					int i = nk + iadd[k] - 1;
					int j = i + npjc;
					for (int m = 0; m < 3; m++)
					{
						xpt[m][j] = xpt[m][i];
					}
				}
				iadd[k] += npjc;
			}

			// COMBINE
			std::vector<std::reference_wrapper<float>> temp_xpt;
			for (int i = 0; i < iaddic; i++)
			{
				// note: pushing back elements from xpt actually pushes back their references
				// nice!
				temp_xpt.push_back(xpt[0][i]);
			}
			combine(npic, xpt, npjc, xpc, rkf1, df);

			npc[ic] = npic + npjc;

			if (npc[ic] == nptot)
			{
				for (int i = 0; i < nptot; i++)
				{
					int j = i + iaddic - 1;
					for (int m = 0; m < 3; m++)
					{
						xp[m][i] = xpt[m][j];
					}
				}
				return;
			}

			// index magic?
			// the FORTRAN indexing goes from jc --> nc-1
			for (int j = jc; j < nc; j++)
			{
				int jp = j + 1;
				iadd[j] = iadd[jp];
				npc[j] = npc[jp];
			}
		}
	}
}

int main()
{
	int npart, nsamp, iccmod;
	float rk, df;
	std::cout << " Enter space-separated list:" << std::endl
			  << "{ npart, nsamp, k0, df, iccmod }: ";
	std::cin >> npart >> nsamp >> rk >> df >> iccmod;

	std::string fout;
	std::cout << "output file: ";
	std::cin >> fout;

	foutstream.open(fout);

	npart = std::min(npart, npd);
	nsamp = std::min(nsamp, npd);
	nsamp = std::max(nsamp, npart);
	int iseed = 0;
	float rkf1 = std::pow(1.0 / rk, 1.0 / df) / 2;

	std::vector<std::vector<float>> xp(3, std::vector<float>(npd));
	ppclus(npart, nsamp, rkf1, df, iccmod, xp, iseed);

	for (int i = 0; i < npart; i++)
	{
		char buffer[200];
		std::snprintf(buffer, 200, "1.  %4.0f  %13.6f  %13.6f  %13.6f\n", xp[0][i], xp[1][i], xp[2][i]);
		foutstream << buffer;
	}
	foutstream.close();

	// original FORTRAN has a user choice to create another particle with different parameters
	// I think this is sort of optional
}
