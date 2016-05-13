// soil.hpp

#ifndef __SOIL_HPP__
#define __SOIL_HPP__

#include <cmath>
#include <cstddef>

class Soil {
public:
	Soil() : _theta(0.1), _theta_r(0.02), _theta_e(0.4), 
		_lambda(0.7), _K_s(24.0), _psi_b(7.0), _deltaTheta(0.00095) 
		{ calcTHETA(); calcK(); calcH_c(); calcpsi(); calcGeff(); 
		calcZd(); }
	Soil(double, double, double, double, double, double, double);

	double Zd() const { return _Zd; }
	double Geff() const { return _psi < _Geff ? _Geff : _psi; }
	double theta() const { return _theta; }
	double K() const { return _K; }

private:
	double _deltaTheta;
	double _timeStep;
	double _Zd;

	double _Geff;
	double _psi_b;
	double _H_c;
	double _psi;

	double _theta;
	double _theta_r;
	double _theta_e;
	double _THETA;

	double _lambda;
	double _K_s;
	double _K;

	void calcTHETA();
	void calcK();
	void calcH_c();
	void calcpsi();
	void calcGeff();
	void calcZd();
};

#endif
