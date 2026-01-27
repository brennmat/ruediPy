function X = rP_digest_step_RGA_SRS (RAW,MS_name,opt)

% function X = rP_digest_step_RGA_SRS (RAW,MS_name,opt)
% 
% Process ("digest") raw PEAK and ZERO data from RGA_SRS mass spectrometer to obatin means and medians of peak heights. This assumes that each datafile corresponds to a single "step" of analysis (i.e., a block of PEAK/ZERO readings corresponding to a given sample, calibration, or blank analyisis). Results can be printed on the terminal and plotted on screen.
% If there is no data for the RGA with the specified name/label, the fields in X are empty.
% If the data files contain any DECONVOLUTION lines, the data will be deconvolved accordingly.
% 
% INPUT:
% RAW: raw data struct (see also OUTPUT of rP_read_datafile)
% MS_name: name / label of RGA_SRS mass spectrometer for which data should be digested (string)
% opt (optional): string or cellstring with keyword(s) to control various behaviours (use defauls if opt is empty). Multiple keywords can be combined in a cellstring.
%	opt = 'showplot' --> show plot(s) of the data (default: no plots are shown)
%	opt = 'printsummary' --> print results to STDOUT (default: don't print anything)
%	opt = 'userwait' --> same as 'printsummary', but wait for user to press a key after printing the results
% 
% OUTPUT:
% X: struct object with "digested" data from file:
%	X.mz_det: mz/detector combination of the digested PEAK-ZERO data (cell string). If interference compensation / deconvolution was applied to the data, the string "deconvolved" is appended to the detector name (example: "15_F" becomes "15_Fdeconvolved"). 
%	X.mean: means of PEAK-ZERO values (for each X.mz value)
%	X.mean_err: errors of X.inens.val data (errors of the means)
%	X.median: medians of PEAK-ZERO values (for each X.mz value)
%	X.median_err: errors of X.inens.val data (errors of the medians)
%	X.unit: unit of X.mean and X.median and their errors (cell string)
%	X.time: epoch time corresponding to X.mean and X.median (mean of PEAK timestamps)
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

if length(RAW) > 1
	error ('rP_digest_step_RGA_SRS: cannot process an array of multiple steps! Please try again with a single step struct...')
end

% init empty data containers for digested data:
% X.type = '?';
X.mz_det = {};
X.mean = [];
X.mean_err = [];
X.median = [];
X.median_err = [];
X.time = [];
X.unit = {};

% X.std = [];
% X.std_unit = {};

% default behaviour:
showplot = false;
printsummary = false;
userwait = false;

if exist('opt','var') % change defaults
	if ~iscellstr(opt)
		opt = {opt};
	end
	if any(strcmp(tolower(opt),'showplot'))
		showplot = true;
	end
	if any(strcmp (tolower(opt),'printsummary'))
		printsummary = true;
	end
	if any(strcmp (tolower(opt),'userwait'))
		userwait = true;
	end
else
	opt = {};
end

% make sure hyphens are treaded correctly:
MS_name = strrep (MS_name,'-','_');

figr = 1;


% get data corresponding to MS_name:
if isfield (RAW,MS_name)
	MS  = getfield (RAW,MS_name);	% MS data
else
	warning (sprintf("rP_digest_step_RGA_SRS: found no MS data for '%s'.",MS_name))
	return
end

% get PEAK and ZERO data:
if isfield (MS,'PEAK')
	P = MS.PEAK; NP = length (P);
else
	P = []; NP = 0;
	warning ('rP_digest_step_RGA_SRS: no PEAKs found!')
end

if isfield (MS,'ZERO')
	Z   = MS.ZERO; NZ = length (Z);	
else
	Z = []; NZ = 0;
	warning ('rP_digest_step_RGA_SRS: no ZEROs found!')
end

% determine PEAK values with associated timestamp, mz, and detector
PEAK_val = PEAK_time = PEAK_mz = [];
PEAK_unit = PEAK_det = {};
for i = 1:NP
    PEAK_time    = [ PEAK_time ; P(i).epochtime ];
    PEAK_mz      = [ PEAK_mz ; P(i).mz ];
    PEAK_val     = [ PEAK_val ; P(i).intensity.val ];
    PEAK_unit{i} = P(i).intensity.unit;
    PEAK_det{i}  = P(i).detector;
end

% determine ZERO values with associated timestamp, mz, and detector
ZERO_val = ZERO_time = ZERO_mz = [];
ZERO_unit = ZERO_det = {};
for i = 1:NZ
    ZERO_time    = [ ZERO_time ; Z(i).epochtime ];
    ZERO_mz      = [ ZERO_mz ; Z(i).mz ];
    ZERO_val     = [ ZERO_val ; Z(i).intensity.val ];
    ZERO_unit{i} = Z(i).intensity.unit;
    ZERO_det{i}  = Z(i).detector;
end

% determine PEAK-ZERO (net peak heights) and calculate mean and error-of-the-mean, for each mz and detector combination
M = unique ( PEAK_mz ); % list of all mz values in data
D = unique ( PEAK_det ); % list of all detectors in data

for iM = 1:length(M) % find all data with mz = M(iM) and process them
    pp = find (PEAK_mz == M(iM)); % index to PEAKs at current mz value
    zz = find (ZERO_mz == M(iM)); % index to ZEROs at current mz value
        
	for iD = 1:length(D) % find all data with detector = D(iD) and process them
		p = find (strcmp(PEAK_det(pp),D{iD})); p = pp(p); % p is index to PEAKs at current mz / detector combination
		z = find (strcmp(ZERO_det(zz),D{iD})); z = zz(z); % z is index to ZEROs at current mz / detector combination
		
		if any(p) % there is PEAK data available for the current mz / detector combination
			
			tp = PEAK_time(p)(:); peaks = PEAK_val(p)(:);
			tz = ZERO_time(z)(:); zeros = ZERO_val(z)(:);
						
			if any(zeros) % inerpolate ZERO values to PEAK timestamps and subtract from PEAK values
									
				[tp,k] = sort(tp); peaks = peaks(k);
				[tz,k] = sort(tz); zeros = zeros(k);				
				
				% keep original ZERO data for plotting
				ZZ = zeros;
				TZ = tz;
				
				% check if ZERO data needs padding for interpolation
				if tz(1) > tp(1)
					tz    = [ tp(1) ; tz ];
					zeros = [ zeros(1) ; zeros ];
				end
				if tz(end) < tp(end)
					tz    = [ tz ; tp(end) ];
					zeros = [ zeros ; zeros(end) ];
				end
	
				h = peaks - interp1(tz,zeros,tp); % peak height = PEAKs - ZEROs
				
			else % there are no ZEROs available, so assume ZERO = 0.0
				warning (sprintf('rP_digest_step_RGA_SRS: found no ZEROs for mz=%i and detector=%s, skipping baseline compensation...',M(iM),D{iD}))
				h = peaks;
			end
			
			% determine mean / error of the mean:
			if length(h) > 1
				e = std (h) / sqrt(length(h)-1);
			else
				warning (sprintf('rP_digest_step_RGA_SRS: found only single PEAK value for mz=%i and detector=%s, cannot determine standard deviation...',M(iM),D{iD}))
				e = NaN;
			end
						
			% store results:
			X.mz_det{end+1}	= sprintf('%i_%s',M(iM),D{iD});
			X.mean			= [ X.mean ; mean(h) ];
			X.mean_err 		= [ X.mean_err ; e ];
			X.median		= [ X.median ; median(h) ];
			X.median_err		= [ X.median_err ; 1.253*e ];
			X.time			= [ X.time ; mean(tp) ] ;
			X.unit{end+1}		= PEAK_unit{p(1)};

			if printsummary % print digest summary			
				disp (sprintf('mz=%i, detector=%s: MEAN = %g +/- %g %s (%s UTC)',...
						M(iM),...
						D{iD},...
						X.mean(end),...
						X.mean_err(end),...
						X.unit{end},...
						datestr(datenum (1970,1,1,0,0) + X.time(end)/86400)))
			end
			
			if showplot	% plot results
				figure(figr); figr = figr+1;
				t1 = min([tp ; tz]);
				t2 = max([tp ; tz]);
				if t2 > t1
					dt = 0.1*(t2-t1);
				else
					dt = 0.1;
				end
				subplot (3,1,1);
				plot (tp-t1,peaks,'r.','markersize',12);
				axis ([-dt t2-t1+dt]);
				ylabel (sprintf('PEAK (%s)',X.unit{end}))
				title (sprintf('PEAKs and ZEROs at mz=%i / detector=%s',M(iM),D{iD}))
				subplot (3,1,2);
				plot (TZ-t1,ZZ,'b.','markersize',12);
				axis ([-dt t2-t1+dt]);
				ylabel (sprintf('ZERO (%s)',X.unit{end}))
				subplot (3,1,3);
				plot (tp-t1,h,'k.','markersize',12 , [-dt t2-t1+dt],[X.mean(end) X.mean(end)],'k-');
				axis ([-dt t2-t1+dt]);
				ylabel (sprintf('PEAK-ZERO (%s)',X.unit{end}))
				xlabel ('Time (s)')
			end
			
		end % if any(p)
	end % for iD = ...
end % for iM = ...


% check for deconvolution instructions:
if isfield (MS,'DECONVOLUTION')

% Aproach:
% * Process additional "helper" peak heights, if any (PEAK_DECONV, ZERO_DECONV)
% * For each DECONVOLUTION line:
% 	* Find all ion-current data from the detector indicated in the DECONVOLUTION line
% 	* Calculate the relative ion-current proportions of the different basis spectra using the data from this detector (even if there is no data from this detector for the target_mz!)
%	* Estimate the RELATIVE ion-curent proportion of the interferences appearing on the target_mz using the linear model (linear combination of the basis spectra at the target_mz): calculate the model estimates with and without including the target_species and compare them.
%	* Correct the ion-curent peak height(s) on target_mz by subtracting the interference proportion (do this for ALL/BOTH detectors!)

	% check for need to process additional deconvolution "helper" data:
	if isfield (MS,'PEAK_DECONV')

		% cobine normal PEAK/ZERO data with "helper" DECONV PEAK/ZERO data, and use the combine data for deconvolution:
		MS_dcv = MS;
		MS_dcv.PEAK = MS_dcv.PEAK_DECONV;
		MS_dcv = rmfield (MS_dcv,'PEAK_DECONV');
		if isfield (MS,'ZERO_DECONV')
			MS_dcv.ZERO = MS_dcv.ZERO_DECONV;
			MS_dcv = rmfield (MS_dcv,'ZERO_DECONV');
		end
		MS_dcv = rmfield (MS_dcv,'DECONVOLUTION');
		RAW_dcv = setfield([],MS_name,MS_dcv);
		X_dcv = rP_digest_step_RGA_SRS (RAW_dcv,MS_name,opt); % determine DECONV helper peak heights

		% clean up time / unit fields (used for backward compatibility only, but not here)
		X_dcv = rmfield (X_dcv,'mean_time');
		X_dcv = rmfield (X_dcv,'mean_unit');

		% combine main and helper peak heights:
		X_dcv.mz_det      = { X.mz_det{:}     X_dcv.mz_det{:} };
		X_dcv.mean        = [ X.mean        ; X_dcv.mean ];
		X_dcv.mean_err    = [ X.mean_err    ; X_dcv.mean_err ];
		X_dcv.median      = [ X.median      ; X_dcv.median ];
		X_dcv.median_err  = [ X.median_err  ; X_dcv.median_err ];
		X_dcv.time        = [ X.time        ; X_dcv.time ];
		X_dcv.unit        = { X.unit{:}       X_dcv.unit{:} };

	else
		% There are no "helper" DECONV peaks, so use the normal PEAK/ZERO data for deconvolution:
		X_dcv = X;
	end
	
	% Deconvolution and peak-height compensation (for each DECONVOLUTION line):
	targets = [];
	for i = 1:length(MS.DECONVOLUTION)

		% check for duplicate m/z values (duplicates not allowed):
		if any(targets == MS.DECONVOLUTION(i).target_mz)
			warning (sprintf('rP_digest_step_RGA_SRS: multiple DECONVOLUTION lines for target_mz = %i found. Ignoring DECONVOLUTION line for species %s at this m/z ratio!',MS.DECONVOLUTION(i).target_mz,MS.DECONVOLUTION(i).target_species))

		% process DECONVOLUTION line:
		else
			
			disp (sprintf ('Deconvolution for %s at m/z=%i, %s detector (MS: %s with %g %s electon energy)...',MS.DECONVOLUTION(i).target_species,MS.DECONVOLUTION(i).target_mz,MS.DECONVOLUTION(i).detector,MS_name,MS.DECONVOLUTION(i).MS_EE.val,MS.DECONVOLUTION(i).MS_EE.unit))

			% add target_mz to list of m/z ratios for compensation
			targets = [ targets ; MS.DECONVOLUTION(i).target_mz ];
			
			% find mz/det values of the sample data in X_dcv:
			s_mz = repmat(NA,size(X_dcv.mz_det));
			s_det = {};
			for j = 1:length(s_mz)
				u = strsplit (X_dcv.mz_det{j},'_');
				s_mz(j) = str2num(u{1});
				s_det{j} = u{2};
			end

			% deconvolution is done using data from the detector specified in the DECONVOLUTION line only, so find the corresponding data:
			kDET = find(strcmp(s_det,MS.DECONVOLUTION(i).detector));
			if isempty(kDET)
				warning (sprintf('rP_digest_step_RGA_SRS: DECONVOLUTION line indicates using data from detector %s, but there is no such data available in the data file. Ignoring DECONVOLUTION line for species %s at m/z=%i ratio!',MS.DECONVOLUTION(i).detector,MS.DECONVOLUTION(i).target_species,MS.DECONVOLUTION(i).target_mz))
			else

				% find the m/z values that are common to s_mzDET and the basis data in the DECONVOLUTION line:
				[mz,k_s,k_b] = intersect(s_mz(kDET)',MS.DECONVOLUTION(i).basis.mz); % mz = m/z ratios that exist both in the data measured with the current detector and in the DECONVOLUTION basis spectra

				% matrix of basis spectra, limited to the m/z ratios in mz:
				B = MS.DECONVOLUTION(i).basis.val(k_b,:);

				% means and medians of sample data, limited to the m/z ratios in mz:
				s_mzDET       = s_mz(kDET(k_s))';
				s_mean        = X_dcv.mean(kDET(k_s));
				s_mean_err    = X_dcv.mean_err(kDET(k_s));
				s_median      = X_dcv.median(kDET(k_s));
				s_median_err  = X_dcv.median_err(kDET(k_s));

				% normalise s_mean and s_median to largest peak:
				s_mean_norm   = max(s_mean);
				s_mean        = s_mean / s_mean_norm;
				s_mean_err    = s_mean_err / s_mean_norm;
				s_median_norm = max(s_median);
				s_median      = s_median / s_median_norm;
				s_median_err  = s_median_err / s_median_norm;


				% determine / estimate errors of ion-current peak-heights:
				% - use error or the mean/median (s_mean_err and s_median_err)
				% - if this yields an unreasonably low error, enforce a reasonable minimum error size
				ERR_REL_MIN   = 0.01; % 1% relative error is about as low as it gets in real-world miniRUEDI analyses (Brennwald et al, ES&T 2016)
				s_mean_err    = sqrt ( (s_mean_err./s_mean).^2 + ERR_REL_MIN.^2 ) .* s_mean;
				s_median_err  = sqrt ( (s_median_err./s_median).^2 + ERR_REL_MIN.^2 ) .* s_median;




				%%%%%%%%%%%%%%%%%%%%%%%%%%%%
				% DECONVOLUTION OF SPECTRA %
				%%%%%%%%%%%%%%%%%%%%%%%%%%%%

				% invert / solve the equation s_mean = a * B
				% where B is the matrix of basis spectra and a is a vector containing the contributions of each basis

				% set up Monte-Carlo replicates for error propagation:
				N = 1000;
				ss_mean_err = repmat (s_mean_err,1,N) .* randn(length(s_mean_err),N);
				ss_mean_err(:,1) = 0;
				ss_mean = repmat (s_mean,1,N) + ss_mean_err;
				ss_median_err = repmat (s_median_err,1,N) .* randn(length(s_median_err),N);
				ss_median_err(:,1) = 0;
				ss_median = repmat (s_median,1,N) + ss_median_err;
				
				% degrees of freedom remaining after fit
				dof = rows(B) - columns(B);
				
				if dof > 0
					% best-fit solution of overdetermined system
					
					% determine weights for the regression fit:
					w_mean   = 1 ./ s_mean_err.^2; 
					w_median = 1 ./ s_median_err.^2;
										
					% Error-weighted least-squares regression (chi2), N Monte-Carlo realisations
					% (the lscov(...) method was confirmed to give the correct result as compared to fminsearch with chi2 target function)
					[a_mean,u,mse_mean] = lscov (B,ss_mean,w_mean);
					a_mean_err   = std(a_mean');
					a_mean       = mean(a_mean');
					mse_mean     = mse_mean(1);
					[a_median,u,mse_median] = lscov (B,ss_median,w_median);
					a_median_err = std(a_median');
					a_median     = mean(a_median');
					mse_median   = mse_median(1);

					% Check "goodness of fit": mse is Chi2 normalised by the number of degrees of freedom: mse = Chi2/dof
					% mse >> 1: either model is not accurate, or data errors are too small
					chi2_mean   = mse_mean*dof;
					chi2_median = mse_median*dof;

					% minimum p-value considered as a "good" fit
					% P_min = 0.05;
					P_min = 1-0.683; % 1-sigma confidence level
					chi2_max = chi2inv(1-P_min,dof) % max. Chi2 value considered as a "good" fit					
					disp (sprintf('Regression fit statistics:\n   * Chi2(MEAN peak heights) = %g\n   * Chi2(MEDIAN peak heights) = %g\n   * Degrees of freedom = %g\n   * Chi2-max(%d %% percentile) = %g',chi2_mean,chi2_median,dof,(1-P_min)*100,chi2_max))
					% re-scale the errors of the fit results (if necessary)
					% note: this is a linear model, and the error-distribution can be assumed to be approximately Gaussian, so the chi2-equation scales by the square of the errors / weights
					if chi2_mean > chi2_max % the fit is not "good", so the data errors are too small (assuming the deconvolution equation system is complete)
						%% disp ('************ Scaling MEAN coefficent errors ************')
						a_mean_err = sqrt (chi2_mean / chi2_max) * a_mean_err;
					end
					if chi2_median > chi2_max % the fit is not "good", so the data errors are too small (assuming the deconvolution equation system is complete)
						%% disp ('************ Scaling MEDIAN coefficent errors ************')
						a_median_err = sqrt (chi2_median / chi2_max) * a_median_err;
					end


				elseif dof == 0
					% exact solution of equation system
					a_mean   = (B\s_mean)';   a_mean_err   = std(ss_mean'/B');
					a_median = (B\s_median)'; a_median_err = std(ss_median'/B');
					disp ('Regression DF = 0. Cannot estimate model uncertainty!')
					
				else
					% underdetermined equation system
					error (sprintf('Cannot deconvolve underdetermined equation sysem (DF = %d).',dof))
				end



				%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
				% COMPENSATION OF INTERFERENCES %
				%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

				% determine relative fraction of target-species contribution to peak height at target mz:
				%% THIS IS NOT RIGHT: k_tgtmz                = find( MS.DECONVOLUTION(i).target_mz == MS.DECONVOLUTION(i).basis.mz ) % index to target mz
				k_tgtmz	= find( MS.DECONVOLUTION(i).target_mz == s_mzDET ); % index to target mz
				k_tgtspecies	= find(strcmp(MS.DECONVOLUTION(i).target_species,MS.DECONVOLUTION(i).basis.species)); % index to target species
				
				frac_mean_target       = ( a_mean(k_tgtspecies) * B(k_tgtmz,k_tgtspecies)' ) / ( a_mean * B(k_tgtmz,:)' );
				frac_mean_target_err   = abs ( a_mean_err(k_tgtspecies) / a_mean(k_tgtspecies) * frac_mean_target );		
				frac_median_target     = ( a_median(k_tgtspecies) * B(k_tgtmz,k_tgtspecies)' ) / ( a_median * B(k_tgtmz,:)' );
				frac_median_target_err = abs ( a_median_err(k_tgtspecies) / a_median(k_tgtspecies) * frac_median_target );

				% make sure compensation fraction is more than 1.0:
				if frac_mean_target > 1
					frac_mean_target = 1;
				end
				if frac_median_target > 1
					frac_median_target = 1;
				end
				
				% make sure compensation is not negative
				if frac_mean_target < 0
					frac_mean_target = 0;
				end
				if frac_median_target < 0
					frac_median_target = 0;
				end
								
				% compensate the (main) peak heights according to the DECONVOLUTION line
				% apply compensation to data in X (not X_dcv):
				done = false;
				for j = 1:length(X.mz_det)
				
					if strcmp ( X.mz_det{j} , sprintf('%d_%s',MS.DECONVOLUTION(i).target_mz,MS.DECONVOLUTION(i).detector) )
						% subtract estimated contribution of interferences:
						X.mean_err(j)   = sqrt (X.mean_err(j)^2 + (frac_mean_target_err * X.mean(j))^2 );
						X.mean(j)       = frac_mean_target * X.mean(j);
						X.median_err(j) = sqrt (X.median_err(j)^2 + (frac_median_target_err * X.median(j))^2 );
						X.median(j)     = frac_median_target * X.median(j);

						X.mz_det{j} = [ X.mz_det{j} 'deconvolved' ];

						disp (sprintf('%s contribution to peak height at m/z=%i (%s detector):',...
							MS.DECONVOLUTION(i).target_species,MS.DECONVOLUTION(i).target_mz,MS.DECONVOLUTION(i).detector))
						disp (sprintf("   * MEAN peak height: (%g +/- %g)%%",frac_mean_target*100,frac_mean_target_err*100))
						disp (sprintf("   * MEDIAN peak height: (%g +/- %g)%%",frac_median_target*100,frac_median_target_err*100))

						done = true;
					end
				end
				
				if ~done
					error ('rP_digest_step_RGA-SRS: did not find the peak that needs compensation. Something is wrong here...')
				end
			end
		end
	end
end


% for backward compatibility:
X.mean_time = X.time;
X.mean_unit = X.unit;
