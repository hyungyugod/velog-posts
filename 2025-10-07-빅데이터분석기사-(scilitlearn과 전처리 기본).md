# 📌 1. scikit-learn 주요 모듈

| 분류 | 모듈명 | 설명 | 주요 알고리즘 및 기능 |
|------|---------|------|----------------------|
| **변수 처리** | `sklearn.preprocessing` | 데이터 전처리에 관한 기능 제공 | 표준화, 정규화, 원-핫 인코딩 등 |
| **데이터 분리·검증** | `sklearn.model_selection` | 데이터 분할 및 교차 검증 등 다양한 검증 방법 제공 | 학습용/테스트용 분리, 교차검증(K-Fold), GridSearchCV 등 |
| **평가** | `sklearn.metrics` | 분류·회귀 등의 모델 평가 지표 제공 | Accuracy, Precision, Recall, F1, ROC-AUC, RMSE 등 |
| **지도학습** | `sklearn.linear_model` | 선형회귀 및 로지스틱 회귀 알고리즘 제공 | Linear Regression, Logistic Regression 등 |
|  | `sklearn.svm` | 서포트 벡터 머신 알고리즘 제공 | SVM, SVR 등 |
|  | `sklearn.neighbors` | 인접 이웃 기반 알고리즘 제공 | KNN (K-Nearest Neighbors) |
|  | `sklearn.tree` | 의사결정나무 알고리즘 제공 | Decision Tree |
|  | `sklearn.ensemble` | 앙상블 학습 기법 제공 | 랜덤 포레스트, 그래디언트 부스팅 등 |
| **비지도학습** | `sklearn.cluster` | 군집화 알고리즘 제공 | K-Means, 평균이동, DBSCAN 등 |

<br>

# 📌 2. scikit-learn 주요 알고리즘 요약

| 알고리즘 | 소속 모듈 | 간단한 설명 |
|-----------|-------------|--------------|
| **StandardScaler (표준화)** | `sklearn.preprocessing` | 평균 0, 표준편차 1로 데이터를 변환하여 모델 학습 안정성을 높임 |
| **MinMaxScaler (정규화)** | `sklearn.preprocessing` | 데이터를 0~1 범위로 스케일링하여 크기 차이를 줄임 |
| **OneHotEncoder (원-핫 인코딩)** | `sklearn.preprocessing` | 범주형 데이터를 0과 1의 이진 벡터로 변환함 |
| **train_test_split** | `sklearn.model_selection` | 데이터를 학습용과 테스트용으로 분할함 |
| **KFold / StratifiedKFold(비율유지)** | `sklearn.model_selection` | 교차검증을 수행해 모델의 일반화 성능을 평가함 |
| **GridSearchCV** | `sklearn.model_selection` | 하이퍼파라미터 조합을 자동으로 탐색해 최적의 모델을 찾음 |
| **accuracy_score / precision_score / recall_score** | `sklearn.metrics` | 분류 모델의 정확도, 정밀도, 재현율을 평가함 |
| **f1_score / roc_auc_score** | `sklearn.metrics` | 모델의 종합적 성능과 ROC 곡선 아래 면적(AUC)을 계산함 |
| **mean_squared_error / r2_score** | `sklearn.metrics` | 회귀 모델의 오차 크기 및 설명력(R²)을 평가함 |
| **LinearRegression** | `sklearn.linear_model` | 입력 변수와 출력 변수 간의 선형 관계를 학습함 |
| **LogisticRegression** | `sklearn.linear_model` | 이진 분류를 위한 선형 모델, 확률적 결과를 예측함 |
| **SVM (Support Vector Machine)** | `sklearn.svm` | 초평면을 이용해 데이터를 구분하는 분류/회귀 알고리즘 |
| **SVR (Support Vector Regression)** | `sklearn.svm` | SVM 개념을 회귀 문제에 적용한 알고리즘 |
| **KNN (K-Nearest Neighbors)** | `sklearn.neighbors` | 가장 가까운 K개의 데이터로부터 다수결로 예측함 |
| **DecisionTreeClassifier / Regressor** | `sklearn.tree` | 데이터를 분할해 예측 규칙을 생성하는 트리 기반 모델 |
| **RandomForestClassifier / Regressor** | `sklearn.ensemble` | 여러 결정트리를 조합해 성능을 향상시키는 앙상블 학습 |
| **GradientBoosting** | `sklearn.ensemble` | 이전 모델의 오차를 보완하며 단계적으로 학습하는 부스팅 기법 |
| **AdaBoost** | `sklearn.ensemble` | 약한 분류기를 결합하여 강력한 분류기를 만드는 부스팅 방법 |
| **KMeans** | `sklearn.cluster` | 비지도학습 군집화 알고리즘, 데이터를 K개의 그룹으로 나눔 |
| **MeanShift** | `sklearn.cluster` | 데이터의 밀집도를 기반으로 자동으로 군집 중심을 찾음 |
| **DBSCAN** | `sklearn.cluster` | 밀도 기반 군집화 알고리즘으로, 노이즈와 이상치를 구분함 |

# 📌 3. scikit-learn와 데이터 전처리
### 3-1. 기원
- SciPy (Scientific Python): 수학, 과학, 공학 계산을 위한 핵심 라이브러리이다.
- scikit-learn은 SciPy의 확장 패키지(“sci-kit”) 중 하나로 시작되었다.
- scikit-image → 이미지 처리용
- scikit-bio → 생물정보학용
- scikit-learn → 머신러닝용

| 구성 요소     | 의미                       | 설명                                                                                           |
| --------- | ------------------------ | -------------------------------------------------------------------------------------------- |
| **sci-**  | science (과학)             | 과학적 계산, 즉 **scientific computing**을 의미함. Python에서 NumPy, SciPy와 같은 과학 연산용 라이브러리의 접두어로 자주 쓰임. |
| **-kit**  | toolkit (도구상자)           | 여러 기능을 하나로 묶은 **확장 패키지**를 뜻함. 즉, SciPy를 기반으로 만들어진 “확장 도구 모음”이라는 의미.                          |
| **learn** | machine learning (기계 학습) | 라이브러리의 핵심 기능인 **머신러닝 알고리즘 구현**을 나타냄.                                                         |

### 3-2. 데이터 전처리 준비
- x = df.drop(['grade'], axis = 1) 'grade'라는 열을 삭제한 변수를 독립변수(설명변수) x로 둔다.
- 머신러닝 모델은 입력값 X → 예측값 ŷ을 배우는 구조이다. 즉, 모델은 X를 보고 y를 예측하려고 한다.
- 그래서 실제로 데이터를 학습시킬 때는
- X: 모델이 관찰할 여러 정보 (입력 특징들)
- y: 그 정보로부터 예측해야 할 값 (정답) 이렇게 나누는 게 필수이다.
```py
import pandas as pd
import numpy as np

df = pd.read_csv('https://raw.githubusercontent.com/YoungjinBD/data/main/dat.csv')

x = df.drop(['grade'], axis = 1)
y = df.grade
```

### 3-3. 데이터 분할 - 단순 무작위 샘플링 (sklearn.model_selection from train_test_split)
- train, test의 비율을 설정한 뒤에 데이터를 무작위로 할당하는 방법 (보통 8:2, 7:3으로 분할)
- 만약 데이터가 치우쳐있다면 랜덤 샘플링이더라도 그 치우침을 유지하게 되므로 주의해야한다.
- (292,) : 292개의 원소가 있지만, 열(column) 차원이 따로 없는 1차원 배열이라는 뜻 -> 1열은 생략
- random_state 값을 0 (또는 어떤 숫자든 동일)으로 주면 실행할 때마다 난수가 고정되어 같은 결과를 얻을 수 있다.
- shuffle = True -> 데이터를 섞어서 train과 test로 분할한다. 
- True → 데이터를 무작위로 섞은 뒤 나눔
- False → 순서대로 앞부분은 train, 뒷부분은 test로 나눔
- xx,yy순으로 할당 받아야한다.
```py
from sklearn.model_selection import train_test_split
train_x, test_x, train_y, test_y = train_test_split(x, y, test_size = 0.2,random_state = 0, shuffle = True, stratify = None)
```

### 3-4. 데이터 분할 - 층화 샘플링
- 각 범주별로 단순무작위 샘플링을 한 후에 결합하는 방식으로 데이터셋을 범주의 비율에 맞게 분할한다.
- stratify=df['school']로 비율을 유지할 기준으로 삼을 컬럼을 지정한다.
- value_counts()를 통해 각 범주의 속성값 비율을 바로 확인해볼 수 있다.
- 또 seaborn의 countplot을 활용하여 이 비율을 시각화해서 확인할 수 있다.
```py
import seaborn as sns

train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.2, random_state=0, shuffle=True, stratify=df['school'])

train_x['school'].value_counts(normalize=True)
sns.countplot(train_x, x='school')
```

### 3-5. 결측치 처리 - 평균값, 중앙값, 최빈값 대치 (SimpleImputer)
- df.isna().sum() 로 결측치가 어디에 존재하는지 빠르게 확인한 후 어떻게 처리할지 결정한다.
- impute (동사) → “어떤 원인이나 책임을 ~에게 돌리다(assign or attribute something to someone)”
- 즉, “무언가의 이유나 값을 추정해서 채워넣거나 책임을 전가하다.” 데이터 과학에서는 이는 결측치를 처리하다 라는 말과 같다.
- df['col'] 은 내부적으로 __getitem__ 메서드가 단일 Key를 받았을 때 Series를 반환하도록 설계되어 있고,
- df[['col']] 은 Key를 **리스트(list)**로 받았기 때문에 그 리스트에 해당하는 여러 열을 DataFrame 형태로 반환하도록 되어 있다.
- scikit-learn 같은 라이브러리가 2D 배열 형태를 요구하기 때문에 값을 넘겨줄때 2차원 배열로 넘겨주어야함을 유의해야한다.
- scikit-learn의 거의 모든 변환기(예: SimpleImputer, StandardScaler, MinMaxScaler)가 따르는 공통 패턴인 it(), transform(), fit_transform()에 대해서도 알 필요가 있다. 이는 아래와 같다.

| 메서드                 | 역할                                     | 비유                    |
| ------------------- | -------------------------------------- | --------------------- |
| **fit()**           | 데이터의 **통계적 특성(평균, 분산, 중앙값 등)** 을 “학습”함 | “기준을 배우는 단계”          |
| **transform()**     | 배운 기준을 바탕으로 데이터를 **변환**함               | “배운 기준으로 데이터를 바꾸는 단계” |
| **fit_transform()** | 위 두 단계를 한 번에 수행 (fit + transform)      | “배우고 바로 적용하기”         |

- 하여 처음에 fit()을 통해 기준을 학습하고 이후에는 fit한 기준에 따라 transform을 수행하기만 하면 된다.
- 또한 원본을 훼손하지 않고 여러 결측치 처리를 시험해보기 위해 copy()를 통해 깊은 복사를 수행한다.
```py
from sklearn.impute import SimpleImputer

imputer_mean = SimpleImputer(strategy = 'mean')
train_x1 = train_x.copy()
test_x1 = test_x.copy()

train_x1['goout'] = imputer_mean.fit_transform(train_x1[['goout']])
test_x1['goout'] = imputer_mean.transform(test_x1[['goout']])
```
- 이때 strategy를 median으로 하면 중앙값으로 대치되고 most_frequent로 하면 최빈값으로 대치되는 변환기 객체를 생성해낼 수 있다.

### 3-6. 결측값 처리 - KNN 대치법 (KNNImputer) 
- KNN은 지도학습(Supervised Learning) 알고리즘으로 어떤 새로운 데이터가 들어왔을 때, 그 주변에서 가장 가까운 K개의 데이터를 보고, 다수가 속한 그룹(클래스)을 따라가도록 학습하게 하는 것이다.
- 이를 결측값 채우기에 사용한다면 결측값이 있는 데이터의 다른 속성들과의 거리를 계산해서 가장 가까운 K개의 샘플을 찾고, 그 샘플들의 해당 속성 평균으로 대체하는 방식을 사용한다.
- 따라서 KNN 기반 결측값 대치(KNNImputer)는 “거리(distance)” 를 계산해서 작동하기때문에 숫자형 데이터만 사용해야 한다.
- 하여 우선 데이터셋을 select_dtypes 함수를 이용하여 number 타입과 object로 분리해두고 KNNImputer로 결측값을 대치한 다음에 나중에 pd.concat을 통해 합쳐 주어야한다.
- 이때 대치한 결과값이 판다스의 데이터프레임으로 나오도록 하려면 set_output(transform='pandas') 옵션을 적용해주어야한다.
- 또한 KNNImputer(n_neighbors=5) 생성자에 n_neighbors=5로 참고할 주변 이웃 개수를 정해주어야한다.
- 이후 학습을 진행하고 (fit) 이후 transform을 활용하여 변환한다.
```py
from sklearn.impute import KNNImputer

train_x2 = train_x.copy()
test_x2 = test_x.copy() 

train_x2_num = train_x2.select_dtypes('number')
test_x2_num = test_x2.select_dtypes('number')

train_x2_cat = train_x2.select_dtypes('object')
test_x2_cat = test_x2.select_dtypes('object')

imputer_knn = KNNImputer(n_neighbors=5).set_output(transform='pandas')
train_x2_num = imputer_knn.fit_transform(train_x2_num)
test_x2_num = imputer_knn.transform(test_x2_num)

train_x2 = pd.concat([train_x2_num, train_x2_cat], axis=1)
test_x2 = pd.concat([test_x2_num, test_x2_cat], axis=1)

train_x2.head()
```