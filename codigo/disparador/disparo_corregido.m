function [t_disparo, j] = disparo_corregido(z, fs, sos)
% DISPARO_CORREGIDO  Disparador STA/LTA causal corregido (componente vertical).
%   [t_disparo, j] = disparo_corregido(z, fs)        usa butter (Signal Processing Toolbox)
%   [t_disparo, j] = disparo_corregido(z, fs, sos)   usa coeficientes dados (sin toolbox)
%   t_disparo: segundos desde la primera muestra (NaN si no dispara)
%   j        : índice de muestra 1-based del disparo (NaN si no dispara)
%
% Parámetros fijados con la muestra de desarrollo 1964-1999 (no con 2000-2020):
%   Butterworth pasa-banda 1-10 Hz de 2.º orden, causal, iniciado en estado estacionario
%   mediana causal de 3 muestras; STA 0.25 s; LTA 2 s anterior a la STA
%   umbral 5 sostenido 0.20 s; piso del LTA = 0.1*max(0.02 gal, paso de cuantización)^2
%   sin disparos antes de STA + LTA + 0.5 s
if nargin < 3 || isempty(sos), sos = coef_bp(fs); end
umbral = 5; dur = 0.20; sta = 0.25; lta = 2.0; piso_abs = 0.02; k_q = 1;

x = z(:); n = numel(x);
% 1) mediana causal de 3 muestras: elimina picos de una sola muestra
xp = [x(1); x(1); x];
x = median([xp(1:end-2), xp(2:end-1), xp(3:end)], 2);
% 2) filtro causal en estado estacionario (restar x(1) equivale, porque el
%    pasa-banda tiene ganancia DC nula): elimina el transitorio de arranque
y = filtro_sos(sos, x - x(1));
% 3) STA/LTA con piso de ruido
ns = redondeo_python(sta*fs); nl = redondeo_python(lta*fs);
c = [0; cumsum(y.^2)];
ii = (ns+nl:n)';
S = (c(ii+1) - c(ii+1-ns)) / ns;
L = (c(ii+1-ns) - c(ii+1-ns-nl)) / nl;
u = unique(round(x(1:min(n, max(floor(fs), 10))), 6));
if numel(u) > 1, q = min(diff(u)); else, q = 0; end
L = max(L, 0.1*max(piso_abs, k_q*q)^2);
r = nan(n, 1); r(ii) = S ./ max(L, 1e-20);
% 4) no se permite disparar durante el arranque
i0 = ns + nl - 1 + floor(0.5*fs);
ok = r >= umbral; ok(1:min(i0, n)) = false;
% 5) la condición debe sostenerse 'dur' s; el disparo se emite al cumplirse
k = max(1, redondeo_python(dur*fs));
run = conv(double(ok), ones(k, 1)); run = run(1:n);
j = find(run >= k, 1, 'first');
if isempty(j), j = NaN; t_disparo = NaN; else, t_disparo = (j-1)/fs; end
end
