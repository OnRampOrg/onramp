// Author: Jason Regina
// Date: 3 May 2016
// Program: Finite Water Content
// Description: This program implements the finite water content
// 	method to simulate infiltration of water into bare soil.

#include <cstddef>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <vector>
#include "soil.hpp"

double infiltrationRate(const Soil&, const Soil&, double, double);
bool GreaterThan(double x, double y) { return (x > y); }

int main( int argc, char** argv )
{
	// Parameters for sand soul column
	double theta_e = 0.417;	// Effective porosity
	double theta_r = 0.020;	// Residual moisture content
	double theta_w = 0.033;	// Wilting point moisture content
	double psi_b   = 7.260;	// Bubbling entry pressure (cm)
	double lambda  = 0.694;	// Pore distribution index
	double K_s	   = 23.56;	// Saturated hydraulic conductivity (cm/h)

	// Parameters for simulation
	double timeStep  = 2.5;		// Time step (s)
	std::size_t N	 = 400;		// Number of moisture content bins
	double totalTime = 3.0;		// Duration of simulation (h)
	double rainStart = 0.0;		// Start of rainfall (h)
	double rainDurat = 0.25;	// Duration of rainfall (h)
	double rainRate  = 50.0;	// Rainfall intensity (cm/h)

	// Generate soil profile
	std::vector<Soil> bins;
	bins.reserve(N);
	double deltaTheta = (theta_e - theta_r) / double(N);
	double theta = theta_r + deltaTheta;

	for (std::size_t j = 0; j != N; ++j)
	{
		Soil s(theta, theta_r, theta_e, lambda, K_s, psi_b, 
			deltaTheta);

		bins.push_back(s);
		theta += deltaTheta;
	}

	// Prepare simulation
	double ponded = 0.0;
	std::vector<double> depth(N, 0.0);
	std::size_t initial = std::size_t(theta_w / deltaTheta);
	std::size_t rightMost = initial;

	// Run simulation
	double rate = 0.0;
	double dt = timeStep / 3600.0;
	std::size_t steps = std::size_t(totalTime / dt);

	// Generate rainfall
	std::vector<double> rain(steps, 0.0);
	std::size_t rs = std::size_t(steps * rainStart / totalTime);
	std::size_t rd = std::size_t(steps * rainDurat / totalTime);
	double depthPerStep = rainRate * timeStep / 3600.0;
	std::fill (rain.begin()+rs,rain.begin()+rs+rd,depthPerStep);

	// Simulation loop
	for (std::size_t i = 0; i != steps; ++i)
	{
		// Collect rainfall
		ponded += rain.at(i);

		// Infiltration (saturated bins)
		rate = bins.at(initial).K() * dt;

		// Determine actual depth of infiltration
		if (rate < ponded)
		{
			ponded -= rate;
		}
		else
		{
			ponded = 0.0;
			if (i >= rs+rd)
			{
				break;
			}
			else
			{
				continue;
			}
		}

		// Infiltration (unsaturated bins)
		for (std::size_t j = initial + 1; j != N; ++j)
		{
			if (depth.at(j) == 0)
			{
				rightMost++;
				if (bins.at(j).Zd() < ponded)
				{
					depth.at(j) = bins.at(j).Zd();
					ponded -= bins.at(j).Zd();
				}
				else
				{
					depth.at(j) = ponded;
					ponded = 0.0;
					break;
				}
			}
			
			// Determine infiltration rate
			rate = infiltrationRate(bins.at(rightMost), bins.at(initial), 
				depth.at(j), ponded);

			// Determine potential depth of infiltration
			rate = rate * dt;

			// Determine actual depth of infiltration
			if (rate < ponded)
			{
				depth.at(j) += rate;
				ponded -= rate;
			}
			else
			{
				depth.at(j) += ponded;
				ponded = 0.0;
				break;
			}
		}

		// Capillary relaxation
		std::sort(depth.begin()+initial+1, depth.end(), GreaterThan);
	}

	// Output
	std::cout << "Ponded (cm): ";
	std::cout << std::setprecision(8) << std::fixed 
			<< ponded << std::endl;
	std::ofstream fout("moisture_profile.csv");
	fout << "#MoistureContent,Depth" << std::endl;
	for (std::size_t j = 0; j != N; ++j)
	{
		fout << std::setprecision(8) << std::fixed 
			<< bins.at(j).theta() << ",";
		fout << depth.at(j) << std::endl;
	}
	fout.close();

	// Terminate
	return 0;
}

// Calculate the infiltration rate
double infiltrationRate(const Soil& d, const Soil& i, double z, double hp)
{
	double rate;

	rate = (d.K() - i.K()) / (d.theta() - i.theta());
	rate = rate * (1 + (d.Geff() + hp)/z);

	return rate;
}
