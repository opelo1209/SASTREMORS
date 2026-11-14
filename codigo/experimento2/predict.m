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