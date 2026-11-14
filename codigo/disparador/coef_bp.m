function sos = coef_bp(fs)
% Butterworth pasa-banda 1-10 Hz de 2.º orden (requiere Signal Processing Toolbox).
[zz, pp, kk] = butter(2, [1, min(10, 0.45*fs)] / (fs/2), 'bandpass');
sos = zp2sos(zz, pp, kk);
end
