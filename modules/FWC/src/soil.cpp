// soil.cpp

#include "soil.hpp"

Soil::Soil(double t, double tr, double te, double l, double ks,
		double pb, double dt)
{
	_theta = t;
	_theta_r = tr;
	_theta_e = te;
	_lambda = l;
	_K_s = ks;
	_psi_b = pb;
	_deltaTheta = dt;

	calcTHETA();
	calcK();
	calcH_c(); 
	calcpsi();
	calcGeff();
	calcZd();
}

void Soil::calcTHETA()
{
	_THETA = (_theta - _theta_r) / (_theta_e - _theta_r);
}

void Soil::calcK()
{
	_K = _K_s * std::pow(_THETA, (3 + 2 / _lambda));
}

void Soil::calcH_c()
{
	_H_c = -_psi_b * (2 + 3 * _lambda) / (1 + 3 * _lambda);
}

void Soil::calcpsi()
{
	_psi = -_H_c * std::pow(_THETA, (-1 / _lambda));
}

void Soil::calcGeff()
{
	double p = 3 + 2 / _lambda;
	_Geff = -_H_c * 2 * p / (p + 3);
}

void Soil::calcZd()
{
	std::size_t NMAX = 10000;
	double ATOL = 0.0005;

	double Zde = 1.0;
	_Zd = this->Geff() * _deltaTheta 
		* std::log(1 + Zde / (_psi * _deltaTheta));

	for ( std::size_t i = 0; i != NMAX; ++i )
	{
		Zde = _Zd;
		_Zd = this->Geff() * _deltaTheta 
			* std::log(1 + Zde / (_psi * _deltaTheta));

		if ( std::abs(_Zd - Zde) < ATOL )
			break;
	}
}
