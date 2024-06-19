import time
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
from dataset.mnist import load_mnist


batch_size = 100;
epoch = 10000;
learning_rate = 0.1;
(x_train, t_train), (x_test, t_test) = load_mnist(normalize=True, one_hot_label=True)
mlp = MLPClassifier(hidden_layer_sizes=(50,), max_iter=epoch, alpha=1e-4,
                    solver='sgd', verbose=10, tol=1e-4, random_state=1,
                    learning_rate_init=learning_rate,batch_size=batch_size)
start = time.time()
mlp.fit(x_train, t_train)
end = time.time()
print(f"training time: {end - start}")
y_pred = mlp.predict(x_test)
print(f"test accuracy: {accuracy_score(t_test, y_pred)}")
