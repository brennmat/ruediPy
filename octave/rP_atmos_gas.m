function [C_atm,v_atm,D,M_mol,H] = rP_atmos_gas (gas,T,S,p_atm,year,hemisphere)

% [C_atm,v_atm,D,M_mol,H] = rP_atmos_gas (gas,T,S,p_atm,year,hemisphere)
%
% Returns dissolved gas concentrations in air-saturated water, volumetric gas content in dry air and molecular diffusivity in water.
% Concentrations are calculated as gas amount (ccSTP) per mass of water (g) at temperature T and salinity S
%
% NOTE: this file was forked from nf_atmos_gas.m in the noblefit package on 14 Jan. 2019
%
% INPUT:
% T:        temperature of water in deg. C
% S:        salinity in per mille (g/kg)
% p_atm:	total atmospheric air pressure, including water vapour (hPa, which is the same as mbar)
% gas:	    'He', 'He-3', 'He-4' (after Weiss)
%           'RHe' (3He/4He ratio)
%           'Ne', 'Ne-20', 'Ne_20','Ne-22', 'Ne_22' (after Weiss, isotope fractionation from Beyerle)
%           'Ar', 'Ar-36', 'Ar_36', 'Ar-40', 'Ar_40' (after Weiss, isotope fractionation from Beyerle)
%           'Kr', 'Kr-78', 'Kr_78', 'Kr-80', 'Kr_80', 'Kr-82', 'Kr_82', 'Kr-84', 'Kr_84', 'Kr-86', 'Kr_86 (after Weiss)
%           'Xe', 'Xe-124', 'Xe_124', 'Xe-126', 'Xe_126', Xe-128', 'Xe_128', 'Xe-129', 'Xe_129', 'Xe-130', 'Xe_130', 'Xe-131', 'Xe_131', 'Xe-132', 'Xe_132', 'Xe-134', 'Xe_134', 'Xe-136', 'Xe_136' (after Clever)
%           'SF6'
%           'CFC11', 'CFC12', 'CFC113'
%           'O2', 'O2-34', 'O2-35', 'O2-36'
%           'N2', 'N2-28, 'N2-29', 'N2-30'
%           'CH4' (no atmospheric partial pressures or aqueous concentrations, just Henry's Law coefficient from Sander (1999) data compilation. Diffusivity not yet implemented.
%           'CO2' (no atmospheric partial pressures or aqueous concentrations, just Henry's Law coefficient from Sander (1999) data compilation. Diffusivity not yet implemented.
%           'C3H8' propane (no atmospheric partial pressures or aqueous concentrations, just Henry's Law coefficient from Sander (1999) data compilation. Diffusivity not yet implemented.
%
% year:     year of gas exchange with atmosphere (calendar year, with decimals; example: 1975.0 corresponds to 1. Jan of 1975.098 corresponds to 5. Feb. 1975, etc.). This is only relevant for those gases with time-variable partial pressures in the atmosphere (e.g. CFCs, SF6)
% hemisphere: string indicating hemisphere (one of 'north', 'south', or 'global'). If the hemisphere argument is not specified, hemisphere = 'global' is used.
%
% OUTPUT:
% C_atm:	concentration in air-saturated water (ccSTP/g)
% v_atm:	volume fraction in dry air
% D: 	    molecular diffusivities (m^2/s)
% M_mol:    molar mass of the gas (g/mol), values taken from http://www.webqc.org/mmcalc.php
% H:        Henrys Law coefficient in (hPa/(ccSTP/g)), as in p* = H * C_atm, where p* is the partial pressure of the gas species in the gas phase
%
% EXAMPLES:
% 1. To get the Kr ASW concentration (ccSTP/g) in fresh water (temperature = 7.5 deg.C) at atmospheric pressure of 991 hPa:
% [C_atm,v_atm,D,M_mol,H] = rP_atmos_gas ('Kr',7.5,0,991); C_atm
%
% DISCLAIMER:
% This file is part of ruediPy, a toolbox for operation of RUEDI mass spectrometer systems.
% 
% ruediPy is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation, either version 3 of the License, or
% (at your option) any later version.
% 
% ruediPy is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
% 
% You should have received a copy of the GNU General Public License
% along with ruediPy.  If not, see <http://www.gnu.org/licenses/>.
% 
% ruediPy: toolbox for operation of RUEDI mass spectrometer systems
% Copyright (C) 2016, 2017, Matthias Brennwald (brennmat@gmail.com)
% 
% This program is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation, either version 3 of the License, or
% (at your option) any later version.
% 
% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
% 
% You should have received a copy of the GNU General Public License
% along with this program.  If not, see <http://www.gnu.org/licenses/>.
% 
% Copyright 2019, Matthias Brennwald (brennmat@gmail.com)

% init to nan values (for unknown/not-implemented values):
C_atm = NaN;
v_atm = NaN;
D = NaN;
M_mol = NaN;

if ~exist('hemisphere','var')
    hemisphere = 'global';
end % if

TKELV = T + 273.15; % Temperature in Kelvin
pATM = p_atm * 0.000986923267; % pressure in atm
mol_2_ccSTP = 22414.1; % multiply mol values by this number to get ccSTP values 
ccSTP_2_mol = 1 / mol_2_ccSTP; % multiply ccSTP values by this number to get Mol values
dens_water_S = __noble_dens (TKELV,S); % density of water with temperature T and salinity S
dens_water_0 = __noble_dens (TKELV,0); % density of fresh water with temperature T
p_water = 10.^((0.7859+0.03477*T)./(1+0.00412*T)); % water vapor pressure in hPa or mbar (Gill 1982)
p_0 = 1013.25; % reference pressure in hPa (mbar)
M_water = 18.016; % molar weight of (pure) water (g/mol)

if p_water > p_atm
    warning ( 'nf_atmos_gas_par_range' , sprintf('nf_atmos_gas.m: atmospheric pressure (%g hPa) is lower than vapour pressure (%g hPa). Pressure correction for calculation of gas concentration in water will go terribly wrong...',p_atm,p_water))
end % if

H = NaN;

switch gas

case {'He', 'He-4', 'He_4'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1010);
    D = D / 1E9;
    C_atm = C_atm ;
    if strcmp(gas,'He-4')
        M_mol = 4;
    else
        M_mol = 4.0026;
    end % if
    
case {'He-3','He_3'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1011);
    D = D / 1E9;
    M_mol = 3;
    
case {'RHe'}
    Ra = 1.384e-6;
	Req=Ra./ exp( (-0.0299645+19.8715./T-1833.92./T./T).*(1+0.000464.*S) );
    C_atm = Req;
    v_atm = Ra;
    M_mol = NaN;
    D = NaN;
    
case {'Ne'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1020);
    D = D / 1E9;
    M_mol = 20.1798;
    
case {'Ne-20','Ne_20'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1021);
    D = D / 1E9;
    M_mol = 20;
    
case {'Ne-22','Ne_22'}

    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1022);
    D = D / 1E9;
    M_mol = 22;
    
case {'Ar'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1030);
    D = D / 1E9;
    M_mol = 39.9481;
    
case {'Ar-36','Ar_36'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1031);
    D = D / 1E9;
    M_mol = 36;
    
case {'Ar-40','Ar_40'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1032);
    D = D / 1E9;
    M_mol = 40;

case {'Kr'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1040);
    D = D / 1E9;
    M_mol = 83.7982;
   
case {'Kr-78','Kr_78'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1040);
    D = D / 1E9;
    M_mol = 78;
    C_atm = C_atm * 0.003469;
    v_atm = v_atm * 0.003469;

case {'Kr-80','Kr_80'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1040);
    D = D / 1E9;
    M_mol = 80;
    C_atm = C_atm * 0.022571;
    v_atm = v_atm * 0.022571;

case {'Kr-82','Kr_82'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1040);
    D = D / 1E9;
    M_mol = 82;
    C_atm = C_atm * 0.11523;
    v_atm = v_atm * 0.11523;

case {'Kr-83','Kr_83'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1040);
    D = D / 1E9;
    M_mol = 83;
    C_atm = C_atm * 0.11477;
    v_atm = v_atm * 0.11477;

case {'Kr-84','Kr_84'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1040);
    D = D / 1E9;
    M_mol = 84;
    C_atm = C_atm * 0.5700;
    v_atm = v_atm * 0.5700;

case {'Kr-86','Kr_86'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1040);
    D = D / 1E9;
    M_mol = 86;
    C_atm = C_atm * 0.17398;
    v_atm = v_atm * 0.17398;

case {'Xe'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1050);
    D = D / 1E9;
    M_mol = 131.2936;
    
case {'Xe-124','Xe_124'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1050);
    D = D / 1E9;
    M_mol = 124;
    C_atm = C_atm * 0.000951;
    v_atm = v_atm * 0.000951;

case {'Xe-126','Xe_126'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1050);
    D = D / 1E9;
    M_mol = 126;
    C_atm = C_atm * 0.000887;
    v_atm = v_atm * 0.000887;

case {'Xe-128','Xe_128'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1050);
    D = D / 1E9;
    M_mol = 128;
    C_atm = C_atm * 0.01919;
    v_atm = v_atm * 0.01919;
    
case {'Xe-129','Xe_129'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1050);
    D = D / 1E9;
    M_mol = 129;
    C_atm = C_atm * 0.2644;
    v_atm = v_atm * 0.2644;
    
case {'Xe-130','Xe_130'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1050);
    D = D / 1E9;
    M_mol = 130;
    C_atm = C_atm * 0.04070;
    v_atm = v_atm * 0.04070;

case {'Xe-131','Xe_131'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1050);
    D = D / 1E9;
    M_mol = 131;
    C_atm = C_atm * 0.2122;
    v_atm = v_atm * 0.2122;

case {'Xe-132','Xe_132'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1050);
    D = D / 1E9;
    M_mol = 132;
    C_atm = C_atm * 0.2689;
    v_atm = v_atm * 0.2689;

case {'Xe-134','Xe_134'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1050);
    D = D / 1E9;
    M_mol = 134;
    C_atm = C_atm * 0.10430;
    v_atm = v_atm * 0.10430;
    
case {'Xe-136','Xe_136'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1050);
    D = D / 1E9;
    M_mol = 136;
    C_atm = C_atm * 0.08857;
    v_atm = v_atm * 0.08857;
    
case {'N2'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1060);
    D = D / 1E9;
    M_mol = 28.0134;    
    
case {'O2'}
    [C_atm,v_atm,D] = __solubility_noble (TKELV,S,pATM,1070);
    D = D / 1E9;
    M_mol = 31.9989;

case {'CO2'}
	warning ('nf_atmos_gas: ignoring chemical partitioning of CO2 in water!')
    C_atm = v_atm = NA; % no universal number here!
    M_mol = 44.01; % from http://en.wikipedia.org/wiki/Carbon_dioxide, 29. Feb 2016
    % Inverse Henry's Law constant, using formulae and data from review/compilation by Rolf Sander (1999), with T in Kelvin:
    %   k°H = Inverse Henry's law constant for solubility in water at 298.15 K, in (mol/L)/atm
    %   d(ln(kH))/d(1/T) = Temperature dependence constant, in K 
    %   kH(T) = k°H * exp( d(ln(kH))/d(1/T) * (1/T - 1/298.15 K) )  Inverse Henry's Law coefficient, in (mol/L)/atm
    
    kH0 = 3.4E-2;   % kH0 at 298.15 K, in (mol/L)/atm
    uT  = 2400;     % uT = ln(kH)/d(1/T) = Temperature dependence constant, in K    
    kH  = kH0 * exp( uT .* (1./TKELV - 1/298.15) ); % inverse Henry's Law coefficient in (mol/L)/atm
    H = 1./kH; % Henry's Law coefficient in atm/(mol/L)
    H = H * 1013.25 * 1000; %Henry's Law coefficient in hPa/(mol/g)
    H = H / mol_2_ccSTP; % convert from mol/g to ccSTP/g

case {'CH4'}
    C_atm = v_atm = NA; % no universal number here!
    D = NA; %%% warning ( "atmos_gas_implementation" , "atmos_gas: diffusivity of CH4 (methane) not yet implemented." )
    M_mol = 16.04; % from http://en.wikipedia.org/wiki/Methane, 9. July 2013
    % Inverse Henry's Law constant, using formulae and data from review/compilation by Rolf Sander (1999), with T in Kelvin:
    %   k°H = Inverse Henry's law constant for solubility in water at 298.15 K, in (mol/L)/atm
    %   d(ln(kH))/d(1/T) = Temperature dependence constant, in K 
    %   kH(T) = k°H * exp( d(ln(kH))/d(1/T) * (1/T - 1/298.15 K) )  Inverse Henry's Law coefficient, in (mol/L)/atm
    kH0 = mean ([ 0.0014 0.0013 0.0013 0.0014 ]);   % kH0 at 298.15 K, in (mol/L)/atm
    uT  = mean ([ 1600 1900 1800 1700 ]);           % uT = ln(kH)/d(1/T) = Temperature dependence constant, in K
    kH  = kH0 * exp( uT .* (1./TKELV - 1/298.15) ); % inverse Henry's Law coefficient in (mol/L)/atm [VALUES FROM THIS WERE CONFIRMED TO BE CONSISTENT WITH INVERSE HENRY COEFFICIENTS GIVEN HYDROSPHÄRE LECTURE NOTES BY DIETER IMBODEN FOR 0:5:25 DEG.C.]
    H = 1./kH; % Henry's Law coefficient in atm/(mol/L)
    H = H * 1013.25 * 1000; %Henry's Law coefficient in hPa/(mol/g)
    H = H / mol_2_ccSTP; % convert from mol/g to ccSTP/g

case{'C3H8'} % propane
    C_atm = v_atm = NA; % no universal number here!
    D = NA; %%% warning ( "atmos_gas_implementation" , "atmos_gas: diffusivity of C3H8 (methane) not yet implemented." )
    M_mol = 44.097; % from https://www.chemicalaid.com/tools/molarmass.php?formula=C3H8 08.05.2019
    % Inverse Henry's Law constant, using formulae and data from review/compilation by Rolf Sander (1999), with T in Kelvin:
    %   k°H = Inverse Henry's law constant for solubility in water at 298.15 K, in (mol/L)/atm
    %   d(ln(kH))/d(1/T) = Temperature dependence constant, in K 
    %   kH(T) = k°H * exp( d(ln(kH))/d(1/T) * (1/T - 1/298.15 K) )  Inverse Henry's Law coefficient, in (mol/L)/atm
    kH0 = mean ([ 0.0014 0.0015 0.0014 0.0015 0.0014 ]);   % kH0 at 298.15 K, in (mol/L)/atm
    uT  = 2700;           % uT = ln(kH)/d(1/T) = Temperature dependence constant, in K
    kH  = kH0 * exp( uT .* (1./TKELV - 1/298.15) ); % inverse Henry's Law coefficient in (mol/L)/atm
    H = 1./kH; % Henry's Law coefficient in atm/(mol/L)
    H = H * 1013.25 * 1000; % Henry's Law coefficient in hPa/(mol/g)
    H = H / mol_2_ccSTP; % convert from mol/g to ccSTP/g

case {'SF6'}
    M_mol = 146.0559;
    v_atm = __SF6_air (year,hemisphere); % volumetric fraction of SF6 in air in the year given

    % Solubility data taken from Bullister et al (2002), Deep Sea Res. I
    % Use eqn(3): ln(K') = a1 + a2*ln(100/T) + a3*ln(T/100) + S * (b1 + b2*(T/100) + b3*(T/100)^2)
    % where T is absolute temperature and S is salinity (in g/kg?)
        
    a1 = -98.7264; a2 = 142.803; a3 = 38.8746; b1 = 0.0268696; b2 = -0.0334407; b3 = 0.0070843; % values for gravimetric concentrations, taken from Tab. 2.
    %%%%%% VOLUMETRIC CONCENTRATIONS --- a1 = -96.5975; a2 = 139.883; a3 = 37.8193; b1 = 0.0310693; b2 = -0.056385; b3 = 0.00743254; % values for volumetric concentrations, taken from Tab. 2.
    
    K = exp ( a1 + a2.*(100./TKELV) + a3.*log(TKELV/100) + S.*( b1 + b2.*(TKELV/100) + b3.*(TKELV/100).^2 ) ); % in mol/kg/atm
    K = 0.35824 / 0.34916 * K; % adjust with fudge factor to make consistent with example given in Tab. 2 of Bullister (2002)
    K = K / 1013.25 / 1000; % in mol/g/hPa
    C_atm = K .* v_atm .* (p_atm-p_water);
    C_atm = C_atm * mol_2_ccSTP; % convert from mol/g to ccSTP/g

case {'CFC11', 'CFC-11'}
    M_mol = 137.3688;
    v_atm = __CFC11_air (year,hemisphere); % volumetric fraction of CFC11 in air in the year given

    % Solubility according to Warner and Weiss 1985, Deep-Sea Res. 32(12), 1485-1497:
    % (equations 8 and 9, Tab. 5) 
    A1 = -232.0411;
    A2 = 322.5546;
    A3 = 120.4956;
    A4 = -1.39165;
    B1 = -0.146531;
    B2 = 0.093621;
    B3 = -0.0160693;
    tt = A1 + A2*(100./TKELV) + A3*log(TKELV/100) + A4*(TKELV/100).^2;
    ss = S*(B1 + B2*(TKELV/100) + B3*(TKELV/100).^2);
    F = exp ( tt + ss ); % F in mol/kg/atm, 'solubility' function for moist air
    C_atm = v_atm * F; % concentration at p_atm = 1atm, in mol/kg
    C_atm = C_atm * p_atm / 1013.25 / 1000; % concentration in mol/g at pressure given
    C_atm = C_atm * mol_2_ccSTP; % convert from mol/g to ccSTP/g
    
case {'CFC12', 'CFC-12'}
    M_mol = 120.9140;
    v_atm = __CFC12_air (year,hemisphere); % volumetric fraction of CFC-12 in air in the year given
    
    % Solubility according to Warner and Weiss 1985, Deep-Sea Res. 32(12), 1485-1497:
    % (equations 8 and 9, Tab. 5) 
    A1 = -220.2120;
    A2 = 301.8695;
    A3 = 114.8533;
    A4 = -1.39165;
    B1 = -0.147718;
    B2 = 0.093175;
    B3 = -0.0157340;
    tt = A1 + A2*(100./TKELV) + A3*log(TKELV/100) + A4*(TKELV/100).^2;
    ss = S*(B1 + B2*(TKELV/100) + B3*(TKELV/100).^2);
    F = exp ( tt + ss ); % F in mol/kg/atm, 'solubility' function for moist air
    C_atm = v_atm * F; % concentration at p_atm = 1atm, in mol/kg
    C_atm = C_atm * p_atm / 1013.25 / 1000; % concentration in mol/g at pressure given
    C_atm = C_atm * mol_2_ccSTP; % convert from mol/g to ccSTP/g

case {'CFC113', 'CFC-113'}
    M_mol = 187.3764;
    v_atm = __CFC113_air (year,hemisphere); % volumetric fraction of CFC-12 in air in the year given
    
    % Solubility according to Bu and Warner 1995, Deep-Sea Res. I 42(7), 1151-1161:
    % (equations 7 and 9, Tab. 4) 
    A1 = -231.902;
    A2 = 322.915;
    A3 = 119.111;
    A4 = -1.3917;
    B1 = -0.02547;
    B2 = 0.004540;
    B3 = -0.0002708;
    tt = A1 + A2*(100./TKELV) + A3*log(TKELV/100) + A4*(TKELV/100).^2;
    ss = S*(B1 + B2*(TKELV/100) + B3*(TKELV/100).^2);
    F = exp ( tt + ss ); % F in mol/kg/atm, 'solubility' function for moist air
    C_atm = v_atm * F; % concentration at p_atm = 1atm, in mol/kg
    C_atm = C_atm * p_atm / 1013.25 / 1000; % concentration in mol/g at pressure given
    C_atm = C_atm * mol_2_ccSTP; % convert from mol/g to ccSTP/g

otherwise
    error (sprintf("nf_atmos_gas: gas %s is unknown.",gas))
end % end of switch gas


% calculate Henry's Law coefficient from partial pressure and aqueous concentration:

if isnan(H)
	H = repmat (NaN,size(C_atm));
	PA = p_atm;
	if ( length(PA) == 1 )
		PA = repmat (PA,size(H));
	end
	V = v_atm;
	if ( length(V) == 1 )
		V = repmat (V,size(H));
	end
	
	k = find ( C_atm > 0 );
	l = find ( C_atm <= 0);
	if any (k)
		H(k) = (PA(k)-p_water(k)).*V(k) ./ C_atm(k);
	end
	if any(l)
		switch gas
			case { "SF6" , "CFC11", "CFC-11" , "CFC12", "CFC-12" , "CFC113", "CFC-113" }
				if ( length(T) == 1 )
					T = repmat (T,size(H));
				end
				if ( length(S) == 1 )
					S = repmat (S,size(H));
				end
		    	[X1,X2,X3,X4,H(l)] = nf_atmos_gas (gas,T(l),S(l),PA(l),2000);
		    otherwise
		    warning ( 'nf_atmos_gas_henry_zerodivision' , sprintf('Could not calculate Henry coefficient for %s, because C_atm is zero or negative. Returning H = NaN.',gas));
	    end
	end
end

endfunction % main function



%%%%%%%%%%%%%%%%%%%%%%%%% Helper functions here:

function [c,vol,D] = __solubility_noble(T,S,pm,gas,NaCl)

% [c,vol,D]=solubility_noble(T,S,pm,gas,NaCl)
% solubility and equilibrium concentration
% from different sources
%
% INPUT
% T:    temperature of water in Kelvin
% S:    salinity in per mille (g/kg)
% pm:	pressure at saturation in atm (moist air)
% gas:	1000                    	: Weiss and S and Clever for Xe 
%          1010, 1011           	: He, 3He
%          1020, 1021, 1022     	: Ne, Ne20, Ne22
%          1030, 1031, 1032       : Ar, Ar36, Ar40
%          1040                 	: Kr
%          1050                 	: Xe 
%          1060, 1061, 1062, 1063	: N2, N2_28, N2_29, N2_30
%          1070, 1071, 1072, 1073 : O2, O2_34, O2_35, O2_36
% 		2000                    	: Clever und /Smith & Kennedy (isotope as in Weiss)
% 		3000                    	: Benson and Krause/ Smith & Kennedy
%       Isotope fractionation for Ne and Ar from Beyerle et al. 2000
% NaCl:	conc. of NaCl in mol/g
%
% OUTPUT
% c:	equilibrium concentration in ccSTP/g
% vol:	volume fraction in air (partial pressure in atm)
% D: 	molecular diffusivities [10-9 m2s-1]
%
% Written by Frank Peeters 20.2.1998; no guarantees


%%%%%%%%%%%%%%%%%%%%%%%%
Tc=(T-273.15)  ;  pw=10.^((0.7859+0.03477*Tc)./(1+0.00412*Tc))/1013.25; % saturation water vapor pressure Gill 1982
p=pm-pw; % pressure dry air

weight_water=18.016; %molar weight of water

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Weiss for He, Ne, Ar and Kr in salinity
% Clever for Xe & Smith & Kennedy
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
	
if gas==1010 % He (Weiss)
	vol=5.24e-6;	
	c=(exp(-167.2178+216.3442*(100./T)+139.2032*log(T/100)-22.6202*(T/100) + S.*(-0.044781+0.023541*(T/100)-0.0034266*(T/100).^2))).*p./(1-pw)/1000  ;  %	L=c./(p*vol*ideal_factor);
	D= 818*exp(-11700/8.3143./T);

elseif gas==1011 % He3 (Weiss)
	vol=5.24e-6;	
	c=(exp(-167.2178+216.3442*(100./T)+139.2032*log(T/100)-22.6202*(T/100) + S.*(-0.044781+0.023541*(T/100)-0.0034266*(T/100).^2))).*p./(1-pw)/1000;
	D= 818*exp(-11700/8.3143./T);
	% for He3
	Ra=1.384e-6;
	Req=Ra./ exp( (-0.0299645+19.8715./T-1833.92./T./T).*(1+0.000464.*S) );
	c=c.*Req;
	vol=vol.*Ra;
	D=D.*sqrt(4/3);
	
elseif gas==1020 % Ne (Weiss)
	vol=1.818e-5  ;  	c=(exp(-170.6018+225.1946*(100./T)+140.8863*log(T/100)-22.629*(T/100) + S.*(-0.127113+0.079277*(T/100)-0.0129095*(T/100).^2))).*p./(1-pw)/1000;
	%	L=c./(p*vol*ideal_factor)  ;
	D= 1608*exp(-14840/8.3143./T);

elseif gas==1021 % Ne20 (assume no Fractionation compared to total Ne)  ;
    RaNe20=0.9050;  % Ozima
    ReNe20=0.9050;													
	vol=1.818e-5.*RaNe20;
	c=(exp(-170.6018+225.1946*(100./T)+140.8863*log(T/100)-22.629*(T/100) + S.*(-0.127113+0.079277*(T/100)-0.0129095*(T/100).^2))).*p./(1-pw)/1000;
	c=c.*ReNe20;
	%	L=c./(p*vol*ideal_factor);
	D= 1608*exp(-14840/8.3143./T);
	
elseif gas==1022 % Ne22 (Fractionation from Beyerle et al. 2000)  ;
    RaNe22=0.092347; % Ozima ratio of 9.800  ; 
    ReNe22=0.092347*1.002;	    												
	vol=1.818e-5.*RaNe22  ;
	c=(exp(-170.6018+225.1946*(100./T)+140.8863*log(T/100)-22.629*(T/100) + S.*(-0.127113+0.079277*(T/100)-0.0129095*(T/100).^2))).*p./(1-pw)/1000;
    c=c.*ReNe22;
	%	L=c./(p*vol*ideal_factor)  ;
	D= 1608*exp(-14840/8.3143./T)*sqrt(20/22);

elseif gas==1030 % Ar (Weiss)
	vol=9.34e-3  ;  	c= (exp(-178.1725+251.8139*(100./T)+145.2337*log(T/100)+(-22.2046)*(T/100) + S.*(-0.038729+0.017171*(T/100)-0.0021281*(T/100).^2))).*p./(1-pw)/1000;
    %	L=c./(p*vol*ideal_factor)  ;
    D = 2233*exp(-16680/8.3143./T);
	 
elseif gas==1031 % Ar 36(Weiss)
    RaAr36=0.003371;
    ReAr36=0.003371*0.9987;
	vol=9.34e-3.*RaAr36  ;  	c= (exp(-178.1725+251.8139*(100./T)+145.2337*log(T/100)+(-22.2046)*(T/100) + S.*(-0.038729+0.017171*(T/100)-0.0021281*(T/100).^2))).*p./(1-pw)/1000;
	c=c.*ReAr36;
    %	L=c./(p*vol*ideal_factor)  ;
    D= 2233*exp(-16680/8.3143./T)*sqrt(40/36);

elseif gas==1032 % Ar 40 (Weiss)
	RaAr40=0.996;
	ReAr40=0.996;
	vol=9.34e-3.*RaAr40;
	c= (exp(-178.1725+251.8139*(100./T)+145.2337*log(T/100)+(-22.2046)*(T/100) + S.*(-0.038729+0.017171*(T/100)-0.0021281*(T/100).^2))).*p./(1-pw)/1000;
	c=c.*ReAr40;
    %	L=c./(p*vol*ideal_factor)  ;
	D= 2233*exp(-16680/8.3143./T);
	
elseif gas==1040 % Kr (Weiss)
	vol=1.14e-6;
	c= (exp(-112.684+153.5817*(100./T)+74.469*log(T/100)+(-10.0189)*(T/100) + S.*(-0.011213-0.001844*(T/100)+0.0011201*(T/100).^2))).*p./(1-pw)/1000;
    %	L=c./(p*vol*ideal_factor)  ;
	D = 6393 * exp (-20200/8.3143./T);
	
elseif gas==1050 || gas==2050 % Xe (Clever, Smith and Kennedy)
	[rhoS,rhoT,densr] = __noble_dens(T,S);
	if nargin==4
	   NaCl=S/58.443/1000;
	end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	vol=8.7e-8;
	XXen = exp(-74.7398+105.21*100./T+27.4664*log(T/100));
	c = XXen./(1-XXen).*22280.4/weight_water.*vol.*exp(-Cl.*(-14.1338+21.8772.*(100./T)+6.5527.*log(T/100))).*p.*densr;
	%	L=c./(p*vol*ideal_factor);
	D= 9007*exp(-21610/8.3143./T);

elseif gas==1060 || gas==2060 % N2 (Weiss)
	vol=0.78084  ;  	c= (exp(-177.0212+254.6078*(100./T)+146.3611*log(T/100)+(-22.0933)*(T/100) + S.*(-0.054052+0.027266*(T/100)-0.003843*(T/100).^2))).*p./(1-pw)/1000 ;
	%	L=c./(p*vol*1242.7);
	ScN2=1970.7-131.45.*Tc+4.1390.*Tc.*Tc-0.052106.*Tc.*Tc.*Tc; % from wanninkhof fresh water
	ScO2=1800.6-120.10.*Tc+3.7818.*Tc.*Tc-0.047608.*Tc.*Tc.*Tc; % from wanninkhof fresh water
%	ScO2=1953.4-128.00.*Tc+3.9918.*Tc.*Tc-0.050091.*Tc.*Tc.*Tc; % from wanninkhof salt water
	DO2= 8869*exp(-20410/8.3143./T); % Himmelblau 1964
	D=DO2.*ScO2./ScN2;               % since Sc = nu /D

elseif gas==1061 || gas==2061 % N2 28 (Weiss)  ;  RaN228=0.9963*0.9963;  ;  ReN228=0.9963*0.9963  ;  
	vol=0.78084.*RaN228;
	c= (exp(-177.0212+254.6078*(100./T)+146.3611*log(T/100)+(-22.0933)*(T/100) + S.*(-0.054052+0.027266*(T/100)-0.003843*(T/100).^2))).*p./(1-pw)/1000;
	c=c.*ReN228;
	%	L=c./(p*vol*1242.7);
	ScN2=1970.7-131.45.*Tc+4.1390.*Tc.*Tc-0.052106.*Tc.*Tc.*Tc; % from wanninkhof fresh water
	ScO2=1800.6-120.10.*Tc+3.7818.*Tc.*Tc-0.047608.*Tc.*Tc.*Tc; % from wanninkhof fresh water
%	ScO2=1953.4-128.00.*Tc+3.9918.*Tc.*Tc-0.050091.*Tc.*Tc.*Tc; % from wanninkhof salt water
	DO2= 8869*exp(-20410/8.3143./T); % Himmelblau 1964
	D=DO2.*ScO2./ScN2;               % since Sc = nu /D

elseif gas==1062 || gas==2062 % N2 29 (Weiss)  ;  RaN229=2*0.0037*0.9963;  ;  ReN229=2*0.0037*0.9963  ;  
	vol=0.78084.*RaN229;
	c= (exp(-177.0212+254.6078*(100./T)+146.3611*log(T/100)+(-22.0933)*(T/100) + S.*(-0.054052+0.027266*(T/100)-0.003843*(T/100).^2))).*p./(1-pw)/1000;
	c=c.*ReN229;
	%	L=c./(p*vol*1242.7);
	ScN2=1970.7-131.45.*Tc+4.1390.*Tc.*Tc-0.052106.*Tc.*Tc.*Tc; % from wanninkhof fresh water 
	ScO2=1800.6-120.10.*Tc+3.7818.*Tc.*Tc-0.047608.*Tc.*Tc.*Tc; % from wanninkhof fresh water
%    ScO2=1953.4-128.00.*Tc+3.9918.*Tc.*Tc-0.050091.*Tc.*Tc.*Tc; % from wanninkhof salt water
    DO2= 8869*exp(-20410/8.3143./T); % Himmelblau 1964
    D=DO2.*ScO2./ScN2;               % since Sc = nu /D  ;
    D=D.*sqrt(28/29);

elseif gas==1063 || gas==2063 % N2 30 (Weiss)
    RaN230=0.0037*0.0037;
    ReN230=0.0037*0.0037;
	vol=0.78084.*RaN230;
	c= (exp(-177.0212+254.6078*(100./T)+146.3611*log(T/100)+(-22.0933)*(T/100) + S.*(-0.054052+0.027266*(T/100)-0.003843*(T/100).^2))).*p./(1-pw)/1000;
	c=c.*ReN230;  %	L=c./(p*vol*1242.7);
	ScN2=1970.7-131.45.*Tc+4.1390.*Tc.*Tc-0.052106.*Tc.*Tc.*Tc; % from wanninkhof fresh water
	ScO2=1800.6-120.10.*Tc+3.7818.*Tc.*Tc-0.047608.*Tc.*Tc.*Tc; % from wanninkhof fresh water
%    ScO2=1953.4-128.00.*Tc+3.9918.*Tc.*Tc-0.050091.*Tc.*Tc.*Tc; % from wanninkhof salt water
    DO2= 8869*exp(-20410/8.3143./T); % Himmelblau 1964
    D=DO2.*ScO2./ScN2;               % since Sc = nu /D  ;
    D=D.*sqrt(28/30)  ;  

elseif gas==1070 || gas==2070% O2 (Weiss)
	vol=0.209476;
	c= (exp(-177.7888+255.5907*(100./T)+146.4813*log(T/100)+(-22.204)*(T/100) + S.*(-0.037362+0.016504*(T/100)-0.0020564*(T/100).^2))).*p./(1-pw)/1000  ;  %	L=c./(p*vol*1242.7)  ;
	D= 8869*exp(-20410/8.3143./T); % Himmelblau 1964

elseif gas==1071 || gas==2071% O2 32(Weiss)
    RaO232=0.99762*0.99762;
    ReO232=0.99762*0.99762;
    vol=0.209476*RaO232;
    c= (exp(-177.7888+255.5907*(100./T)+146.4813*log(T/100)+(-22.204)*(T/100) + S.*(-0.037362+0.016504*(T/100)-0.0020564*(T/100).^2))).*p./(1-pw)/1000;
    c=c*ReO232;
    %	L=c./(p*vol*1242.7);
    D= 8869*exp(-20410/8.3143./T); % Himmelblau 1964

elseif gas==1072 || gas==2072% O2 34(Weiss)
    RaO234=2*0.002*0.99762;
    ReO234=2*0.002*0.99762*(1+(-0.73+427./T)/1000); % Fractionation from Benson 1984
	vol=0.209476*RaO234;
	c= (exp(-177.7888+255.5907*(100./T)+146.4813*log(T/100)+(-22.204)*(T/100) + S.*(-0.037362+0.016504*(T/100)-0.0020564*(T/100).^2))).*p./(1-pw)/1000;
	c=c*ReO234;  
%	L=c./(p*vol*1242.7)
    D= 8869*exp(-20410/8.3143./T); % Himmelblau 1964
    D=D.*sqrt(32/34);

elseif gas==1073 || gas==2073% O2 36(Weiss)
    RaO234=0.002*0.002;
    ReO234=0.002*0.002;
	vol=0.209476*RaO234;
	c = (exp(-177.7888+255.5907*(100./T)+146.4813*log(T/100)+(-22.204)*(T/100) + S.*(-0.037362+0.016504*(T/100)-0.0020564*(T/100).^2))).*p./(1-pw)/1000;
	c=c*ReO234;
	%	L=c./(p*vol*1242.7)  ;
	D= 8869*exp(-20410/8.3143./T); % Himmelblau 1964
	D=D.*sqrt(32/36);
	

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Clever He Ne Ar and Kr using chlorinity from Smith & Kennedy; 
% 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

elseif gas==2010 % He (Clever , Smith and Kennedy
	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	vol=5.24e-6;	
	XHe = exp(-41.4611+42.5962*100./T+14.0094*log(T/100))  ;  	c = XHe./(1-XHe).*22436.4/weight_water.*vol...
		.*exp(-Cl.*(-9.6723+14.4725.*(100./T)+4.6188.*log(T/100))).*p.*densr  ;  %	L=c./(p*vol*ideal_factor)  ;  	D= 818*exp(-11700/8.3143./T)  ;  	
elseif gas==2011 % He3

	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	vol=5.24e-6;	
	XHe = exp(-41.4611+42.5962*100./T+14.0094*log(T/100))  ;  	c = XHe./(1-XHe).*22436.4/weight_water.*vol...
		.*exp(-Cl.*(-9.6723+14.4725.*(100./T)+4.6188.*log(T/100))).*p.*densr  ;  %	L=c./(p*vol*ideal_factor)  ;  	D= 818*exp(-11700/8.3143./T)  ;  
	% for He3
	Ra=1.384e-6  ;  	Req=Ra./ exp( (-0.0299645+19.8715./T-1833.92./T./T).*(1+0.000464.*S) )  ;  	c=c.*Req  ;  	vol=vol.*Ra  ;  	D=D.*sqrt(4/3)  ;  
elseif gas==2020 % Ne (Clever, Smith and Kennedy)
	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	vol=1.818e-5  ;  	XNe = exp(-52.8573+61.0494*100./T+18.9157*log(T/100))  ;  	c = XNe./(1-XNe).*22421.7/weight_water.*vol...
		.*exp(-Cl.*(-11.5250+17.7408.*(100./T)+5.3421.*log(T/100))).*p.*densr  ;  %	L=c./(p*vol*ideal_factor)  ;  	D= 1608*exp(-14840/8.3143./T)  ;  
elseif gas==2021 % Ne20 (Clever, Smith and Kennedy, Fractionation Beyerle et al 2000)									!!  ;  RaNe20=0.9050;  % Ozima  ;  
ReNe20=0.9050;													
	vol=1.818e-5.*RaNe20  ;  
	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	XNe = exp(-52.8573+61.0494*100./T+18.9157*log(T/100))  ;  	c = XNe./(1-XNe).*22421.7/weight_water.*vol...
		.*exp(-Cl.*(-11.5250+17.7408.*(100./T)+5.3421.*log(T/100))).*p.*densr;  ;  c=c.*ReNe20  ;  %	L=c./(p*vol*ideal_factor)  ;  	D= 1608*exp(-14840/8.3143./T)  ;  
elseif gas==2022 % Ne22 (Clever, Smith and Kennedy, Fractionation Beyerle et al 2000)									!!  ;  RaNe22=0.092347; % Ozima ratio of 9.800  ;  ReNe22=0.092347*1.002;													
	vol=1.818e-5.*RaNe22  ;  
	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	XNe = exp(-52.8573+61.0494*100./T+18.9157*log(T/100))  ;  	c = XNe./(1-XNe).*22421.7/weight_water.*vol...
		.*exp(-Cl.*(-11.5250+17.7408.*(100./T)+5.3421.*log(T/100))).*p.*densr;  ;  c=c.*ReNe22  ;  %	L=c./(p*vol*ideal_factor)  ;  	D= 1608*exp(-14840/8.3143./T)*sqrt(20/22)  ;  	
elseif gas==2030 % Ar (Clever, Smith and Kennedy)
	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	vol=9.34e-3  ;  	XAr = exp(-57.6661+74.7627*100./T+20.1398*log(T/100))  ;  	c = XAr./(1-XAr).*22386.5/weight_water.*vol...
		.*exp(-Cl.*(-10.2710+16.0950.*(100./T)+4.7539.*log(T/100))).*p.*densr  ;  %	L=c./(p*vol*ideal_factor)  ;  	D= 2233*exp(-16680/8.3143./T)  ;  	
elseif gas==2031 % 36Ar (Clever, Smith and Kennedy)								36!
	RaAr36=0.003371  ;  	ReAr36=0.003371*0.9987  ;  	vol=9.34e-3.*RaAr36  ;  	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	XAr = exp(-57.6661+74.7627*100./T+20.1398*log(T/100))  ;  	c = XAr./(1-XAr).*22386.5/weight_water.*vol...
		.*exp(-Cl.*(-10.2710+16.0950.*(100./T)+4.7539.*log(T/100))).*p.*densr;  ;  c=c.*ReAr36  ;  %	L=c./(p*vol*ideal_factor)  ;  	D= 2233*exp(-16680/8.3143./T)*sqrt(40/36)  ;  
elseif gas==2032 % 40Ar (Clever, Smith and Kennedy)								36!
	RaAr40=0.996  ;  	ReAr40=0.996  ;  	vol=9.34e-3.*RaAr40  ;  	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	XAr = exp(-57.6661+74.7627*100./T+20.1398*log(T/100))  ;  	c = XAr./(1-XAr).*22386.5/weight_water.*vol...
		.*exp(-Cl.*(-10.2710+16.0950.*(100./T)+4.7539.*log(T/100))).*p.*densr;  ;  c=c.*ReAr40  ;  %	L=c./(p*vol*ideal_factor)  ;  	D= 2233*exp(-16680/8.3143./T)  ;  		
elseif gas==2040 % Kr (Clever Smith and Kennedy)
	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	vol=1.14e-6  ;  	XKr = exp(-66.9928+91.0166*100./T+24.2207*log(T/100))  ;  	c = XKr./(1-XKr).*22351.2/weight_water.*vol...
		.*exp(-Cl.*(-9.5534+15.1039.*(100./T)+4.4164.*log(T/100))).*p.*densr  ;  %	L=c./(p*vol*ideal_factor)  ;  	D= 6393*exp(-20200/8.3143./T)  ;  % Xenon see 1050 (2050 is included there)


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Benson and Krause	and Smith & Kennedy
% note: pressure must be for dry air !!! Therefore correction of p.	 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

elseif gas==3010 % He
	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	vol=5.24e-6; a0=-5.0746; a1=-4127.8; a2=627250; 
	L=exp(a0+a1./T+a2./T./T); 
	c=L./(1-L).*vol.*p.*22436.4/weight_water  ;  	c=c.*exp(-Cl.*(-9.6723+14.4725.*(100./T)+4.6188.*log(T/100))).*densr; % salt efffect according to clever expressed in Cl (NaCl)
	D= 818*exp(-11700/8.3143./T)  ;  	
elseif gas==3011 % He3
	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	vol=5.24e-6; a0=-5.0746; a1=-4127.8; a2=627250; 
	L=exp(a0+a1./T+a2./T./T); 
	c=L./(1-L).*vol.*p.*22436.4/weight_water  ;  	c=c.*exp(-Cl.*(-9.6723+14.4725.*(100./T)+4.6188.*log(T/100))).*densr; % salt efffect according to clever expressed in Cl (NaCl)
	D= 818*exp(-11700/8.3143./T)  ;  	% for He3
	Ra=1.384e-6  ;  	Req=Ra./ exp( (-0.0299645+19.8715./T-1833.92./T./T).*(1+0.000464.*S) )  ;  	c=c.*Req  ;  	vol=vol.*Ra  ;  	D=D.*sqrt(4/3)  ;  	
elseif gas==3020 % Ne
	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	vol=1.818e-5; a0=-4.2988; a1=-4871.1; a2=793580; 
	L=exp(a0+a1./T+a2./T./T); 
	c=L./(1-L).*vol.*p.*22421.7/weight_water  ;  	c=c.*exp(-Cl.*(-11.5250+17.7408.*(100./T)+5.3421.*log(T/100))).*densr; % salt efffect according to clever expressed in Cl (NaCl)
	D= 1608*exp(-14840/8.3143./T)  ;  
elseif gas==3021 % Ne20													!!  ;  
RaNe20=0.9050;  % Ozima  ;  
ReNe20=0.9050;													
	vol=1.818e-5.*RaNe20  ;  
	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	a0=-4.2988; a1=-4871.1; a2=793580; 
	L=exp(a0+a1./T+a2./T./T); 
	c=L./(1-L).*vol.*p.*22421.7/weight_water  ;  	c=c.*exp(-Cl.*(-11.5250+17.7408.*(100./T)+5.3421.*log(T/100))).*densr; % salt efffect according to clever expressed in Cl (NaCl)  ;  c=c.*ReNe20  ;  	D= 1608*exp(-14840/8.3143./T)  ;  	
elseif gas==3022 % Ne															!!  ;  RaNe22=0.092347; % Ozima ratio of 9.800  ;  ReNe22=0.092347*1.002;													
	vol=1.818e-5.*RaNe22  ;  
	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	a0=-4.2988; a1=-4871.1; a2=793580; 
	L=exp(a0+a1./T+a2./T./T); 
	c=L./(1-L).*vol.*p.*22421.7/weight_water  ;  	c=c.*exp(-Cl.*(-11.5250+17.7408.*(100./T)+5.3421.*log(T/100))).*densr; % salt efffect according to clever expressed in Cl (NaCl)  ;  c=c.*ReNe22  ;  	D= 1608*exp(-14840/8.3143./T)*sqrt(20/22)  ;  	
elseif gas==3030 % Ar
	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	vol=9.34e-3; a0=-4.2123; a1=-5239.6; a2=995240; 
	L=exp(a0+a1./T+a2./T./T); 
	c=L./(1-L).*vol.*p.*22386.5/weight_water  ;  	c=c.*exp(-Cl.*(-10.2710+16.0950.*(100./T)+4.7539.*log(T/100))).*densr;  % salt effect according to clever expressed in Cl (NaCl)
	D= 2233*exp(-16680/8.3143./T)  ;  	
elseif gas==3031 % Ar36
	RaAr36=0.003371  ;  	ReAr36=0.003371*0.9987  ;  	vol=9.34e-3.*RaAr36  ;  	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	a0=-4.2123; a1=-5239.6; a2=995240; 
	L=exp(a0+a1./T+a2./T./T); 
	c=L./(1-L).*vol.*p.*22386.5/weight_water  ;  	c=c.*exp(-Cl.*(-10.2710+16.0950.*(100./T)+4.7539.*log(T/100))).*densr;  % salt effect according to clever expressed in Cl (NaCl)  ;  c=c.*ReAr36;	  ;  D= 2233*exp(-16680/8.3143./T)*sqrt(40/36)  ;  
elseif gas==3032 % Ar40
	RaAr40=0.996  ;  	ReAr40=0.996  ;  	vol=9.34e-3.*RaAr40  ;  	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	a0=-4.2123; a1=-5239.6; a2=995240; 
	L=exp(a0+a1./T+a2./T./T); 
	c=L./(1-L).*vol.*p.*22386.5/weight_water  ;  	c=c.*exp(-Cl.*(-10.2710+16.0950.*(100./T)+4.7539.*log(T/100))).*densr;  % salt effect according to clever expressed in Cl (NaCl)  ;  c=c.*ReAr40;	  ;  D= 2233*exp(-16680/8.3143./T)  ;  
elseif gas==3040 % Kr
	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	vol=1.14e-6; a0=-3.6326; a1=-5664.0; a2=1122400; 
	L=exp(a0+a1./T+a2./T./T); 
	c=L./(1-L).*vol.*p.*22351.2/weight_water  ;  	c=c.*exp(-Cl.*(-9.5534+15.1039.*(100./T)+4.4164.*log(T/100))).*densr; % salt effect according to clever expressed in Cl (NaCl)
	D= 6393*exp(-20200/8.3143./T)  ;  	
elseif gas==3050 % Xe
	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy
	vol=8.7e-8; a0=-2.0917; a1=-6693.5; a2=1341700; 
	L=exp(a0+a1./T+a2./T./T); 
	c=L./(1-L).*vol.*p.*22280.4/weight_water  ;  	c=c.*exp(-Cl.*(-14.1338+21.8772.*(100./T)+6.5527.*log(T/100))).*densr; % salt effect according to clever expressed in Cl (NaCl)
	D= 9007*exp(-21610/8.3143./T)  ;  	
elseif gas==3060 % N2                             ;  disp('N2 from benson Krause: !!! here are still things missing dontt use')
	[rhoS,rhoT,densr] = __noble_dens(T,S); 
	if nargin==4, NaCl=S/58.443/1000; end
	Cl=NaCl.*rhoS; % NaCl in g/l and density ratio for Smith and Kennedy

	ideal_gas=mol_2_ccSTP; % molar volume in cc/mol  ;  ideal_factor=ideal_gas/weight_water;	
	vol=0.78084; a0=-4.3338; a1=-5485.7; a2=1010800;   ;  L=exp(a0+a1./T+a2./T./T); 
	c=L.*vol.*p.*ideal_factor  ;    ;  Sc=1970.7-131.45.*T+4.1390.*T.*T-0.052106.*T.*T.*T;  ;  dyn_visc=dyn_viscosity(Tc);  ;  D=Sc./dyn_visc.*rhoT  ;  
elseif gas==3070 % O2  ;  disp('O2 from benson Krause: !!! here are still things missing dontt use')

	ideal_gas=mol_2_ccSTP; % molar volume in cc/mol
	ideal_factor=ideal_gas/weight_water  ;  	vol=0.20948; a0=-4.0605; a1=-5416.7; a2=1026100; L=exp(a0+a1./T+a2./T./T); 
	c=L.*vol.*p.*ideal_factor  ;  else
	error(['gas ',int2str(gas),' is not in list or typing error'])
end

endfunction % function [c,vol,D] = __solubility_noble(T,S,pm,gas,NaCl)


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [rhotot,rho0T,densr] = __noble_dens(T,s);
% T in K
% S g/kg
% density in g/L, nach Unesco or Gill 1982; no pressure

index=s<0  ;  s(index)=zeros(size(s(index)));	% for negative s set density to density with s=0  ;  
t=T-273.15  ;  

a(1,:)=[999.842594,8.244930E-01,-5.724660E-03,4.831400E-04]  ;  a(2,:)=[6.793952E-02,-4.089900E-03,1.022700E-04,0]  ;  a(3,:)=[-9.095290E-03,7.643800E-05,-1.654600E-06,0]  ;  a(4,:)=[1.001685E-04,-8.246700E-07,0,0]  ;  a(5,:)=[-1.120083E-06,5.387500E-09,0,0]  ;  a(6,:)=[6.536332E-09,0,0,0]  ;  


T1=t; T2=T1.*t; T3=T2.*t; T4=T3.*t; T5=T4.*t  ;  S1=s; S2=s.^(3/2); S3=s.*s  ;  
rho0T=a(1,1)+a(2,1).*T1+a(3,1).*T2+a(4,1).*T3+a(5,1).*T4+a(6,1).*T5  ;  rho0TS1=(a(1,2)+a(2,2).*T1+a(3,2).*T2+a(4,2).*T3+a(5,2).*T4).*S1  ;  rho0TS2=(a(1,3)+a(2,3).*T1+a(3,3).*T2).*S2  ;  rho0TS3=(a(1,4)).*S3  ;  rhotot=rho0T+rho0TS1+rho0TS2+rho0TS3  ;  
densr=rho0T./rhotot  ;  
endfunction % function [rhotot,rho0T,densr] = __noble_dens(T,s);


function v = __SF6_air (year,hemisphere); % returns the SF6 concentration in air (vol/vol) as a function of year (1975.0 corresponds to 1. Jan 1975)

% load input data:
W = warning ('query','Octave:load-file-in-path'); warning ('off','Octave:load-file-in-path');
u = load ('SF6_ATMOS_HISTORY.TXT'); 
warning (W.state,'Octave:load-file-in-path');

t = u(:,1);
switch hemisphere % select output according to hemisphere:
    case "global"
        k = 4;
    case "north"
        k = 2;
    case "south"
        k = 3;
end % switch

% i = find (~isnan(v));
% t = t(i); v = v(i);

v = repmat(NaN,size(year));

if any (i = find(year < min(t)))
    warning ( 'nf_atmos_gas_timerange' , sprintf('SF6 concentration in atmosphere not known before year %.1f. Using the %.1f value...',min(t),min(t)))
    v(i) = u(1,k);
end
if any (i = find(year > max(t)))
    warning ( 'nf_atmos_gas_timerange' , sprintf('SF6 concentration in atmosphere not known after year %.1f. Using NaN...',max(t)))
    v(i) = NaN;
end
if any (i = find( year >= min(t)  &  year <= max(t) ))
    v(i) = interp1 (t,u(:,k),year(i));
end % if

endfunction % function v = __SF6_air (year,hemisphere);



function v = __CFC11_air (year,hemisphere); % returns the CFC11 concentration in air (vol/vol) as a function of year (1975.0 corresponds to 1. Jan 1975)

% load input data:
W = warning ('query','Octave:load-file-in-path'); warning ('off','Octave:load-file-in-path');
u = load ('CFC11_ATMOS_HISTORY.TXT'); 
warning (W.state,'Octave:load-file-in-path');

t = u(:,1);
switch hemisphere % select output according to hemisphere:
    case "global"
        k = 4;
    case "north"
        k = 2;
    case "south"
        k = 3;
end % switch

% i = find (~isnan(v));
% t = t(i); v = v(i);

v = repmat(NaN,size(year));

if any (i = find(year < min(t)))
    warning ( 'nf_atmos_gas_timerange' , sprintf('CFC11 concentration in atmosphere not known before year %.1f. Using the %.1f value...',min(t),min(t)))
    v(i) = u(1,k);
end
if any (i = find(year > max(t)))
    warning ( 'nf_atmos_gas_timerange' , sprintf('CFC11 concentration in atmosphere not known after year %.1f. Using NaN...',max(t)))
    v(i) = NaN;
end
if any (i = find( year >= min(t)  &  year <= max(t) ))
    v(i) = interp1 (t,u(:,k),year(i));
end % if

endfunction % function v = __CFC11_air (year,hemisphere);




function v = __CFC12_air (year,hemisphere); % returns the CFC12 concentration in air (vol/vol) as a function of year (1975.0 corresponds to 1. Jan 1975)

% load input data:
W = warning ('query','Octave:load-file-in-path'); warning ('off','Octave:load-file-in-path');
u = load ('CFC12_ATMOS_HISTORY.TXT');
warning (W.state,'Octave:load-file-in-path');

t = u(:,1);
switch hemisphere % select output according to hemisphere:
    case "global"
        k = 4;
    case "north"
        k = 2;
    case "south"
        k = 3;
end % switch

% i = find (~isnan(v));
% t = t(i); v = v(i);

v = repmat(NaN,size(year));

if any (i = find(year < min(t)))
    warning ( 'nf_atmos_gas_timerange' , sprintf('CFC12 concentration in atmosphere not known before year %.1f. Using the %.1f value...',min(t),min(t)))
    v(i) = u(1,k);
end
if any (i = find(year > max(t)))
    warning ( 'nf_atmos_gas_timerange' , sprintf('CFC12 concentration in atmosphere not known after year %.1f. Using NaN...',max(t)))
    v(i) = NaN;
end
if any (i = find( year >= min(t)  &  year <= max(t) ))
    v(i) = interp1 (t,u(:,k),year(i));
end % if

endfunction % function v = __CFC12_air (year,hemisphere);



function v = __CFC113_air (year,hemisphere); % returns the CFC113 concentration in air (vol/vol) as a function of year (1975.0 corresponds to 1. Jan 1975)

% load input data:
W = warning ('query','Octave:load-file-in-path'); warning ('off','Octave:load-file-in-path');
u = load ('CFC113_ATMOS_HISTORY.TXT');
warning (W.state,'Octave:load-file-in-path');

t = u(:,1);
switch hemisphere % select output according to hemisphere:
    case "global"
        k = 4;
    case "north"
        k = 2;
    case "south"
        k = 3;
end % switch

% i = find (~isnan(v));
% t = t(i); v = v(i);

v = repmat(NaN,size(year));

if any (i = find(year < min(t)))
    warning ( 'nf_atmos_gas_timerange' , sprintf('CFC113 concentration in atmosphere not known before year %.1f. Using the %.1f value...',min(t),min(t)))
    v(i) = u(1,k);
end
if any (i = find(year > max(t)))
    warning ( 'nf_atmos_gas_timerange' , sprintf('CFC113 concentration in atmosphere not known after year %.1f. Using NaN...',max(t)))
    v(i) = NaN;
end
if any (i = find( year >= min(t)  &  year <= max(t) ))
    v(i) = interp1 (t,u(:,k),year(i));
end % if

endfunction % function v = __CFC113_air (year,hemisphere);
