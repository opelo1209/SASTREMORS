function r = redondeo_python(v)
% Redondeo "a par" como round() de Python (12.5 -> 12, 13.5 -> 14), para que los
% tamaños de ventana en muestras coincidan exactamente con la versión en Python.
r = round(v);
if abs(v - fix(v)) == 0.5 && mod(r, 2) == 1
    r = r - sign(v);
end
end
