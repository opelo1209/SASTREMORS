function [z, fs, canal, orient] = leer_asa_vertical(ruta)
% Lee la componente vertical de un archivo ASA 2.0 (ancho fijo según 'FORMATO DATOS').
fid = fopen(ruta, 'r', 'n', 'ISO-8859-1'); txt = fread(fid, '*char')'; fclose(fid);
txt = strrep(txt, char(13), '');
i = strfind(txt, 'DATOS DE ACELERACION'); hdr = txt(1:i(1)-1);
tok = regexp(hdr, 'FORMATO DATOS.*?:\s*(\d+)\s*F\s*(\d+)\.(\d+)', 'tokens', 'once');
if isempty(tok), nc = 3; w = 10; else, nc = str2double(tok{1}); w = str2double(tok{2}); end
dt = regexp(hdr, 'INTERVALO DE MUESTREO, C1-C6[^:]*:\s*/?\s*([0-9.]+)', 'tokens', 'once');
fs = 1 / str2double(dt{1});
lin = strsplit(txt(i(1):end), newline);
k = find(contains(lin(1:min(8, numel(lin))), 'CANAL-1'), 1);
orient = strsplit(strtrim(lin{k+1}));
s = k + 3;
while s <= numel(lin) && startsWith(lin{s}, '---'), s = s + 1; end
lin = lin(s:end); lin = lin(~cellfun(@(l) isempty(strtrim(l)), lin));
X = nan(numel(lin), nc);
for a = 1:numel(lin)
    l = lin{a};
    for c = 1:nc
        p1 = (c-1)*w + 1; p2 = min(c*w, numel(l));
        if p1 <= p2
            v = strtrim(l(p1:p2));
            if ~isempty(v), X(a, c) = str2double(v); end
        end
    end
end
canal = [];
for c = 1:numel(orient)
    partes = strsplit(upper(orient{c}), ';'); o = partes{end};
    if ~isempty(regexp(o, '^[+-]?V$', 'once')) || any(strcmp(o, {'UP', 'Z'}))
        canal = c; break
    end
end
if isempty(canal), error('Sin canal vertical: %s', ruta); end
z = X(:, canal); z = z(~isnan(z));
end
