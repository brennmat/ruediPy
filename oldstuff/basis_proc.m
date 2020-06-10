% load raw measurements of basis spectra and process (normalise) them and display results

1;

function X = _basisproc (label,f)
	R = rP_read_datafile (f);
	X = rP_digest_step_RGA_SRS (R,'omanRUEDI');
	X.mean_err = X.mean_err/max(X.mean);
	X.mean = X.mean/max(X.mean);
	X.median_err = X.median_err/max(X.median);		
	X.median = X.median/max(X.median);		
	X.gate = R.omanRUEDI.PEAK(1).gate.val;
	uMEAN = uMEDIAN = label;
	mz = [];
	for i = 1:length(X.mz_det)
		v = strsplit (X.mz_det{i},'_');
		uMEAN = sprintf('%s, %s, %g',uMEAN,v{1},X.mean(i));
		uMEDIAN = sprintf('%s, %s, %g',uMEDIAN,v{1},X.median(i));
		mz = [ mz , str2num(v{1}) ];
	end
	disp (sprintf('\nGas=%s, gate=%3f s:\n*MEAN: (%s)\n*MEDIAN: (%s)\n\n', label, X.gate, uMEAN, uMEDIAN))

	% plot peaks:
	figure(1);
	x = [1:50];
	y = repmat(eps,size(x));
	[u,k] = intersect(x,mz);
	y(k) = X.mean;
	h = stairs(x,y);
	hold on
	set(h,'displayname',label,'linewidth',3)

endfunction

figure(1); clf;

% Ar, 2.4s
_basisproc ('Ar','~/ruediPy/branches/deconv/testfiles/basis_measurements/2020-02-04_16-33-34_SAMPLE.txt');
% Ar, 1s
%_basisproc ('Ar','~/ruediPy/branches/deconv/testfiles/basis_measurements/2020-02-04_16-40-29_SAMPLE.txt');
% Ar, 0.1s
%_basisproc ('Ar','~/ruediPy/branches/deconv/testfiles/basis_measurements/2020-02-04_16-52-41_SAMPLE.txt');

% CO2, 2.4s
_basisproc ('CO2','~/ruediPy/branches/deconv/testfiles/basis_measurements/2020-02-04_15-46-08_SAMPLE.txt');
% CO2, 1s
%_basisproc ('CO2','~/ruediPy/branches/deconv/testfiles/basis_measurements/2020-02-04_16-06-30_SAMPLE+1.txt');
% CO2, 0.1s
%_basisproc ('CO2','~/ruediPy/branches/deconv/testfiles/basis_measurements/2020-02-04_16-18-42_SAMPLE.txt');


% CH4, 2.4s
_basisproc ('CH4','~/ruediPy/branches/deconv/testfiles/basis_measurements/2020-02-05_09-05-06_SAMPLE.txt');
% CH4, 1s
%_basisproc ('CH4','~/ruediPy/branches/deconv/testfiles/basis_measurements/2020-02-05_09-12-01_SAMPLE.txt');
% CH4, 0.1s
%_basisproc ('CH4','~/ruediPy/branches/deconv/testfiles/basis_measurements/2020-02-05_09-24-13_SAMPLE.txt');


% Synthetic Air, 2.4S
_basisproc ('AIR','~/ruediPy/branches/deconv/testfiles/basis_measurements/2020-02-05_09-59-25_SAMPLE.txt');
% Synthetic Air, 1s
%_basisproc ('AIR','~/ruediPy/branches/deconv/testfiles/basis_measurements/2020-02-05_10-06-20_SAMPLE.txt');
% Synthetic Air, 0.1s
%_basisproc ('AIR','~/ruediPy/branches/deconv/testfiles/basis_measurements/2020-02-05_10-18-32_SAMPLE.txt');


% N2, 2.4S
_basisproc ('N2','~/ruediPy/branches/deconv/testfiles/basis_measurements/2020-02-05_10-43-45_SAMPLE.txt');
% N2, 1S
%_basisproc ('N2','~/ruediPy/branches/deconv/testfiles/basis_measurements/2020-02-05_10-50-40_SAMPLE.txt');
% N2, 0.1S
%_basisproc ('N2','~/ruediPy/branches/deconv/testfiles/basis_measurements/2020-02-05_11-02-52_SAMPLE.txt');



set(gca,'linewidth',3)

width = 16; height = 8; set(gcf,'PaperUnits','inches','PaperOrientation','landscape','PaperSize',[width,height],'PaperPosition',[0,0,width,height]);

set(gca,'yscale','log')
axis([0 50 1e-5 2])
legend('location','eastoutside');
title('Basis Mass Spectra')
xlabel ('m/z');
ylabel ('Intensity (normalised)')

print ('basis_spectra.eps','-depsc2');
