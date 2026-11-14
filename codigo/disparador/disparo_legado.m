function [t_disparo, j] = disparo_legado(z, fs, sos)
% Reconstrucción del disparador descrito en la sección 4.2 del manuscrito:
% Butterworth causal 2.º orden 1-10 Hz (estado inicial cero), STA 0.25 s,
% LTA 2 s anterior a la STA, razón >= 4 sostenida 0.10 s. Sin correcciones.
if nargin < 3 || isempty(sos), sos = coef_bp(fs); end
umbral = 4; dur = 0.10;
y = filtro_sos(sos, z(:));
r = razon_sta_lta(y, fs, 0.25, 2.0, 0);
ok = r >= umbral;
k = max(1, redondeo_python(dur*fs));
j = primer_sostenido(ok, k);
if isnan(j), t_disparo = NaN; else, t_disparo = (j-1)/fs; end
end

function r = razon_sta_lta(y, fs, sta, lta, piso)
ns = redondeo_python(sta*fs); nl = redondeo_python(lta*fs); n = numel(y);
c = [0; cumsum(y.^2)];
ii = (ns+nl:n)';
S = (c(ii+1) - c(ii+1-ns)) / ns;
L = (c(ii+1-ns) - c(ii+1-ns-nl)) / nl;
L = max(L, piso);
r = nan(n, 1); r(ii) = S ./ max(L, 1e-20);
end

function j = primer_sostenido(ok, k)
run = conv(double(ok(:)), ones(k, 1));
run = run(1:numel(ok));
j = find(run >= k, 1, 'first');
if isempty(j), j = NaN; end
end
