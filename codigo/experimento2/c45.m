function tree = c45(X, y)
    tree = struct('attribute',[],'threshold',[],'left',[],'right',[],'value',[],'num_examples',[]);
    if numel(unique(y)) == 1 % Caso base: todas las muestras tienen la misma clase
        tree.value = y(1);
        tree.num_examples = numel(y); % Establecer el número de ejemplos en la hoja final
    elseif isempty(X) % Caso base: no hay características disponibles
        tree.value = mode(y);
        tree.num_examples = numel(y); % Establecer el número de ejemplos en la hoja final
    else % Caso recursivo: seleccionar la mejor característica y dividir el conjunto de datos
        [best_attr, best_thresh] = select_best_feature(X, y);
        if ~isempty(best_attr) && ~isempty(best_thresh) % Verifica que los valores no estén vacíos
            tree.attribute = best_attr;
            tree.threshold = best_thresh;

            X_left = X(X(:,best_attr) <= best_thresh,:);
            y_left = y(X(:,best_attr) <= best_thresh);
            X_right = X(X(:,best_attr) > best_thresh,:);
            y_right = y(X(:,best_attr) > best_thresh);

            if isempty(X_left) || isempty(X_right)
                tree.value = mode(y); % Establecer el valor de la hoja como la clase mayoritaria
                tree.num_examples = numel(y); % Establecer el número de ejemplos en la hoja final
            else
                tree.left = c45(X_left, y_left);
                tree.right = c45(X_right, y_right);
                
                % Calcular el número de ejemplos en la hoja final como la suma de las hojas izquierda y derecha
                tree.num_examples = tree.left.num_examples + tree.right.num_examples;
            end
        else
            tree.value = mode(y); % En caso de que no se encuentre una separación válida
            tree.num_examples = numel(y); % Establecer el número de ejemplos en la hoja final
        end
    end
end


% Función para seleccionar la mejor característica para dividir el conjunto de datos
function [best_attr, best_thresh] = select_best_feature(X, y)
    n_features = size(X, 2);
    best_attr = [];
    best_thresh = [];
    best_gain = -1;
    for i = 1:n_features
        values = unique(X(:, i));
        for j = 1:numel(values)
            threshold = values(j);
            gain = information_gain(X, y, i, threshold);
            if gain > best_gain
                best_attr = i;
                best_thresh = threshold;
                best_gain = gain;
            end
        end
    end
end


% Función para calcular la ganancia de información de una característica
function gain = information_gain(X, y, attribute, threshold)
    n_samples = size(y,1);
    n_classes = numel(unique(y));
    parent_entropy = entropy(y,n_classes);
    idx_left = X(:,attribute) <= threshold;
    idx_right = X(:,attribute) > threshold;
    if sum(idx_left) == 0 || sum(idx_right) == 0 % No se puede dividir el conjunto de datos
        gain = -Inf;
    else
        child_entropy = sum(idx_left)/n_samples*entropy(y(idx_left),n_classes) + ...
            sum(idx_right)/n_samples*entropy(y(idx_right),n_classes);
        gain = parent_entropy - child_entropy;
    end
end

% Función para calcular la entropía de un conjunto de datos
function entropy_value = entropy(y, n_classes)
    entropy_value = 0;
    for j = 1:n_classes
        p = sum(y==j)/numel(y);
        if p > 0
            entropy_value = entropy_value - p*log2(p);
        end
    end
end

% Función para predecir las clases de un conjunto de datos mediante un árbol de decisión
function y_pred = predict(tree, X)
    n_samples = size(X,1);
    y_pred = zeros(n_samples,1);
    for i = 1:n_samples
        node = tree;
        while isempty(node.value)
            if X(i,node.attribute) <= node.threshold
                node = node.left;
            else
                node = node.right;
            end
        end
        y_pred(i) = node.value;
    end
end


function visualizar_arbol(arbol, atributos_nombres)

    % Función recursiva para visualizar el árbol
    function visualizar_nodo(arbol, nodo_idx, x, y)
        atributo = arbol.atributo(nodo_idx);
        threshold = arbol.threshold(nodo_idx);
        izquierda = arbol.izquierda(nodo_idx);
        derecha = arbol.derecha(nodo_idx);
        valor = arbol.value(nodo_idx);

        if atributo == 0
            % Si el atributo es 0, el nodo es una hoja
            if valor == 0
                label = sprintf('Clase 0\nEjemplos: %d', arbol.num_examples(nodo_idx));
            else
                label = sprintf('Clase 1\nEjemplos: %d', arbol.num_examples(nodo_idx));
            end
            text(x, y, label, 'HorizontalAlignment', 'center');
        else
            % Si el atributo no es 0, el nodo es una división interna
            label = atributos_nombres{atributo};
            text(x, y, label, 'HorizontalAlignment', 'center');
            
            % Visualizar el subárbol izquierdo
            visualizar_nodo(arbol, izquierda, x-1, y-1);
            
            % Visualizar el subárbol derecho
            visualizar_nodo(arbol, derecha, x+1, y-1);
            
            % Dibujar la conexión entre el nodo actual y los subárboles izquierdo y derecho
            line([x, x-1], [y, y-1], 'Color', 'k');
            line([x, x+1], [y, y-1], 'Color', 'k');
        end
    end

    % Definir el tamaño de la figura para que el árbol sea visible
    figure('Position', [100, 100, 800, 600]);
    
    % Visualizar el árbol comenzando desde la raíz
    visualizar_nodo(arbol, 1, 0, 0);
    
    % Ajustar los límites de los ejes para que el árbol se vea bien
    axis equal;
    xlim([-2, 2]);
    ylim([-1, 8]);
    
    % Etiquetas de los ejes
    xlabel('Atributo');
    ylabel('Nivel del árbol');
    
    % Título del gráfico
    title('Árbol de Decisión C4.5');
end