import neptune.new as neptune
import xgboost as xgb
from neptune.new.integrations.xgboost import NeptuneCallback
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split

# Create run
run = neptune.init(
    project="common/xgboost-integration",
    api_token="ANONYMOUS",
    name="xgb-train",
    tags=["xgb-integration", "train"],
)

# Create neptune callback
neptune_callback = NeptuneCallback(run=run, log_tree=[0, 1, 2, 3])

# Prepare data
X, y = load_boston(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=123
)
dtrain = xgb.DMatrix(X_train, label=y_train)
dval = xgb.DMatrix(X_test, label=y_test)

# Define parameters
model_params = {
    "eta": 0.7,
    "gamma": 0.001,
    "max_depth": 9,
    "objective": "reg:squarederror",
    "eval_metric": ["mae", "rmse"],
}
evals = [(dtrain, "train"), (dval, "valid")]
num_round = 57

# Train the model and log metadata to the run in Neptune
xgb.train(
    params=model_params,
    dtrain=dtrain,
    num_boost_round=num_round,
    evals=evals,
    callbacks=[
        neptune_callback,
        xgb.callback.LearningRateScheduler(lambda epoch: 0.99**epoch),
        xgb.callback.EarlyStopping(rounds=30),
    ],
)
