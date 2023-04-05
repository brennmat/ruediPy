function [P_val,P_err,SPECIES,SAMPLES,TIME] = rP_calibrate_batch(data,MS_names,SENSOR_names,varargin)

% function [P_val,P_err,SPECIES,SAMPLES,TIME] = rP_calibrate_batch (data,MS_names,SENSOR_names,varargin)
% 
% Calibrate a batch of ruediPy analysis steps by combining data from samples, calibrations, and blanks. Write results to CSV data file.
% Note that even if data from a total gas pressure sensor is available, the partial pressures are NOT normalised to the total gas pressure. 
%
% INPUT:
% data: files to be processed (string with file/path pattern)
% MS_names: names / labels of mass spectrometers for which data should be processed (cellstring). Use MS_names = {} to automatically use the data from all RGA MS objects (if any).
% SENSOR_names: names / labels of sensors (e.g., pressure, temperature, etc.) for which data should be processed (cellstring). Use MS_names = {} to automatically use the data from all SENSOR objects (if any).
%
% Optinal INPUTS:
%	- 'digest_method',MZ_DET,M: method to use for digesting peak-height data from mass spectrometer. MZ_DET and M are strings (for single item) or cellstring (for multiple items). Available methods are M = 'MEAN' and M = 'MEDIAN'. If not specified, MEAN is used by default. See example below.
%	- 'no_peak_zero_plot': don't plot PEAK and ZERO values
%	- 'no_sensitivity_plot': don't plot sensitivities
%	- 'no_partialpressure_plot': don't plot partial pressures
%	- 'no_plots','noplots': don't plot anything
%	- 'standardgas_pressure',X,unit: use this gas inlet pressure for all standard analyses (X: number, unit: string)
%	- 'wait_exit': wait for key press by user before exiting this function (useful for interactive use from shell scripts)
%	- 'output_file': file name to use for writing results. If not specified, the code will ask for a file name.
%	- 'use_zenity': use Zenity/GUI to ask stuff from user instead of command-line terminal.
% 
% OUTPUT:
% P_val: partial pressures of samples (matrix)
% P_err: uncertainties of partial pressures, taking into account ONLY the counting statistics of the data, not the overall reproducibility of the measurements (matrix)
% SPECIES: species names (cell string)
% SAMPLES: sample names (cell string)
% TIME: sample time stamps (epoch times as returned by rP_digest_RGA_SRS_step) (matrix)
%
% EXAMPLE 1:
% process data in *.txt files stored in 'mydata' directory, automatically detect names of RGA/MS and SENSOR objects in the data set, assume 970 hPa inlet pressure for all standard analyses:
% > [P_val,P_err,SPECIES,SAMPLES,TIME] = rP_calibrate_batch ("mydata/*.txt",{},{},"standardgas_pressure",970,"hPa")
%
% EXAMPLE 2:
% Similar to above, but only process data from ruediMS (RGA object) and T_sens (SENSOR object), don't plot PEAK and ZERO data, and assume 970 hPa inlet pressure for all standard analyses:
% > [P_val,P_err,SPECIES,SAMPLES,TIME] = rP_calibrate_batch ("mydata/*.txt","ruediMS","T_sens","no_peak_zero_plot","standardgas_pressure",970,"hPa")
%
% EXAMPLE 3:
% Similar to EXAMPLE 1, but use MEDIAN peak hights instead of MEAN for CH4 (m/z=15) and Kr (m/z=84) measured on M detector:
% > [P_val,P_err,SPECIES,SAMPLES,TIME] = rP_calibrate_batch ("mydata/*.txt",{},{},"standardgas_pressure",970,"hPa","digest_method",{"15_M","84_M"},{"MEDIAN","MEDIAN"})
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
% Copyright 2016, Matthias Brennwald (brennmat@gmail.com)



% ************************************
% ************************************
% main function:
% ************************************
% ************************************



% option defaults (plotting etc.):
digest_mz_det = {};
digest_meth = {};
flag_plot_peak_zero = true;
flag_plot_sensitivity = true;
flag_plot_partialpressure = true;
MS = 12; % default marker size
standardgas_pressure_val = NA;
standardgas_pressure_unit = '?';
wait_exit = false;
out_file_name = '';
use_zenity = false;

% parse options:
i = 0;
while i < length(varargin) % parse options
	i = i+1;
	switch tolower(varargin{i})
	
		% plotting options:
		case 'no_peak_zero_plot'
			flag_plot_peak_zero = false;
			disp ('rP_calibrate_batch: plotting of PEAK and ZERO data turned off.')
		case 'no_sensitivity_plot'
			flag_plot_peak_zero = false;
			disp ('rP_calibrate_batch: plotting of sensitivities turned off.')
		case 'no_partialpressure_plot'
			flag_plot_partialpressure = false;
			disp ('rP_calibrate_batch: plotting of partialpressures turned off.')
		case {'no_plots','noplots'}
			flag_plot_peak_zero = false;
			flag_plot_sensitivity = false;
			flag_plot_partialpressure = false;
			disp ('rP_calibrate_batch: plotting turned off.')
		
		% digest methods:
		case 'digest_method'
			digest_mz_det = varargin{i+1};
			digest_meth   = toupper ( varargin{i+2} );
			i = i+2;
			if ~iscell(digest_mz_det)
				digest_mz_det = cellstr (digest_mz_det);
			end
			if ~iscell(digest_meth)
				digest_meth = cellstr (digest_meth);
			end
			if length(digest_mz_det) ~= length(digest_meth)
				error ('rP_calibrate_batch: length of cell strings used to specify digest methods (mz_det and method strings) must be the same!')
			end

		% other options:
		case 'standardgas_pressure'
			standardgas_pressure_val = varargin{i+1};
			standardgas_pressure_unit = varargin{i+2};
			i = i+2;
			disp (sprintf('rP_calibrate_batch: using %g %s as inlet pressure for all STANDARDs.',standardgas_pressure_val,standardgas_pressure_unit))

		case 'output_file'
			out_file_name = varargin{i+1};
			i = i+1;

		case 'use_zenity'
			% disp ('rP_calibrate_batch: using Zenity/GUI for user interaction.')
			use_zenity = true;

		case 'wait_exit'
			disp ('rP_calibrate_batch: will wait for user confirmation after completion.')
			wait_exit = true;
		
		otherwise
			warning (sprintf("rP_calibrate_batch: unknown option '%s'. Ignoring...",varargin{i}))
	end
end


% ************************************
% Load and digest raw data from files:
% ************************************

% load raw data from files:
RAW = rP_read_datafile (data);

% remove any non-SAMPLE/STANDARD/BLANK steps:
k = [];
N_SMPL = N_STD = N_BLNK = 0;
for i = 1:length(RAW)

	if strcmp(upper(RAW{i}.DATAFILE.ANALYSISTYPE.type),'SAMPLE')
		N_SMPL += 1;
		k = [k, i];

	elseif strcmp(upper(RAW{i}.DATAFILE.ANALYSISTYPE.type),'STANDARD')
		N_STD += 1;
		k = [k, i];

	elseif strcmp(upper(RAW{i}.DATAFILE.ANALYSISTYPE.type),'BLANK')
		N_BLNK += 1;
		k = [k, i];

	else
		warning ("rP_calibrate_batch: file %s contains no SAMPLE, STANDARD or BLANK data. Skipping this file...", RAW{i}.file)

	end
end
if N_SMPL == 0
	error ("rP_calibrate_batch: dataset contains no SAMPLE data. Cannot continue.")
elseif N_STD == 0
	error ("rP_calibrate_batch: dataset contains no STANDARD data. Cannot continue.")
elseif N_BLNK == 0
	error ("rP_calibrate_batch: dataset contains no BLANK data. Cannot continue.")
else
	RAW = RAW(k);
end

% check if MS names are given explicitly, otherwise determine from data set:
if exist ('MS_names','var')
	if ~iscellstr(MS_names)
		MS_names = cellstr (MS_names);
	end
else
	MS_names = {};
end
if isempty(MS_names)
	disp ('Scanning for RGA objects...')
	MS_names = {};
	for i = 1:length(RAW)
		if any( k = find(strcmp(RAW{i}.fieldtypes,'RGA_SRS')) )
			MS_names{end+1} = fieldnames (RAW{i}){k};
		end
	end
	MS_names = unique (MS_names);
	if length (MS_names) == 0
		disp ('...no RGA objects found.')
	else
		for i = 1:length(MS_names)
			disp (sprintf('Found RGA object: %s',MS_names{i}))
		end
	end
end


% check if SENSOR names are given explicitly, otherwise determine from data set:
if exist ('SENSOR_names','var')
	if ~iscellstr(SENSOR_names)
		SENSOR_names = cellstr (SENSOR_names);
	end
else
	SENSOR_names = {};
end
if isempty(SENSOR_names)
	disp ('Scanning for SENSOR objects...')
	SENSOR_names = {};
	for i = 1:length(RAW)
		if any( k = find(strcmp(RAW{i}.fieldtypes,'TEMPERATURESENSOR')) )
			SENSOR_names{end+1} = fieldnames (RAW{i}){k};
		end
		if any( k = find(strcmp(RAW{i}.fieldtypes,'PRESSURESENSOR')) )
			SENSOR_names{end+1} = fieldnames (RAW{i}){k};
		end
	end
	SENSOR_names = unique (SENSOR_names);
	if length (SENSOR_names) == 0
		disp ('...no SENSOR objects found.')
	else
		for i = 1:length(SENSOR_names)
			disp (sprintf('Found SENSOR object: %s',SENSOR_names{i}))
		end
	end
end


% digest data and store results in array (X):
X = [];
for i = 1:length(RAW)

	disp (sprintf('rP_calibrate_batch: parsing file %s...',RAW{i}.file))

	info = rP_digest_step_DATAFILEINFO(RAW{i});

	ms = {};
	sens = {};

	% digest MS data (abort if not available):
	for k = 1:length(MS_names)
		u = rP_digest_step_RGA_SRS (RAW{i},MS_names{k}); % digest RGA_SRS data
		if ~isempty(u.mean) % only keep data if digesting was successful
			ms{length(ms)+1} = u;
		end
	end
	if length(ms) > 1
		warning ("rP_calibrate_batch: there are data from different mass spectrometers. Skipping this file...")
		ms = {};
	elseif length(ms) == 0
		warning ("rP_calibrate_batch: found no mass spectrometer data for specified RGA_SRS names. Skipping this file...")
		ms = {};
	else
		ms = ms{1};
	end
	
	if ~isempty(ms) % otherwise skip parsing the rest of this file
		% digest SENSORs data:
		for k = 1:length(SENSOR_names)
			sens{k} = rP_digest_step_SENSOR (RAW{i},SENSOR_names{k});
		end
		
		xx.INFO        = info;
		xx.MS          = ms;
		xx.SENSORS     = sens;
	    X = [ X ; xx ];
	end
	

end % for


% *************************************************
% Process calibrations data (standards and blanks):
% *************************************************

% sort out samples, standards, blanks; and determine list of unique mz/detector combinations:
iSTANDARD = iBLANK = iSAMPLE = [];
mz_det = {};	% list of all mz/detector combinations in the data set
for i = 1:length(X)

	switch X(i).INFO.type
		case 'STANDARD'
			iSTANDARD = [ iSTANDARD , i ];
		case 'BLANK'
			iBLANK    = [ iBLANK , i ];
		case 'SAMPLE'
			iSAMPLE   = [ iSAMPLE , i ];
		otherwise
			warning (sprintf("rP_calibrate_batch: unknown analysis type \'%s\' in file %s. Ignoring this step...",X(i).INFO.type,RAW{i}.file))
	end % switch
	
	mz_det = { mz_det{:} X(i).MS.mz_det{:} };
	
end % for

mz_det = unique ( mz_det );

% make sure we've got (enough) STANDARDs and BLANKs:
if isempty(iSTANDARD)
	# check if there are any STANDARDs:
	error ('rP_calibrate_batch: there are no STANDARDs! Aborting...')
elseif length(iSTANDARD) < 2
	# check if there are enough STANDARDs (need at least 2):
	error ('rP_calibrate_batch: there are not enough STANDARDs (need at least two)! Aborting...')
elseif isempty(iBLANK)
	# check if there are any STANDARDs:
	error ('rP_calibrate_batch: there are no BLANKs! Aborting...')
end

% Determine sample names:
for i = 1:length(iSAMPLE)
	SAMPLES{i} = X(iSAMPLE(i)).INFO.name.name;
end % for i = ...


% sort out digested values for all mz/detector combinations
v_standard = v_blank = v_sample = []; % mean values
e_standard = e_blank = e_sample = []; % error-of-the mean values
t_standard = t_blank = t_sample = []; % time stamps


for i = 1:length(mz_det)

	% determine digesting method:
	method = 'MEAN'; % default
	if length(digest_mz_det) > 0
		k = strcmp(mz_det(i),digest_mz_det);
		if any(k)
			method = digest_meth{k};
		end
	end
	method = toupper (method);

	disp (sprintf('rP_calibrate_batch: using %s peak heights for %s...',method,mz_det{i}))

	% standards:
	[v,e,t]    = __filter_by_MZ_DET ( X(iSTANDARD) , mz_det{i} , method );
	v_standard = [ v_standard ; v ];
	e_standard = [ e_standard ; e ];
	t_standard = [ t_standard ; t ];
	
	% blanks:
	[v,e,t]    = __filter_by_MZ_DET ( X(iBLANK)    , mz_det{i} , method );
	v_blank    = [ v_blank ; v ];
	e_blank    = [ e_blank ; e ];
	t_blank    = [ t_blank ; t ];
   
	% samples:
	[v,e,t]    = __filter_by_MZ_DET ( X(iSAMPLE)   , mz_det{i} , method );
	v_sample   = [ v_sample ; v ];
	e_sample   = [ e_sample ; e ];
	t_sample   = [ t_sample ; t ];
		
end % for

% determine mean blanks and subtract from STANDARDs and SAMPLEs:
Bmean = Berr = repmat (0,length(mz_det),1);
for i = 1:length(mz_det)
	Bmean(i) = mean (v_blank(i,:));							% mean blank
	Berr(i)  = std (v_blank(i,:)) / sqrt(length(v_blank(i,:))-1);	% uncertainty of the mean blank
	if length(v_blank(i,:))-1 <= 0
		warning (sprintf('rP_calibrate_batch: not enough BLANKs to determine uncertainty of BLANKs for %s.',mz_det{i}))
	end
	
	% blank-corrected standards:
	V_standard(i,:) = v_standard(i,:) - Bmean(i);
	E_standard(i,:) = sqrt ( e_standard(i,:).^2 + Berr(i).^2 );

	% blank-corrected samples:
	V_sample(i,:) = v_sample(i,:) - Bmean(i);
	E_sample(i,:) = sqrt ( e_sample(i,:).^2 + Berr(i).^2 );
	
end

% plot STANDARD and BLANK data:
if flag_plot_peak_zero
	t1 = min ([ t_standard(:) ; t_blank(:) ; t_sample(:) ]);
	t2 = max ([ t_standard(:) ; t_blank(:) ; t_sample(:) ]);
	dt = (t2-t1)/20; t1 = t1-dt; t2 = t2+dt;
	
	for i = 1:length(mz_det)
		figure()
		subplot (3,1,1)
		plot (t_standard(i,:),v_standard(i,:),'r.-','markersize',MS); axis ([t1 t2]);
		title (sprintf('STANDARDs: %s peak heights',strrep(mz_det{i},'_','\_')))
		set (gca,'xticklabel','')
		subplot (3,1,2)
		plot (t_blank(i,:),v_blank(i,:),'b.','markersize',MS , [t1 t2],[Bmean(i) Bmean(i)],'b-' ); axis ([t1 t2]);
		title (sprintf('BLANKs: %s peak heights',strrep(mz_det{i},'_','\_')))
		set (gca,'xticklabel','')
		subplot (3,1,3)
		plot (t_standard(i,:),V_standard(i,:),'k.-','markersize',MS); axis ([t1 t2]);
		title (sprintf('STANDARDs - mean BLANK: %s peak heights',strrep(mz_det{i},'_','\_')))
	end % for
end


PRESS_standard = repmat(standardgas_pressure_val,size(iSTANDARD));
unit = standardgas_pressure_unit;

% get standard gas info for STANDARDs and determine sensitivities:
S_val = S_err = repmat (NA,length(mz_det),length(iSTANDARD)); % matrices with sensitivities (and their uncertainties) of all mz_det combinations for all STANDARD steps (each row corresponds to one step)
SPECIES = cellstr(repmat('?',length(mz_det),1));
for i = 1:length(mz_det) % determine sensitivities S_val(i,:) / S_err(i,:) for all mz_det cominations
	u   = strsplit(mz_det{i},'_');
	MZ  = str2num(u{1});
	DET = u{2};	
	for j = 1:length(iSTANDARD) % determine blank-corrected sensitivity S_val(i,j) and S_err(i,j) for mz_det{i} in step iSTANDARD(j)
		k = find ( X(iSTANDARD(j)).INFO.standard.mz == MZ );
		if ~isempty(k) % there is (at least) one standard entry for this MZ value
			if length(k) > 1 % don't know how to treat this...
				error (sprintf('rP_calibrate_batch: there are multiple STANDARD entries for the same mz value in STANDARD step %s. Aborting...',X(j).INFO.name))
			else
				SPECIES{i} = [ X(iSTANDARD(j)).INFO.standard.species{k} , ' (' , mz_det{i} , ')' ];
				l = find(strcmp( X(iSTANDARD(j)).MS.mz_det , mz_det{i})); % l is index to mz_det{i} combination in current step/measurement.
				if any(l) % skip if l is empty
					pi = PRESS_standard(j) * X(iSTANDARD(j)).INFO.standard.conc(k); % partial pressure
					if isnan (PRESS_standard(j))
						warning (sprintf('Total gas pressure unknown for STANDARD!'))
					end
					
					% Use blank corrected value and its error divided by corresponding partial pressure of the STANDARD step:
					S_val(i,j) = V_standard(i,j) / pi; 
					S_err(i,j) = E_standard(i,j) / pi;
										
				end % if l = ...
			end % if length(k) > 1
		end % if ~isempty(k)
	end % for j = ...	
end % for i = ...

% plot sensitivities (S_val) vs. time:
if flag_plot_sensitivity
	figure()
	tt = rP_epochtime2datenum (t_standard);
	tt1 = min(min(tt));
	tt2 = max(max(tt));
	dtt = (tt2-tt1)/20; tt1 = tt1-dtt; tt2 = tt2+dtt;

	% S_val: sensitivities, size(S_val,1) = number of mz-detector combinations, size(S_val,2) = number of standards

	if size(S_val,2) == 1
		y = [ S_val repmat(NA,size(S_val)) ];
		m = S_val;
		x = [ tt repmat(NA,size(tt)) ];
	else
		y = S_val;
		m = repmat (NA,1,size(S_val,1));
		for k = 1:size(S_val,1) % loop through all mz-detector combinations
			u = S_val(k,:);
			u = u(~isnan(u));
			if length(u) > 0
				m(k) = mean(u); % mean sensitivity for k-th mz-detector combination
			end
		end
		% m = mean(S_val(~isnan(S_val))')';
		x = tt;
	end
	k = find (m<0);

	expon = round(log10(abs(m')));
	scal = repmat (10.^expon,1,size(S_val,2));
	scal(k,:) = -scal(k,:);

	x0 = min(min(x));
	hours = (x-x0)*24;

	plot (hours',y'./scal','.-','markersize',MS);
	xlabel (sprintf('Time (hours after %s)',datestr(x0)));
	ylabel (sprintf('Sensitivity (A/%s)',unit))
	leg = strrep(SPECIES,'_','');
	for i = 1:length(leg)
		if ( expon(i) ~= 0 )
			if ( expon(i) == 1 )
				leg{i} = sprintf('%s x 10',leg{i});
			else
				leg{i} = sprintf('%s x 10^{%i}',leg{i},expon(i));
			end
		end
	end
	legend (leg,'location','southoutside','orientation','horizontal');
	title ('MS sensitivity vs. time')

end

% convert SAMPLEs peak heights to partial pressures using the S_val and S_err (interpolate in time):
P_val = P_err = repmat (NA,length(mz_det),length(iSAMPLE)); % matrices with sample partial pressures (and their uncertainties) of all mz_det combinations (each row corresponds to one step)
for i = 1:length(mz_det)
	
	tS = t_standard(i,:);
	Sv  = S_val(i,:);
		Se  = S_err(i,:);
	k = find (~isnan(Sv)); tS = tS(k); Sv = Sv(k); Se = Se(k); % remove NA and NaN entries
	if length(Sv) == 0
		warning (sprintf('rP_calibrate_batch: no valid STANDARDs data for %s. Skipping...',mz_det{i}))
	else
		[tS,k] = sort(tS); Sv = Sv(k); Se = Se(k);
		% If necessary, add 'fake' STANDARD steps before first SAMPLE and after last SAMPLE to allow interpolation / bracketing:
		if tS(1) > min(t_sample(i,:))
			tS = [ min(t_sample(i,:))-1 , tS ];
			Sv  = [ Sv(1) , Sv ];
			Se  = [ Se(1) , Se ];
		end % if min() ...
		if tS(end) < max(t_sample(i,:))
			tS = [ tS , max(t_sample(i,:))+1 ];
			Sv  = [ Sv , Sv(end) ];
			Se  = [ Se , Se(end) ];
		end % if min() ...
		
		% sensitivities at SAMPLE analysis times:
		S_smpl_val = interp1 ( tS , Sv , t_sample(i,:) );
		S_smpl_err = interp1 ( tS , Se , t_sample(i,:) );
	
		% sample partial pressures:	
		P_val(i,:) = V_sample(i,:) ./ S_smpl_val ; % V_sample and S_smpl_val are both blank-corrected values
		P_err(i,:) = sqrt ( (e_sample(i,:)./V_sample(i,:)).^2 + (S_smpl_err./S_smpl_val).^2 ) .* P_val(i,:) ; % error from counting statistics (NOT overall reproducibility of analyses!)

	end
end % for i = ...

TIME = t_sample;


% *************************************************
% Plot SAMPLE results vs. time
% *************************************************

if flag_plot_partialpressure
	figure()
	tt = rP_epochtime2datenum (TIME);
	tt1 = min(min(tt));
	tt2 = max(max(tt));
	dtt = (tt2-tt1)/20; tt1 = tt1-dtt; tt2 = tt2+dtt;
	
	if size(P_val,2) == 1
		y = [ P_val repmat(NA,size(P_val)) ];
		m = P_val;
		x = [ tt repmat(NA,size(tt)) ];
	else
		y = P_val;
		m = mean(P_val')';
		x = tt;
	end
	k = find (m<0);
	expon = round(log10(abs(m))); scal = repmat (10.^expon,1,size(P_val,2)); scal(k,:) = -scal(k,:);

	% plot (x',y'./scal','.-','markersize',MS);
	% datetick;
	% xlabel ('Time (UTC)');
	x0 = min(min(x));
	hours = (x-x0)*24;
	plot (hours',y'./scal','.-','markersize',MS);
	xlabel (sprintf('Time (hours after %s)',datestr(x0)));
	
	ylabel (sprintf('Partial pressure (%s)',unit));
	leg = strrep(SPECIES,'_','');
	for i = 1:length(leg)
		if ( expon(i) ~= 0 )
			if ( expon(i) == 1 )
				leg{i} = sprintf('%s x 10',leg{i});
			else
				leg{i} = sprintf('%s x 10^{%i}',leg{i},expon(i));
			end
		end
	end
	legend (leg,'location','southoutside','orientation','horizontal');
	title ('Partial pressures vs. time')

end

if flag_plot_sensitivity || flag_plot_partialpressure
	% workaround for plotting issue with last figure remaining black:
	figure(); pause(0.1); close(); # opening a new figure and then allow some time will allow updating the previous plot, then close the new figure again.
end

% *************************************************
% Write SAMPLE results to data file
% *************************************************

PARTIALPRESSURES.species = SPECIES;
PARTIALPRESSURES.val     = P_val;
PARTIALPRESSURES.err     = P_err;
PARTIALPRESSURES.time    = TIME;
PARTIALPRESSURES.unit    = unit;

% SENSORS data from samples:
SENSORS = {};
for i = 1:length(iSAMPLE)
	SENSORS{i} = X(iSAMPLE(i)).SENSORS; 
end

__write_datafile (...
	SAMPLES,...
	PARTIALPRESSURES,...
	SENSORS,...
	fileparts(data),...
	out_file_name,...
	use_zenity
	)

if wait_exit
	input ("Processing complete! Press ENTER to exit...", "s");
else
	disp ("Processing complete!")
end



endfunction % main function




% ************************************************************************************************************************************************




% ************************************
% ************************************
% helper functions:
% ************************************
% ************************************

function [val,err,t] = __filter_by_MZ_DET (steps,mz_det,method)
% return time series of data measured on specified mz/detector combination (value, error, and datetime)
	val = err = t = [];
	method = toupper(method);
	for j = 1:length(steps)
		k = find(strcmp(steps(j).MS.mz_det,mz_det)); % find index to specified mz_det combination
		if isempty(k)
			warning (sprintf('rP_calibrate_batch: there are no data for %s in file %s!',mz_det,steps(j).INFO.file))
			val = [ val , NA ];
			err = [ err , NA ];
			t   = [ t   , NA ];
		else
			switch method
				case "MEAN"
					val = [ val , steps(j).MS.mean(k)      ];
					err = [ err , steps(j).MS.mean_err(k)  ];
				case "MEDIAN"
					val = [ val , steps(j).MS.median(k)      ];
					err = [ err , steps(j).MS.median_err(k)  ];
				otherwise
					error (sprintf('rP_calibrate_batch: unknown digesting method %s',method))
			end
			t = [ t   , steps(j).MS.time(k) ];
		end % if isempty(k)
	end % for	
endfunction


function __write_datafile (samples,partialpressures,sensors,path,name,use_zenity)
% write processed data to CSV data file

	species = partialpressures.species;
	p_val   = partialpressures.val;
	p_err   = partialpressures.err;
	time    = partialpressures.time;
	p_unit  = partialpressures.unit;

	if isempty (name)
		name = rP_get_output_filename (use_zenity,'Data file for partial pressure data','CSV');
	end

	if isempty(name)
		disp ('rP_calibrate_batch: no file name given, not writing data to file.')
	
	else
	
		% open ASCII file for writing:
		if length(path) == 0
			path = pwd;
		end
		if strcmp(path(end),filesep)
			path = path(1:end-1);
		end


		% open ASCII file for writing:
		[fid,msg] = fopen (name, 'wt');
		if fid == -1
			error (sprintf('rP_calibrate_batch: could not open file for writing (%s).',msg))
		else
		
			disp (sprintf('Writing data to %s...',path))
			
			% write header:
			fprintf (fid,'SAMPLE')
			for j = 1:length(species)
				fprintf (fid,';%s TIME (EPOCH);%s PARTIALPRESSURE (%s);%s PARTIALPRESSURE ERR (%s)',species{j},species{j},p_unit,species{j},p_unit)
			end	
			if ~isempty(sensors)			
				nsens = length(sensors{1});
				for j = 1:nsens

					sns_unit = '???';
					k = 1;
					while k <= length(samples)
						if ischar(sensors{k}{j}.mean_unit)
							if ~strcmp(sensors{k}{j}.mean_unit,'NA')
								sns_unit = sensors{k}{j}.mean_unit;
								k = length(samples) + 1;
							end
						end
						k = k+1;
					end
					if strcmp (sns_unit,'???')
						warning (sprintf('rP_calibrate_batch: could not determine units of %s sensor data.',sensors{1}{j}.sensor))
					end
					fprintf (fid,';%s TIME (EPOCH);%s (%s);%s ERR (%s)',sensors{1}{j}.sensor,sensors{1}{j}.sensor,sns_unit,sensors{1}{j}.sensor,sns_unit)

				end
			end
			
						
			% write data:
			for i = 1:length(samples)
				fprintf (fid,'\n');
				
				% sample name:
				fprintf (fid,'"%s"',samples{i});
				
				% gas partial pressures:
				for j = 1:length(species)				
					fprintf (fid,';%.2f;%g;%g',time(j,i),p_val(j,i),abs(p_err(j,i)))
				end

				% sensor data (if any):
				if ~isempty(sensors)				
					for j = 1:nsens						
						fprintf (fid,';%.2f;%g;%g',sensors{i}{j}.mean_time,sensors{i}{j}.mean,sensors{i}{j}.mean_err)
					end
				end

			end % for i = 

			fclose (fid);

		end % if fid == -1
	end % if isempty(name)
	
endfunction
