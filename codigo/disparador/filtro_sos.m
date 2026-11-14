function y = filtro_sos(sos, x)
% Filtro en cascada de secciones de 2.º orden con MATLAB base (sin toolbox).
% sos: matriz [b0 b1 b2 a0 a1 a2] por fila. Estado inicial cero.
y = x(:);
for s = 1:size(sos, 1)
    y = filter(sos(s, 1:3), sos(s, 4:6), y);
end
end
