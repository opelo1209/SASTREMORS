function ejecutar_experimento2(carpeta)
% Experimento 2: repite comparar_tres_componentes.m (mismos modelos, mismas
% caracteristicas, rng(72,'twister'), AdaBoostM1 con 1000 ciclos) sobre varios
% escenarios. Cada escenario es un archivo escenario_*.csv en esta carpeta.
% carpeta: ruta de ProgramasMary\Red_en_Matlab (contiene c45.m y predict.m).
addpath(carpeta,'-begin');
salida = fileparts(mfilename('fullpath'));
cols = {'pico_abs_gal','rms_gal','integral_acel_cuadrada_gal2_s','media_abs_gal','pico_a_pico_gal'};
extras = {'pico_h_menor','pico_h_mayor','integral_h_menor','integral_h_mayor','integral_tres','log_relacion_potencia'};
modelos = ["C4.5 vertical","C4.5 tres componentes","AdaBoost vertical","AdaBoost tres componentes"];
escenarios = ["E0_original_etiqueta_historica","E1_original_etiqueta_final", ...
              "E2_disparo_corregido","E2c_control_disparo_original", ...
              "E3_onda_P_referencia","E3c_control_disparo_original"];
metricas = {};
predicciones = table();
fprintf('MATLAB %s\n', version);
for e = escenarios
    archivo = fullfile(salida, "escenario_" + e + ".csv");
    datos = readtable(archivo,'TextType','string');
    for t = 1:3
        a = datos(datos.ventana_s==t & datos.periodo=="1964-1999",:);
        b = datos(datos.ventana_s==t & datos.periodo=="2000-2020",:);
        y = a.etiqueta; v = b.etiqueta;
        fprintf('\n%s  ventana %d s: entrenamiento %d (%d positivos), prueba %d (%d positivos)\n', ...
            e, t, height(a), sum(y), height(b), sum(v));
        for modelo = modelos
            campos = cols;
            if endsWith(modelo,"tres componentes"), campos = [cols,extras]; end
            X = a{:,campos}; Z = b{:,campos};
            rng(72,'twister');
            tic;
            try
                p = probar(modelo,X,y,Z); p = p(:);
                assert(numel(p)==numel(v) && all(ismember(p,[0 1])));
                tp=sum(p==1 & v==1); fn=sum(p==0 & v==1);
                fp=sum(p==1 & v==0); tn=sum(p==0 & v==0);
                sens=tp/(tp+fn); fpr=fp/(fp+tn);
                fila = {e,t,modelo,"ok","",height(a),height(b),tp,fn,fp,tn,sens,fpr,(sens+1-fpr)/2};
                bloque = table(repmat(e,numel(v),1),b.archivo,repmat(t,numel(v),1),repmat(modelo,numel(v),1),v,p, ...
                    'VariableNames',{'escenario','archivo','ventana_s','modelo','etiqueta','prediccion'});
                predicciones = [predicciones; bloque]; %#ok<AGROW>
            catch err
                fila = {e,t,modelo,"error",string(err.message),height(a),height(b),NaN,NaN,NaN,NaN,NaN,NaN,NaN};
            end
            metricas(end+1,:) = fila; %#ok<AGROW>
            fprintf('   %-26s %s  EB=%.4f  sens=%.4f  FA=%.4f  (%.0f s) %s\n', modelo, fila{4}, fila{14}, fila{12}, fila{13}, toc, fila{5});
            writetable(cell2table(metricas,'VariableNames',{'escenario','ventana_s','modelo','estado','detalle', ...
                'n_entrenamiento','n_prueba','TP','FN','FP','TN','sensibilidad','tasa_falsas_alarmas','exactitud_balanceada'}), ...
                fullfile(salida,'metricas_experimento2.csv'));
        end
    end
    writetable(predicciones,fullfile(salida,'predicciones_experimento2.csv'));
end
fprintf('\nListo. Archivos: metricas_experimento2.csv y predicciones_experimento2.csv\n');
end

function p = probar(modelo,X,y,Z)
if startsWith(modelo,"C4.5")
    p = predict(c45(X,y),Z);
else
    p = predict(fitcensemble(X,y,'Method','AdaBoostM1','NumLearningCycles',1000),Z);
end
end
