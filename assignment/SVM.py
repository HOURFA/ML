import time
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from mlxtend.plotting import plot_decision_regions


iris = load_iris()
x = iris.data[:100, :2]
t = iris.target[:100]
x_train, x_test, t_train, t_test = train_test_split(x, t, test_size=0.3, random_state=0)
svm = SVC(kernel='linear', C=10.0, random_state=0)
start = time.time()
svm.fit(x_train, t_train)
end = time.time()
print(f"training time: {end - start}")
y_pred = svm.predict(x_test)
print(f"test accuracy: {accuracy_score(t_test, y_pred)}")

plt.title('SVM on Iris')
plt.xlabel('X1')
plt.ylabel('X2')
# draw the hyperplane
plot_decision_regions(x, t, clf=svm, legend=2,colors='red,blue')

plt.show()
